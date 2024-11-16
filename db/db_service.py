from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from enum import Enum
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///503M.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
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

    def __init__(self, admin_id, admin_management, customer_support, logs, product_management, order_management, customer_management, inventory_management, reports):
        super(AdminRole, self).__init__(admin_id=admin_id, admin_management=admin_management, customer_support=customer_support, customer_management=customer_management, logs=logs, product_management=product_management, order_management=order_management, inventory_management=inventory_management, reports=reports)

class AdminRoleSchema(ma.Schema):
    class Meta:
        model = AdminRole
        fields = ('admin_role_id', 'admin_id', 'admin_management', 'customer_management', 'customer_support', 'logs', 'product_management', 'order_management', 'inventory_management', 'reports')

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
    user_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    details = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(80), nullable=False)

    def __init__(self, user_id, timestamp, details, action):
        super(Log, self).__init__(user_id=user_id, timestamp=timestamp, details=details, action=action)

class LogSchema(ma.Schema):
    class Meta:
        model = Log
        fields = ('log_id', 'user_id', 'timestamp', 'details', 'action')  

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

# Promotion
class PromotionType(Enum):
    percentage = 'percentage'
    fixed = 'fixed'

class Promotion(db.Model):
    promotion_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    discount_type = db.Column(db.String(80), nullable=False)
    discount_value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    user_tier = db.Column(db.String(80), nullable=False)
    def __init__(self, name, discount_type, discount_value, start_date, end_date, user_tier):
        super(Promotion, self).__init__(name=name, discount_type=discount_type, discount_value=discount_value, start_date=start_date, end_date=end_date, user_tier=user_tier)

class PromotionSchema(ma.Schema):
    class Meta:
        fields = ('promotion_id', 'name', 'discount_type', 'discount_value', 'start_date', 'end_date', 'user_tier')

promotion_schema = PromotionSchema()
promotions_schema = PromotionSchema(many=True)


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


# Admin routes

@app.route('/admin/authenticate', methods=['POST'])
def authenticate_admin():
    '''
    Login as Admin.

    Requires:
        email (str)
        password (str)

    Returns:
        200: JWT Token
        401: Unauthorized
        500: Internal server error
    '''
    required_fields = ['email', 'password']
    # Check if all required fields are present
    if not all(field in request.json for field in required_fields):
        return abort(400, "Bad request")

    email = request.json['email']
    password = request.json['password']

    if type(email) != str or type(password) != str:
        return abort(400, "Bad request")
    
    admin = Admin.query.filter_by(email=email, password=password).first()
    if not admin:
        return abort(401, "Unauthorized")
    return admin_schema.dump(admin)

@app.route('/admin/<int:admin_id>', methods=['GET'])
def get_admin(admin_id):
    '''
    Get admin by admin_id

    Requires:
        admin_id (int)

    Returns:
        200: Admin
        404: Admin not found
    '''
    a = Admin.query.filter_by(id=admin_id).first()
    if not a:
        return abort(404, "Admin not found")
    return jsonify(admin_schema.dump(a))


@app.route('/admin/email/<string:email>', methods=['GET'])
def get_admin_by_email(email):
    '''
    Get admin by email

    Requires:
        email (str)

    Returns:
        200: Admin
        404: Admin not found
    '''
    admin = Admin.query.filter_by(email=email).first()
    if not admin:
        return abort(404, "Admin not found")
    return jsonify(admin_schema.dump(admin))


@app.route('/add-admin', methods=['POST'])
def add_admin():
    '''
    Create new Admin.

    Requires:
        name (str)
        email (str)
        password (str)
        phone (int)

    Returns:
        201: Admin created successfully
        400: Bad request
        500: Internal server error
    '''

    required_fields = ['name', 'email', 'password', 'phone']

    if not all(field in request.json for field in required_fields):
        return abort(400, "Bad request")
    
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    phone = request.json['phone']
    
    if type(name) != str or type(email) != str or type(password) != str or type(phone) != int:
        return abort(400, "Bad request")
    
    try:
        admin = Admin(name=name, email=email, password=password, phone=phone)

        log_detail = f'{admin.name} is now an admin'
        log = Log(user_id=admin.admin_id, timestamp=datetime.now(), details=log_detail, action='CREATE ADMIN')
        
        db.session.add(admin)
        db.session.add(log)
        db.session.commit()
        
        return admin_schema.dump(admin), 201
    except:
        return abort(400, "Server Error")


# AdminRole routes

@app.route('/add-admin-role', methods=['POST'])
def add_admin_role():
    '''
    Create Admin Role for an Admin.

    Requires:
        admin_id (int)
        customer_support (bool)
        logs (bool)
        product_management (bool)
        order_management (bool)
        customer_management (bool)
        inventory_management (bool)
        reports (bool)

    Returns:
        201: Admin Role created successfully
        400: Bad request
        500: Internal server error
    '''

    required_fields = ['admin_id', 'customer_support', 'logs', 'product_management', 'order_management', 'customer_management', 'inventory_management', 'reports']

    if not all(field in request.json for field in required_fields):
        return abort(400, "Bad request")
    
    admin_id = request.json['admin_id']
    customer_support = request.json['customer_support']
    logs = request.json['logs']
    product_management = request.json['product_management']
    order_management = request.json['order_management']
    customer_management = request.json['customer_management']
    inventory_management = request.json['inventory_management']
    reports = request.json['reports']

    if type(admin_id) != int or type(customer_support) != bool or type(logs) != bool or type(product_management) != bool or type(order_management) != bool or type(customer_management) != bool or type(inventory_management) != bool or type(reports) != bool:
        return abort(400, "Bad request")

    admin_role = AdminRole(
        admin_id=admin_id,
        customer_support=customer_support,
        logs=logs,
        product_management=product_management,
        order_management=order_management,
        customer_management=customer_management,
        inventory_management=inventory_management,
        reports=reports
    )
    db.session.add(admin_role)

    admin = Admin.query.filter_by(admin_id=admin_id).first()

    log_details = f'{admin.name} roles updated'
    log = Log(user_id=admin.admin_id, timestamp=datetime.now(), details=log_details, action='UPDATE ADMIN ROLES')
    db.session.add(log)
    
    db.session.commit()
    return admin_role_schema.dump(admin_role), 201

def create_tables_and_populate():
    """Create tables and populate with initial data."""
    with app.app_context():
        db.create_all()  # Create all tables

        if Admin.query.first():
            print("Database already populated.")
            return

        # Populate with example data
        try:
            # Admin
            admin1 = Admin(name="John Doe", email="john@example.com", phone=1234567890, password="password123")
            admin2 = Admin(name="Jane Smith", email="jane@example.com", phone=9876543210, password="securepassword")
            db.session.add_all([admin1, admin2])

            # AdminRole
            role1 = AdminRole(admin_id=1, admin_management=True, customer_support=True, logs=True, product_management=True,
                            order_management=True, customer_management=True, inventory_management=True, reports=True)
            role2 = AdminRole(admin_id=2, admin_management=True, customer_support=False, logs=False, product_management=True,
                            order_management=True, customer_management=True, inventory_management=False, reports=False)
            db.session.add_all([role1, role2])

            # Log
            log1 = Log(user_id=1, timestamp=datetime.datetime.now(), details="Logged in", action="Login")
            log2 = Log(user_id=1, timestamp=datetime.datetime.now(), details="Added a product", action="Add Product")
            log3 = Log(user_id=2, timestamp=datetime.datetime.now(), details="Viewed a report", action="View Report")
            db.session.add_all([log1, log2, log3])

            # Customer
            customer1 = Customer(name="Alice Johnson", email="alice@example.com", phone_number=1111111111,
                                address="123 Main St, Cityville", tier=CustomerTier.NORMAL)
            customer2 = Customer(name="Bob Brown", email="bob@example.com", phone_number=2222222222,
                                address="456 Elm St, Townsville", tier=CustomerTier.PREMIUM)
            db.session.add_all([customer1, customer2])

            # Support
            support1 = Support(customer_id=1, issue_description="Order not received", status="open",
                            created_at=datetime.datetime.now(), resolved_at=None)
            support2 = Support(customer_id=2, issue_description="Defective product", status="closed",
                            created_at=datetime.datetime.now(), resolved_at=datetime.datetime.now())
            db.session.add_all([support1, support2])

            # Wishlist
            wishlist1 = Wishlist(customer_id=1, product_id=1, quantity=2)
            wishlist2 = Wishlist(customer_id=2, product_id=2, quantity=1)
            db.session.add_all([wishlist1, wishlist2])

            # ProductCategory
            category1 = ProductCategory(name="Electronics", description="Gadgets and devices")
            category2 = ProductCategory(name="Books", description="Fiction and non-fiction books")
            db.session.add_all([category1, category2])

            # Product
            product1 = Product(category_id=1, name="Smartphone", image="smartphone.jpg", description="Latest model smartphone",
                            subcategory="Mobile", price=699.99, quantity_in_stock=50,
                            created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
            product2 = Product(category_id=2, name="Mystery Novel", image="book.jpg", description="A thrilling mystery novel",
                            subcategory="Mystery", price=15.99, quantity_in_stock=200,
                            created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
            db.session.add_all([product1, product2])

            # Report
            report1 = Report(product_id=1, report_date=datetime.datetime.now(), turnover_rate=0.5,
                            demand_forecast=100, most_popular="Smartphone")
            report2 = Report(product_id=2, report_date=datetime.datetime.now(), turnover_rate=0.8,
                            demand_forecast=50, most_popular="Mystery Novel")
            db.session.add_all([report1, report2])

            # Order
            order1 = Order(customer_id=1, status=OrderStatus.PENDING, total_amount=1399.98,
                        created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
            order2 = Order(customer_id=2, status=OrderStatus.DELIVERED, total_amount=15.99,
                        created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
            db.session.add_all([order1, order2])

            # OrderItem
            order_item1 = OrderItem(order_id=1, product_id=1, quantity=2, price_at_purchase=699.99)
            order_item2 = OrderItem(order_id=2, product_id=2, quantity=1, price_at_purchase=15.99)
            db.session.add_all([order_item1, order_item2])

            # Return
            return1 = Return(order_id=2, return_reason="Defective item", status=ReturnStatus.COMPLETE,
                            created_at=datetime.datetime.now())
            db.session.add(return1)

            # Commit all changes
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"Error populating the database: {e}")


@app.route('/admin/<int:admin_id>/role', methods=['GET'])
def get_admin_role(admin_id):
    '''
    Get admin role.

    Requires:
        admin_id (int)

    Returns:
        200: Admin role
        404: Admin or admin role not found
        500: Internal server error
    '''
    try:
        admin = Admin.query.filter_by(admin_id=admin_id).first()
        if not admin:
            return abort(404, "Admin not found")
        
        ar = AdminRole.query.filter_by(admin_id=admin_id).first()
        if not ar:
            return abort(404, "Admin role not found")
        
        return jsonify(admin_role_schema.dump(ar))
    except:
        return abort(500, "Internal server error")

@app.route('/get_logs', methods=['GET'])
def get_logs():
    '''
    Get logs.

    Returns:
        200: Logs retrieved successfully
        500: Server Error
    '''
    try:
        logs = Log.query.all()
        return jsonify(logs_schema.dump(logs)), 200
    except:
        return abort(500, "Internal server error")

# Customer routes

@app.route('/get_customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify(customers_schema.dump(customers))


# Support routes

@app.route('/get_supports', methods=['GET'])
def get_supports():
    # Query all Support entries
    supports = Support.query.all()
    return jsonify(supports_schema.dump(supports))


# Wishlist routes

@app.route('/get_wishlists', methods=['GET'])
def get_wishlists():
    # Query all Wishlist entries
    wishlists = Wishlist.query.all()
    return jsonify(wishlists_schema.dump(wishlists))


# Inventory routes

@app.route('/inventory', methods=['GET'])
def get_inventory():
    '''
    Get inventory.

    Returns:
        200: Inventory retrieved successfully
        500: Server Error
    '''
    
    try:
        products = Product.query.all()
        product_categories = ProductCategory.query.all()

        return jsonify({'products': products_schema.dump(products), 'product_categories': product_categories_schema.dump(product_categories)}), 200
    except:
        return abort(500, "Something went wrong")


@app.route('/products', methods=['GET'])
def get_products():
    '''
    Get products.

    Returns:
        200: Products retrieved successfully
        500: Server Error
    '''
    
    try:
        products = Product.query.all()
        return jsonify(products_schema.dump(products)), 200
    except Exception as e:
        print(e)
        return abort(500, "Something went wrong")


@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    '''
    Get product.

    Requires:
        product_id (int)

    Returns:
        200: Product retrieved successfully
        404: Product not found
        500: Server Error
    '''
    if type(product_id) != int:
        return abort(400, "Invalid product id")
    
    try:
        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            return abort(404, "Product not found")
        return jsonify(product_schema.dump(product)), 200
    except:
        return abort(500, "Something went wrong")

@app.route('/product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    '''
    Update product.

    Requires:
        token (jwt)
        product_id (int)
        name (str) - optional
        quantity (int) - optional
        price (float) - optional
        description (str) - optional
        category_id (int) - optional
        promotion_id (int) - optional
        image (str) - optional
        subcategory (str) - optional

    Returns:
        200: Inventory updated successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        404: Product not found
        500: Internal server error
    '''

    if type(product_id) != int:
        return abort(400, "Invalid product id")
    
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return abort(404, "Product not found")
    
    # Required fields
    required_fields = ['name', 'quantity', 'price', 'description', 'category_id', 'promotion_id', 'image', 'subcategory']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
    
    name = request.json['name']
    quantity = request.json['quantity']
    price = request.json['price']
    description = request.json['description']
    category_id = request.json['category_id']
    promotion_id = request.json['promotion_id']
    image = request.json['image']
    subcategory = request.json['subcategory']

    if type(name) != str or type(quantity) != int or type(price) != float or type(description) != str or type(category_id) != int or type(promotion_id) != int or type(image) != str or type(subcategory) != str:
        return abort(400, "Invalid data type")
    
    try:
        product.name = name
        product.quantity += quantity
        product.price = price
        product.description = description
        product.category_id = category_id
        product.promotion_id = promotion_id
        product.image = image
        product.subcategory = subcategory

        log_details = f'Updated product {product.name}'
        log = Log(user_id=product.admin_id, timestamp=datetime.now(), details=log_details, action='UPDATE PRODUCT')
        
        db.session.add(log)
        db.session.commit()
    except:
        return abort(500, "Something went wrong")

    return product_schema.dump(product), 200


@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    '''
    Delete product.

    Requires:
        token (jwt)
        product_id (int)

    Returns:
        200: Product deleted successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        404: Product not found
        500: Internal server error
    '''

    if type(product_id) != int:
        return abort(400, "Bad request")
    
    try:
        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            return abort(404, "Product not found")
        
        log_details = f'Deleted product {product.name}'
        log = Log(user_id=product.admin_id, timestamp=datetime.now(), details=log_details, action='DELETE PRODUCT')
        
        db.session.add(log)
        db.session.delete(product)
        db.session.commit()
        
        return {"message": "Product deleted successfully"}, 200
    except:
        return abort(500, "Something went wrong")
    
@app.route('/add-product', methods=['POST'])
def add_product():
    '''
    Create Product.

    Requires:
        token (jwt)
        name (str)
        quantity (int)
        price (float)
        description (str)
        category_id (int)
        promotion_id (int)
        image (str)
        subcategory (str)

    Returns:
        201: Product created successfully
        400: Bad request
        403: Invalid or expired token
        500: Internal server error
    '''
    # Required fields
    required_fields = ['name', 'quantity', 'price', 'description', 'category_id', 'promotion_id', 'image', 'subcategory']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    name = request.json['name']
    quantity = request.json['quantity']
    price = request.json['price']
    description = request.json['description']
    category_id = request.json['category_id']
    promotion_id = request.json['promotion_id']
    image = request.json['image']
    subcategory = request.json['subcategory']

    try:
        category = ProductCategory.query.filter_by(category_id=category_id).first()

        if category is None:
            return abort(400, "Category not found")
        
        product = Product(category_id=category_id, name=name, quantity_in_stock=quantity, price=price, description=description, promotion_id=promotion_id, image=image, subcategory=subcategory, created_at=datetime.now(), updated_at=datetime.now())

        log_details = f'Added product {name}'
        log = Log(user_id=category.admin_id, timestamp=datetime.now(), details=log_details, action='ADD PRODUCT')
        
        db.session.add(log)
        db.session.add(product)
        db.session.commit()

        return product_schema.dump(product), 201
    except:
        return abort(500, "Something went wrong")


@app.route('/add-category', methods=['POST'])
def add_category():
    '''
    Create Category.

    Requires:
        token (jwt)
        name (str)
        description (str)

    Returns:
        201: Category created successfully
        400: Bad request
        403: Invalid or expired token
        500: Internal server error
    '''
    # Required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    name = request.json['name']
    description = request.json['description']

    if type(name) != str or type(description) != str:
        return abort(400, "Invalid data type")

    try:
        dup = ProductCategory.query.filter_by(name=name).first()
        if dup:
            return abort(400, "Category already exists")
        
        category = ProductCategory(name=name, description=description)

        log_details = f'Added category {name}'
        log = Log(user_id=category.admin_id, timestamp=datetime.now(), details=log_details, action='ADD CATEGORY')
        
        db.session.add(log)
        db.session.add(category)
        db.session.commit()

        return product_category_schema.dump(category), 201
    except:
        return abort(500, "Something went wrong")

@app.route('/delete-category', methods=['DELETE'])
def delete_category():
    '''
    Delete Category.

    Requires:
        token (jwt)
        category_id (int)

    Returns:
        200: Category deleted successfully
        400: Bad request
        403: Invalid or expired token
        404: Category not found
        500: Internal server error
    '''
    # Required fields
    required_fields = ['category_id']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    category_id = request.json['category_id']

    if type(category_id) != int:
        return abort(400, "Invalid data type")

    try:
        category = ProductCategory.query.filter_by(category_id=category_id).first()

        if category is None:
            return abort(400, "Category not found")

        log = Log(user_id=category.admin_id, timestamp=datetime.now(), details=f'Deleted category {category.name}', action='DELETE CATEGORY')
        
        db.session.add(log)
        
        db.session.delete(category)
        db.session.commit()

        return {"message": "Category deleted successfully"}, 200
    except:
        return abort(500, "Something went wrong")

@app.route('/categories', methods=['GET'])
def get_categories():
    '''
    Get categories.

    Returns:
        200: Categories retrieved successfully
        500: Server Error
    '''
    
    try:
        categories = ProductCategory.query.all()
        return jsonify(product_categories_schema.dump(categories)), 200
    except:
        return abort(500, "Something went wrong")
    

@app.route('/reports', methods=['GET'])
def get_reports():
    '''
    Get reports.

    Returns:
        200: Reports retrieved successfully
        500: Server Error
    '''
    
    try:
        reports = Report.query.all()
        return jsonify(reports_schema.dump(reports)), 200
    except:
        return abort(500, "Something went wrong")
    

@app.route('/orders', methods=['GET'])
def get_orders():
    '''
    Get orders.

    Returns:
        200: Orders retrieved successfully
        500: Server Error
    '''
    
    try:
        orders = Order.query.all()
        return jsonify(orders_schema.dump(orders)), 200
    except:
        return abort(500, "Something went wrong")
    

@app.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    '''
    Get order by order_id.

    Requires:
        order_id (int)

    Returns:
        200: Order retrieved successfully
        400: Bad request
        404: Order not found
        500: Server Error
    '''
    if type(order_id) != int:
        return abort(400, "Bad request")
    
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            abort(404, 'Order not found')

        return jsonify(order_schema.dump(order)), 200

    except:
        return abort(500, "Internal server error")
    

@app.route('/order-items/<int:order_id>', methods=['GET'])
def get_order_items(order_id):
    '''
    Get order items by order_id.

    Requires:
        order_id (int)

    Returns:
        200: Order items retrieved successfully
        400: Bad request
        404: Order not found
        500: Server Error
    '''
    if type(order_id) != int:
        return abort(400, "Bad request")
    
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            abort(404, 'Order not found')

        order_items = OrderItem.query.filter_by(order_id).all()

        return jsonify(order_items_schema.dump(order_items)), 200

    except:
        return abort(500, "Internal server error")

@app.route('/promote/<int:product_id>', methods=['POST'])
def promote(product_id):
    '''
    Promote product by product_id.

    Requires:
        token (jwt)
        product_id (int)
        promotion_type (str)
        promotion_value (float)
        user_tier (str)
        name (str)

    Returns:
        200: Product promoted successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        404: Product not found
        500: Internal server error
    '''
    # Required fields
    required_fields = ['product_id', 'promotion_type', 'promotion_value', 'user_tier', 'name']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")

    product_id = request.json['product_id']
    promotion_type = request.json['promotion_type']
    promotion_value = request.json['promotion_value']
    user_tier = request.json['user_tier']
    name = request.json['name']

    if type(product_id) != int or type(promotion_type) != str or type(promotion_value) != float or type(user_tier) != str or type(name) != str:
        return abort(400, "Invalid data type")

    try:
        product = Product.query.filter_by(product_id=product_id).first()
    
        if product is None:
            return abort(404, "Product not found")
        
        promotion = Promotion(name=name, product_id=product_id, promotion_type=promotion_type, promotion_value=promotion_value, user_tier=user_tier)

        db.session.add(promotion)
        db.session.commit()

        return product_schema.dump(product), 200
    except:
        return abort(500, "Something went wrong")

@app.route('/promotions', methods=['GET'])
def get_promotions():
    '''
    Get promotions.

    Returns:
        200: Promotions retrieved successfully
        500: Server Error
    '''
    
    try:
        promotions = Promotion.query.all()
        return jsonify(promotions_schema.dump(promotions)), 200
    except:
        return abort(500, "Something went wrong")

@app.route('/promote/<int:product_id>', methods=['DELETE'])
def delete_promotion(product_id):
    '''
    Delete promotion by promotion_id.

    Requires:
        promotion_id (int)

    Returns:
        200: Promotion deleted successfully
        400: Bad request
        404: Promotion not found
        500: Internal server error
    '''
    if 'promotion_id' not in request.json:
        return abort(400, "Missing promotion_id")
    
    promotion_id = request.json['promotion_id']

    if type(promotion_id) != int or type(product_id) != int:
        return abort(400, "Invalid promotion_id")
    
    try:
        promotion = Promotion.query.filter_by(promotion_id=promotion_id).first()
        
        if promotion is None:
            return abort(404, "Promotion not found")
        
        db.session.delete(promotion)
        db.session.commit()

        return promotion_schema.dump(promotion), 200
    except:
        return abort(500, "Something went wrong")

@app.route('/returns', methods=['GET'])
def get_returns():
    '''
    Get returns.

    Returns:
        200: Returns retrieved successfully
        500: Server Error
    '''
    
    try:
        returns = Return.query.all()
        return jsonify(returns_schema.dump(returns)), 200
    except:
        return abort(500, "Something went wrong")
    
@app.route('/refund/<int:order_id>', methods=['POST'])
def refund(order_id):
    '''
    Refund order by order_id.

    Requires:
        order_id (int)

    Returns:
        200: Order refunded successfully
        400: Bad request
        404: Order not found
        500: Internal server error
    '''
    order_id = request.json['order_id']

    if type(order_id) != int:
        return abort(400, "Invalid order_id")
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if order is None:
            return abort(404, "Order not found")
        
        order.status = "refunded"

        log_details = f'Refunded order {order.order_id}'
        log = Log(user_id=order.customer_id, timestamp=datetime.now(), details=log_details, action='REFUND ORDER')
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify(order_schema.dump(order)), 200
    except:
        return abort(500, "Internal server error")

@app.route('/cancel-order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    '''
    Cancel order by order_id.

    Requires:
        order_id (int)

    Returns:
        200: Order canceled successfully
        400: Bad request
        404: Order not found
        500: Internal server error
    '''
    
    order_id = request.json['order_id']

    if type(order_id) != int:
        return abort(400, "Invalid order_id")
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if order is None:
            return abort(404, "Order not found")
        
        order.status = "canceled"
        
        log_details = f'Canceled order {order.order_id}'
        log = Log(user_id=order.customer_id, timestamp=datetime.now(), details=log_details, action='CANCEL ORDER')
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify(order_schema.dump(order)), 200
    except:
        return abort(500, "Internal server error")
    
@app.route('/replace-order/<int:order_id>', methods=['POST'])
def replace_order(order_id):
    '''
    Replace order by order_id.

    Requires:
        order_id (int)

    Returns:
        200: Order replaced successfully
        400: Bad request
        404: Order not found
        500: Internal server error
    '''
    order_id = request.json['order_id']

    if type(order_id) != int:
        return abort(400, "Invalid order_id")
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if order is None:
            return abort(404, "Order not found")
        
        order.status = "replaced"

        ## PLACE NEW ORDER HERE
        
        log_details = f'Replaced order {order.order_id}'
        log = Log(user_id=order.customer_id, timestamp=datetime.now(), details=log_details, action='REPLACE ORDER')
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify(order_schema.dump(order)), 200
    except:
        return abort(500, "Internal server error")
    
@app.route('/inventory-report', methods=['POST'])
def generate_inventory_report():
    '''
    Generate inventory report.

    Returns:
        200: Inventory report generated successfully
        400: Bad request
    '''
    try:
        # Fetch products and order items
        products = Product.query.all()
        order_items = OrderItem.query.all()

        if not products or not order_items:
            return jsonify({"message": "No data available for generating reports"}), 400

        # Calculate total sales for each product
        sales_data = {}
        for item in order_items:
            if item.product_id not in sales_data:
                sales_data[item.product_id] = 0
            sales_data[item.product_id] += item.quantity
        
        # Find the most popular product
        most_popular_product_id = max(sales_data, key=sales_data.get)
        most_popular_name = next(
            (product.name for product in products if product.product_id == most_popular_product_id),
            "Unknown"
        )

        # Generate report data
        report_data = []
        for product in products:
            turnover_rate = (
                sales_data.get(product.product_id, 0) /
                max(product.quantity_in_stock, 1)
            )
            demand_forecast = sales_data.get(product.product_id, 0) * 1.05  # Assume 5% growth

            report_data.append({
                "product_id": product.product_id,
                "report_date": datetime.now(),
                "turnover_rate": turnover_rate,
                "demand_forecast": int(demand_forecast),
                "most_popular": "Yes" if product.product_id == most_popular_product_id else "No"
            })
        
        # Save reports
        report_objects = [Report(**data) for data in report_data]
        db.session.bulk_save_objects(report_objects)
        db.session.commit()
        
        return jsonify({
            "message": "Reports generated successfully",
            "most_popular_product": most_popular_name,
            "most_popular_sales": sales_data[most_popular_product_id]
        }), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return abort(500, "Internal server error")

# Run Flask App
if __name__ == '__main__':
    create_tables_and_populate()
    app.run(debug=True, port=3000)