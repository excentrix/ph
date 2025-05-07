from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class BaseSchema(BaseModel):
    """Base schema with common fields."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
class StandardResponse(BaseModel):
    """Standard API response format."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[dict] = None
