from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow

from secret_key import SECRET_KEY
from admin.db_config import DB_CONFIG
from app import extract_auth_token, decode_token, jwt, datetime

app = Flask(__name__)
ma = Marshmallow(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONFIG
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models.product import Product, product_schema, products_schema
from models.product_category import ProductCategory, product_category_schema, product_categories_schema
from models.report import Report, report_schema, reports_schema
from models.promotion import Promotion, promotion_schema, promotions_schema
from admin.models.admin import Admin


@app.route('/inventory', methods=['GET'])
def get_inventory():
    '''
    Get inventory.

    Returns:
        200: Inventory retrieved successfully
        401: Unauthorized
    '''
    
    try:
        products = Product.query.all()
        promotions = Promotion.query.all()
        product_categories = ProductCategory.query.all()

        return jsonify({'products': products_schema.dump(products), 'promotions': promotions_schema.dump(promotions), 'product_categories': product_categories_schema.dump(product_categories)}), 200
    except:
        return abort(500, "Something went wrong")


@app.route('/products', methods=['GET'])
def get_products():
    '''
    Get products.

    Returns:
        200: Products retrieved successfully
        401: Unauthorized
    '''
    
    try:
        products = Product.query.all()
        return jsonify({products_schema.dump(products)}), 200
    except:
        return abort(500, "Something went wrong")
    

@app.route('/categories', methods=['GET'])
def get_categories():
    '''
    Get categories.

    Returns:
        200: Categories retrieved successfully
        401: Unauthorized
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

    Requires:
        token (jwt)

    Returns:
        200: Reports retrieved successfully
        401: Unauthorized
        403: Invalid or expired token
    '''

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
    try:        
        reports = Report.query.all()
        return jsonify({reports_schema.dump(reports)}), 200
    except:
        return abort(500, "Something went wrong")
    

@app.route('/update', methods=['POST'])
def update_inventory():
    '''
    Update inventory product.

    Requires:
        token (jwt)
        product_id (int)
        name (str) - optional
        quantity (int) - optional
        price (float) - optional
        description (str) - optional
        category_id (int) - optional
        promotion_id (int) - optional
        iamge (str) - optional

    Returns:
        200: Inventory updated successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
    '''

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return jsonify({
            'message': 'Unauthorized'
        }), 401
    
    # Required fields
    product_id = request.json['product_id']

    # Optional fields
    name = request.json.get('name')
    quantity = request.json.get('quantity')
    price = request.json.get('price')
    description = request.json.get('description')
    category_id = request.json.get('category_id')
    promotion_id = request.json.get('promotion_id')
    image = request.json.get('image')

    try:
        product = Product.query.filter_by(product_id=product_id).first()

        if product is None:
            return abort(400, "Product not found")
        product.name = name
        product.quantity = quantity
        product.price = price
        product.description = description
        product.category_id = category_id
        product.promotion_id = promotion_id
        product.image = image
        
        db.session.commit()

        return product_schema.dump(product), 200
    except:
        return abort(500, "Something went wrong")
    

@app.route('/delete', methods=['POST'])
def delete_product():
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

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
    # Required fields
    product_id = request.json['product_id']

    try:
        product = Product.query.filter_by(product_id=product_id).first()

        if product is None:
            return abort(400, "Product not found")
        
        db.session.delete(product)
        db.session.commit()

        return product_schema.dump(product), 200
    except:
        return abort(500, "Something went wrong")
    

@app.route('/promote', methods=['POST'])
def promote_product():
    '''
    Promote product.

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

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
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

    try:
        product = Product.query.filter_by(product_id=product_id).first()
    
        if product is None:
            return abort(400, "Product not found")
        
        promotion = Promotion(name=name, product_id=product_id, promotion_type=promotion_type, promotion_value=promotion_value, user_tier=user_tier)

        db.session.add(promotion)
        db.session.commit()

        return product_schema.dump(product), 200
    except:
        return abort(500, "Something went wrong")


@app.route('/add-product', methods=['POST'])
def add_product():
    '''
    Add product.

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
        200: Product added successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
    '''

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
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
        promotion = Promotion.query.filter_by(promotion_id=promotion_id).first()

        if category is None:
            return abort(400, "Category not found")
        
        if promotion is None:
            return abort(400, "Promotion not found")
        
        product = Product(category_id=category_id, name=name, quantity_in_stock=quantity, price=price, description=description, promotion_id=promotion_id, image=image, subcategory=subcategory, created_at=datetime.now(), updated_at=datetime.now())

        db.session.add(product)
        db.session.commit()

        return product_schema.dump(product), 200  
    except:
        return abort(500, "Something went wrong")


@app.route('/add-category', methods=['POST'])
def add_category():
    '''
    Add category.

    Requires:
        token (jwt)
        name (str)
        description (str)

    Returns:
        200: Category added successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
    '''

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
    # Required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    name = request.json['name']
    description = request.json['description']

    try:
        category = ProductCategory(name=name, description=description)

        db.session.add(category)
        db.session.commit()

        return product_category_schema.dump(category), 200
    except:
        return abort(500, "Something went wrong")
    

@app.route('/delete-category', methods=['POST'])
def delete_category():
    '''
    Delete category.

    Requires:
        token (jwt)
        category_id (int)

    Returns:
        200: Category deleted successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
    '''

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
    # Required fields
    required_fields = ['category_id']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    category_id = request.json['category_id']

    try:
        category = ProductCategory.query.filter_by(category_id=category_id).first()

        if category is None:
            return abort(400, "Category not found")
        
        db.session.delete(category)
        db.session.commit()

        return product_category_schema.dump(category), 200
    except:
        return abort(500, "Something went wrong")


@app.route('/delete-promotion', methods=['POST'])
def delete_promotion():
    '''
    Delete promotion.

    Requires:
        token (jwt)
        promotion_id (int)

    Returns:
        200: Promotion deleted successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        500: Internal server error
    '''

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
    # Required fields
    promotion_id = request.json['promotion_id']

    try:
        promotion = Promotion.query.filter_by(promotion_id=promotion_id).first()

        if promotion is None:
            return abort(400, "Promotion not found")
        
        db.session.delete(promotion)
        db.session.commit()

        return promotion_schema.dump(promotion), 200
    except:
        return abort(500, "Something went wrong")


@app.route('/change-price', methods=['POST'])
def change_price():
    '''
    Change price.

    Requires:
        token (jwt)
        product_id (int)
        price (float)

    Returns:
        200: Price changed successfully
        400: Bad request
        401: Unauthorized
        403: Invalid or expired token
        404: Product not found
        500: Internal server error
    '''

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")

    # Check if admin exists
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if admin is None:
        return abort(401, "Unauthorized")
    
    # Required fields
    required_fields = ['product_id', 'price']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    product_id = request.json['product_id']
    price = request.json['price']

    try:
        product = Product.query.filter_by(product_id=product_id).first()

        if product is None:
            return abort(400, "Product not found")

        product.price = price
        db.session.commit()

        return product_schema.dump(product), 200
    except:
        return abort(500, "Something went wrong")



