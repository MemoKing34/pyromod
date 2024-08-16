from typing import Callable, Union, Optional, List
from asyncio import Future

from pyrogram import filters
import pyrogram

from .listener import Listener

class CallbackQueryListener(Listener):
    def __init__(self, 
        client: 'pyrogram.Client' = None,
        future: Future = None, 
        callback: Callable = None, 
        chat_instance: Union[Union[int, str], List[Union[int, str]]] = None,
        chat_id: Union[Union[int, str], List[Union[int, str]]] = None,
        user_id: Union[Union[int, str], List[Union[int, str]]] = None, 
        message_id: Union[int, List[int]] = None,
        inline_message_id: Union[str, List[str]] = None,
        custom_filters: Optional['filters.Filter'] = None,
        unallowed_click_text: str = None, 
        alert_it: bool = True
    ):
        _filters = filters.chat_instance(chat_instance) if chat_instance is not None else filters.chat(chat_id)
        if message_id:
            _filters = _filters & filters.message(message_id)
        if inline_message_id:
            _filters = _filters & filters.inline_message_id(inline_message_id)
        self.user_filter = filters.user(user_id) if user_id else filters.all
        self.unallowed_click_text = unallowed_click_text
        if (not self.unallowed_click_text) and (self.user_filter is not filters.all):
            _filters = _filters & self.user_filter
        self.alert_it = alert_it
        super().__init__(client, future, callback, _filters)
            
    
    async def callback(self, client: "pyrogram.Client", update: "pyrogram.types.CallbackQuery"):
        if (not self.unallowed_click_text) or (await self.user_filter(client, update)):
            return await super().callback(client, update)
        if self.unallowed_click_text.strip():
            await update.answer(self.unallowed_click_text, show_alert=self.alert_it)
        raise pyrogram.ContinuePropagation
            