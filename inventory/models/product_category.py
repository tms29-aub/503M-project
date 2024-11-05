from inventory import db, ma

class ProductCategory(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)

    def __init__(self, name, description):
        super(ProductCategory, self).__init__(name=name, description=description)


class ProductCategorySchema(ma.ModelSchema):
    class Meta:
        model = ProductCategory
        fields = ('category_id', 'name', 'description')

product_category_schema = ProductCategorySchema()
product_categories_schema = ProductCategorySchema(many=True)