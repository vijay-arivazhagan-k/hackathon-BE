"""
Category service for business logic
"""
from typing import Optional, List, Tuple
from database_categories import CategoryRepository, Category, CategoryHistory


class CategoryService:
    """Service for category business logic"""
    
    def __init__(self):
        self.repository = CategoryRepository()
    
    def create_category(self, categoryname: str, categorydescription: Optional[str] = None,
                       maximumamount: Optional[float] = None, status: bool = True,
                       approval_criteria: Optional[str] = None,
                       created_by: str = 'ADMIN') -> Category:
        """Create a new category"""
        return self.repository.create_category(
            categoryname, categorydescription, maximumamount, status,
            approval_criteria, created_by
        )
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.repository.get_category(category_id)
    
    def update_category(self, category_id: int, categoryname: Optional[str] = None,
                       categorydescription: Optional[str] = None, maximumamount: Optional[float] = None,
                       status: Optional[bool] = None, approval_criteria: Optional[str] = None,
                       comments: str = "Category updated",
                       updated_by: str = 'ADMIN') -> Optional[Category]:
        """Update category"""
        return self.repository.update_category(
            category_id, categoryname, categorydescription, maximumamount,
            status, approval_criteria, comments, updated_by
        )
    
    def list_categories(self, page: int = 1, page_size: int = 20) -> Tuple[List[Category], int]:
        """List categories with pagination"""
        return self.repository.list_categories(page, page_size)
    
    def get_category_history(self, category_id: int) -> List[CategoryHistory]:
        """Get category history"""
        return self.repository.get_category_history(category_id)
    
    def validate_category_data(self, categoryname: Optional[str] = None,
                              maximumamount: Optional[float] = None,
                              approval_criteria: Optional[str] = None) -> dict:
        """Validate category data"""
        errors = []
        
        if not categoryname or categoryname.strip() == '':
            errors.append('Category name is required')
        
        if not approval_criteria or approval_criteria.strip() == '':
            errors.append('Approval criteria is required')
        
        if maximumamount is not None and maximumamount < 0:
            errors.append('Maximum amount must be a positive number')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
