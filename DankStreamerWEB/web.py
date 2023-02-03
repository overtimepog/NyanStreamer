import requests
from flask import Flask, redirect, render_template, request, jsonify, session
from discord import Webhook, SyncWebhook
from flask_session import Session
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Step 1: Create a Twitch application
# ...

# Step 2: Get the client ID
# ...

@app.route("/")
def index():
    return render_template('home.html')

@app.route("/webhook")
def webhook():
    #get the args from the url
    #get the webhook url
    webhook_url = request.args.get("url")
    #save the webhook to a session variable
    session["webhook_url"] = webhook_url
    print(webhook_url)
    return redirect("https://id.twitch.tv/oauth2/authorize?client_id=xulcmh65kzbfefzuvfuulnh7hzrfhj&redirect_uri=https://dankstreamer.lol/callback&response_type=code&scope=user:read:email")


@app.route("/callback")
def callback():
    #get the webhook url from the session variable
    webhook_url = session["webhook_url"]
    print(webhook_url)
    # Step 4: Handle the authorization code
    code = request.args.get("code")
    client_id = "xulcmh65kzbfefzuvfuulnh7hzrfhj"
    client_secret = "fsbndw0gusm5lzvqnz7v5d59x34n94"

    # Step 5: Obtain an access token
    response = requests.post("https://id.twitch.tv/oauth2/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "https://dankstreamer.lol/callback"
    })
    
    access_token = response.json()["access_token"]

    # Step 6: Use the access token to request the user's information
    response = requests.get("https://api.twitch.tv/helix/users", headers={
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    })
    user = response.json()["data"][0]

    # Step 7: Send the information to the Discord webhook
    webhook = SyncWebhook.from_url(webhook_url)
    #webhook.send(f"New user has logged in: Username: {user['login']}, Email: {user['email']}, ID: {user['id']}, Display Name: {user['display_name']}, Broadcaster Type: {user['broadcaster_type']}")
    webhook.send(f"TWITCH USERNAME: {user['login']}")
    webhook.send(f"TWITCH ID: {user['id']}")
    
    return redirect("https://dankstreamer.lol")

if __name__ == "__main__":
    app.run(debug=True)