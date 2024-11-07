from order import db, ma
from enum import Enum

class OrderStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    status = db.Column(db.Enum(OrderStatus), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    def __init__(self, customer_id, status, total_amount, created_at, updated_at):
        super(Order, self).__init__(customer_id=customer_id, status=status, total_amount=total_amount, created_at=created_at, updated_at=updated_at)

class OrderSchema(ma.Schema):
    class Meta:
        model = Order
        fields = ('order_id', 'customer_id', 'status', 'total_amount', 'created_at', 'updated_at')

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)