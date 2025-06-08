import os

from dotenv import load_dotenv




load_dotenv()

BOT_TOKEN=os.getenv('BOT_TOKEN')

DB_NAME=os.getenv('DB_NAME')       
DB_USER=os.getenv('DB_USER')  
DB_PASSWORD=os.getenv('DB_PASSWORD')   
DB_HOST=os.getenv('DB_HOST')        
DB_PORT=os.getenv('DB_PORT')

YOOKASSA_SHOP_ID=os.getenv('YOOKASSA_SHOP_ID')
YOOKASSA_SECRET_KEY=os.getenv('YOOKASSA_SECRET_KEY')

BOT_NAME=os.getenv('BOT_NAME')


API_URL=os.getenv('API_URL')