"""
Request schemas for API validation
"""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class RequestBase(BaseModel):
    """Base request model"""
    user_id: str = Field(..., max_length=25)
    total_amount: Optional[float] = Field(None)
    invoice_date: Optional[str] = Field(None)
    invoice_number: Optional[str] = Field(None, max_length=50)
    category_name: Optional[str] = Field(None, max_length=100)
    comments: Optional[str] = Field(None, max_length=4000)
    approvaltype: Optional[str] = Field(default='Auto', max_length=25)
    
    model_config = ConfigDict(populate_by_name=True)


class RequestCreate(RequestBase):
    """Schema for creating a request"""
    pass


class RequestResponse(BaseModel):
    """Schema for request response - returns camelCase fields"""
    id: int = Field(..., alias='ID')
    user_id: str = Field(..., alias='USER_ID')
    total_amount: Optional[float] = Field(None, alias='TOTAL_AMOUNT')
    invoice_date: Optional[str] = Field(None, alias='INVOICE_DATE')
    invoice_number: Optional[str] = Field(None, alias='INVOICE_NUMBER')
    category_name: Optional[str] = Field(None, alias='CATEGORY_NAME')
    current_status: str = Field(..., alias='CURRENT_STATUS')
    comments: Optional[str] = Field(None, alias='COMMENTS')
    approvaltype: str = Field(..., alias='APPROVALTYPE')
    created_on: str = Field(..., alias='CREATED_ON')
    updated_on: str = Field(..., alias='UPDATED_ON')
    created_by: str = Field(..., alias='CREATED_BY')
    updated_by: str = Field(..., alias='UPDATED_BY')
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class RequestStatusUpdate(BaseModel):
    """Schema for updating request status"""
    status: str = Field(..., pattern='^(Pending|Approved|Rejected)$')
    comments: Optional[str] = Field(None, max_length=4000)
    updated_by: Optional[str] = Field(default='Admin', max_length=25)


class RequestHistoryResponse(BaseModel):
    """Schema for request history response"""
    id: int = Field(..., alias='ID')
    request_id: int = Field(..., alias='REQUEST_ID')
    user_id: str = Field(..., alias='USER_ID')
    total_amount: Optional[float] = Field(None, alias='TOTAL_AMOUNT')
    invoice_date: Optional[str] = Field(None, alias='INVOICE_DATE')
    invoice_number: Optional[str] = Field(None, alias='INVOICE_NUMBER')
    category_name: Optional[str] = Field(None, alias='CATEGORY_NAME')
    current_status: str = Field(..., alias='CURRENT_STATUS')
    comments: Optional[str] = Field(None, alias='COMMENTS')
    approvaltype: str = Field(..., alias='APPROVALTYPE')
    created_on: str = Field(..., alias='CREATED_ON')
    updated_on: str = Field(..., alias='UPDATED_ON')
    created_by: str = Field(..., alias='CREATED_BY')
    updated_by: str = Field(..., alias='UPDATED_BY')
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PaginatedRequests(BaseModel):
    """Schema for paginated requests response"""
    items: List[RequestResponse]
    page: int
    page_size: int
    total: int


class InsightsResponse(BaseModel):
    """Schema for insights response"""
    total: int
    approved: int
    rejected: int
    pending: int
    status_breakdown: dict = {}