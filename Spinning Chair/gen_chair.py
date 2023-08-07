import asyncio
from spinning_model_maker import spinning_model

async def main():
    model_path = "Chair.egg"
    image_url = "https://media.discordapp.net/attachments/755517144426479786/1135374566844284998/1.png?width=794&height=794"
    frames = 30
    filename = "spinning_chair"
    await spinning_model(model_path, image_url, frames, filename,
                     model_pos=(0, 0, 0), 
                     model_hpr=(0, 96, 25),
                     cam_pos=(0, -3, 0))

if __name__ == "__main__":
    asyncio.run(main())
