from admin import db, ma

class Log(db.Model):
    log_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    details = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(80), nullable=False)

    def __init__(self, admin_id, timestamp, details, action):
        super(Log, self).__init__(admin_id=admin_id, timestamp=timestamp, details=details, action=action)

class LogSchema(ma.ModelSchema):
    class Meta:
        model = Log
        fields = ('log_id', 'admin_id', 'timestamp', 'details', 'action')  

log_schema = LogSchema()
logs_schema = LogSchema(many=True)