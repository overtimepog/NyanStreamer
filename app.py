from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/callback')
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    # use code and state to get access_token
    # ...
    print(code, state)
    print("Authentication Successful")
    return "Authentication Successful"

if __name__ == '__main__':
    app.run()