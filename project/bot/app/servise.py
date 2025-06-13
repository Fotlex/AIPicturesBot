import aiohttp, json, os
import logging
import base64
from io import BytesIO
from PIL import Image

from project import config

async def generate_avatar(auth_key, zip_url, model_name, trigger_phrase, target_url):
    payload = {
        "auth_key": auth_key,
        "url": zip_url,
        "name": model_name,
        "trigger_phrase": trigger_phrase,
        "steps": 1000,
        "learning_rate": 0.0005,
        "training_style": "subject",
        "face_crop": False
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{config.TARGET_POST_URL}{target_url}', json=payload, allow_redirects=True) as response:
                response.raise_for_status() 

                response_data = await response.json()
                logging.info(f"Сервер успешно ответил: {response_data}")
                return response_data
                
    except aiohttp.ClientResponseError as e:
        logging.error(f"Ошибка отправки: статус {e.status}, сообщение: {e.message}")

        
    except Exception as e:
        logging.error(f"Произошла непредвиденная ошибка: {e}")
        
def write_json_response_to_file(response_json, filepath="ai_responses.txt"):
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True) 
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(response_json)
        
async def generate_photo(auth_key, model_api_name, promt, seed=None, size='square_hd'):
    post_generate = {
        "auth_key": auth_key,
        "name": model_api_name,
        "prompt": promt,
        "image_size": size,
        "num_inference_steps": 25,
        "guidance_scale": 3,
        "seed": seed,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{config.TARGET_POST_URL}/generate', json=post_generate, allow_redirects=True) as response:
                response.raise_for_status() 

                response_data = await response.json()
                write_json_response_to_file(response_data.get('image_base64'))
                return response_data["image_base64"]
                
    except aiohttp.ClientResponseError as e:
        logging.error(f"Ошибка отправки: статус {e.status}, сообщение: {e.message}")

        
    except Exception as e:
        logging.error(f"Произошла непредвиденная ошибка: {e}")



def decode_base64_to_image(base64_string: str) -> Image.Image:
    if "base64," in base64_string:
        base64_string = base64_string.split("base64,", 1)[1]
    
    image_bytes = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_bytes))
    return image

def convert_pil_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    bio = BytesIO()
    image.save(bio, format=format)
    return bio.getvalue()