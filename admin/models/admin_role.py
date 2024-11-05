from admin import db, ma, bcrypt

class AdminRole(db.Model):
    admin_role_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
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