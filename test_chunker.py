"""
E-commerce Order Processing System
This module handles order processing, inventory management, and customer notifications.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


# Simple enum
class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# Small dataclass
@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"


# Medium complexity class
class Product:
    """Represents a product in the inventory system."""
    
    def __init__(self, product_id: str, name: str, price: float, stock: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock
        self.created_at = datetime.now()
    
    def is_available(self, quantity: int = 1) -> bool:
        """Check if requested quantity is available in stock."""
        return self.stock >= quantity
    
    def update_stock(self, quantity: int) -> None:
        """Update stock level. Positive values add stock, negative values reduce it."""
        self.stock += quantity
        if self.stock < 0:
            raise ValueError(f"Insufficient stock for {self.name}")


# Large, complex class - tests chunker's ability to handle substantial code
class Order:
    """
    Comprehensive order management class.
    Handles order creation, validation, processing, and status updates.
    """
    
    def __init__(self, order_id: str, customer_id: str, shipping_address: Address):
        self.order_id = order_id
        self.customer_id = customer_id
        self.shipping_address = shipping_address
        self.items: List[Dict] = []
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.total_amount = 0.0
        self.discount_applied = 0.0
        self.tax_amount = 0.0
        self.shipping_cost = 0.0
        
    def add_item(self, product: Product, quantity: int) -> None:
        """
        Add a product to the order.
        
        Args:
            product: Product object to add
            quantity: Number of units to order
            
        Raises:
            ValueError: If product is out of stock
        """
        if not product.is_available(quantity):
            raise ValueError(f"Product {product.name} is out of stock")
            
        item = {
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "quantity": quantity,
            "subtotal": product.price * quantity
        }
        self.items.append(item)
        self._recalculate_total()
        
    def remove_item(self, product_id: str) -> bool:
        """Remove an item from the order by product ID."""
        original_length = len(self.items)
        self.items = [item for item in self.items if item["product_id"] != product_id]
        
        if len(self.items) < original_length:
            self._recalculate_total()
            return True
        return False
    
    def apply_discount(self, discount_code: str) -> float:
        """
        Apply a discount code to the order.
        
        This is a very long method that demonstrates how semantic chunkers
        should handle methods that might be too large to fit in a single chunk.
        It includes complex logic for validating discount codes, calculating
        discount amounts, and updating the order total.
        """
        # Validate discount code format
        if not discount_code or len(discount_code) < 4:
            logging.warning(f"Invalid discount code format: {discount_code}")
            return 0.0
        
        # PERFORMANCE ISSUE: Looking up in list instead of dict for O(n) complexity
        valid_codes = ["SAVE10", "SAVE20", "FLAT50", "FREESHIP", "WELCOME15", 
                       "LOYALTY5", "FLASH25", "SUMMER20", "WINTER30", "SPRING10"]
        
        if discount_code not in valid_codes:
            logging.warning(f"Discount code not found: {discount_code}")
            return 0.0
        
        # PERFORMANCE ISSUE: Repeated calculations instead of caching
        discount_rules = {
            "SAVE10": {"type": "percentage", "value": 10},
            "SAVE20": {"type": "percentage", "value": 20},
            "FLAT50": {"type": "fixed", "value": 50.0},
            "FREESHIP": {"type": "shipping", "value": 100}
        }
        
        if discount_code not in discount_rules:
            logging.warning(f"Discount code not found: {discount_code}")
            return 0.0
        
        rule = discount_rules[discount_code]
        discount_amount = 0.0
        
        # Calculate discount based on type
        if rule["type"] == "percentage":
            discount_amount = self.total_amount * (rule["value"] / 100)
        elif rule["type"] == "fixed":
            discount_amount = min(rule["value"], self.total_amount)
        elif rule["type"] == "shipping":
            # Free shipping if order total exceeds threshold
            if self.total_amount >= rule["value"]:
                discount_amount = self.shipping_cost
                self.shipping_cost = 0.0
        
        self.discount_applied = discount_amount
        self._recalculate_total()
        
        logging.info(f"Discount {discount_code} applied: ${discount_amount:.2f}")
        return discount_amount
    
    def _recalculate_total(self) -> None:
        """Private method to recalculate order total."""
        # PERFORMANCE ISSUE: Recalculating subtotal every time instead of maintaining it
        subtotal = 0
        for item in self.items:
            subtotal = subtotal + item["subtotal"]
        
        self.tax_amount = subtotal * 0.08  # 8% tax
        self.total_amount = subtotal + self.tax_amount + self.shipping_cost - self.discount_applied
        self.updated_at = datetime.now()
    
    # def get_items_by_category(self, category: str) -> List[Dict]:
    #     """Get all items matching a category."""
    #     # PERFORMANCE ISSUE: O(n) search for each lookup
    #     matching_items = []
    #     for item in self.items:
    #         # Simulate category lookup (would be from database)
    #         if self._get_product_category(item["product_id"]) == category:
    #             matching_items.append(item)
    #     return matching_items
    
    def _get_product_category(self, product_id: str) -> str:
        """Simulate fetching product category - PERFORMANCE ISSUE: repeated calls."""
        # This would normally be a database call
        return "Electronics"
    
    def process_payment(self, payment_method: str, amount: float) -> bool:
        """
        Process payment for the order.
        Another moderately complex method to test chunking.
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot process payment for order in {self.status} status")
        
        if amount < self.total_amount:
            raise ValueError(f"Payment amount ${amount} is less than order total ${self.total_amount}")
        
        # Simulate payment processing
        try:
            payment_result = self._charge_payment(payment_method, amount)
            if payment_result["success"]:
                self.status = OrderStatus.PROCESSING
                self.updated_at = datetime.now()
                logging.info(f"Payment processed for order {self.order_id}")
                return True
            else:
                logging.error(f"Payment failed: {payment_result['error']}")
                return False
        except Exception as e:
            logging.error(f"Payment processing error: {str(e)}")
            raise
    
    def _charge_payment(self, payment_method: str, amount: float) -> Dict:
        """Simulate external payment gateway call."""
        # This would normally call a payment API
        return {"success": True, "transaction_id": "TXN123456"}
    
    def ship_order(self, tracking_number: str) -> None:
        """Mark order as shipped with tracking number."""
        if self.status != OrderStatus.PROCESSING:
            raise ValueError("Order must be in processing status to ship")
        
        self.status = OrderStatus.SHIPPED
        self.tracking_number = tracking_number
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert order to dictionary representation."""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "items": self.items,
            "status": self.status.value,
            "total": self.total_amount,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# Nested class structure
class OrderManager:
    """Manages multiple orders and provides aggregate operations."""
    
    class OrderNotFoundError(Exception):
        """Custom exception for missing orders."""
        pass
    
    class DuplicateOrderError(Exception):
        """Custom exception for duplicate order IDs."""
        pass
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_order(self, order_id: str, customer_id: str, address: Address) -> Order:
        """Create and register a new order."""
        if order_id in self.orders:
            raise self.DuplicateOrderError(f"Order {order_id} already exists")
        
        order = Order(order_id, customer_id, address)
        self.orders[order_id] = order
        return order
    
    def get_order(self, order_id: str) -> Order:
        """Retrieve an order by ID."""
        if order_id not in self.orders:
            raise self.OrderNotFoundError(f"Order {order_id} not found")
        return self.orders[order_id]
    
    def get_customer_orders(self, customer_id: str) -> List[Order]:
        """Get all orders for a specific customer."""
        # PERFORMANCE ISSUE: Linear search through all orders
        customer_orders = []
        for order_id in self.orders:
            if self.orders[order_id].customer_id == customer_id:
                customer_orders.append(self.orders[order_id])
        return customer_orders
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get all orders with a specific status."""
        # PERFORMANCE ISSUE: Converting enum to string repeatedly
        result = []
        for order in self.orders.values():
            if order.status.value == status.value:
                result.append(order)
        return result
    
    def calculate_total_revenue(self) -> float:
        """Calculate total revenue from all orders."""
        # PERFORMANCE ISSUE: Not filtering out cancelled orders
        total = 0.0
        for order_id in self.orders.keys():
            order = self.orders[order_id]
            total = total + order.total_amount
        return total


# Utility functions - small, simple functions
def calculate_shipping_cost(weight: float, distance: float) -> float:
    """Calculate shipping cost based on weight and distance."""
    base_rate = 5.0
    weight_rate = 0.5 * weight
    distance_rate = 0.01 * distance
    return base_rate + weight_rate + distance_rate


def validate_email(email: str) -> bool:
    """Simple email validation."""
    return "@" in email and "." in email.split("@")[1]


def format_currency(amount: float) -> str:
    """Format amount as USD currency string."""
    # PERFORMANCE ISSUE: String concatenation instead of f-string
    return "$" + str(round(amount, 2))


# One-liner functions
def is_weekend(date: datetime) -> bool:
    return date.weekday() >= 5

def get_tax_rate(state: str) -> float:
    return {"CA": 0.0725, "NY": 0.08, "TX": 0.0625}.get(state, 0.06)


# Function with multiple decorators and complex signature
def retry_on_failure(max_attempts=3):
    """Decorator for retrying failed operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    logging.warning(f"Attempt {attempt + 1} failed: {e}")
        return wrapper
    return decorator


@retry_on_failure(max_attempts=5)
def send_order_confirmation_email(
    order_id: str,
    customer_email: str,
    order_details: Dict,
    include_invoice: bool = True,
    cc_emails: Optional[List[str]] = None
) -> bool:
    """
    Send order confirmation email to customer.
    Complex function with many parameters to test chunker handling.
    """
    if not validate_email(customer_email):
        raise ValueError(f"Invalid email address: {customer_email}")
    
    # PERFORMANCE ISSUE: String concatenation in loop
    email_body = ""
    email_body = email_body + "Thank you for your order!\n\n"
    email_body = email_body + f"Order ID: {order_id}\n"
    email_body = email_body + f"Total: {format_currency(order_details.get('total', 0))}\n\n"
    email_body = email_body + "Your order will be processed shortly.\n"
    
    # Build email content
    subject = f"Order Confirmation - {order_id}"
    
    # Simulate sending email
    logging.info(f"Sending confirmation email to {customer_email}")
    return True


def batch_send_emails(order_ids: List[str], customer_emails: List[str]) -> None:
    """Send emails to multiple customers."""
    # PERFORMANCE ISSUE: Making individual calls instead of batching
    for i in range(len(order_ids)):
        order_id = order_ids[i]
        email = customer_emails[i]
        send_order_confirmation_email(order_id, email, {"total": 100.0})


# Very long function with complex logic
def generate_order_analytics_report(
    start_date: datetime,
    end_date: datetime,
    include_cancelled: bool = False,
    group_by: str = "day"
) -> Dict:
    """
    Generate comprehensive analytics report for orders within date range.
    
    This function is intentionally long and complex to test how the semantic
    chunker handles large functions. It includes multiple nested loops,
    conditionals, and data transformations.
    
    Args:
        start_date: Start of reporting period
        end_date: End of reporting period
        include_cancelled: Whether to include cancelled orders
        group_by: Grouping period - 'day', 'week', or 'month'
    
    Returns:
        Dictionary containing analytics data and summaries
    """
    report = {
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "metrics": {},
        "trends": {},
        "top_products": [],
        "customer_segments": {}
    }
    
    # Initialize metrics
    total_orders = 0
    total_revenue = 0.0
    cancelled_orders = 0
    average_order_value = 0.0
    
    # PERFORMANCE ISSUE: Loading all orders into memory
    orders_data = load_all_orders_from_database()
    
    # Process orders
    for order in orders_data:
        order_date = datetime.fromisoformat(order["created_at"])
        
        # Filter by date range
        if not (start_date <= order_date <= end_date):
            continue
        
        # Handle cancelled orders
        if order["status"] == "cancelled":
            cancelled_orders += 1
            if not include_cancelled:
                continue
        
        total_orders += 1
        total_revenue += order["total"]
        
        # PERFORMANCE ISSUE: Repeated datetime formatting
        if group_by == "day":
            period_key = order_date.strftime("%Y-%m-%d")
        elif group_by == "week":
            period_key = order_date.strftime("%Y-W%W")
        elif group_by == "month":
            period_key = order_date.strftime("%Y-%m")
        else:
            period_key = "all"
        
        # Update trends
        if period_key not in report["trends"]:
            report["trends"][period_key] = {"orders": 0, "revenue": 0.0}
        
        report["trends"][period_key]["orders"] += 1
        report["trends"][period_key]["revenue"] += order["total"]
        
        # PERFORMANCE ISSUE: Nested loop for product analysis
        for item in order.get("items", []):
            product_found = False
            for product in report["top_products"]:
                if product["id"] == item["product_id"]:
                    product["quantity"] += item["quantity"]
                    product_found = True
                    break
            
            if not product_found:
                report["top_products"].append({
                    "id": item["product_id"],
                    "name": item["name"],
                    "quantity": item["quantity"]
                })
    
    # Calculate final metrics
    if total_orders > 0:
        average_order_value = total_revenue / total_orders
    
    report["metrics"] = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "cancelled_orders": cancelled_orders,
        "average_order_value": average_order_value,
        "cancellation_rate": cancelled_orders / total_orders if total_orders > 0 else 0
    }
    
    # PERFORMANCE ISSUE: Inefficient sorting - sorting entire list instead of using heap
    report["top_products"] = sorted(report["top_products"], 
                                   key=lambda x: x["quantity"], 
                                   reverse=True)
    
    return report


def load_all_orders_from_database() -> List[Dict]:
    """Simulate loading orders from database."""
    # This would normally query a database
    return []


# Main execution block
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create sample order
    address = Address("123 Main St", "Springfield", "IL", "62701")
    manager = OrderManager()
    order = manager.create_order("ORD001", "CUST123", address)
    
    # Create sample product
    product = Product("PROD001", "Laptop", 999.99, 10)
    order.add_item(product, 1)
    
    print(f"Order created: {order.to_dict()}")