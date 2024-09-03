'''
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Docker World!!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
'''

from flask import Flask
def create_app():
    app = Flask(__name__)
    @app.route('/')
    def hello_world():
        return 'Hello, World!'
    return app
app = create_app()