# Simple Flask server for testing
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from test Flask server!"

if __name__ == '__main__':
    print("Starting Flask test server...")
    app.run(host='localhost', port=3000, debug=True)
