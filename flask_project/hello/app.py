from flask import Flask, abort, request

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello Flask'

@app.route('/hello/<user>', methods=['get', 'post'])
@app.route('/hello/', methods=['get', 'post'])
def hello(user=None):
    if user:
        print(name)
        return 'fuck u {}'.format(user)	
    else:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
