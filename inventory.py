from flask import Flask, request, jsonify, abort, flash, redirect, url_for
import requests
from werkzeug.utils import secure_filename
import pandas as pd
import magic
import os

from secret_key import SECRET_KEY
from app import extract_auth_token, decode_token, jwt, datetime, DB_PATH

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'csv'}


@app.route('/reports', methods=['GET'])
def get_reports():
    '''
    Get reports.
    Must be an Admin with reports role

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
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['reports'] == False:
        return abort(401, "Unauthorized")
    
    response = requests.get(f'{DB_PATH}/reports')
    reports = response.json()

    if response.status_code != 200:
        return abort(500, "Something went wrong")
    
    return reports, 200
    

@app.route('/update-inventory', methods=['POST'])
def update_inventory():
    '''
    Update inventory.
    Must be an admin with inventory_management role

    Requires:
        token (jwt)
        product_id (int)
        quantity (int)

    Returns:
        200: Inventory updated successfully
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
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['inventory_management'] == False:
        return abort(401, "Unauthorized")
    
    product_id = request.json['product_id']
    quantity = request.json['quantity']

    response = requests.get(f"{DB_PATH}/product/{product_id}")
    if response.code == 404:
        return abort(404, "Product not found")
    
    product = response.json()
    product['quantity'] += quantity

    response = requests.post(f"{DB_PATH}/product/{product_id}", json=product)
    if response.code == 500:
        return abort(500, "Something went wrong")
    
    return response.json(), 200


@app.route('/update-product', methods=['POST'])
def update_product():
    '''
    Update product.
    Must be an admin with product_management role

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
        500: Internal server error
    '''

    token = extract_auth_token(request)
    if not token:
        abort(403, "Something went wrong")
    try:
        admin_id = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        abort(403, "Something went wrong")
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    # Required fields
    product_id = request.json['product_id']

    # Optional fields
    name = request.json.get('name')
    price = request.json.get('price')
    description = request.json.get('description')
    category_id = request.json.get('category_id')
    promotion_id = request.json.get('promotion_id')
    image = request.json.get('image')
    subcategory = request.json.get('subcategory')

    response = requests.post(f"{DB_PATH}/product/{product_id}", json={
        'name': name,
        'price': price,
        'description': description,
        'category_id': category_id,
        'promotion_id': promotion_id,
        'image': image,
        'subcategory': subcategory
    })
    if response.code == 500:
        return abort(500, "Something went wrong")
    
    return response.json(), 200

@app.route('/delete-product', methods=['POST'])
def delete_product():
    '''
    Delete product.
    Must be an admin with product_management role

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
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    # Required fields
    product_id = request.json['product_id']

    # Check if product exists
    response = requests.get(f"{DB_PATH}/product/{product_id}")
    if response.code == 404:
        return abort(404, "Product not found")

    # Delete product
    response = requests.delete(f"{DB_PATH}/product/{product_id}")
    if response.code == 500:
        return abort(500, "Something went wrong")
    
    return response.json(), 200
    

# @app.route('/promote', methods=['POST'])
# def promote_product():
#     '''
#     Promote product.

#     Requires:
#         token (jwt)
#         product_id (int)
#         promotion_type (str)
#         promotion_value (float)
#         user_tier (str)
#         name (str)

#     Returns:
#         200: Product promoted successfully
#         400: Bad request
#         401: Unauthorized
#         403: Invalid or expired token
#         404: Product not found
#         500: Internal server error
#     '''

#     token = extract_auth_token(request)
#     if not token:
#         abort(403, "Something went wrong")
#     try:
#         admin_id = decode_token(token)
#     except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
#         abort(403, "Something went wrong")

#     # Check if admin exists
#     admin = Admin.query.filter_by(admin_id=admin_id).first()
#     if admin is None:
#         return abort(401, "Unauthorized")
    
#     # Check admin role
#     admin_role = AdminRole.query.filter_by(admin_id=admin_id).first()
#     if admin_role.product_management == False:
#         return abort(401, "Unauthorized")
    
#     # Required fields
#     required_fields = ['product_id', 'promotion_type', 'promotion_value', 'user_tier', 'name']
#     for field in required_fields:
#         if field not in request.json:
#             return abort(400, "Missing required field")
        
#     product_id = request.json['product_id']
#     promotion_type = request.json['promotion_type']
#     promotion_value = request.json['promotion_value']
#     user_tier = request.json['user_tier']
#     name = request.json['name']

#     try:
#         product = Product.query.filter_by(product_id=product_id).first()
    
#         if product is None:
#             return abort(400, "Product not found")
        
#         promotion = Promotion(name=name, product_id=product_id, promotion_type=promotion_type, promotion_value=promotion_value, user_tier=user_tier)

#         db.session.add(promotion)
#         db.session.commit()

#         return product_schema.dump(product), 200
#     except:
#         return abort(500, "Something went wrong")


@app.route('/add-product', methods=['POST'])
def add_product():
    '''
    Add product.
    Must be an admin with product_management role

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
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    # Required fields
    required_fields = ['name', 'quantity', 'price', 'description', 'category_id', 'promotion_id', 'image', 'subcategory']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    # Add product
    response = requests.post(f"{DB_PATH}/add-product", json=request.json)
    if response.code == 500:
        return abort(500, "Something went wrong")
    
    return response.json(), 200


@app.route('/add-category', methods=['POST'])
def add_category():
    '''
    Add category.
    Must be an admin with product_management role

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
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    # Required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    # Add category
    response = requests.post(f"{DB_PATH}/add-category", json=request.json)
    if response.code == 500:
        return abort(500, "Something went wrong")
    
    elif response.code == 400:
        return abort(400, "Category already exists")
    
    return response.json(), 200
    

@app.route('/delete-category', methods=['POST'])
def delete_category():
    '''
    Delete category.
    Must be an admin with product_management role

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
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    
    # Required fields
    required_fields = ['category_id']
    for field in required_fields:
        if field not in request.json:
            return abort(400, "Missing required field")
        
    response = requests.post(f"{DB_PATH}/delete-category", json=request.json)
    if response.code == 500:
        return abort(500, "Something went wrong")
    
    elif response.code == 404:
        return abort(404, "Category not found")
    
    return response.json(), 200


# @app.route('/delete-promotion', methods=['POST'])
# def delete_promotion():
#     '''
#     Delete promotion.

#     Requires:
#         token (jwt)
#         promotion_id (int)

#     Returns:
#         200: Promotion deleted successfully
#         400: Bad request
#         401: Unauthorized
#         403: Invalid or expired token
#         500: Internal server error
#     '''

#     token = extract_auth_token(request)
#     if not token:
#         abort(403, "Something went wrong")
#     try:
#         admin_id = decode_token(token)
#     except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
#         abort(403, "Something went wrong")

#     # Check if admin exists
#     admin = Admin.query.filter_by(admin_id=admin_id).first()
#     if admin is None:
#         return abort(401, "Unauthorized")
    
#     # Check admin role
#     admin_role = AdminRole.query.filter_by(admin_id=admin_id).first()
#     if admin_role.product_management == False:
#         return abort(401, "Unauthorized")
    
#     # Required fields
#     promotion_id = request.json['promotion_id']

#     try:
#         promotion = Promotion.query.filter_by(promotion_id=promotion_id).first()

#         if promotion is None:
#             return abort(400, "Promotion not found")
        
#         db.session.delete(promotion)
#         db.session.commit()

#         return promotion_schema.dump(promotion), 200
#     except:
#         return abort(500, "Something went wrong")



def allowed_file_type(file_path):
    # Use magic to determine the file type
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_file(file_path)
    return file_mime_type in ['text/csv', 'application/vnd.ms-excel']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_csv(filepath):
    '''
    Process a CSV file and return a list of Product instances.
    '''
    # Load the CSV file into a DataFrame
    df = pd.read_csv(filepath)
    
    # Convert 'created_at' and 'updated_at' to datetime objects
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    
    # Create a list to store Product objects
    products = []
    
    # Iterate over the DataFrame rows and create Product instances
    for _, row in df.iterrows():
        product = {
            "product_id": row["product_id"],
            "category_id": row["category_id"],
            "name": row["name"],
            "description": row["description"],
            "subcategory": row["subcategory"],
            "price": row["price"],
            "quantity_in_stock": row["quantity_in_stock"],
            "reorder_level": row["reorder_level"],
            "image": row["image"] if pd.notna(row["image"]) else None,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
        products.append(product)
    
    return products


@app.route('/add-products-csv', methods=["POST"])
def add_products_csv():
    '''
    Add products from CSV.

    Requires:
        token (jwt)
        file (csv)

    Returns:
        200: Products added successfully
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
    response = requests.get(f"{DB_PATH}/admin/{admin_id}")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    # Check admin role
    response = requests.get(f"{DB_PATH}/admin/{admin_id}/role")
    if response.code == 404:
        return abort(404, "Admin not found")
    
    admin_role = response.json()
    if admin_role['product_management'] == False:
        return abort(401, "Unauthorized")
    # admin_role = AdminRole.query.filter_by(admin_id=admin_id).first()
    # if admin_role.product_management == False:
    #     return abort(401, "Unauthorized")
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    #Save the file if extention is allowed
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print("entered secure file name\n")
        print(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filename)  # Save the file
            print('File successfully saved')
        except Exception as e:
            flash(f'Error saving file: {e}')
            print(f'Error: {e}')
        
        
        
        # Check the file type using magic
        if not allowed_file_type(filename):
            os.remove(filename)
            print('Invalid file type.')
            return redirect(request.url)
        
        # Process the CSV file
        products = process_csv(file_path)
        for p in products:
            response = requests.post(f'{DB_PATH}/add-product', json=p)
            if response.status_code != 200:
                return abort(500, "Something went wrong")
        flash('Products added successfully.')
        return redirect(url_for('get_products'))
    else:
        flash('Invalid file extension.')
        return redirect(request.url)