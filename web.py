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
from discord.ext.commands import Bot, Context
from discord import Intents
from discord.ext import commands, tasks
from typing import Any, Dict, List

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='your secret key')  # replace with your secret key

templates = Jinja2Templates(directory="templates")


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
    return RedirectResponse(url="https://id.twitch.tv/oauth2/authorize?client_id=xulcmh65kzbfefzuvfuulnh7hzrfhj&redirect_uri=https://nyanstreamer.lol/callback&response_type=code&scope=user:read:email%20chat:read%20user:read:broadcast")

@app.get("/callback")
async def callback(request: Request):
    if not os.path.isfile("config.json"):
        sys.exit("'config.json' not found! Please add it and try again.")
    else:
        with open("config.json") as file:
            config = json.load(file)
    code = request.query_params.get("code")
    client_id = config["CLIENT_ID"]
    client_secret = config["CLIENT_SECRET"]
    response = requests.post("https://id.twitch.tv/oauth2/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "https://nyanstreamer.lol/callback"
    })

    print(response.json())
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]

    response = requests.get("https://api.twitch.tv/helix/users", headers={
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    })

    user = response.json()["data"][0]
    discord_id = request.session["discord_user_id"]
    broadcaster_type = user["broadcaster_type"]
    

    await db_manager.set_twitch_oauth_token(discord_id, access_token)
    await db_manager.set_twitch_refresh_token(discord_id, refresh_token)
    await db_manager.connect_twitch_id(discord_id, user['id'])  
    print("connected twitch id")
    await db_manager.connect_twitch_name(discord_id, user['login'])
    print("connected twitch name")

    if broadcaster_type in ["affiliate", "partner"]:
        emotePrefix = user['login'][:4]
        await db_manager.add_streamer(user['login'], discord_id, emotePrefix, user['id'], broadcaster_type)
        await db_manager.update_is_streamer(discord_id)
        description = "Your accounts have been connected! You have been registered as a streamer!"
    else:
        description = "Your accounts have been connected!"


    if broadcaster_type in ["affiliate", "partner"]:
        return templates.TemplateResponse("thanks.html", {
            "request": request, 
            "discord_id": discord_id,
            "twitch_id": user['id'],
            "description": description,
            "broadcaster_type": broadcaster_type,
            "twitch_name": user['login'],
            "prefix": emotePrefix
        })
    else:
        return templates.TemplateResponse("thanks.html", {
             "request": request,
            "discord_id": discord_id,
            "twitch_id": user['id'],
            "description": description,
            "broadcaster_type": "User",
            "twitch_name": user['login'],
            "prefix": "None"
        })

@app.get("/api/data/items", response_model=Dict[str, Any])
async def get_all_items():
    items = await db_manager.get_items()
    return {"items": items}

@app.get("/api/data/jobs", response_model=Dict[str, Any])
async def get_all_jobs():
    jobs = await db_manager.get_jobs()
    return {"jobs": jobs}

@app.get("/api/data/chests", response_model=Dict[str, Any])
async def get_all_chests():
    chests = await db_manager.get_chests()
    return {"chests": chests}

@app.get("/api/data/searches", response_model=Dict[str, Any])
async def get_search():    
    with open('assets/search.json') as f:
        data = json.load(f)
        locations = data['searches']
        #get the searches from assets\search.json
    return {"searches": locations}

@app.get("/api/data/begs", response_model=Dict[str, Any])
async def get_beg():        
    with open('assets/beg.json') as f:
        data = json.load(f)
        begs = data['begs']
        #get the begs from assets\beg.json
    return {"begs": begs}


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=5000)