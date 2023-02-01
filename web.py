import requests
from flask import Flask, redirect, request, jsonify
from discord import Webhook, SyncWebhook
from waitress import serve

app = Flask(__name__)

# Step 1: Create a Twitch application
# ...

# Step 2: Get the client ID
# ...

@app.route("/")
def index():
    return "hello world"

@app.route("/callback")
def callback():
    # Step 4: Handle the authorization code
    code = request.args.get("code")
    
    client_id = "xulcmh65kzbfefzuvfuulnh7hzrfhj"
    client_secret = "oehogzzpc9lec7lxgf1aqht9swzgq0"

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
        "Authorization": f"Bearer {access_token}"
    })

    user = response.json()["data"][0]

    #send the information to the discord webhook
    webhook_url = "https://discord.com/api/webhooks/1069631304196436029/4kR9H23BJ5f14U1U3ZuTXEo9vhoBC5zBN9E1j1nz7etj1pHf2Vq14eiE1aWb50JpYDG3"
    webhook = SyncWebhook.from_url(webhook_url)
    webhook.send(f"New user has logged in: Username: {user['login']}, Email: {user['email']}")
    
    data = jsonify(user)
    webhook.send(data)

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=8080, threads=1) #WAITRESS!
