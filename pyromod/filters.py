from typing import Union, List

from pyrogram.filters import *
from pyrogram.types import Message, CallbackQuery, Update
import pyrogram

class chat_instance(Filter, set):
    def __init__(self, instances: Union[str, int, List[Union[str, int]]] = None):
        instances = [] if instances is None else instances if isinstance(instances, list) else [instances]
        super().__init__(
            str(instance) for instance in instances
        )
    
    async def __call__(self, _, query: CallbackQuery):
        return query.chat_instance and str(query.chat_instance) in self
pyrogram.filters.chat_instance = chat_instance

class message(Filter, set):
    def __init__(self, ids: Union[int, List[int]] = None):
        super().__init__(
            [] if ids is None else ids if isinstance(ids, list) else [ids]
        )
    
    async def __call__(self, _, update: Update):
        if isinstance(update, Message):
            return update.id in self
        if isinstance(update, CallbackQuery):
            return update.message.id in self
pyrogram.filters.message = message

class inline_message_id(Filter, set):
    def __init__(self, ids: Union[str, List[str]] = None):
        super().__init__(
            [] if ids is None else ids if isinstance(ids, list) else [ids]
        )
        
    async def __call__(self, _, query: CallbackQuery):
        return self.inline_message_id and self.inline_message_id in self
pyrogram.filters.inline_message_id = inline_message_id

class chat(chat):
    async def __call__(self, _, update: Update):
        if isinstance(update, CallbackQuery):
            return await super().__call__(_, update.message)
        return await super().__call__(_, update)
pyrogram.filters.chat = chat

class user(user):
    async def __call__(self, _, update: Update):
        if hasattr(update, 'from_user'):
            return await super().__call__(_, update)
        return await super().__call__(_, update.message)
pyrogram.filters.user = user