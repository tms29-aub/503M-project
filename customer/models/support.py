from customer import db, ma

class Support(db.Model):
    ticket_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
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