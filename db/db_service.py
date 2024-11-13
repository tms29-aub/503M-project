from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from enum import Enum


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///503M.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)

# AdminRole
class AdminRole(db.Model):
    admin_role_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    admin_management = db.Column(db.Boolean, nullable=False)
    inventory_management = db.Column(db.Boolean, nullable=False)
    order_management = db.Column(db.Boolean, nullable=False)
    product_management = db.Column(db.Boolean, nullable=False)
    customer_management = db.Column(db.Boolean, nullable=False)
    customer_support = db.Column(db.Boolean, nullable=False)
    logs = db.Column(db.Boolean, nullable=False)
    reports = db.Column(db.Boolean, nullable=False)

    def __init__(self, admin_id, customer_support, logs, product_management, order_management, customer_management, inventory_management, reports):
        super(AdminRole, self).__init__(admin_id=admin_id, customer_support=customer_support, customer_management=customer_management, logs=logs, product_management=product_management, order_management=order_management, inventory_management=inventory_management, reports=reports)

class AdminRoleSchema(ma.Schema):
    class Meta:
        model = AdminRole
        fields = ('admin_role_id', 'admin_id', 'customer_management', 'customer_support', 'logs', 'product_management', 'order_management', 'inventory_management', 'reports')

admin_role_schema = AdminRoleSchema()
admin_roles_schema = AdminRoleSchema(many=True)



# Admin
class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)


    def __init__(self, name, email, phone, password):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        super(Admin, self).__init__(name=name, email=email, phone=phone, hashed_password=hashed_password) 

class AdminSchema(ma.Schema):
    class Meta:
        model = Admin
        fields = ('admin_id', 'name', 'email', 'phone')

admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)



# Log
class Log(db.Model):
    log_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    details = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(80), nullable=False)

    def __init__(self, admin_id, timestamp, details, action):
        super(Log, self).__init__(admin_id=admin_id, timestamp=timestamp, details=details, action=action)

class LogSchema(ma.Schema):
    class Meta:
        model = Log
        fields = ('log_id', 'admin_id', 'timestamp', 'details', 'action')  

log_schema = LogSchema()
logs_schema = LogSchema(many=True)


# Customer
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

    def __init__(self, name, email, phone_number, address, tier):
        super(Customer, self).__init__(name=name, email=email, phone_number=phone_number, address=address, tier=tier)


class CustomerSchema(ma.Schema):
    class Meta:
        model = Customer
        fields = ('customer_id', 'name', 'email', 'phone_number', 'address', 'tier')


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)



# Support
class Support(db.Model):
    ticket_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    issue_description = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Enum('open', 'closed'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, customer_id, issue_description, status, created_at, resolved_at):
        super(Support, self).__init__(customer_id=customer_id, issue_description=issue_description, status=status, created_at=created_at, resolved_at=resolved_at)


class SupportSchema(ma.Schema):
    class Meta:
        model = Support
        fields = ('ticket_id', 'customer_id', 'issue_description', 'status', 'created_at', 'resolved_at')

support_schema = SupportSchema()
supports_schema = SupportSchema(many=True)



# Wishlist
class Wishlist(db.Model):
    wishlist_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    def __init__(self, customer_id, product_id, quantity):
        super(Wishlist, self).__init__(customer_id=customer_id, product_id=product_id, quantity=quantity)


class WishlistSchema(ma.Schema):
    class Meta:
        model = Wishlist
        fields = ('wishlist_id', 'customer_id', 'product_id', 'quantity')

wishlist_schema = WishlistSchema()
wishlists_schema = WishlistSchema(many=True)


# ProductCategory
class ProductCategory(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)

    def __init__(self, name, description):
        super(ProductCategory, self).__init__(name=name, description=description)


class ProductCategorySchema(ma.Schema):
    class Meta:
        model = ProductCategory
        fields = ('category_id', 'name', 'description')

product_category_schema = ProductCategorySchema()
product_categories_schema = ProductCategorySchema(many=True)




# Product
class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('product_category.category_id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    subcategory = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, category_id, name, image, description, price, quantity_in_stock, subcategory, created_at, updated_at):
        super(Product, self).__init__(category_id=category_id, image=image, name=name, description=description, subcategory=subcategory, price=price, quantity_in_stock=quantity_in_stock, created_at=created_at, updated_at=updated_at)

class ProductSchema(ma.Schema):
    class Meta:
        model = Product
        fields = ('product_id', 'category_id', 'name', 'image', 'subcategory', 'description', 'price', 'quantity_in_stock', 'created_at', 'updated_at')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)



# Report
class Report(db.Model):
    report_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    report_date = db.Column(db.DateTime, nullable=False)
    turnover_rate = db.Column(db.Float, nullable=False)
    demand_forecast = db.Column(db.Integer, nullable=False)
    most_popular = db.Column(db.String(80), nullable=False)
    def __init__(self, product_id, report_date, turnover_rate, demand_forecast, most_popular):
        super(Report, self).__init__(product_id=product_id, report_date=report_date, turnover_rate=turnover_rate, demand_forecast=demand_forecast, most_popular=most_popular)


class ReportSchema(ma.Schema):
    class Meta:
        model = Report
        fields = ('report_id', 'product_id', 'report_date', 'turnover_rate', 'demand_forecast', 'most_popular')


report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)


# OrderItem
class OrderItem(db.Model):
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
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




# Order
class OrderStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
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


# Return
class ReturnStatus(Enum):
    PENDING = 'pending'
    COMPLETE = 'complete'

class Return(db.Model):
    return_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=False)
    return_reason = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Enum(ReturnStatus), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    replaced_order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=True)
    def __init__(self, order_id, return_reason, status, created_at):
        super(Return, self).__init__(order_id=order_id, return_reason=return_reason, status=status, created_at=created_at)


class ReturnSchema(ma.Schema):
    class Meta:
        model = Return
        fields = ('return_id', 'order_id', 'return_reason', 'status', 'created_at')

return_schema = ReturnSchema()
returns_schema = ReturnSchema(many=True)

# Run Flask App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
