import datetime, re

from app import db

def slugify(s):
    return re.sub('[^\w]+','-',s).lower()

class Entry(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100))
	slug = db.Column(db.String(100), unique=True)
	body = db.Column(db.Text)
	created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
	modified_timestamp = db.Column(db.DateTime, default=daettime.datetime.now, onupdate=datetime.datetime.now)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

