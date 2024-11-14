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

@app.route('/admin/<int:admin_id>', methods=['GET'])
def get_admin(admin_id):
    a = Admin.query.filter_by(id=admin_id).first()
    if not a:
        return abort(404, "Admin not found")
    return jsonify(admin_schema.dump(a))


@app.route('/admin/email/<string:email>', methods=['GET'])
def get_admin_by_email(email):
    # Query the Admin model by email
    admin = Admin.query.filter_by(email=email).first()
    if not admin:
        return abort(404, "Admin not found")
    return jsonify(admin_schema.dump(admin))


@app.route('/add-admin', methods=['POST'])
def add_admin():
    data = request.get_json()
    try:
        admin = Admin(name=data['name'], email=data['email'], password=data['password'], phone=data['phone'])

        log_detail = f'{admin.name} is now an admin'
        log = Log(user_id=admin.admin_id, timestamp=datetime.now(), details=log_detail, action='CREATE ADMIN')
        
        db.session.add(admin)
        db.session.add(log)
        db.session.commit()
        
        return admin_schema.dump(admin), 201
    except:
        return abort(400, "Bad request")


# AdminRole routes

@app.route('/add-admin-role', methods=['POST'])
def add_admin_role():
    data = request.get_json()
    admin_role = AdminRole(
        admin_id=data['admin_id'],
        customer_support=data['customer_support'],
        logs=data['logs'],
        product_management=data['product_management'],
        order_management=data['order_management'],
        customer_management=data['customer_management'],
        inventory_management=data['inventory_management'],
        reports=data['reports']
    )
    admin = Admin.query.filter_by(admin_id=data['admin_id']).first()
    log_details = f'{admin.name} roles updated'
    log = Log(user_id=admin.admin_id, timestamp=datetime.now(), details=log_details, action='UPDATE ADMIN ROLES')

    db.session.add(admin_role)
    db.session.commit()
    return admin_role_schema.dump(admin_role), 201


@app.route('/admin/<int:admin_id>/role', methods=['GET'])
def get_admin_role(admin_id):
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
    logs = Log.query.all()
    return jsonify(logs_schema.dump(logs))

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
        return jsonify({products_schema.dump(products)}), 200
    except:
        return abort(500, "Something went wrong")


@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    '''
    Get product.

    Returns:
        200: Product retrieved successfully
        404: Product not found
        500: Server Error
    '''
    try:
        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            return abort(404, "Product not found")
        return jsonify(product_schema.dump(product))
    except:
        return abort(500, "Something went wrong")

@app.route('/product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    data = request.get_json()
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return abort(404, "Product not found")
    
    try:
        product.name = data['name']
        product.quantity += data['quantity']
        product.price = data['price']
        product.description = data['description']
        product.category_id = data['category_id']
        product.promotion_id = data['promotion_id']
        product.image = data['image']
        product.subcategory = data['subcategory']

        log_details = f'Updated product {product.name}'
        log = Log(user_id=product.admin_id, timestamp=datetime.now(), details=log_details, action='UPDATE PRODUCT')
        
        db.session.add(log)
        db.session.commit()
    except:
        return abort(500, "Something went wrong")

    return product_schema.dump(product)


@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            return abort(404, "Product not found")
        
        log_details = f'Deleted product {product.name}'
        log = Log(user_id=product.admin_id, timestamp=datetime.now(), details=log_details, action='DELETE PRODUCT')
        
        db.session.add(log)
        db.session.delete(product)
        db.session.commit()
    except:
        return abort(500, "Something went wrong")
    

@app.route('/add-product', methods=['POST'])
def add_product():
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

        return product_schema.dump(product), 200  
    except:
        return abort(500, "Something went wrong")


@app.route('/add-category', methods=['POST'])
def add_category():
    name = request.json['name']
    description = request.json['description']

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

        return product_category_schema.dump(category), 200
    except:
        return abort(500, "Something went wrong")

@app.route('/delete-category', methods=['DELETE'])
def delete_category():
    category_id = request.json['category_id']

    try:
        category = ProductCategory.query.filter_by(category_id=category_id).first()

        if category is None:
            return abort(400, "Category not found")

        log = Log(user_id=category.admin_id, timestamp=datetime.now(), details=f'Deleted category {category.name}', action='DELETE CATEGORY')
        
        db.session.add(log)
        
        db.session.delete(category)
        db.session.commit()

        return product_category_schema.dump(category), 200
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
        return jsonify({product_categories_schema.dump(categories)}), 200
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
        return jsonify({reports_schema.dump(reports)}), 200
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
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            abort(404, 'Order not found')

        return jsonify(order_schema.dump(order)), 200

    except:
        return abort(500, "Internal server error")
    

@app.route('/order-items/<int:order_id>', methods=['GET'])
def get_order_items(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            abort(404, 'Order not found')

        order_items = OrderItem.query.filter_by(order_id).all()

        return jsonify(order_items_schema.dump(order_items)), 200

    except:
        return abort(500, "Internal server error")


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
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if order is None:
            return abort(404, "Order not found")
        
        order.status = "refunded"

        log_details = f'Refunded order {order.order_id}'
        log = Log(user_id=order.customer_id, timestamp=datetime.now(), details=log_details, action='REFUND ORDER')
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({order_schema.dump(order)}), 200
    except:
        return abort(500, "Internal server error")

@app.route('/cancel-order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        
        if order is None:
            return abort(404, "Order not found")
        
        order.status = "canceled"
        
        log_details = f'Canceled order {order.order_id}'
        log = Log(user_id=order.customer_id, timestamp=datetime.now(), details=log_details, action='CANCEL ORDER')
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({order_schema.dump(order)}), 200
    except:
        return abort(500, "Internal server error")
    
@app.route('/replace-order/<int:order_id>', methods=['POST'])
def replace_order(order_id):
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
        
        return jsonify({order_schema.dump(order)}), 200
    except:
        return abort(500, "Internal server error")

# Run Flask App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3000)
