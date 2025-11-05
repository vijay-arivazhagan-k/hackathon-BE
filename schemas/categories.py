"""
Pydantic schemas for category endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryCreate(BaseModel):
    """Schema for creating a category"""
    categoryname: str = Field(..., description="Category name (will be converted to uppercase)")
    categorydescription: Optional[str] = Field(None, description="Category description")
    maximumamount: Optional[float] = Field(None, description="Maximum approval amount")
    status: bool = Field(default=True, description="Category status")
    approval_criteria: Optional[str] = Field(None, description="Approval criteria for this category")


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    categoryname: Optional[str] = Field(None, description="Category name")
    categorydescription: Optional[str] = Field(None, description="Category description")
    maximumamount: Optional[float] = Field(None, description="Maximum approval amount")
    status: Optional[bool] = Field(None, description="Category status")
    approval_criteria: Optional[str] = Field(None, description="Approval criteria")
    comments: str = Field(default="Category updated", description="Update comments")


class CategoryResponse(BaseModel):
    """Schema for category response"""
    id: int = Field(..., alias="ID")
    categoryname: str = Field(..., alias="CATEGORYNAME")
    categorydescription: Optional[str] = Field(None, alias="CATEGORYDESCRIPTION")
    maximumamount: Optional[float] = Field(None, alias="MAXIMUMAMOUNT")
    status: bool = Field(default=True, alias="STATUS")
    requestcount: Optional[int] = Field(None, alias="REQUESTCOUNT")
    approval_criteria: Optional[str] = Field(None, alias="APPROVAL_CRITERIA")
    createdon: Optional[str] = Field(None, alias="CREATEDON")
    createdby: Optional[str] = Field(None, alias="CREATEDBY")
    updatedon: Optional[str] = Field(None, alias="UPDATEDON")
    updatedby: Optional[str] = Field(None, alias="UPDATEDBY")
    
    class Config:
        populate_by_name = True
    
    @classmethod
    def model_validate(cls, obj):
        """Validate object from database model"""
        if hasattr(obj, '__dict__'):
            obj = obj.__dict__
        return super().model_validate(obj)


class CategoryHistoryResponse(BaseModel):
    """Schema for category history response"""
    id: int = Field(..., alias="ID")
    category_id: int = Field(..., alias="CATEGORY_ID")
    categoryname: Optional[str] = Field(None, alias="CATEGORYNAME")
    categorydescription: Optional[str] = Field(None, alias="CATEGORYDESCRIPTION")
    maximumamount: Optional[float] = Field(None, alias="MAXIMUMAMOUNT")
    status: Optional[bool] = Field(None, alias="STATUS")
    requestcount: Optional[int] = Field(None, alias="REQUESTCOUNT")
    approval_criteria: Optional[str] = Field(None, alias="APPROVAL_CRITERIA")
    comments: str = Field(..., alias="COMMENTS")
    createdon: Optional[str] = Field(None, alias="CREATEDON")
    createdby: Optional[str] = Field(None, alias="CREATEDBY")
    
    class Config:
        populate_by_name = True
    
    @classmethod
    def model_validate(cls, obj):
        """Validate object from database model"""
        if hasattr(obj, '__dict__'):
            obj = obj.__dict__
        return super().model_validate(obj)


class PaginatedCategories(BaseModel):
    """Schema for paginated category response"""
    items: List[CategoryResponse]
    page: int
    page_size: int
    total: int
