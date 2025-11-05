"""
Category API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Query, Form
from fastapi.responses import JSONResponse
from typing import Optional
from schemas.categories import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryHistoryResponse,
    PaginatedCategories
)
from services.category_service import CategoryService
import io


router = APIRouter(prefix="/api/categories", tags=["categories"])
service = CategoryService()


def serialize_response(model_or_list, exclude_aliases=True):
    """Helper to serialize Pydantic models without aliases (using field names)"""
    if isinstance(model_or_list, list):
        return [m.model_dump(by_alias=False, exclude_none=False) if hasattr(m, 'model_dump') else m 
                for m in model_or_list]
    elif hasattr(model_or_list, 'model_dump'):
        return model_or_list.model_dump(by_alias=False, exclude_none=False)
    return model_or_list


def db_to_dict(db_obj):
    """Convert database object to dictionary"""
    if hasattr(db_obj, '__dict__'):
        return {k: v for k, v in db_obj.__dict__.items() if not k.startswith('_')}
    return dict(db_obj)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    categoryname: str = Form(...),
    categorydescription: Optional[str] = Form(None),
    maximumamount: Optional[float] = Form(None),
    status_param: bool = Form(default=True),
    approval_criteria: str = Form(...)
):
    """
    Create a new category
    
    Args:
        categoryname: Category name (will be converted to uppercase)
        categorydescription: Category description
        maximumamount: Maximum approval amount
        status_param: Category status (enabled/disabled)
        approval_criteria: Approval criteria for this category
        
    Returns:
        CategoryResponse: Created category
    """
    # Validate
    validation = service.validate_category_data(categoryname, maximumamount, approval_criteria)
    if not validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation['errors']
        )
    
    # Convert categoryname to uppercase
    categoryname_upper = categoryname.upper()
    
    try:
        cat = service.create_category(
            categoryname_upper, categorydescription, maximumamount, status_param,
            approval_criteria, created_by='ADMIN'
        )
        
        response = {
            'id': cat.ID,
            'categoryname': cat.CATEGORYNAME,
            'categorydescription': cat.CATEGORYDESCRIPTION,
            'maximumamount': cat.MAXIMUMAMOUNT,
            'status': cat.STATUS,
            'requestcount': cat.REQUESTCOUNT,
            'approval_criteria': cat.APPROVAL_CRITERIA,
            'createdon': cat.CREATEDON,
            'createdby': cat.CREATEDBY,
            'updatedon': cat.UPDATEDON,
            'updatedby': cat.UPDATEDBY,
        }
        
        print(f"Created category: {cat.CATEGORYNAME} (ID: {cat.ID}) with approval criteria: {cat.APPROVAL_CRITERIA}")
        return JSONResponse(content=response, status_code=201)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating category: {str(e)}"
        )


@router.get("/", response_model=PaginatedCategories)
async def list_categories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100)
):
    """
    List all categories with pagination
    
    Args:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        
    Returns:
        PaginatedCategories: Paginated categories
    """
    try:
        categories, total = service.list_categories(page, page_size)
        
        items = []
        for cat in categories:
            items.append({
                'id': cat.ID,
                'categoryname': cat.CATEGORYNAME,
                'categorydescription': cat.CATEGORYDESCRIPTION,
                'maximumamount': cat.MAXIMUMAMOUNT,
                'status': cat.STATUS,
                'requestcount': cat.REQUESTCOUNT,
                'approval_criteria': cat.APPROVAL_CRITERIA,
                'createdon': cat.CREATEDON,
                'createdby': cat.CREATEDBY,
                'updatedon': cat.UPDATEDON,
                'updatedby': cat.UPDATEDBY,
            })
        
        return JSONResponse(content={
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total
        })
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing categories: {str(e)}"
        )


@router.get("/{category_id}")
async def get_category(category_id: int):
    """
    Get category by ID
    
    Args:
        category_id: Category ID
        
    Returns:
        CategoryResponse: Category details
        
    Raises:
        HTTPException: 404 if category not found
    """
    try:
        cat = service.get_category(category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )
        
        response = {
            'id': cat.ID,
            'categoryname': cat.CATEGORYNAME,
            'categorydescription': cat.CATEGORYDESCRIPTION,
            'maximumamount': cat.MAXIMUMAMOUNT,
            'status': cat.STATUS,
            'requestcount': cat.REQUESTCOUNT,
            'approval_criteria': cat.APPROVAL_CRITERIA,
            'createdon': cat.CREATEDON,
            'createdby': cat.CREATEDBY,
            'updatedon': cat.UPDATEDON,
            'updatedby': cat.UPDATEDBY,
        }
        
        return JSONResponse(content=response)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching category: {str(e)}"
        )


@router.patch("/{category_id}")
async def update_category(
    category_id: int,
    categoryname: Optional[str] = Form(None),
    categorydescription: Optional[str] = Form(None),
    maximumamount: Optional[float] = Form(None),
    status_param: Optional[bool] = Form(None),
    approval_criteria: str = Form(...),
    comments: str = Form(default="Category updated")
):
    """
    Update category
    
    Args:
        category_id: Category ID
        categoryname: Category name (will be converted to uppercase)
        categorydescription: Category description
        maximumamount: Maximum approval amount
        status_param: Category status
        approval_criteria: Approval criteria
        comments: Update comments
        
    Returns:
        CategoryResponse: Updated category
        
    Raises:
        HTTPException: 404 if category not found
    """
    try:
        # Check if category exists
        existing = service.get_category(category_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )
        
        # Validate approval criteria and other fields for update
        validation = service.validate_category_data(categoryname, maximumamount, approval_criteria)
        if not validation['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation['errors']
            )

        # Convert categoryname to uppercase if provided
        categoryname_upper = categoryname.upper() if categoryname else None
        
        cat = service.update_category(
            category_id, categoryname_upper, categorydescription, maximumamount,
            status_param, approval_criteria, comments, 'ADMIN'
        )
        
        response = {
            'id': cat.ID,
            'categoryname': cat.CATEGORYNAME,
            'categorydescription': cat.CATEGORYDESCRIPTION,
            'maximumamount': cat.MAXIMUMAMOUNT,
            'status': cat.STATUS,
            'requestcount': cat.REQUESTCOUNT,
            'approval_criteria': cat.APPROVAL_CRITERIA,
            'createdon': cat.CREATEDON,
            'createdby': cat.CREATEDBY,
            'updatedon': cat.UPDATEDON,
            'updatedby': cat.UPDATEDBY,
        }
        
        return JSONResponse(content=response)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating category: {str(e)}"
        )


@router.get("/{category_id}/history")
async def get_category_history(category_id: int):
    """
    Get category history
    
    Args:
        category_id: Category ID
        
    Returns:
        List[CategoryHistoryResponse]: Category history
    """
    try:
        # First check if category exists
        cat = service.get_category(category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )
        
        history = service.get_category_history(category_id)
        
        items = []
        for h in history:
            items.append({
                'id': h.ID,
                'category_id': h.CATEGORY_ID,
                'categoryname': h.CATEGORYNAME,
                'categorydescription': h.CATEGORYDESCRIPTION,
                'maximumamount': h.MAXIMUMAMOUNT,
                'status': h.STATUS,
                'requestcount': h.REQUESTCOUNT,
                'approval_criteria': h.APPROVAL_CRITERIA,
                'comments': h.COMMENTS,
                'createdon': h.CREATEDON,
                'createdby': h.CREATEDBY,
            })
        
        return JSONResponse(content=items)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching category history: {str(e)}"
        )
