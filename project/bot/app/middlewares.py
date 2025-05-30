import sys

from typing import Callable, Any, Dict, Awaitable
from aiogram import BaseMiddleware
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
            data: Dict[str, Any]
    ) -> Any:
        from_user = event.from_user

        try:
            user = await User.objects.aget(id=from_user.id)
        except User.DoesNotExist:
            user = await User.objects.acreate(
                id=from_user.id,
                first_name=from_user.first_name or '',
                last_name=from_user.last_name or '',
            )

        data['user'] = user

        return await handler(event, data)