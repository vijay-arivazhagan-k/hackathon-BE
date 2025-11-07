"""
SQLite3 database configuration for category master data management
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple
from contextlib import contextmanager

# Configure logging
from utils.logger_config import get_logger
logger = get_logger(__name__)


class CategoryDatabaseManager:
    """Database manager for categories"""
    
    def __init__(self):
        logger.info("[ENTER] CategoryDatabaseManager.__init__")
        self._connection = None
        self._initialize_database()
        logger.info("[EXIT] CategoryDatabaseManager.__init__")
    
    def _initialize_database(self):
        """Initialize the database with required tables"""
        logger.info("[ENTER] _initialize_database")
        try:
            self._connection = sqlite3.connect(':memory:', check_same_thread=False)
            self._connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Create tables
            self._create_tables()
            logger.info("✓ Database initialized with IV_MA_CATEGORY and IV_MA_CATEGORY_HISTORY tables")
            logger.info("[EXIT] _initialize_database")
        except Exception as e:
            logger.error(f"[ERROR] _initialize_database: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
    def _create_tables(self):
        """Create the required tables"""
        cursor = self._connection.cursor()
        
        # Create IV_MA_CATEGORY table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS IV_MA_CATEGORY (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CATEGORYNAME VARCHAR(100) NOT NULL,
                CATEGORYDESCRIPTION VARCHAR(4000),
                MAXIMUMAMOUNT REAL,
                STATUS BOOLEAN DEFAULT 1,
                REQUESTCOUNT INTEGER,
                APPROVAL_CRITERIA TEXT,
                CREATEDON TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CREATEDBY VARCHAR(100),
                UPDATEDON TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UPDATEDBY VARCHAR(100)
            )
        ''')
        
        # Create IV_MA_CATEGORY_HISTORY table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS IV_MA_CATEGORY_HISTORY (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CATEGORY_ID INTEGER NOT NULL,
                CATEGORYNAME VARCHAR(100),
                CATEGORYDESCRIPTION VARCHAR(4000),
                MAXIMUMAMOUNT REAL,
                STATUS BOOLEAN,
                REQUESTCOUNT INTEGER,
                APPROVAL_CRITERIA TEXT,
                COMMENTS TEXT NOT NULL,
                CREATEDON TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CREATEDBY VARCHAR(100),
                FOREIGN KEY (CATEGORY_ID) REFERENCES IV_MA_CATEGORY (ID)
            )
        ''')
        
        self._connection.commit()
    
    @contextmanager
    def get_cursor(self):
        """Get database cursor with automatic commit/rollback"""
        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()


# Global database manager instance
category_db_manager = CategoryDatabaseManager()


class Category:
    """Category model representing IV_MA_CATEGORY table"""
    
    def __init__(self, row_data=None, **kwargs):
        if row_data:
            # Initialize from database row (sqlite3.Row object)
            self.ID = row_data['ID']
            self.CATEGORYNAME = row_data['CATEGORYNAME']
            self.CATEGORYDESCRIPTION = row_data['CATEGORYDESCRIPTION']
            self.MAXIMUMAMOUNT = row_data['MAXIMUMAMOUNT']
            self.STATUS = row_data['STATUS'] if row_data['STATUS'] is not None else True
            self.REQUESTCOUNT = row_data['REQUESTCOUNT']
            self.APPROVAL_CRITERIA = row_data['APPROVAL_CRITERIA']
            self.CREATEDON = row_data['CREATEDON']
            self.CREATEDBY = row_data['CREATEDBY']
            self.UPDATEDON = row_data['UPDATEDON']
            self.UPDATEDBY = row_data['UPDATEDBY']
        else:
            # Initialize from keyword arguments
            self.ID = kwargs.get('ID')
            self.CATEGORYNAME = kwargs.get('CATEGORYNAME')
            self.CATEGORYDESCRIPTION = kwargs.get('CATEGORYDESCRIPTION')
            self.MAXIMUMAMOUNT = kwargs.get('MAXIMUMAMOUNT')
            self.STATUS = kwargs.get('STATUS', True)
            self.REQUESTCOUNT = kwargs.get('REQUESTCOUNT', 0)
            self.APPROVAL_CRITERIA = kwargs.get('APPROVAL_CRITERIA')
            self.CREATEDON = kwargs.get('CREATEDON')
            self.CREATEDBY = kwargs.get('CREATEDBY', 'ADMIN')
            self.UPDATEDON = kwargs.get('UPDATEDON')
            self.UPDATEDBY = kwargs.get('UPDATEDBY', 'ADMIN')


class CategoryHistory:
    """Category history model representing IV_MA_CATEGORY_HISTORY table"""
    
    def __init__(self, row_data=None, **kwargs):
        if row_data:
            self.ID = row_data['ID']
            self.CATEGORY_ID = row_data['CATEGORY_ID']
            self.CATEGORYNAME = row_data['CATEGORYNAME']
            self.CATEGORYDESCRIPTION = row_data['CATEGORYDESCRIPTION']
            self.MAXIMUMAMOUNT = row_data['MAXIMUMAMOUNT']
            self.STATUS = row_data['STATUS']
            self.REQUESTCOUNT = row_data['REQUESTCOUNT']
            self.APPROVAL_CRITERIA = row_data['APPROVAL_CRITERIA']
            self.COMMENTS = row_data['COMMENTS']
            self.CREATEDON = row_data['CREATEDON']
            self.CREATEDBY = row_data['CREATEDBY']
        else:
            self.ID = kwargs.get('ID')
            self.CATEGORY_ID = kwargs.get('CATEGORY_ID')
            self.CATEGORYNAME = kwargs.get('CATEGORYNAME')
            self.CATEGORYDESCRIPTION = kwargs.get('CATEGORYDESCRIPTION')
            self.MAXIMUMAMOUNT = kwargs.get('MAXIMUMAMOUNT')
            self.STATUS = kwargs.get('STATUS')
            self.REQUESTCOUNT = kwargs.get('REQUESTCOUNT')
            self.APPROVAL_CRITERIA = kwargs.get('APPROVAL_CRITERIA')
            self.COMMENTS = kwargs.get('COMMENTS')
            self.CREATEDON = kwargs.get('CREATEDON')
            self.CREATEDBY = kwargs.get('CREATEDBY')


class CategoryRepository:
    """Repository for category database operations"""
    
    def __init__(self):
        self.db = category_db_manager
    
    def create_category(self, categoryname: str, categorydescription: Optional[str] = None,
                       maximumamount: Optional[float] = None, status: bool = True,
                       approval_criteria: Optional[str] = None,
                       created_by: str = 'ADMIN') -> Category:
        """Create a new category"""
        with self.db.get_cursor() as cursor:
            current_time = datetime.now().isoformat()
            categoryname_upper = categoryname.upper()
            
            cursor.execute('''
                INSERT INTO IV_MA_CATEGORY 
                (CATEGORYNAME, CATEGORYDESCRIPTION, MAXIMUMAMOUNT, STATUS, 
                 APPROVAL_CRITERIA, CREATEDON, CREATEDBY, UPDATEDON, UPDATEDBY)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (categoryname_upper, categorydescription, maximumamount, status,
                  approval_criteria, current_time, created_by, current_time, created_by))
            
            category_id = cursor.lastrowid
            
            # Add to history
            self._add_to_history(cursor, category_id, categoryname_upper, categorydescription,
                               maximumamount, status, approval_criteria,
                               f"Category created", created_by)
            
            # Fetch and return the created category
            cursor.execute('SELECT * FROM IV_MA_CATEGORY WHERE ID = ?', (category_id,))
            row = cursor.fetchone()
            return Category(row)
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM IV_MA_CATEGORY WHERE ID = ?', (category_id,))
            row = cursor.fetchone()
            return Category(row) if row else None
    
    def update_category(self, category_id: int, categoryname: Optional[str] = None,
                       categorydescription: Optional[str] = None, maximumamount: Optional[float] = None,
                       status: Optional[bool] = None, approval_criteria: Optional[str] = None,
                       comments: str = "Category updated",
                       updated_by: str = 'ADMIN') -> Optional[Category]:
        """Update category"""
        with self.db.get_cursor() as cursor:
            # Get current category data
            cursor.execute('SELECT * FROM IV_MA_CATEGORY WHERE ID = ?', (category_id,))
            current_row = cursor.fetchone()
            if not current_row:
                return None
            
            current_time = datetime.now().isoformat()
            
            # Prepare update values - use current values if not provided
            new_categoryname = categoryname.upper() if categoryname else current_row['CATEGORYNAME']
            new_description = categorydescription if categorydescription is not None else current_row['CATEGORYDESCRIPTION']
            new_amount = maximumamount if maximumamount is not None else current_row['MAXIMUMAMOUNT']
            new_status = status if status is not None else current_row['STATUS']
            new_approval_criteria = approval_criteria if approval_criteria is not None else current_row['APPROVAL_CRITERIA']
            
            # Update main category
            cursor.execute('''
                UPDATE IV_MA_CATEGORY 
                SET CATEGORYNAME = ?, CATEGORYDESCRIPTION = ?, MAXIMUMAMOUNT = ?, 
                    STATUS = ?, APPROVAL_CRITERIA = ?,
                    UPDATEDON = ?, UPDATEDBY = ?
                WHERE ID = ?
            ''', (new_categoryname, new_description, new_amount, new_status,
                  new_approval_criteria, current_time, updated_by, category_id))
            
            # Add to history
            self._add_to_history(cursor, category_id, new_categoryname, new_description,
                               new_amount, new_status, new_approval_criteria,
                               comments, updated_by)
            
            # Return updated category
            cursor.execute('SELECT * FROM IV_MA_CATEGORY WHERE ID = ?', (category_id,))
            row = cursor.fetchone()
            return Category(row)
    
    def list_categories(self, page: int = 1, page_size: int = 20) -> Tuple[List[Category], int]:
        """List categories with pagination"""
        with self.db.get_cursor() as cursor:
            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM IV_MA_CATEGORY")
            total = cursor.fetchone()['total']
            
            # Get paginated results
            offset = (page - 1) * page_size
            cursor.execute('''
                SELECT * FROM IV_MA_CATEGORY
                ORDER BY CREATEDON DESC
                LIMIT ? OFFSET ?
            ''', (page_size, offset))
            rows = cursor.fetchall()
            
            categories = [Category(row) for row in rows]
            return categories, total
    
    def get_category_history(self, category_id: int) -> List[CategoryHistory]:
        """Get category history"""
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                SELECT * FROM IV_MA_CATEGORY_HISTORY 
                WHERE CATEGORY_ID = ? 
                ORDER BY CREATEDON DESC
            ''', (category_id,))
            rows = cursor.fetchall()
            return [CategoryHistory(row) for row in rows]
    
    def _add_to_history(self, cursor, category_id: int, categoryname: str,
                       categorydescription: Optional[str], maximumamount: Optional[float],
                       status: bool, approval_criteria: Optional[str],
                       comments: str, created_by: str):
        """Add entry to category history"""
        current_time = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO IV_MA_CATEGORY_HISTORY 
            (CATEGORY_ID, CATEGORYNAME, CATEGORYDESCRIPTION, MAXIMUMAMOUNT, STATUS,
             APPROVAL_CRITERIA, COMMENTS, CREATEDON, CREATEDBY)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (category_id, categoryname, categorydescription, maximumamount, status,
              approval_criteria, comments, current_time, created_by))
