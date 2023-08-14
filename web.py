import io
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
from starlette.responses import StreamingResponse
import aiohttp
import json
import random
from io import BytesIO
from petpetgif import petpet

from jeyyapi import JeyyAPIClient
client = JeyyAPIClient('6COJCCHO74OJ2CPM6GRJ4C9O6OS3G.9PSM2RH0ADQ74PB1DLIN4.FOauZ8Gi-J7wAuWDj_hH-g')

from assets.endpoints import dominos, johnoliver, bateman, abandon, aborted, affect, airpods, america, armor, balloon, bed, bongocat, boo, brain, brazzers, byemom, cancer, changemymind, cheating, citation, communism, confusedcat, corporate, crab, cry, dab, dank, deepfry, delete, disability, doglemon, door, dream, egg, emergencymeeting, excuseme, expanddong, expandingwwe, facts, failure, fakenews, farmer, fedora, floor, fuck, garfield, gay, godwhy, goggles, hitler, humansgood, inator, invert, ipad, jail, justpretending, keepurdistance, kimborder, knowyourlocation, kowalski, laid, letmein, lick, madethis, magik, master, meme, note, nothing, obama, ohno, piccolo, plan, presentation, profile, quote, radialblur, rip, roblox, salty, satan, savehumanity, screams, shit, sickfilth, slap, slapsroof, sneakyfox, spank, stroke, surprised, sword, theoffice, thesearch, trash, trigger, tweet, ugly, unpopular, violence, violentsparks, vr, walking, wanted, warp, whodidthis, whothisis, yomomma, youtube

from fastapi import APIRouter
app = FastAPI(
    title="Nyan Streamer",
    description="The Best and Biggest Meme Gen API",
    version="0.0.2",
)

def format_text(text):
    replacements = {
        "_": "__",
        " ": "_",
        "-": "--",
        "\n": "~n",
        "?": "~q",
        "&": "~a",
        "%": "~p",
        "#": "~h",
        "/": "~s",
        "\\": "~b",
        "<": "~l",
        ">": "~g",
        "\"": "''"
    }

    for key, value in replacements.items():
        text = text.replace(key, value)

    return text

async def get_current_api_key(request: Request):
    print(request.headers)
    auth_header = request.headers.get("Authorization")
    print(f"Received Authorization Header: {auth_header}")  # Debug print

    if not auth_header:
        print("No Authorization header found.")  # Debug print
        raise HTTPException(status_code=403, detail="API key required")
    
    # Splitting the header value to get the actual API key
    # Format: "Bearer YOUR_API_KEY"
    parts = auth_header.split(" ")
    print(f"Header parts: {parts}")  # Debug print
    
    api_key = parts[1]
    print(f"Extracted API Key: {api_key}")  # Debug print
    
    # Check if the API key exists in the database
    key_exists = await db_manager.api_key_value_exists(api_key)
    print(f"API Key exists in database: {key_exists}")  # Debug print

    if not key_exists:
        print("API Key not found in database.")  # Debug print
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

import glob

def delete_all_download_files():
    """Delete all files in the current directory that start with 'download_'."""
    for file in glob.glob("download_*"):
        try:
            os.remove(file)
            logging.info(f"Deleted file: {file}")
        except Exception as e:
            logging.error(f"Error deleting file {file}: {e}")

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

@app.get("/3d/nuke", tags=["3D", "API Key Needed"])
async def become_a_nuke(avatar_url: str, background_tasks: BackgroundTasks, api_key: str = Depends(get_current_api_key)):
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
        background_tasks.add_task(delete_all_download_files)
        
        return response
    except Exception as e:
        logging.error(f"Failed to generate GIF: {str(e)}")
        return JSONResponse(content={"error": "Failed to generate the nuke GIF. Please try again."}, status_code=500)

def run_nuke_subprocess(model_path, avatar_url, frames, filename):
    logging.info(f"Starting subprocess to generate GIF for avatar: {avatar_url}")
    
    # Use subprocess.Popen to start the process
    subprocess.Popen([sys.executable, 'helpers/spinning_model_maker.py', model_path, avatar_url, str(frames), filename, '0,0,0', '0,0,45', '0,-4,0'])


@app.get("/3d/chair", tags=["3D", "API Key Needed"])
async def become_a_chair(avatar_url: str, background_tasks: BackgroundTasks, api_key: str = Depends(get_current_api_key)):
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
        background_tasks.add_task(delete_all_download_files)
        
        return response
    except Exception as e:
        logging.error(f"Failed to generate GIF: {str(e)}")
        return JSONResponse(content={"error": "Failed to generate the nuke GIF. Please try again."}, status_code=500)

def run_chair_subprocess(model_path, avatar_url, frames, filename):
    logging.info(f"Starting subprocess to generate GIF for avatar: {avatar_url}")
    
    # Use subprocess.Popen to start the process
    subprocess.Popen([sys.executable, 'helpers/spinning_model_maker.py', model_path, avatar_url, str(frames), filename, '0,0,0', '0,96,25', '0,-3,0'])

@app.get("/3d/can", tags=["3D", "API Key Needed"])
async def become_a_can(avatar_url: str, background_tasks: BackgroundTasks, api_key: str = Depends(get_current_api_key)):
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
        background_tasks.add_task(delete_all_download_files)
        
        return response
    except Exception as e:
        logging.error(f"Failed to generate GIF: {str(e)}")
        return JSONResponse(content={"error": "Failed to generate the nuke GIF. Please try again."}, status_code=500)

def run_can_subprocess(model_path, avatar_url, frames, filename):
    logging.info(f"Starting subprocess to generate GIF for avatar: {avatar_url}")
    
    # Use subprocess.Popen to start the process
    subprocess.Popen([sys.executable, 'helpers/spinning_model_maker.py', model_path, avatar_url, str(frames), filename, '0,0,-0.85', '0,100,0', '0,-5,0'])

@app.get("/image/abandon", tags=["Image"])
async def abandon_text(text: str):
    abandon_instance = abandon.Abandon()
    image_data = abandon_instance.generate([], text, [], "")
    return StreamingResponse(image_data, media_type="image/png")

@app.get("/image/aborted", tags=["Image"])
async def abort_user(avatar_url: str):
    aborted_instance = aborted.Aborted()
    image_data = aborted_instance.generate([avatar_url], "", [], "")
    return StreamingResponse(image_data, media_type="image/png")

@app.get("/image/affect", tags=["Image"])
async def affect_user(avatar_url: str):
    affect_instance = affect.Affect()
    image_data = affect_instance.generate([avatar_url], "", [], "")
    return StreamingResponse(image_data, media_type="image/png")

@app.get("/image/airpods", tags=["Image"])
async def give_user_airpods(avatar_url: str):
    airpods_instance = airpods.Airpods()
    image_data = airpods_instance.generate([avatar_url], "", [], "")
    return StreamingResponse(image_data, media_type="image/gif")

@app.get("/image/armor", tags=["Image"])
async def armor_text(text: str):
    armor_instance = armor.Armor()
    image_data = armor_instance.generate([], text, [], "")
    return StreamingResponse(image_data, media_type="image/png")

@app.get("/image/balloon", tags=["Image"])
async def balloon_text(text1: str, text2: str):
    balloon_instance = balloon.Balloon()
    image_data = balloon_instance.generate([], f"{text1}, {text2}", [], "")
    return StreamingResponse(image_data, media_type="image/png")

@app.get("/image/bed", tags=["Image"])
async def put_users_in_bed(user1_avatar_url: str, user2_avatar_url: str):
    bed_instance = bed.Bed()
    image_data = bed_instance.generate([user1_avatar_url, user2_avatar_url], "", [], "")
    return StreamingResponse(image_data, media_type="image/png")

@app.get("/image/crab", tags=["Image", "API Key Needed"])
async def crab_rave(text1: str, text2: str, api_key: str = Depends(get_current_api_key)):
    crab_instance = crab.Crab()
    video_data = crab_instance.generate([], f"{text1},{text2}", [], "")
    return StreamingResponse(video_data, media_type="video/mp4")

@app.get("/image/america", tags=["Image"])
async def americanize_user(avatar_url: str):
    america_instance = america.America()
    image_data = america_instance.generate([avatar_url], "", [], "")
    return StreamingResponse(image_data, media_type="image/gif")

@app.get("/image/salty", tags=["Image"])
async def someones_salty(avatar_url: str):
    salty_instance = salty.Salty()
    image_data = salty_instance.generate([avatar_url], "", [], "")
    
    # Ensure the image data is in bytes format
    if not isinstance(image_data, bytes):
        # Handle the error or convert to bytes
        pass

    # Return the image data with the correct content type
    return StreamingResponse(image_data, media_type="image/png")


@app.get("/image/trigger", tags=["Image"])
async def trigger_a_user(avatar_url: str):
    triggered_instance = trigger.Trigger()
    image_data = triggered_instance.generate([avatar_url], "", [], "")
    # Return the image data with the correct content type
    return StreamingResponse(image_data, media_type="image/png")

#tweet image
@app.get("/image/tweet", tags=["Image"])
async def make_a_user_tweet_something_funny(avatar_url: str, text: str, username: str):
    tweet_instance = tweet.Tweet()
    image_data = tweet_instance.generate([avatar_url], f'{text}', [username], "")
    return StreamingResponse(image_data, media_type="image/png")

#bateman
@app.get("/image/bateman", tags=["Image"])
async def fr(avatar_url: str):
    bateman_instance = bateman.Bateman()
    image_data = bateman_instance.generate([avatar_url], "", [], "")
    return StreamingResponse(image_data, media_type="video/mp4")

@app.get("/image/citation", tags=["Image"])
async def write_a_citation(title: str, text: str, footer: str):
    citation_instance = citation.Citation
    image = citation_instance.generate("", "", f"{title},{text},{footer}", [], "")
    return StreamingResponse(image, media_type="image/png")

#john oliver
@app.get("/image/johnoliver", tags=["Image"])
async def john_oliver_wants_to_show_you_something(avatar_url: str):
    johnoliver_instance = johnoliver.JohnOliver
    image_data = johnoliver_instance.generate("", [avatar_url], "", [], "")
    return StreamingResponse(image_data, media_type="image/png")

#dominos
@app.get("/image/dominos", tags=["Image"])
async def this_is_what_happends(text1: str, text2: str):
    dominos_instance = dominos.Dominoes
    image_data = dominos_instance.generate("", "", f"{text1}, {text2}", [], "")
    return StreamingResponse(image_data, media_type="image/png")
        
@app.get("/image/eject", tags=["Image", "API Key Needed"])
async def eject_a_user(avatar_url: str, username: str, imposter: str = None, api_key: str = Depends(get_current_api_key)):
    # Open config.json
    with open("config.json") as file:
        data = json.load(file)

    # Get the API key
    sr_api_key = data["SRA-KEY"]

    if imposter is None:
        outcome = random.choice(["true", "false"])
    elif imposter == "True":
        outcome = "true"
    elif imposter == "False":
        outcome = "false"

    url = f"https://some-random-api.com/premium/amongus?avatar={avatar_url}&key={sr_api_key}&username={username[0:35]}&imposter={outcome}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail="Could not download file... The Api is down :(")
            image_data = await resp.read()
            return StreamingResponse(io.BytesIO(image_data), media_type="image/gif")

@app.get("/image/simp", tags=["Image"])
async def simp(avatar_url: str):
    url = f"https://some-random-api.com/canvas/simpcard?avatar={avatar_url}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail="Could not download file... The Api is down :(")
            image_data = await resp.read()
            return StreamingResponse(io.BytesIO(image_data), media_type="image/png")

@app.get("/image/horny", tags=["Image"])
async def horny(avatar_url: str):
    url = f"https://some-random-api.com/canvas/horny?avatar={avatar_url}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail="Could not download file... The Api is down :(")
            image_data = await resp.read()
            return StreamingResponse(io.BytesIO(image_data), media_type="image/png")

@app.get("/image/pat", tags=["Image"])
async def pat(avatar_url: str):
    # Fetch the user's avatar
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail="Failed to fetch avatar")
            image_content = await resp.read()

    # Process the image
    source = BytesIO(image_content)
    dest = BytesIO()
    petpet.make(source, dest)
    dest.seek(0)
    
    # Return the processed image
    return StreamingResponse(dest, media_type="image/gif")

@app.get("/image/jail", tags=["Image"])
async def send_a_user_to_jail(avatar_url: str):
    jail_instance = jail.Jail()
    image_data = jail_instance.generate([avatar_url], f'', "", "")
    return StreamingResponse(image_data, media_type="image/png")


@app.get("/jeyy/matrix", tags=["Jeyy"])
async def put_someone_in_the_matrix(avatar_url: str):
    image_data = await client.matrix(avatar_url)
    return StreamingResponse(image_data, media_type="image/gif")

@app.get("/jeyy/balls", tags=["Jeyy"])
async def lol_balls(avatar_url: str):
    image_data = await client.balls(avatar_url)
    return StreamingResponse(image_data, media_type="image/gif")

@app.get("/jeyy/billboard", tags=["Jeyy"])
async def become_a_billboard(avatar_url: str):
    image_data = await client.billboard(avatar_url)
    return StreamingResponse(image_data, media_type="image/png")

@app.get("/jeyy/heartlocket", tags=["Jeyy"])
async def become_a_heartlocket(avatar_url: str):
    image_data = await client.heart_locket(avatar_url, avatar_url)
    return StreamingResponse(image_data, media_type="image/gif")

@app.get("/jeyy/pizza", tags=["Jeyy"])
async def become_a_pizza(avatar_url: str):
    image_data = await client.pizza(avatar_url)
    return StreamingResponse(image_data, media_type="image/png")

@app.get("/jeyy/zonk", tags=["Jeyy"])
async def get_zonked(avatar_url: str):
    image_data = await client.zonk(avatar_url)
    return StreamingResponse(image_data, media_type="image/gif")


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=5000)