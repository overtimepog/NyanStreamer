from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import requests
import discord
from helpers import db_manager
from itsdangerous import URLSafeTimedSerializer
import uvicorn
import os
import sys
import json

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='your secret key')  # replace with your secret key

templates = Jinja2Templates(directory="templates")

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/thanks")
async def thanks(request: Request):
    return templates.TemplateResponse("thanks.html", {"request": request})

@app.get("/webhook")
async def webhook(request: Request):
    discord_user_id = request.query_params.get("discord_id")
    request.session["discord_user_id"] = discord_user_id
    return RedirectResponse(url="https://id.twitch.tv/oauth2/authorize?client_id=xulcmh65kzbfefzuvfuulnh7hzrfhj&redirect_uri=https://dankstreamer.lol/callback&response_type=code&scope=user:read:email")

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
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
    discord_id = request.session["discord_user_id"]
    broadcaster_type = user["broadcaster_type"]

    await db_manager.edit_twitchCreds(access_token)  
    await db_manager.connect_twitch_id(discord_id, user['id'])  
    await db_manager.connect_twitch_name(discord_id, user['login'])  

    if broadcaster_type in ["affiliate", "partner"]:
        emotePrefix = user['login'][:4]
        await db_manager.add_streamer(user['login'], discord_id, emotePrefix, user['id'], broadcaster_type)
        embed_description = "Your accounts have been connected! You have been registered as a streamer. Your generated prefix is: " + emotePrefix
    else:
        embed_description = "Your accounts have been connected!"

    embed = discord.Embed(title="Connected!", description=embed_description, color=0x00ff00)
    embed.set_footer(text=f"Discord ID: {discord_id} | Twitch ID: {user['id']}")
    intents = discord.Intents.all()
    client = discord.Client(intents)
    client.start(config['token'])
    client.get_user(int(discord_id)).send(embed=embed)
    print(f"Connected {discord_id} to {user['id']}!")
    client.close()

    return RedirectResponse(url="https://dankstreamer.lol/thanks")

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=5000)