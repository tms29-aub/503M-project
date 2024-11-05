from order import db, ma
from enum import Enum

class ReturnStatus(Enum):
    PENDING = 'pending'
    REFUNDED = 'refunded'
    REPLACED = 'replaced'

class Returns(db.Model):
    return_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    return_reason = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Enum(ReturnStatus), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    def __init__(self, order_id, return_reason, status, created_at):
        super(Returns, self).__init__(order_id=order_id, return_reason=return_reason, status=status, created_at=created_at)


class ReturnsSchema(ma.Schema):
    class Meta:
        model = Returns
        fields = ('return_id', 'order_id', 'return_reason', 'status', 'created_at')

return_schema = ReturnsSchema()
returns_schema = ReturnsSchema(many=True)
