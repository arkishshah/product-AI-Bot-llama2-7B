from models.pydantic_models import ProductComparison, SephoraProduct
from utils.ingredient_analyzer import IngredientAnalyzer

class ProductComparer:
    def __init__(self, ingredient_analyzer: IngredientAnalyzer):
        self.ingredient_analyzer = ingredient_analyzer
    
    def compare_products(self, product1: SephoraProduct, product2: SephoraProduct) -> ProductComparison:
        similarities = []
        differences = {product1.name: [], product2.name: []}
        
        # Compare basic attributes
        if product1.brand == product2.brand:
            similarities.append(f"Same brand: {product1.brand}")
        else:
            differences[product1.name].append(f"Brand: {product1.brand}")
            differences[product2.name].append(f"Brand: {product2.brand}")
        
        # Compare skin types
        if product1.skin_type and product2.skin_type:
            common_skin_types = set(product1.skin_type) & set(product2.skin_type)
            if common_skin_types:
                similarities.append(f"Suitable for {', '.join(common_skin_types)} skin")
        
        # Compare concerns
        if product1.skincare_concerns and product2.skincare_concerns:
            common_concerns = set(product1.skincare_concerns) & set(product2.skincare_concerns)
            if common_concerns:
                similarities.append(f"Addresses {', '.join(common_concerns)}")
        
        # Compare formulation
        if product1.formulation == product2.formulation:
            similarities.append(f"Same formulation: {product1.formulation}")
        else:
            differences[product1.name].append(f"Formulation: {product1.formulation}")
            differences[product2.name].append(f"Formulation: {product2.formulation}")
        
        # Compare ingredients
        if product1.ingredients and product2.ingredients:
            ingredients1 = set(product1.ingredient_analysis.ingredients_list)
            ingredients2 = set(product2.ingredient_analysis.ingredients_list)
            ingredient_overlap = len(ingredients1 & ingredients2) / len(ingredients1 | ingredients2)
            
            # Compare beneficial ingredients
            if product1.ingredient_analysis and product2.ingredient_analysis:
                common_benefits = set(product1.ingredient_analysis.key_benefits) & \
                                set(product2.ingredient_analysis.key_benefits)
                if common_benefits:
                    similarities.append(f"Shared beneficial ingredients: {', '.join(common_benefits)}")
        else:
            ingredient_overlap = 0
        
        return ProductComparison(
            similarities=similarities,
            differences=differences,
            price_difference=abs(product1.price - product2.price),
            rating_difference=abs((product1.rating or 0) - (product2.rating or 0)),
            ingredient_overlap=ingredient_overlap
        )