from inventory import db, ma

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.category_id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotions.promotion_id'), nullable=True)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    reorder_level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, category_id, name, description, price, quantity_in_stock, reorder_level, created_at, updated_at):
        super(Product, self).__init__(category_id=category_id, name=name, description=description, price=price, quantity_in_stock=quantity_in_stock, reorder_level=reorder_level, created_at=created_at, updated_at=updated_at)

class ProductSchema(ma.ModelSchema):
    class Meta:
        model = Product
        fields = ('product_id', 'category_id', 'name', 'description', 'price', 'quantity_in_stock', 'reorder_level', 'created_at', 'updated_at')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)