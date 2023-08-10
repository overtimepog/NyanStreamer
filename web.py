from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import requests
import discord
import os
import sys
import json
import time
import subprocess
import fcntl
from typing import Any, Dict, List
from helpers import db_manager
from itsdangerous import URLSafeTimedSerializer
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse

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

    print("Access Token: " + access_token)
    print("Refresh Token: " + refresh_token)

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

import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/api/3d/nuke")
async def nuke(avatar_url: str):
    logging.info(f"Received request to generate nuke GIF for avatar: {avatar_url}")
    
    frames = 24
    timestamp = int(time.time())
    filename = f"nuke_image_{timestamp}"  # Unique filename based on timestamp
    model_path = "/root/NyanStreamer/assets/models/Nuke.egg"
    
    if not os.path.exists(model_path):
        logging.error("The nuke model is missing.")
        return JSONResponse(content={"error": "The nuke model is missing. Please try again later."}, status_code=500)
    
    # Run the image generation synchronously
    try:
        run_nuke_subprocess(model_path, avatar_url, frames, filename)
        gif_path = filename + ".gif"
        logging.info(f"Successfully generated GIF: {gif_path}")
        response = FileResponse(gif_path, media_type="image/gif")
        os.remove(gif_path)  # Cleanup: Delete the GIF after serving
        return response
    except Exception as e:
        logging.error(f"Failed to generate GIF: {str(e)}")
        return JSONResponse(content={"error": "Failed to generate the nuke GIF. Please try again."}, status_code=500)

def run_nuke_subprocess(model_path, avatar_url, frames, filename):
    try:
        logging.info(f"Starting subprocess to generate GIF for avatar: {avatar_url}")
        
        # Use subprocess.run to wait for the process to complete
        result = subprocess.run([sys.executable, 'helpers/spinning_model_maker.py', model_path, avatar_url, str(frames), filename, '0,0,0', '0,0,45', '0,-4,0'])
        
        # Check if the subprocess completed successfully
        if result.returncode != 0:
            logging.error(f"Subprocess failed with return code: {result.returncode}")
            raise Exception("Failed to generate GIF due to subprocess error")

        gif_path = filename + ".gif"
        timeout = 300  
        check_interval = 1  
        elapsed_time = 0

        while elapsed_time < timeout:
            if os.path.exists(gif_path):
                with open(gif_path, 'rb') as f:
                    try:
                        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        fcntl.flock(f, fcntl.LOCK_UN)
                        break
                    except IOError:
                        pass
            time.sleep(check_interval)
            elapsed_time += check_interval

        if not os.path.exists(gif_path):
            logging.error(f"Timeout reached. Failed to generate GIF: {gif_path}")
            raise Exception("Failed to generate GIF")
    except Exception as e:
        logging.error(f"Error during GIF generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=5000)