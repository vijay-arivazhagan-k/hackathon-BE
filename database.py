"""
SQLite3 in-memory database configuration and models for request management
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple
from contextlib import contextmanager

# Configure logging
from utils.logger_config import get_logger
logger = get_logger(__name__)


class DatabaseManager:
    """Database manager for SQLite3 in-memory database"""
    
    def __init__(self):
        logger.info("[ENTER] DatabaseManager.__init__")
        self._connection = None
        self._initialize_database()
        logger.info("[EXIT] DatabaseManager.__init__")
    
    def _initialize_database(self):
        """Initialize the database with required tables"""
        logger.info("[ENTER] _initialize_database")
        try:
            self._connection = sqlite3.connect(':memory:', check_same_thread=False)
            self._connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Create tables
            self._create_tables()
            logger.info("✓ Database initialized with IV_TR_REQUESTS and IV_TR_REQUEST_HISTORY tables")
            logger.info("[EXIT] _initialize_database")
        except Exception as e:
            logger.error(f"[ERROR] _initialize_database: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
    def _create_tables(self):
        """Create the required tables"""
        cursor = self._connection.cursor()
        
        # Create IV_TR_REQUESTS table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS IV_TR_REQUESTS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USER_ID VARCHAR(25) NOT NULL,
                TOTAL_AMOUNT DECIMAL(10,2),
                INVOICE_DATE DATE,
                INVOICE_NUMBER VARCHAR(50),
                CATEGORY_NAME VARCHAR(100),
                CURRENT_STATUS VARCHAR(25) DEFAULT 'Pending',
                COMMENTS VARCHAR(4000),
                APPROVALTYPE VARCHAR(25) DEFAULT 'Auto',
                CREATED_ON TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UPDATED_ON TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CREATED_BY VARCHAR(25),
                UPDATED_BY VARCHAR(25)
            )
        ''')
        
        # Create IV_TR_REQUEST_HISTORY table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS IV_TR_REQUEST_HISTORY (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                REQUEST_ID INTEGER NOT NULL,
                USER_ID VARCHAR(25) NOT NULL,
                TOTAL_AMOUNT DECIMAL(10,2),
                INVOICE_DATE DATE,
                INVOICE_NUMBER VARCHAR(50),
                CATEGORY_NAME VARCHAR(100),
                CURRENT_STATUS VARCHAR(25),
                COMMENTS VARCHAR(4000),
                APPROVALTYPE VARCHAR(25),
                CREATED_ON TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UPDATED_ON TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CREATED_BY VARCHAR(25),
                UPDATED_BY VARCHAR(25),
                FOREIGN KEY (REQUEST_ID) REFERENCES IV_TR_REQUESTS(ID)
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
db_manager = DatabaseManager()


class Request:
    """Request model representing IV_TR_REQUESTS table"""
    
    def __init__(self, row_data=None, **kwargs):
        if row_data:
            # Initialize from database row
            self.ID = row_data['ID']
            self.USER_ID = row_data['USER_ID']
            self.TOTAL_AMOUNT = row_data['TOTAL_AMOUNT']
            self.INVOICE_DATE = row_data['INVOICE_DATE']
            self.INVOICE_NUMBER = row_data['INVOICE_NUMBER']
            self.CATEGORY_NAME = row_data['CATEGORY_NAME']
            self.CURRENT_STATUS = row_data['CURRENT_STATUS']
            self.COMMENTS = row_data['COMMENTS']
            self.APPROVALTYPE = row_data['APPROVALTYPE']
            self.CREATED_ON = row_data['CREATED_ON']
            self.UPDATED_ON = row_data['UPDATED_ON']
            self.CREATED_BY = row_data['CREATED_BY']
            self.UPDATED_BY = row_data['UPDATED_BY']
        else:
            # Initialize from keyword arguments
            self.ID = kwargs.get('ID')
            self.USER_ID = kwargs.get('USER_ID')
            self.TOTAL_AMOUNT = kwargs.get('TOTAL_AMOUNT')
            self.INVOICE_DATE = kwargs.get('INVOICE_DATE')
            self.INVOICE_NUMBER = kwargs.get('INVOICE_NUMBER')
            self.CATEGORY_NAME = kwargs.get('CATEGORY_NAME')
            self.CURRENT_STATUS = kwargs.get('CURRENT_STATUS', 'Pending')
            self.COMMENTS = kwargs.get('COMMENTS')
            self.APPROVALTYPE = kwargs.get('APPROVALTYPE', 'Auto')
            self.CREATED_ON = kwargs.get('CREATED_ON')
            self.UPDATED_ON = kwargs.get('UPDATED_ON')
            self.CREATED_BY = kwargs.get('CREATED_BY')
            self.UPDATED_BY = kwargs.get('UPDATED_BY')


class RequestHistory:
    """Request history model representing IV_TR_REQUEST_HISTORY table"""
    
    def __init__(self, row_data=None, **kwargs):
        if row_data:
            self.ID = row_data['ID']
            self.REQUEST_ID = row_data['REQUEST_ID']
            self.USER_ID = row_data['USER_ID']
            self.TOTAL_AMOUNT = row_data['TOTAL_AMOUNT']
            self.INVOICE_DATE = row_data['INVOICE_DATE']
            self.INVOICE_NUMBER = row_data['INVOICE_NUMBER']
            self.CATEGORY_NAME = row_data['CATEGORY_NAME']
            self.CURRENT_STATUS = row_data['CURRENT_STATUS']
            self.COMMENTS = row_data['COMMENTS']
            self.APPROVALTYPE = row_data['APPROVALTYPE']
            self.CREATED_ON = row_data['CREATED_ON']
            self.UPDATED_ON = row_data['UPDATED_ON']
            self.CREATED_BY = row_data['CREATED_BY']
            self.UPDATED_BY = row_data['UPDATED_BY']
        else:
            self.ID = kwargs.get('ID')
            self.REQUEST_ID = kwargs.get('REQUEST_ID')
            self.USER_ID = kwargs.get('USER_ID')
            self.TOTAL_AMOUNT = kwargs.get('TOTAL_AMOUNT')
            self.INVOICE_DATE = kwargs.get('INVOICE_DATE')
            self.INVOICE_NUMBER = kwargs.get('INVOICE_NUMBER')
            self.CATEGORY_NAME = kwargs.get('CATEGORY_NAME')
            self.CURRENT_STATUS = kwargs.get('CURRENT_STATUS')
            self.COMMENTS = kwargs.get('COMMENTS')
            self.APPROVALTYPE = kwargs.get('APPROVALTYPE')
            self.CREATED_ON = kwargs.get('CREATED_ON')
            self.UPDATED_ON = kwargs.get('UPDATED_ON')
            self.CREATED_BY = kwargs.get('CREATED_BY')
            self.UPDATED_BY = kwargs.get('UPDATED_BY')


class RequestRepository:
    """Repository for request database operations"""
    
    def __init__(self):
        self.db = db_manager
    
    def create_request(self, user_id: str, total_amount: Optional[float], 
                      invoice_date: Optional[str], invoice_number: Optional[str],
                      category_name: Optional[str], comments: Optional[str] = None,
                      approval_type: str = 'Auto', created_by: str = 'AI',
                      status: str = 'Pending') -> Request:
        """Create a new request"""
        with self.db.get_cursor() as cursor:
            current_time = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO IV_TR_REQUESTS 
                (USER_ID, TOTAL_AMOUNT, INVOICE_DATE, INVOICE_NUMBER, CATEGORY_NAME, 
                 CURRENT_STATUS, COMMENTS, APPROVALTYPE, CREATED_ON, UPDATED_ON, 
                 CREATED_BY, UPDATED_BY)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, total_amount, invoice_date, invoice_number, category_name,
                  status, comments, approval_type, current_time, current_time,
                  created_by, created_by))
            
            request_id = cursor.lastrowid
            
            # Add to history
            self._add_to_history(cursor, request_id, user_id, total_amount, 
                               invoice_date, invoice_number, category_name,
                               status, comments, approval_type, created_by)
            
            # Fetch and return the created request
            cursor.execute('SELECT * FROM IV_TR_REQUESTS WHERE ID = ?', (request_id,))
            row = cursor.fetchone()
            return Request(row)
    
    def get_request(self, request_id: int) -> Optional[Request]:
        """Get request by ID"""
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM IV_TR_REQUESTS WHERE ID = ?', (request_id,))
            row = cursor.fetchone()
            return Request(row) if row else None
    
    def update_request_status(self, request_id: int, new_status: str, 
                             comments: Optional[str] = None, 
                             updated_by: str = 'Admin') -> Optional[Request]:
        """Update request status"""
        with self.db.get_cursor() as cursor:
            current_time = datetime.now().isoformat()
            
            # Get current request data
            cursor.execute('SELECT * FROM IV_TR_REQUESTS WHERE ID = ?', (request_id,))
            current_row = cursor.fetchone()
            if not current_row:
                return None
            
            # Update main request
            cursor.execute('''
                UPDATE IV_TR_REQUESTS 
                SET CURRENT_STATUS = ?, COMMENTS = ?, UPDATED_ON = ?, UPDATED_BY = ?
                WHERE ID = ?
            ''', (new_status, comments or current_row['COMMENTS'], current_time, updated_by, request_id))
            
            # Add to history
            self._add_to_history(cursor, request_id, current_row['USER_ID'],
                               current_row['TOTAL_AMOUNT'], current_row['INVOICE_DATE'],
                               current_row['INVOICE_NUMBER'], current_row['CATEGORY_NAME'],
                               new_status, comments or current_row['COMMENTS'],
                               current_row['APPROVALTYPE'], updated_by)
            
            # Return updated request
            cursor.execute('SELECT * FROM IV_TR_REQUESTS WHERE ID = ?', (request_id,))
            row = cursor.fetchone()
            return Request(row)
    
    def list_requests(self, page: int = 1, page_size: int = 20,
                     status_filter: Optional[str] = None,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     category_id: Optional[str] = None) -> Tuple[List[Request], int]:
        """List requests with pagination and optional filters"""
        with self.db.get_cursor() as cursor:
            # Build query with filters
            where_clauses = []
            params = []
            
            if status_filter and status_filter.lower() != 'all':
                where_clauses.append("CURRENT_STATUS = ?")
                params.append(status_filter.title())
            
            # Add date range filters
            # NOTE: Date filtering is now based strictly on CREATED_ON (request creation timestamp)
            if start_date:
                if 'T' in start_date:
                    start_date = start_date.split('T')[0]
                where_clauses.append("DATE(CREATED_ON) >= DATE(?)")
                params.append(start_date)
                print(f"🔍 Added start_date filter: DATE(CREATED_ON) >= DATE('{start_date}')")
            
            if end_date:
                if 'T' in end_date:
                    end_date = end_date.split('T')[0]
                where_clauses.append("DATE(CREATED_ON) <= DATE(?)")
                params.append(end_date)
                print(f"🔍 Added end_date filter: DATE(CREATED_ON) <= DATE('{end_date}')")
            
            # Add category filter
            if category_id and category_id.lower() != 'all':
                where_clauses.append("CATEGORY_NAME = ?")
                params.append(category_id)
            
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM IV_TR_REQUESTS {where_clause}"
            print(f"🔍 DB Count Query: {count_query}")
            print(f"🔍 DB Params: {params}")
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            print(f"🔍 DB Query: Found {total} total requests with filters: status={status_filter}, start={start_date}, end={end_date}, category={category_id}")
            
            # Debug: Print all rows without filter
            cursor.execute("SELECT ID, INVOICE_DATE, CURRENT_STATUS, CATEGORY_NAME FROM IV_TR_REQUESTS")
            all_rows = cursor.fetchall()
            print(f"🔍 DB Total rows without filter: {len(all_rows)}")
            for row in all_rows[:5]:  # Print first 5
                print(f"  - ID={row['ID']}, Date={row['INVOICE_DATE']}, Status={row['CURRENT_STATUS']}, Category={row['CATEGORY_NAME']}")
            
            # Get paginated results
            offset = (page - 1) * page_size
            query = f'''
                SELECT * FROM IV_TR_REQUESTS {where_clause}
                ORDER BY CREATED_ON DESC
                LIMIT ? OFFSET ?
            '''
            params.extend([page_size, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            print(f"🔍 DB Query Result: Retrieved {len(rows)} rows")
            for row in rows:
                print(f"  - Request ID={row['ID']}, Date={row['INVOICE_DATE']}, Status={row['CURRENT_STATUS']}, Category={row['CATEGORY_NAME']}")
            
            requests = [Request(row) for row in rows]
            return requests, total
    
    def get_request_history(self, request_id: int) -> List[RequestHistory]:
        """Get request history"""
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                SELECT * FROM IV_TR_REQUEST_HISTORY 
                WHERE REQUEST_ID = ? 
                ORDER BY CREATED_ON DESC
            ''', (request_id,))
            rows = cursor.fetchall()
            return [RequestHistory(row) for row in rows]
    
    def get_filtered_requests_for_export(self,
                                         start_date: Optional[str] = None,
                                         end_date: Optional[str] = None,
                                         category: Optional[str] = None,
                                         status: Optional[str] = None) -> List[Request]:
        """Get filtered requests for export (no pagination)"""
        with self.db.get_cursor() as cursor:
            # Build query with filters
            where_parts = []
            params = []
            
            if start_date:
                if 'T' in start_date:
                    start_date = start_date.split('T')[0]
                where_parts.append("DATE(CREATED_ON) >= DATE(?)")
                params.append(start_date)
            
            if end_date:
                if 'T' in end_date:
                    end_date = end_date.split('T')[0]
                where_parts.append("DATE(CREATED_ON) <= DATE(?)")
                params.append(end_date)
            
            if category and category.lower() != 'all':
                where_parts.append("CATEGORY_NAME = ?")
                params.append(category)
            
            if status and status.lower() != 'all':
                where_parts.append("CURRENT_STATUS = ?")
                params.append(status.title())
            
            where_clause = "WHERE " + " AND ".join(where_parts) if where_parts else ""
            
            query = f'''
                SELECT * FROM IV_TR_REQUESTS {where_clause}
                ORDER BY CREATED_ON DESC
            '''
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [Request(row) for row in rows]
    
    def get_insights(self, start_date: Optional[str] = None, end_date: Optional[str] = None, duration_filter: Optional[str] = None) -> dict:
        """Get request statistics with date filters"""
        with self.db.get_cursor() as cursor:
            # Build date filter
            where_clauses = []
            params = []
            
            if start_date:
                if 'T' in start_date:
                    start_date = start_date.split('T')[0]
                where_clauses.append("DATE(CREATED_ON) >= DATE(?)")
                params.append(start_date)
            
            if end_date:
                if 'T' in end_date:
                    end_date = end_date.split('T')[0]
                where_clauses.append("DATE(CREATED_ON) <= DATE(?)")
                params.append(end_date)
            
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            # Get status counts
            cursor.execute(f'''
                SELECT 
                    CURRENT_STATUS,
                    COUNT(*) as count,
                    COALESCE(SUM(TOTAL_AMOUNT), 0) as total_amount
                FROM IV_TR_REQUESTS {where_clause}
                GROUP BY CURRENT_STATUS
            ''', params)
            
            status_data = {row['CURRENT_STATUS']: {'count': row['count'], 'amount': row['total_amount']} 
                          for row in cursor.fetchall()}
            
            # Get totals
            cursor.execute(f'SELECT COUNT(*) as total FROM IV_TR_REQUESTS {where_clause}', params)
            total = cursor.fetchone()['total']
            
            return {
                'total': total,
                'approved': status_data.get('Approved', {'count': 0})['count'],
                'rejected': status_data.get('Rejected', {'count': 0})['count'],
                'pending': status_data.get('Pending', {'count': 0})['count'],
                'status_breakdown': status_data
            }
    
    def _add_to_history(self, cursor, request_id: int, user_id: str,
                       total_amount: Optional[float], invoice_date: Optional[str],
                       invoice_number: Optional[str], category_name: Optional[str],
                       status: str, comments: Optional[str], approval_type: str,
                       created_by: str):
        """Add entry to request history"""
        current_time = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO IV_TR_REQUEST_HISTORY 
            (REQUEST_ID, USER_ID, TOTAL_AMOUNT, INVOICE_DATE, INVOICE_NUMBER, 
             CATEGORY_NAME, CURRENT_STATUS, COMMENTS, APPROVALTYPE, 
             CREATED_ON, UPDATED_ON, CREATED_BY, UPDATED_BY)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (request_id, user_id, total_amount, invoice_date, invoice_number,
              category_name, status, comments, approval_type, current_time,
              current_time, created_by, created_by))