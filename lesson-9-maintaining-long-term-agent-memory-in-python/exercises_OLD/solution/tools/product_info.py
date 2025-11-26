# tools/product_info.py
from semantic_kernel.functions import kernel_function
import logging

logger = logging.getLogger(__name__)

class ProductInfoTools:
    @kernel_function(name="get_product_info", description="Get detailed information about a product by product ID")
    def get_product_info(self, product_id: str):
        """
        Get detailed information about a product by its ID.
        
        Args:
            product_id: The unique identifier for the product
            
        Returns:
            Dictionary containing product information
        """
        try:
            logger.info(f"Getting product info for product ID: {product_id}")
            
            # Mock product data - in a real application, this would query a database
            mock_products = {
                "PROD-001": {
                    "product_id": "PROD-001",
                    "name": "Wireless Bluetooth Headphones",
                    "price": 99.99,
                    "category": "Electronics",
                    "description": "High-quality wireless headphones with noise cancellation",
                    "in_stock": True,
                    "stock_quantity": 50,
                    "rating": 4.5,
                    "reviews": 128
                },
                "PROD-002": {
                    "product_id": "PROD-002",
                    "name": "Smart Fitness Watch",
                    "price": 199.99,
                    "category": "Wearables",
                    "description": "Advanced fitness tracking watch with heart rate monitoring",
                    "in_stock": True,
                    "stock_quantity": 25,
                    "rating": 4.8,
                    "reviews": 89
                },
                "PROD-003": {
                    "product_id": "PROD-003",
                    "name": "Portable Phone Charger",
                    "price": 29.99,
                    "category": "Accessories",
                    "description": "High-capacity portable charger for smartphones",
                    "in_stock": False,
                    "stock_quantity": 0,
                    "rating": 4.2,
                    "reviews": 67
                }
            }
            
            if product_id in mock_products:
                return mock_products[product_id]
            else:
                return {
                    "product_id": product_id,
                    "name": "Unknown Product",
                    "message": "Product not found"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get product info: {e}")
            return {
                "product_id": product_id,
                "name": "Unknown Product",
                "message": f"Error retrieving product info: {e}"
            }
