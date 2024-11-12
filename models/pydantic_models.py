from pydantic import BaseModel
from typing import List, Optional, Dict, Union

# Base message model
class ChatMessage(BaseModel):
    role: str
    content: str

# Product-related models
class IngredientAnalysis(BaseModel):
    ingredients_list: List[str]
    potentially_harmful: List[str]
    key_benefits: List[str]
    common_allergens: List[str]

class ProductComparison(BaseModel):
    similarities: List[str]
    differences: Dict[str, List[str]]
    price_difference: float
    rating_difference: float
    ingredient_overlap: float

class SephoraProduct(BaseModel):
    pid: str
    name: str
    brand: str
    price: float
    category: str
    description: str
    rating: Optional[float]
    reviews: Optional[int]
    ingredients: Optional[str]
    skin_type: Optional[List[str]]
    skincare_concerns: Optional[List[str]]
    formulation: Optional[str]
    ingredient_analysis: Optional[IngredientAnalysis]

# Request/Response models
class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    filters: Optional[Dict[str, Union[str, List[str], List[float]]]] = None
    excluded_ingredients: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    products: Optional[List[SephoraProduct]] = None
    comparison: Optional[ProductComparison] = None