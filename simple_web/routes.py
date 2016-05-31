#!/usr/bin/env python3
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from arcus_client import Arcus, ArcusLocator, ArcusMCNodeAllocator, ArcusTranscoder

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['arcus'] = True
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(50), unique=True)
    email = db.Column(String(50), unique=True)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)


def get_arcus_client():
    zk = "localhost:2181"
    code = "test"
    client = Arcus(ArcusLocator(ArcusMCNodeAllocator(ArcusTranscoder())))
    client.connect(zk, code)
    return client

arcus = None
if app.config['arcus']:
    arcus = get_arcus_client()

@app.route('/',methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form['name'] and request.form['rank']:
            db.session.add(User(request.form['name'],request.form['rank']))
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('home.html')

@app.route('/search', methods = ['GET', 'POST'])
def search():
    result = []
    if request.method == 'POST':
        search_str=request.form['search']
        if search_str:
            if app.config['arcus']:
                ret = arcus.get(search_str).get_result()
                if ret:
                    result = ret
                else:
                    result = User.query.filter( User.name.like(search_str)).all()[0].email
                    a=arcus.set(search_str, result)
            else:
                result = User.query.filter( User.name.like(search_str)).all()[0].email
    return render_template('search.html',result=result)

@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True,host='0.0.0.0')
