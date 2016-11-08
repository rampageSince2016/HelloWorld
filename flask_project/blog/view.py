from app import app
from flask import render_template, request

@app.route('/abc', methods=['get', 'post'])
def homepage():
    user = request.args.get('user')
    number = request.args.get('number')
    return render_template('homepage.html', name=user, number=number)
