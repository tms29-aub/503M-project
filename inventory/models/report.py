from inventory import db, ma

'''
report_id (Primary Key)
product_id (Foreign Key to Products)
report_date
turnover_rate
demand_forecast
most_popular
'''


class Report(db.Model):
    report_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
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