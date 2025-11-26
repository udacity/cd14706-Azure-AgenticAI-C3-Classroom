# tools/order_status.py
from semantic_kernel.functions import kernel_function
import logging

logger = logging.getLogger(__name__)

class OrderStatusTools:
    @kernel_function(name="get_order_status", description="Get the status of an order by order ID")
    def get_order_status(self, order_id: str):
        """
        Get the status of an order by its ID.
        
        Args:
            order_id: The unique identifier for the order
            
        Returns:
            Dictionary containing order status information
        """
        try:
            logger.info(f"Getting order status for order ID: {order_id}")
            
            # Simulated database query - uses mock data for demonstration purposes
            mock_orders = {
                "ORD-001": {
                    "order_id": "ORD-001",
                    "status": "shipped",
                    "tracking_number": "TRK123456789",
                    "estimated_delivery": "2024-01-15",
                    "items": ["Product A", "Product B"]
                },
                "ORD-002": {
                    "order_id": "ORD-002", 
                    "status": "processing",
                    "tracking_number": None,
                    "estimated_delivery": "2024-01-20",
                    "items": ["Product C"]
                },
                "ORD-003": {
                    "order_id": "ORD-003",
                    "status": "delivered",
                    "tracking_number": "TRK987654321",
                    "estimated_delivery": "2024-01-10",
                    "items": ["Product D", "Product E"]
                }
            }
            
            if order_id in mock_orders:
                return mock_orders[order_id]
            else:
                return {
                    "order_id": order_id,
                    "status": "not_found",
                    "message": "Order not found"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get order status: {e}")
            return {
                "order_id": order_id,
                "status": "error",
                "message": f"Error retrieving order status: {e}"
            }
