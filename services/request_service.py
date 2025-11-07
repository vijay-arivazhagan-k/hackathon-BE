"""
Request service for business logic
"""
from typing import List, Optional, Tuple
from database import RequestRepository, Request

# Configure logging
from utils.logger_config import get_logger
logger = get_logger(__name__)


class RequestService:
    """Service for request business logic"""
    
    def __init__(self):
        logger.info("[ENTER] RequestService.__init__")
        self.repository = RequestRepository()
        logger.info("[EXIT] RequestService.__init__")
    
    def create_request_from_invoice(self, user_id: str, invoice_data: dict,
                                  approval_status: str = 'Pending',
                                  created_by: str = 'AI',
                                  comments: Optional[str] = None) -> Request:
        """
        Create a request from invoice extraction data
        
        Args:
            user_id: User ID who owns the invoice
            invoice_data: Extracted invoice data
            approval_status: Initial approval status (Approved, Pending, or Rejected)
            created_by: Who created the request
            comments: Optional comments (e.g., approval reasons from evaluator)
            
        Returns:
            Request: Created request
        """
        logger.info(f"[ENTER] create_request_from_invoice: user_id={user_id}, approval_status={approval_status}")
        try:
            # Extract relevant fields from invoice data
            total_amount = invoice_data.get('total_amount')
            invoice_date = invoice_data.get('invoice_date')
            invoice_number = invoice_data.get('invoice_number')
            
            # Determine category from filename or invoice data
            category_name = invoice_data.get('category_name', 'General')
            
            # Auto-determine approval type based on existing logic
            approval_type = self._determine_approval_type(invoice_data)
            
            # Use provided comments or generate default
            if comments is None:
                comments = f"Auto-created from invoice processing"
            
            logger.info(f"[INFO] create_request_from_invoice: invoice_number={invoice_number}, category={category_name}, amount={total_amount}")
            
            result = self.repository.create_request(
                user_id=user_id,
                total_amount=total_amount,
                invoice_date=invoice_date,
                invoice_number=invoice_number,
                category_name=category_name,
                comments=comments,
                approval_type=approval_type,
                created_by=created_by,
                status=approval_status  # Pass the approval status here
            )
            logger.info(f"[EXIT] create_request_from_invoice: request_id={result.ID if result else None}")
            return result
        except Exception as e:
            logger.error(f"[ERROR] create_request_from_invoice: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
    def get_request(self, request_id: int) -> Optional[Request]:
        """
        Get request by ID
        
        Args:
            request_id: Request ID
            
        Returns:
            Optional[Request]: Request or None
        """
        logger.info(f"[ENTER] get_request: request_id={request_id}")
        try:
            result = self.repository.get_request(request_id)
            logger.info(f"[EXIT] get_request: found={result is not None}")
            return result
        except Exception as e:
            logger.error(f"[ERROR] get_request: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
    def list_requests(self, page: int = 1, page_size: int = 20,
                     status: Optional[str] = None,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     category_id: Optional[str] = None) -> Tuple[List[Request], int]:
        """List requests with pagination and filters.

        Date range filters apply to the request creation timestamp (CREATED_ON),
        not the invoice date.

        Args:
            page: Page number
            page_size: Page size
            status: Status filter
            start_date: Start creation date filter (YYYY-MM-DD)
            end_date: End creation date filter (YYYY-MM-DD)
            category_id: Category name filter

        Returns:
            Tuple[List[Request], int]: Requests and total count
        """
        logger.info(f"[ENTER] list_requests: page={page}, page_size={page_size}, status={status}, start={start_date}, end={end_date}, category={category_id}")
        try:
            result = self.repository.list_requests(page, page_size, status, start_date, end_date, category_id)
            logger.info(f"[EXIT] list_requests: count={len(result[0]) if result else 0}, total={result[1] if result else 0}")
            print(f"✅ Service returned {len(result[0]) if result else 0} requests out of {result[1] if result else 0} total")
            return result
        except Exception as e:
            logger.error(f"[ERROR] list_requests: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
    def update_request_status(self, request_id: int, new_status: str,
                             comments: Optional[str] = None,
                             updated_by: str = 'Admin') -> Optional[Request]:
        """
        Update request status
        
        Args:
            request_id: Request ID
            new_status: New status
            comments: Comments
            updated_by: User who updated
            
        Returns:
            Optional[Request]: Updated request or None
        """
        logger.info(f"[ENTER] update_request_status: request_id={request_id}, new_status={new_status}")
        try:
            result = self.repository.update_request_status(
                request_id, new_status, comments, updated_by
            )
            logger.info(f"[EXIT] update_request_status: updated={result is not None}")
            return result
        except Exception as e:
            logger.error(f"[ERROR] update_request_status: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
    def get_insights(self, start_date: Optional[str] = None, end_date: Optional[str] = None, duration: Optional[str] = None) -> dict:
        """Get request insights.

        Date range filters apply to CREATED_ON.

        Args:
            start_date: Start creation date filter (YYYY-MM-DD)
            end_date: End creation date filter (YYYY-MM-DD)
            duration: Duration filter (deprecated)

        Returns:
            dict: Insights data
        """
        logger.info(f"[ENTER] get_insights: start={start_date}, end={end_date}, duration={duration}")
        try:
            result = self.repository.get_insights(start_date=start_date, end_date=end_date, duration_filter=duration)
            logger.info(f"[EXIT] get_insights: insights_retrieved")
            return result
        except Exception as e:
            logger.error(f"[ERROR] get_insights: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
    def get_request_history(self, request_id: int) -> List:
        """
        Get request history
        
        Args:
            request_id: Request ID
            
        Returns:
            List: Request history
        """
        return self.repository.get_request_history(request_id)
    
    def get_filtered_requests_for_export(self, 
                                         start_date: Optional[str] = None,
                                         end_date: Optional[str] = None,
                                         category: Optional[str] = None,
                                         status: Optional[str] = None) -> List[Request]:
        """
        Get filtered requests for export (no pagination)
        
        Args:
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            category: Category filter
            status: Status filter
            
        Returns:
            List[Request]: All matching requests
        """
        return self.repository.get_filtered_requests_for_export(
            start_date, end_date, category, status
        )
    
    def _determine_approval_type(self, invoice_data: dict) -> str:
        """
        Determine approval type based on invoice data
        
        Args:
            invoice_data: Invoice data
            
        Returns:
            str: Approval type (Auto/Manual)
        """
        # Get approval info if available
        approval_info = invoice_data.get('approval_info', {})
        approval_status = approval_info.get('status', 'pending')
        
        # If already auto-approved, mark as Auto
        if approval_status == 'approved':
            return 'Auto'
        
        # Check amount threshold for auto approval
        total_amount = invoice_data.get('total_amount', 0)
        if isinstance(total_amount, (int, float)) and total_amount < 2000:
            return 'Auto'
        
        return 'Manual'