from typing import List, Dict, Optional, Union  # Added Optional
from models.pydantic_models import IngredientAnalysis
import pandas as pd

class IngredientAnalyzer:
    def __init__(self):
        self.potentially_harmful = {
            'parabens': ['methylparaben', 'propylparaben', 'butylparaben'],
            'sulfates': ['sodium lauryl sulfate', 'sodium laureth sulfate'],
            'phthalates': ['dibutyl phthalate', 'diethyl phthalate'],
            'formaldehyde': ['quaternium-15', 'dmdm hydantoin', 'imidazolidinyl urea']
        }
        
        self.common_allergens = [
            'fragrance', 'parfum', 'essential oils', 'lanolin', 
            'propylene glycol', 'methylisothiazolinone'
        ]
        
        self.beneficial_ingredients = {
            'hydrating': ['hyaluronic acid', 'glycerin', 'ceramides', 'squalane'],
            'antioxidants': ['vitamin c', 'vitamin e', 'niacinamide', 'green tea'],
            'exfoliating': ['salicylic acid', 'glycolic acid', 'lactic acid'],
            'soothing': ['aloe vera', 'centella asiatica', 'chamomile', 'allantoin']
        }
    
    def analyze_ingredients(self, ingredients_str: Union[str, float]) -> Optional[IngredientAnalysis]:
        """Analyze ingredients string and return structured analysis"""
        # Handle empty or invalid input
        if pd.isna(ingredients_str) or not isinstance(ingredients_str, str) or not ingredients_str.strip():
            return IngredientAnalysis(
                ingredients_list=[],
                potentially_harmful=[],
                key_benefits=[],
                common_allergens=[]
            )
            
        # Process valid ingredients string
        try:
            ingredients_list = [i.strip().lower() for i in ingredients_str.split(',')]
            
            # Find potentially harmful ingredients
            harmful = []
            for category, ingredients in self.potentially_harmful.items():
                found = [i for i in ingredients if any(i in ing.lower() for ing in ingredients_list)]
                if found:
                    harmful.extend(found)
            
            # Find allergens
            allergens = [a for a in self.common_allergens 
                        if any(a in ing.lower() for ing in ingredients_list)]
            
            # Find beneficial ingredients
            benefits = []
            for benefit, ingredients in self.beneficial_ingredients.items():
                found = [i for i in ingredients if any(i in ing.lower() for ing in ingredients_list)]
                if found:
                    benefits.append(f"{benefit.title()}: {', '.join(found)}")
            
            return IngredientAnalysis(
                ingredients_list=ingredients_list,
                potentially_harmful=harmful,
                key_benefits=benefits,
                common_allergens=allergens
            )
            
        except Exception as e:
            print(f"Error processing ingredients: {str(e)}")
            return IngredientAnalysis(
                ingredients_list=[],
                potentially_harmful=[],
                key_benefits=[],
                common_allergens=[]
            )