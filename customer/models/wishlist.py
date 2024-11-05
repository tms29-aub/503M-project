from customer import db, ma

class Wishlist(db.Model):
    wishlist_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    def __init__(self, customer_id, product_id, quantity):
        super(Wishlist, self).__init__(customer_id=customer_id, product_id=product_id, quantity=quantity)


class WishlistSchema(ma.ModelSchema):
    class Meta:
        model = Wishlist
        fields = ('wishlist_id', 'customer_id', 'product_id', 'quantity')

wishlist_schema = WishlistSchema()
wishlists_schema = WishlistSchema(many=True)