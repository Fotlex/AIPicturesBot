import asyncio
import sys

from typing import Callable, Any, Dict, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import User


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        bot: Bot = data['bot']
        from_user = event.from_user
        bot_info = await bot.get_me()
        try:
            user = await User.objects.aget(id=from_user.id)
        except User.DoesNotExist:
            user = await User.objects.acreate(
                id=from_user.id,
                first_name=from_user.first_name or '',
                last_name=from_user.last_name or '',
                refferal_link=f'https://t.me/{bot_info.username}?start=ref{from_user.id}'
            )

        data['user'] = user

        return await handler(event, data)
    
ALBUM_DELAY = 1.0
  
class MediaGroupMiddleware(BaseMiddleware):
    album_data: Dict[str, list[Message]] = {}
    locks: Dict[str, asyncio.Lock] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        media_group_id = str(event.media_group_id)

        if media_group_id not in self.locks:
            self.locks[media_group_id] = asyncio.Lock()
        
        lock = self.locks[media_group_id]
        
        async with lock:
            if media_group_id not in self.album_data:
                self.album_data[media_group_id] = []
            
            self.album_data[media_group_id].append(event)
        
        await asyncio.sleep(ALBUM_DELAY)

        async with lock:
            if media_group_id not in self.album_data:
                return
            
            album_messages = self.album_data.pop(media_group_id)
            self.locks.pop(media_group_id, None)
            
        album_messages.sort(key=lambda x: x.message_id)
        
        data["album"] = album_messages
        
        return await handler(album_messages[0], data)