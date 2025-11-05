"""
Request service for business logic
"""
from typing import List, Optional, Tuple
from database import RequestRepository, Request


class RequestService:
    """Service for request business logic"""
    
    def __init__(self):
        self.repository = RequestRepository()
    
    def create_request_from_invoice(self, user_id: str, invoice_data: dict,
                                  approval_status: str = 'Pending',
                                  created_by: str = 'AI') -> Request:
        """
        Create a request from invoice extraction data
        
        Args:
            user_id: User ID who owns the invoice
            invoice_data: Extracted invoice data
            approval_status: Initial approval status
            created_by: Who created the request
            
        Returns:
            Request: Created request
        """
        # Extract relevant fields from invoice data
        total_amount = invoice_data.get('total_amount')
        invoice_date = invoice_data.get('invoice_date')
        invoice_number = invoice_data.get('invoice_number')
        
        # Determine category from filename or invoice data
        category_name = invoice_data.get('category_name', 'General')
        
        # Auto-determine approval type based on existing logic
        approval_type = self._determine_approval_type(invoice_data)
        
        return self.repository.create_request(
            user_id=user_id,
            total_amount=total_amount,
            invoice_date=invoice_date,
            invoice_number=invoice_number,
            category_name=category_name,
            comments=f"Auto-created from invoice processing",
            approval_type=approval_type,
            created_by=created_by
        )
    
    def create_request(self, user_id: str, total_amount: Optional[float],
                      invoice_date: Optional[str], invoice_number: Optional[str],
                      category_name: Optional[str], comments: Optional[str],
                      approval_type: str = 'Manual') -> Request:
        """
        Create a new request manually
        
        Args:
            user_id: User ID
            total_amount: Total amount
            invoice_date: Invoice date
            invoice_number: Invoice number
            category_name: Category name
            comments: Comments
            approval_type: Approval type (Manual/Auto)
            
        Returns:
            Request: Created request
        """
        return self.repository.create_request(
            user_id, total_amount, invoice_date, invoice_number,
            category_name, comments, approval_type, user_id
        )
    
    def get_request(self, request_id: int) -> Optional[Request]:
        """
        Get request by ID
        
        Args:
            request_id: Request ID
            
        Returns:
            Optional[Request]: Request or None
        """
        return self.repository.get_request(request_id)
    
    def list_requests(self, page: int = 1, page_size: int = 20,
                     status: Optional[str] = None) -> Tuple[List[Request], int]:
        """
        List requests with pagination and filters
        
        Args:
            page: Page number
            page_size: Page size
            status: Status filter
            
        Returns:
            Tuple[List[Request], int]: Requests and total count
        """
        return self.repository.list_requests(page, page_size, status)
    
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
        return self.repository.update_request_status(
            request_id, new_status, comments, updated_by
        )
    
    def get_insights(self, duration: Optional[str] = None) -> dict:
        """
        Get request insights
        
        Args:
            duration: Duration filter (not implemented yet)
            
        Returns:
            dict: Insights data
        """
        return self.repository.get_insights(duration)
    
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