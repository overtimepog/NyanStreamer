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
from fastapi.security import HTTPBearer

from jeyyapi import JeyyAPIClient
client = JeyyAPIClient('6COJCCHO74OJ2CPM6GRJ4C9O6OS3G.9PSM2RH0ADQ74PB1DLIN4.FOauZ8Gi-J7wAuWDj_hH-g')

from assets.endpoints import abandon, aborted, affect, airpods, america, armor, balloon, bed, bongocat, boo, brain, brazzers, byemom, cancer, changemymind, cheating, citation, communism, confusedcat, corporate, crab, cry, dab, dank, deepfry, delete, disability, doglemon, door, dream, egg, emergencymeeting, excuseme, expanddong, expandingwwe, facts, failure, fakenews, farmer, fedora, floor, fuck, garfield, gay, godwhy, goggles, hitler, humansgood, inator, invert, ipad, jail, justpretending, keepurdistance, kimborder, knowyourlocation, kowalski, laid, letmein, lick, madethis, magik, master, meme, note, nothing, obama, ohno, piccolo, plan, presentation, profile, quote, radialblur, rip, roblox, salty, satan, savehumanity, screams, shit, sickfilth, slap, slapsroof, sneakyfox, spank, stroke, surprised, sword, theoffice, thesearch, trash, trigger, tweet, ugly, unpopular, violence, violentsparks, vr, walking, wanted, warp, whodidthis, whothisis, yomomma, youtube

from fastapi import APIRouter
app = FastAPI(
    title="Nyan Streamer!",
    description="The Best and Biggest Meme Gen API",
    version="0.0.1",
)


# This is a placeholder for your actual API key validation logic

async def get_current_api_key(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=403, detail="API key required")
    
    # Splitting the header value to get the actual API key
    # Format: "Bearer YOUR_API_KEY"
    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0].lower() != "Bearer":
        raise HTTPException(status_code=403, detail="Invalid authorization header format")
    
    api_key = parts[1]
    
    # Check if the API key exists in the database
    if not await db_manager.api_key_value_exists(api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return api_key

app.add_middleware(SessionMiddleware, secret_key='your secret key')  # replace with your secret key

templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/thanks", include_in_schema=False)
async def thanks(request: Request):
    return templates.TemplateResponse("thanks.html", {"request": request})

@app.get("/webhook", include_in_schema=False)
async def webhook(request: Request):
    discord_user_id = request.query_params.get("discord_id")
    request.session["discord_user_id"] = discord_user_id
    return RedirectResponse(url="https://id.twitch.tv/oauth2/authorize?client_id=xulcmh65kzbfefzuvfuulnh7hzrfhj&redirect_uri=https://nyanstreamer.lol/callback&response_type=code&scope=user:read:email%20chat:read%20user:read:broadcast")

@app.get("/callback", include_in_schema=False)
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

def wait_for_unlock(filename):
    timeout = 300  
    check_interval = 1  
    elapsed_time = 0

    while elapsed_time < timeout:
        try:
            with open(filename, 'rb') as f:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Try to acquire an exclusive lock
                fcntl.flock(f, fcntl.LOCK_UN)  # Release the lock
                return
        except IOError:
            pass
        
        time.sleep(check_interval)
        elapsed_time += check_interval

    logging.error(f"Timeout reached. Failed to generate GIF: {filename}")
    raise Exception("Failed to generate GIF due to timeout")

def delete_file(filename: str):
    """Delete a file after a delay to ensure it's been sent to the user."""
    time.sleep(10)  # Wait for 10 seconds to ensure the file has been sent
    if os.path.exists(filename):
        os.remove(filename)

@app.get("/3d/nuke", tags=["3D (Requires API Key)"])
async def nuke(avatar_url: str, background_tasks: BackgroundTasks, api_key: str = Depends(get_current_api_key)):
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
        
        # Wait for the GIF to be unlocked (i.e., fully generated)
        gif_path = filename + ".gif"
        wait_for_unlock(gif_path)
        
        logging.info(f"Successfully generated GIF: {gif_path}")
        response = FileResponse(gif_path, media_type="image/gif")
        
        # Schedule the cleanup task to run in the background after sending the response
        background_tasks.add_task(delete_file, gif_path)
        
        return response
    except Exception as e:
        logging.error(f"Failed to generate GIF: {str(e)}")
        return JSONResponse(content={"error": "Failed to generate the nuke GIF. Please try again."}, status_code=500)

def run_nuke_subprocess(model_path, avatar_url, frames, filename):
    logging.info(f"Starting subprocess to generate GIF for avatar: {avatar_url}")
    
    # Use subprocess.Popen to start the process
    subprocess.Popen([sys.executable, 'helpers/spinning_model_maker.py', model_path, avatar_url, str(frames), filename, '0,0,0', '0,0,45', '0,-4,0'])


@app.get("/3d/chair", tags=["3D (Requires API Key)"])
async def chair(avatar_url: str, background_tasks: BackgroundTasks, api_key: str = Depends(get_current_api_key)):
    logging.info(f"Received request to generate chair GIF for avatar: {avatar_url}")
    
    frames = 24
    timestamp = int(time.time())
    filename = f"chair_image_{timestamp}"  # Unique filename based on timestamp
    model_path = "/root/NyanStreamer/assets/models/Chair.egg"
    
    if not os.path.exists(model_path):
        logging.error("The chair model is missing.")
        return JSONResponse(content={"error": "The chair model is missing. Please try again later."}, status_code=500)
    
    # Run the image generation synchronously
    try:
        run_chair_subprocess(model_path, avatar_url, frames, filename)
        
        # Wait for the GIF to be unlocked (i.e., fully generated)
        gif_path = filename + ".gif"
        wait_for_unlock(gif_path)
        
        logging.info(f"Successfully generated GIF: {gif_path}")
        response = FileResponse(gif_path, media_type="image/gif")
        
        # Schedule the cleanup task to run in the background after sending the response
        background_tasks.add_task(delete_file, gif_path)
        
        return response
    except Exception as e:
        logging.error(f"Failed to generate GIF: {str(e)}")
        return JSONResponse(content={"error": "Failed to generate the nuke GIF. Please try again."}, status_code=500)

def run_chair_subprocess(model_path, avatar_url, frames, filename):
    logging.info(f"Starting subprocess to generate GIF for avatar: {avatar_url}")
    
    # Use subprocess.Popen to start the process
    subprocess.Popen([sys.executable, 'helpers/spinning_model_maker.py', model_path, avatar_url, str(frames), filename, '0,0,0', '0,96,25', '0,-3,0'])

@app.get("/3d/can", tags=["3D (Requires API Key)"])
async def chair(avatar_url: str, background_tasks: BackgroundTasks, api_key: str = Depends(get_current_api_key)):
    logging.info(f"Received request to generate chair GIF for avatar: {avatar_url}")
    
    frames = 24
    timestamp = int(time.time())
    filename = f"can_image_{timestamp}"  # Unique filename based on timestamp
    model_path = "/root/NyanStreamer/assets/models/Can.egg"
    
    if not os.path.exists(model_path):
        logging.error("The can model is missing.")
        return JSONResponse(content={"error": "The chair model is missing. Please try again later."}, status_code=500)
    
    # Run the image generation synchronously
    try:
        run_can_subprocess(model_path, avatar_url, frames, filename)
        
        # Wait for the GIF to be unlocked (i.e., fully generated)
        gif_path = filename + ".gif"
        wait_for_unlock(gif_path)
        
        logging.info(f"Successfully generated GIF: {gif_path}")
        response = FileResponse(gif_path, media_type="image/gif")
        
        # Schedule the cleanup task to run in the background after sending the response
        background_tasks.add_task(delete_file, gif_path)
        
        return response
    except Exception as e:
        logging.error(f"Failed to generate GIF: {str(e)}")
        return JSONResponse(content={"error": "Failed to generate the nuke GIF. Please try again."}, status_code=500)

def run_can_subprocess(model_path, avatar_url, frames, filename):
    logging.info(f"Starting subprocess to generate GIF for avatar: {avatar_url}")
    
    # Use subprocess.Popen to start the process
    subprocess.Popen([sys.executable, 'helpers/spinning_model_maker.py', model_path, avatar_url, str(frames), filename, '0,0,-0.85', '0,100,0', '0,-5,0'])


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=5000)