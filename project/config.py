import os

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN=os.getenv('BOT_TOKEN')

DB_NAME=os.getenv('POSTGRES_DB')       
DB_USER=os.getenv('POSTGRES_USER')  
DB_PASSWORD=os.getenv('POSTGRES_PASSWORD')   
DB_HOST=os.getenv('POSTGRES_HOST')        
DB_PORT=os.getenv('POSTGRES_PORT')

YOOKASSA_SHOP_ID=os.getenv('YOOKASSA_SHOP_ID')
YOOKASSA_SECRET_KEY=os.getenv('YOOKASSA_SECRET_KEY')

BOT_NAME=os.getenv('BOT_NAME')

ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("ALLOWED_HOSTS", "").split(",") if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
REDIS_HOST=os.getenv('REDIS_HOST')
REDIS_PORT=os.getenv('REDIS_PORT')
API_URL=os.getenv('API_URL')
DEVELOP_URL=os.getenv('DEVELOP_URL')

TARGET_POST_URL=os.getenv('TARGET_POST_URL')
LORA_KEY=os.getenv('LORA_KEY')
SUPPORT_URL=os.getenv('SUPPORT_URL')