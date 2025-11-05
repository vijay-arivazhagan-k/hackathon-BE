"""
Microsoft Teams Integration Module
Handles sending Adaptive Cards for invoice approval workflow
"""

import requests
import json
import os
from typing import Dict
from urllib.parse import quote


class TeamsNotifier:
    """Handle Microsoft Teams notifications using webhooks and Adaptive Cards."""
    
    def __init__(self, webhook_url: str, base_url: str = "http://localhost:5000"):
        """
        Initialize Teams notifier.
        
        Args:
            webhook_url: Microsoft Teams incoming webhook URL
            base_url: Base URL for API callbacks
        """
        self.webhook_url = webhook_url
        self.base_url = base_url
    
    def create_approval_card(self, invoice_data: Dict, approval_info: Dict, 
                            invoice_filename: str, file_path: str) -> Dict:
        """
        Create an Adaptive Card for invoice approval.
        
        Args:
            invoice_data: Extracted invoice data
            approval_info: Approval status information
            invoice_filename: Name of the invoice file
            file_path: Path to the invoice file
            
        Returns:
            Adaptive Card JSON
        """
        invoice_number = invoice_data.get('invoice_number', 'N/A')
        invoice_date = invoice_data.get('invoice_date', 'N/A')
        total_price = invoice_data.get('total_price', 'N/A')
        item_count = approval_info.get('item_count', 0)
        total_amount = approval_info.get('total_amount', 0)
        reasons = approval_info.get('reasons', [])
        
        # Build items list for display
        items = invoice_data.get('items', [])
        items_text = []
        for i, item in enumerate(items[:5], 1):  # Show first 5 items
            item_name = item.get('item_name', 'Unknown')
            item_price = item.get('item_price', 'N/A')
            items_text.append(f"{i}. {item_name}: {item_price}")
        
        if len(items) > 5:
            items_text.append(f"... and {len(items) - 5} more items")
        
        items_display = "\n\n".join(items_text) if items_text else "No items found"
        
        # Create callback URLs for approve/reject actions
        # Encode the filename for URL safety
        encoded_filename = quote(invoice_filename)
        approve_url = f"{self.base_url}/api/invoice/approve/{encoded_filename}"
        reject_url = f"{self.base_url}/api/invoice/reject/{encoded_filename}"
        
        # Create the Adaptive Card
        card = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "Container",
                                "style": "warning",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": "⏳ Invoice Pending Approval",
                                        "weight": "Bolder",
                                        "size": "Large",
                                        "color": "Warning"
                                    }
                                ]
                            },
                            {
                                "type": "Container",
                                "spacing": "Medium",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": "**Invoice Details**",
                                        "weight": "Bolder",
                                        "size": "Medium"
                                    },
                                    {
                                        "type": "FactSet",
                                        "facts": [
                                            {
                                                "title": "Invoice Number:",
                                                "value": invoice_number
                                            },
                                            {
                                                "title": "Date:",
                                                "value": invoice_date
                                            },
                                            {
                                                "title": "Total Amount:",
                                                "value": total_price
                                            },
                                            {
                                                "title": "Item Count:",
                                                "value": str(item_count)
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "Container",
                                "spacing": "Medium",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": "**Pending Reason**",
                                        "weight": "Bolder",
                                        "size": "Medium"
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": " • " + "\n • ".join(reasons),
                                        "wrap": True,
                                        "color": "Warning"
                                    }
                                ]
                            },
                            {
                                "type": "Container",
                                "spacing": "Medium",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": "**Line Items**",
                                        "weight": "Bolder",
                                        "size": "Medium"
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": items_display,
                                        "wrap": True,
                                        "spacing": "Small"
                                    }
                                ]
                            },
                            {
                                "type": "Container",
                                "spacing": "Medium",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"**File:** {invoice_filename}",
                                        "wrap": True,
                                        "size": "Small",
                                        "isSubtle": True
                                    }
                                ]
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": "📎 View Invoice",
                                "url": f"{self.base_url}/api/invoice/view/{encoded_filename}",
                                "style": "default"
                            },
                            {
                                "type": "Action.OpenUrl",
                                "title": "✅ Approve",
                                "url": approve_url,
                                "style": "positive"
                            },
                            {
                                "type": "Action.OpenUrl",
                                "title": "❌ Reject",
                                "url": reject_url,
                                "style": "destructive"
                            }
                        ]
                    }
                }
            ]
        }
        
        return card
    
    def send_approval_request(self, invoice_data: Dict, approval_info: Dict, 
                             invoice_filename: str, file_path: str) -> bool:
        """
        Send an approval request card to Teams.
        
        Args:
            invoice_data: Extracted invoice data
            approval_info: Approval status information
            invoice_filename: Name of the invoice file
            file_path: Path to the invoice file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            card = self.create_approval_card(invoice_data, approval_info, 
                                            invoice_filename, file_path)
            
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(card),
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✓ Teams notification sent for {invoice_filename}")
                return True
            else:
                print(f"✗ Teams notification failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error sending Teams notification: {str(e)}")
            return False
    
    def send_approval_result(self, invoice_filename: str, approved: bool, 
                           invoice_number: str = "N/A") -> bool:
        """
        Send a notification about approval/rejection result.
        
        Args:
            invoice_filename: Name of the invoice file
            approved: True if approved, False if rejected
            invoice_number: Invoice number for reference
            
        Returns:
            True if successful, False otherwise
        """
        try:
            status = "✅ Approved" if approved else "❌ Rejected"
            color = "Good" if approved else "Attention"
            
            card = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                            "type": "AdaptiveCard",
                            "version": "1.4",
                            "body": [
                                {
                                    "type": "Container",
                                    "style": "good" if approved else "attention",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": f"{status} - Invoice Processed",
                                            "weight": "Bolder",
                                            "size": "Large"
                                        }
                                    ]
                                },
                                {
                                    "type": "FactSet",
                                    "facts": [
                                        {
                                            "title": "Invoice Number:",
                                            "value": invoice_number
                                        },
                                        {
                                            "title": "File:",
                                            "value": invoice_filename
                                        },
                                        {
                                            "title": "Status:",
                                            "value": "Approved" if approved else "Rejected"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(card),
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"✗ Error sending result notification: {str(e)}")
            return False
