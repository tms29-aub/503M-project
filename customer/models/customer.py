from customer import db, ma
from enum import Enum


class CustomerTier(Enum):
    NORMAL = 1
    PREMIUM = 2
    GOLD = 3

class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(80), nullable=False)
    tier = db.Column(db.Enum(CustomerTier), nullable=False)
    support_ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.support_ticket_id'), nullable=False)

    def __init__(self, name, email, phone_number, address, support_ticket_id, tier):
        super(Customer, self).__init__(name=name, email=email, phone_number=phone_number, address=address, support_ticket_id=support_ticket_id, tier=tier)


class CustomerSchema(ma.Schema):
    class Meta:
        model = Customer
        fields = ('customer_id', 'name', 'email', 'phone_number', 'address', 'support_ticket_id', 'tier')


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)