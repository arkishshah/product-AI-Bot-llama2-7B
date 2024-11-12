import re
from typing import List, Optional, Dict
from models.pydantic_models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ProductComparison,
    SephoraProduct
)
from utils.product_recommender import ProductRecommender

class ChatHandler:
    def __init__(self, recommender: ProductRecommender):
        self.recommender = recommender
    
    def _extract_filters(self, message: str) -> Dict:
        """Extract filters from user message"""
        filters = {}
        
        # Extract price range
        price_match = re.search(r'under\s*\$(\d+)', message.lower())
        if price_match:
            filters['price_range'] = [0, float(price_match.group(1))]
        
        # Extract skin type
        skin_types = ['dry', 'oily', 'combination', 'sensitive', 'normal']
        for skin_type in skin_types:
            if skin_type in message.lower():
                filters['skin_type'] = skin_type
                break
        
        return filters
    
    def _extract_ingredient_exclusions(self, message: str) -> List[str]:
        """Extract ingredients to exclude"""
        excluded = []
        patterns = [
            r"without\s+([\w\s,]+)",
            r"exclude\s+([\w\s,]+)",
            r"no\s+([\w\s,]+)",
            r"avoid\s+([\w\s,]+)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message.lower())
            if matches:
                excluded.extend(
                    [ing.strip() for ing in ' '.join(matches).split(',')]
                )
        
        return excluded

    def _format_product_response(
        self, 
        products: List[SephoraProduct], 
        excluded_ingredients: Optional[List[str]] = None
    ) -> str:
        """Format the response with product recommendations"""
        if not products:
            return "I couldn't find any products matching your criteria. Could you try with different requirements?"
        
        response = f"I found some products that match your needs. The top recommendation is {products[0].name} "
        response += f"by {products[0].brand} (${products[0].price:.2f}). "
        
        if products[0].rating:
            response += f"It has a rating of {products[0].rating}/5 based on {products[0].reviews} reviews. "
        
        if products[0].skin_type:
            response += f"It's suitable for {', '.join(products[0].skin_type)} skin types. "
        
        if excluded_ingredients:
            response += f"As requested, this product doesn't contain {', '.join(excluded_ingredients)}. "
        
        if len(products) > 1:
            response += f"\n\nAlternative options include: "
            for product in products[1:]:
                response += f"\n- {product.name} by {product.brand} (${product.price:.2f})"
        
        return response
    
    def _format_comparison_response(self, comparison: ProductComparison) -> str:
        """Format the product comparison response"""
        response = "Here's how these products compare:\n\n"
        
        if comparison.similarities:
            response += "Similarities:\n"
            for similarity in comparison.similarities:
                response += f"- {similarity}\n"
        
        response += "\nDifferences:\n"
        for product, differences in comparison.differences.items():
            if differences:
                response += f"\n{product}:\n"
                for diff in differences:
                    response += f"- {diff}\n"
        
        response += f"\nPrice difference: ${comparison.price_difference:.2f}"
        if comparison.rating_difference > 0:
            response += f"\nRating difference: {comparison.rating_difference:.1f} stars"
        
        if comparison.ingredient_overlap > 0:
            response += f"\nIngredient similarity: {comparison.ingredient_overlap*100:.1f}%"
        
        return response

    def handle_chat(self, request: ChatRequest) -> ChatResponse:
        """Handle incoming chat requests"""
        current_message = request.messages[-1].content
        
        # Check for comparison request
        comparison_match = re.search(r'compare\s+(\w+)\s+and\s+(\w+)', current_message.lower())
        if comparison_match:
            product1_id, product2_id = comparison_match.groups()
            comparison = self.recommender.compare_products(product1_id, product2_id)
            response = self._format_comparison_response(comparison)
            return ChatResponse(response=response, comparison=comparison)
        
        # Extract filters and exclusions
        filters = request.filters or self._extract_filters(current_message)
        excluded_ingredients = request.excluded_ingredients or self._extract_ingredient_exclusions(current_message)
        
        # Get recommendations
        recommended_products = self.recommender.find_similar_products(
            query=current_message,
            filters=filters,
            excluded_ingredients=excluded_ingredients
        )
        
        # Format and return response
        response = self._format_product_response(recommended_products, excluded_ingredients)
        return ChatResponse(response=response, products=recommended_products)