# tools/inventory.py
from semantic_kernel.functions import kernel_function
import requests
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class InventoryTools:
    """Tools for inventory management and stock checking using external APIs"""
    
    def __init__(self):
        # Using JSONPlaceholder as a mock API for demonstration
        self.base_url = "https://jsonplaceholder.typicode.com"
    
    @kernel_function(name="check_inventory", description="Check inventory levels for products using external API")
    def check_inventory(self, product_ids: str = None, category: str = None) -> Dict[str, Any]:
        """
        Check inventory levels for specific products or categories using external API.
        
        Args:
            product_ids: Comma-separated list of product IDs to check
            category: Product category to check inventory for
            
        Returns:
            Dictionary containing inventory information from external API
        """
        try:
            logger.info(f"Checking inventory via external API for products: {product_ids}, category: {category}")
            
            # Simulate API call to external inventory service
            # In a real implementation, this would call your actual inventory API
            api_response = {
                "status": "success",
                "timestamp": "2024-01-15T12:00:00Z",
                "data": {
                    "PROD-001": {
                        "product_id": "PROD-001",
                        "name": "Wireless Bluetooth Headphones",
                        "category": "Electronics",
                        "in_stock": True,
                        "quantity_available": 150,
                        "quantity_reserved": 25,
                        "quantity_available_for_sale": 125,
                        "warehouse_location": "Warehouse A",
                        "last_updated": "2024-01-15T10:30:00Z",
                        "supplier": "TechCorp Inc",
                        "cost_price": 45.00,
                        "retail_price": 99.99
                    },
                    "PROD-002": {
                        "product_id": "PROD-002", 
                        "name": "Smart Fitness Watch",
                        "category": "Wearables",
                        "in_stock": True,
                        "quantity_available": 75,
                        "quantity_reserved": 10,
                        "quantity_available_for_sale": 65,
                        "warehouse_location": "Warehouse B",
                        "last_updated": "2024-01-15T09:45:00Z",
                        "supplier": "FitTech Solutions",
                        "cost_price": 120.00,
                        "retail_price": 199.99
                    },
                    "PROD-003": {
                        "product_id": "PROD-003",
                        "name": "Portable Phone Charger", 
                        "category": "Accessories",
                        "in_stock": False,
                        "quantity_available": 0,
                        "quantity_reserved": 0,
                        "quantity_available_for_sale": 0,
                        "warehouse_location": "Warehouse A",
                        "last_updated": "2024-01-14T16:20:00Z",
                        "supplier": "PowerTech Ltd",
                        "cost_price": 15.00,
                        "retail_price": 29.99,
                        "restock_date": "2024-01-25T00:00:00Z"
                    }
                }
            }
            
            results = []
            
            if product_ids:
                # Check specific products
                product_list = [pid.strip() for pid in product_ids.split(",")]
                for product_id in product_list:
                    if product_id in api_response["data"]:
                        results.append(api_response["data"][product_id])
                    else:
                        results.append({
                            "product_id": product_id,
                            "name": "Unknown Product",
                            "in_stock": False,
                            "quantity_available": 0,
                            "message": "Product not found in inventory system"
                        })
            elif category:
                # Check products by category
                for product_id, product_data in api_response["data"].items():
                    if product_data.get("category", "").lower() == category.lower():
                        results.append(product_data)
            else:
                # Return all inventory
                results = list(api_response["data"].values())
            
            return {
                "api_source": "External Inventory Management System",
                "api_endpoint": f"{self.base_url}/inventory",
                "inventory_check": {
                    "timestamp": api_response["timestamp"],
                    "status": api_response["status"],
                    "total_products_checked": len(results),
                    "products_in_stock": len([p for p in results if p.get("in_stock", False)]),
                    "products_out_of_stock": len([p for p in results if not p.get("in_stock", False)]),
                    "products": results
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to check inventory via external API: {e}")
            return {
                "api_source": "External Inventory Management System",
                "api_endpoint": f"{self.base_url}/inventory",
                "inventory_check": {
                    "timestamp": "2024-01-15T12:00:00Z",
                    "status": "error",
                    "error": f"API call failed: {e}",
                    "products": []
                }
            }
    
    @kernel_function(name="get_supplier_info", description="Get supplier information for products")
    def get_supplier_info(self, product_id: str) -> Dict[str, Any]:
        """
        Get supplier information for a specific product using external API.
        
        Args:
            product_id: Product ID to get supplier info for
            
        Returns:
            Dictionary containing supplier information
        """
        try:
            logger.info(f"Getting supplier info via external API for product: {product_id}")
            
            # Simulate API call to supplier management system
            supplier_api_response = {
                "status": "success",
                "timestamp": "2024-01-15T12:00:00Z",
                "data": {
                    "PROD-001": {
                        "supplier_id": "SUP-001",
                        "supplier_name": "TechCorp Inc",
                        "contact_email": "orders@techcorp.com",
                        "contact_phone": "+1-555-0123",
                        "lead_time_days": 7,
                        "minimum_order_quantity": 50,
                        "payment_terms": "Net 30",
                        "rating": 4.8,
                        "reliability_score": 95
                    },
                    "PROD-002": {
                        "supplier_id": "SUP-002", 
                        "supplier_name": "FitTech Solutions",
                        "contact_email": "sales@fittech.com",
                        "contact_phone": "+1-555-0456",
                        "lead_time_days": 14,
                        "minimum_order_quantity": 25,
                        "payment_terms": "Net 45",
                        "rating": 4.6,
                        "reliability_score": 92
                    },
                    "PROD-003": {
                        "supplier_id": "SUP-003",
                        "supplier_name": "PowerTech Ltd",
                        "contact_email": "orders@powertech.com",
                        "contact_phone": "+1-555-0789",
                        "lead_time_days": 21,
                        "minimum_order_quantity": 100,
                        "payment_terms": "Net 30",
                        "rating": 4.4,
                        "reliability_score": 88
                    }
                }
            }
            
            if product_id in supplier_api_response["data"]:
                return {
                    "api_source": "External Supplier Management System",
                    "api_endpoint": f"{self.base_url}/suppliers",
                    "supplier_info": supplier_api_response["data"][product_id]
                }
            else:
                return {
                    "api_source": "External Supplier Management System",
                    "api_endpoint": f"{self.base_url}/suppliers",
                    "supplier_info": {
                        "product_id": product_id,
                        "message": "Supplier information not found"
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get supplier info via external API: {e}")
            return {
                "api_source": "External Supplier Management System",
                "api_endpoint": f"{self.base_url}/suppliers",
                "supplier_info": {
                    "product_id": product_id,
                    "error": f"API call failed: {e}"
                }
            }
