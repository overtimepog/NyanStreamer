import requests
from PIL import Image, ImageSequence
from io import BytesIO

# List of emojis
emojis = [
    "🍎",  # :apple:
    "🍒",  # :cherries:
    "🍇",  # :grapes:
    "🍋",  # :lemon:
    "🍑",  # :peach:
    "🍊",  # :tangerine:
    "🍉",  # :watermelon:
    "🍓",  # :strawberry:
    "🍌",  # :banana:
    "🍍",  # :pineapple:
    "🥝",  # :kiwi:
    "🍐",  # :pear:
    "👑",  # :crown:
    "💎",  # :gem:
]

# Convert the emojis to their corresponding URLs
emoji_urls = []
for emoji in emojis:
    if emoji.startswith("<:"):  # Discord static emoji
        emoji_id = emoji.split(":")[-1][:-1]  # Extract the emoji id
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
    elif emoji.startswith("<a:"):  # Discord animated emoji
        emoji_id = emoji.split(":")[-1][:-1]  # Extract the emoji id
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.gif"
    else:  # Regular emoji
        url = f"https://twemoji.maxcdn.com/v/latest/72x72/{'-'.join(hex(ord(c))[2:] for c in emoji)}.png"
    emoji_urls.append(url)

print("Emoji URLs:", emoji_urls)

# Download the emojis and open them as PIL Images
emoji_images = []
for url in emoji_urls:
    print("Downloading:", url)
    response = requests.get(url)
    print("Response status code:", response.status_code)
    if url.endswith(".gif"):  # Animated emoji
        img = Image.open(BytesIO(response.content))
        img.seek(0)  # Go to the first frame
        img = img.convert("RGBA")  # Convert image to RGBA
    else:  # Static emoji
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGBA")  # Convert image to RGBA
    emoji_images.append(img)

print("Downloaded all emojis")

# Create a new GIF image
print("Creating GIF")
output = BytesIO()

# Set the disposal method for each frame to '2' (replace)
gif_images = [img.copy() for img in emoji_images]
for img in gif_images:
    img.info['duration'] = 100  # Decrease this value to make the animation faster
    img.info['transparency'] = 255
    img.info['disposal'] = 2  # 'replace'

# Save the images as a GIF
gif_images[0].save(output, format='GIF', append_images=gif_images[1:], save_all=True, loop=0)  # Set loop to 0 for infinite loop

# Get the GIF data
gif_data = output.getvalue()

print("GIF created")

# Save the GIF as a file
with open('spin.gif', 'wb') as f:
    f.write(gif_data)

print("GIF saved as spin.gif")

# Now you can send the GIF data in a Discord message
# await ctx.send(file=discord.File(BytesIO(gif_data), 'spin.gif'))