"""
Category service for business logic
"""
from typing import Optional, List, Tuple
from database_categories import CategoryRepository, Category, CategoryHistory

# Configure logging
from utils.logger_config import get_logger
logger = get_logger(__name__)


class CategoryService:
    """Service for category business logic"""
    
    def __init__(self):
        logger.info("[ENTER] CategoryService.__init__")
        self.repository = CategoryRepository()
        logger.info("[EXIT] CategoryService.__init__")
    
    def create_category(self, categoryname: str, categorydescription: Optional[str] = None,
                       maximumamount: Optional[float] = None, status: bool = True,
                       approval_criteria: Optional[str] = None,
                       created_by: str = 'ADMIN') -> Category:
        """Create a new category"""
        logger.info(f"[ENTER] create_category: categoryname='{categoryname}'")
        try:
            result = self.repository.create_category(
                categoryname, categorydescription, maximumamount, status,
                approval_criteria, created_by
            )
            logger.info(f"[EXIT] create_category: created category_id={result.ID if result else None}")
            return result
        except Exception as e:
            logger.error(f"[ERROR] create_category: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        logger.info(f"[ENTER] get_category: category_id={category_id}")
        try:
            result = self.repository.get_category(category_id)
            logger.info(f"[EXIT] get_category: found={result is not None}")
            return result
        except Exception as e:
            logger.error(f"[ERROR] get_category: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
    def get_category_by_name(self, categoryname: str) -> Optional[Category]:
        """Get category by name"""
        logger.info(f"[ENTER] get_category_by_name: categoryname='{categoryname}'")
        try:
            with self.repository.db.get_cursor() as cursor:
                cursor.execute('SELECT * FROM IV_MA_CATEGORY WHERE UPPER(CATEGORYNAME) = ?', (categoryname.upper(),))
                row = cursor.fetchone()
                result = Category(row) if row else None
                logger.info(f"[EXIT] get_category_by_name: found={result is not None}")
                return result
        except Exception as e:
            logger.error(f"[ERROR] get_category_by_name: {type(e).__name__}: {str(e)}", exc_info=True)
            return None
    
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
