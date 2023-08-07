import asyncio
from helpers.spinning_model_maker import spinning_model

async def main():
    model_path = "Bomb_1.egg"
    image_url = "https://media.discordapp.net/attachments/755517144426479786/1135374566844284998/1.png?width=794&height=794"
    frames = 30
    filename = "spinning_bomb"
    await spinning_model(model_path, image_url, frames, filename,
                     model_pos=(0, 0, 0), 
                     model_hpr=(0, 0, 45),
                     cam_pos=(0, -4, 0))

if __name__ == "__main__":
    asyncio.run(main())