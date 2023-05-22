from flask import Flask, redirect, request, session
import requests
import discord
from helpers import db_manager
from bot import bot
from waitress import serve

app = Flask(__name__)
app.secret_key = 'your secret key'  # replace with your secret key

@app.route("/webhook")
def webhook():
    discord_user_id = request.args.get("discord_id")
    session["discord_user_id"] = discord_user_id
    return redirect("https://id.twitch.tv/oauth2/authorize?client_id=xulcmh65kzbfefzuvfuulnh7hzrfhj&redirect_uri=https://dankstreamer.lol/callback&response_type=code&scope=user:read:email")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    client_id = "xulcmh65kzbfefzuvfuulnh7hzrfhj"
    client_secret = "fsbndw0gusm5lzvqnz7v5d59x34n94"
    response = requests.post("https://id.twitch.tv/oauth2/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "https://dankstreamer.lol/callback"
    })

    access_token = response.json()["access_token"]

    response = requests.get("https://api.twitch.tv/helix/users", headers={
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    })

    user = response.json()["data"][0]
    discord_id = session["discord_user_id"]
    broadcaster_type = user["broadcaster_type"]

    db_manager.edit_twitchCreds(access_token)  
    db_manager.connect_twitch_id(discord_id, user['id'])  
    db_manager.connect_twitch_name(discord_id, user['login'])  

    # Get broadcaster_type and generate emotePrefix
    if broadcaster_type in ["affiliate", "partner"]:
        # Generate emotePrefix from user's Twitch name, taking the first four characters
        emotePrefix = user['login'][:4]
        db_manager.add_streamer(user['login'], discord_id, emotePrefix, user['id'], broadcaster_type)

        embed_description = "Your accounts have been connected! You have been registered as a streamer. Your generated prefix is: " + emotePrefix
    else:
        embed_description = "Your accounts have been connected!"

    embed = discord.Embed(title="Connected!", description=embed_description, color=0x00ff00)
    #add a footer saying the users discord id and twitch id
    embed.set_footer(text=f"Discord ID: {discord_id} | Twitch ID: {user['id']}")
    #send the embed
    bot.get_user(int(discord_id)).send(embed=embed)
    print(f"Connected {discord_id} to {user['id']}!")

    return redirect("https://dankstreamer.lol/thanks")

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000, url_scheme='https')