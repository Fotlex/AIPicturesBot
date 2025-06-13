import io
import zipfile
from typing import List

from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
from aiogram import Bot 

from .models import UserArchive



async def process_and_save_photos(bot: Bot, user_id: int, file_ids: List[str]):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, file_id in enumerate(file_ids):
            file_info = await bot.get_file(file_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            
            zipf.writestr(f"photo_{i+1}.jpg", downloaded_file.read())
    
    zip_buffer.seek(0)
    zip_bytes = zip_buffer.read()

    
    @sync_to_async
    def save_to_django(uid: int, file_name: str, data: bytes) -> str:
        archive, _ = UserArchive.objects.get_or_create(telegram_user_id=uid)
        archive.archive_file.save(file_name, ContentFile(data), save=True)
        return archive.archive_file.url

    file_url = await save_to_django(user_id, f"user_{user_id}.zip", zip_bytes)
    return file_url