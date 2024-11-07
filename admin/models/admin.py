from admin import db, ma, bcrypt

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