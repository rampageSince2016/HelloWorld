#coding utf-8

import os

from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

class Configuration:
    debug = True
    APPLICATION_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_PATH = os.path.join(APPLICATION_DIR, 'data.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % DATABASE_PATH

app = Flask(__name__)

app.config.from_object(Configuration)
db = SQLAlchemy(app)


class Scene(db.Model):
    __tablename__ = 'Scene'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    attrgroup_rel = db.relationship("Attr_Group", backref="Scene")

    def __init__(self, *args, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)

class Attr_Group(db.Model):
    __tablename__ = 'Attr_Group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    scene_id = db.Column(db.Integer, db.ForeignKey("Scene.id"))
    attr_rel = db.relationship("Attr", backref="Attr_Group")

    def __init__(self, *args, **kwargs):
        super(Attr_Group, self).__init__(*args, **kwargs)

class Attr(db.Model):
    __tablename__ = 'Attr'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    attr_group_id = db.Column(db.Integer, db.ForeignKey("Attr_Group.id"))

    def __init__(self, *args, **kwargs):
        super(Attr_Group, self).__init__(*args, **kwargs)

if not os.path.exists(Configuration.DATABASE_PATH):
    db.create_all()

app.jinja_env.globals['Attr'] = Attr
app.jinja_env.globals['Attr_Group'] = Attr_Group
app.jinja_env.globals['Scene'] = Scene

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
