import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
from models.pydantic_models import SephoraProduct, ProductComparison
from utils.ingredient_analyzer import IngredientAnalyzer
from utils.product_comparer import ProductComparer

class ProductRecommender:
    def __init__(self, data_path: str):
        self.df = pd.read_csv(data_path)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.ingredient_analyzer = IngredientAnalyzer()
        self.product_comparer = ProductComparer(self.ingredient_analyzer)
        self.product_embeddings = None
        self._preprocess_data()
        self._compute_embeddings()
    
    def _preprocess_data(self):
        """Preprocess the raw Sephora data"""
        # Handle missing values
        self.df['description'] = self.df['description'].fillna('')
        self.df['ingredients'] = self.df['ingredients'].fillna('')
        self.df['brand'] = self.df['brand'].fillna('')
        self.df['name'] = self.df['name'].fillna('')
        self.df['Category'] = self.df['Category'].fillna('')
        
        # Clean price - remove currency symbol and convert to float
        if 'price' in self.df.columns:
            self.df['price'] = self.df['price'].apply(lambda x: 
                float(str(x).replace('$', '').replace(',', '')) if pd.notnull(x) else 0.0
            )
        
        # Clean ratings
        if 'rating' in self.df.columns:
            self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce').fillna(0.0)
        if 'reviews' in self.df.columns:
            self.df['reviews'] = pd.to_numeric(self.df['reviews'], errors='coerce').fillna(0)
        
        # Extract structured data from description
        descriptions = self.df['description'].apply(self._extract_from_description)
        
        # Add extracted columns with proper handling
        self.df['skin_type'] = descriptions.apply(lambda x: x.get('skin_type', []))
        self.df['skincare_concerns'] = descriptions.apply(lambda x: x.get('skincare_concerns', []))
        self.df['formulation'] = descriptions.apply(lambda x: x.get('formulation', ''))
        
        # Analyze ingredients
        print("Analyzing ingredients...")
        self.df['ingredient_analysis'] = self.df['ingredients'].apply(
            self.ingredient_analyzer.analyze_ingredients
        )
        print("Finished analyzing ingredients")

    def _extract_from_description(self, description: str) -> Dict:
        """Extract structured information from HTML description"""
        if not isinstance(description, str):
            return {'skin_type': [], 'skincare_concerns': [], 'formulation': ''}
            
        try:
            soup = BeautifulSoup(description, 'html.parser')
            text = soup.get_text()
            
            extracted = {
                'skin_type': [],
                'skincare_concerns': [],
                'formulation': ''
            }
            
            # Extract skin type
            if 'Skin Type:' in text:
                skin_type_text = text.split('Skin Type:')[1].split('<br>')[0].strip()
                extracted['skin_type'] = [t.strip() for t in skin_type_text.split(',')]
            
            # Extract skincare concerns
            if 'Skincare Concerns:' in text:
                concerns_text = text.split('Skincare Concerns:')[1].split('<br>')[0].strip()
                extracted['skincare_concerns'] = [c.strip() for c in concerns_text.split(',')]
            
            # Extract formulation
            if 'Formulation:' in text:
                formulation_text = text.split('Formulation:')[1].split('<br>')[0].strip()
                extracted['formulation'] = formulation_text
            
            return extracted
            
        except Exception as e:
            print(f"Error extracting from description: {str(e)}")
            return {'skin_type': [], 'skincare_concerns': [], 'formulation': ''}

    def _apply_filters(self, mask: np.ndarray, filters: Dict) -> np.ndarray:
        """Apply filters to the product selection"""
        if not filters:
            return mask
            
        for key, value in filters.items():
            if key == 'price_range' and isinstance(value, list) and len(value) == 2:
                mask &= (self.df['price'] >= float(value[0])) & (self.df['price'] <= float(value[1]))
            elif key == 'skin_type' and value:
                mask &= self.df['skin_type'].apply(lambda x: value in x if isinstance(x, list) else False)
            elif key == 'concerns' and value:
                mask &= self.df['skincare_concerns'].apply(lambda x: value in x if isinstance(x, list) else False)
            elif key == 'brand' and value:
                mask &= self.df['brand'].str.contains(str(value), case=False, na=False)
            elif key == 'rating_min' and value:
                mask &= self.df['rating'] >= float(value)
        return mask

    def find_similar_products(
        self,
        query: str,
        filters: Optional[Dict] = None,
        excluded_ingredients: Optional[List[str]] = None,
        n_results: int = 3
    ) -> List[SephoraProduct]:
        """Find products based on query and filters"""
        # Get query embedding
        query_embedding = self.embedding_model.encode([query])
        similarities = np.dot(self.product_embeddings, query_embedding.T).squeeze()
        
        # Initialize mask
        mask = np.ones(len(self.df), dtype=bool)
        
        # Apply filters if provided
        if filters:
            try:
                mask = self._apply_filters(mask, filters)
            except Exception as e:
                print(f"Error applying filters: {str(e)}")
        
        # Apply ingredient exclusions if provided
        if excluded_ingredients:
            for ingredient in excluded_ingredients:
                mask &= ~self.df['ingredients'].str.contains(str(ingredient), case=False, na=False)
        
        # Get top results considering filters
        filtered_similarities = similarities.copy()
        filtered_similarities[~mask] = -np.inf
        top_indices = np.argsort(filtered_similarities)[-n_results:][::-1]
        
        # Convert to product models
        return [self._create_product_model(self.df.iloc[i]) for i in top_indices]

    def _create_product_model(self, row: pd.Series) -> SephoraProduct:
        """Convert DataFrame row to Pydantic model with proper type handling"""
        return SephoraProduct(
            pid=str(row['pid']),  # Ensure pid is string
            name=str(row['name']),
            brand=str(row['brand']),
            price=float(row['price']) if pd.notnull(row['price']) else 0.0,
            category=str(row.get('Category', '')),
            description=str(row['description']),
            rating=float(row['rating']) if pd.notnull(row['rating']) else None,
            reviews=int(row['reviews']) if pd.notnull(row['reviews']) else None,
            ingredients=str(row['ingredients']) if pd.notnull(row['ingredients']) else '',
            skin_type=row['skin_type'] if isinstance(row['skin_type'], list) else [],
            skincare_concerns=row['skincare_concerns'] if isinstance(row['skincare_concerns'], list) else [],
            formulation=str(row.get('formulation', '')),
            ingredient_analysis=row['ingredient_analysis']
        )

    def _compute_embeddings(self):
        """Compute embeddings for all products"""
        product_texts = self.df.apply(
            lambda x: f"{x['name']} {x['brand']} {x['description']} " + 
                     f"{' '.join(x['skin_type'] if isinstance(x['skin_type'], list) else [])} " +
                     f"{' '.join(x['skincare_concerns'] if isinstance(x['skincare_concerns'], list) else [])}",
            axis=1
        ).tolist()
        
        self.product_embeddings = self.embedding_model.encode(
            product_texts,
            show_progress_bar=True
        )
        