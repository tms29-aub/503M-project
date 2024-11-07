from order import db, ma

class OrderItem(db.Model):
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
    def __init__(self, order_id, product_id, quantity, price_at_purchase):
        super(OrderItem, self).__init__(order_id=order_id, product_id=product_id, quantity=quantity, price_at_purchase=price_at_purchase)


class OrderItemSchema(ma.Schema):
    class Meta:
        model = OrderItem
        fields = ('order_item_id', 'order_id', 'product_id', 'quantity', 'price_at_purchase')

order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)