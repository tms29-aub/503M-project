from inventory import db, ma
from enum import Enum
from customer.models.customer import CustomerTier

class PromotionType(Enum):
    percentage = 'percentage'
    fixed = 'fixed'

class Promotion(db.Model):
    promotion_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    discount_type = db.Column(db.String(80), nullable=False)
    discount_value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    user_tier = db.Column(db.Enum(CustomerTier), nullable=False)

    def __init__(self, name, product_id, discount_type, discount_value, start_date, end_date, user_tier):
        super(Promotion, self).__init__(name=name, product_id=product_id, discount_type=discount_type, discount_value=discount_value, start_date=start_date, end_date=end_date, user_tier=user_tier)


class PromotionSchema(ma.Schema):
    class Meta:
        fields = ('promotion_id', 'name', 'product_id', 'discount_type', 'discount_value', 'start_date', 'end_date', 'user_tier')


promotion_schema = PromotionSchema()
promotions_schema = PromotionSchema(many=True)