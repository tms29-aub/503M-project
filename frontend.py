from flask import Flask, render_template, request, abort, make_response, redirect, url_for
from flask_cors import CORS
import requests
from app import extract_auth_token, decode_token, jwt, DB_PATH, ADMIN_PATH
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/admin-login', methods=['GET', 'POST'])
def login():
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('token', '', expires=0)
    return resp

@app.route('/logs', methods=['GET'])
def logs_page():
    return render_template('logs.html')

@app.route('/orders', methods=['GET'])
def orders_page():
    return render_template('orders.html')

@app.route('/products', methods=['GET'])
def products_page():
    return render_template('products.html')

@app.route('/reports', methods=['GET'])
def reports_page():
    
    return render_template('reports.html')

@app.route('/create_admin', methods=['GET'])
def create_admin_page():
    return render_template('create_admin.html')


if __name__ == '__main__':
    app.run(debug=True, port=5004)
