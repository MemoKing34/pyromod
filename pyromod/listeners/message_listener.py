from typing import Callable, Union, Optional, List
from asyncio import Future

from pyrogram import filters
import pyrogram

from .listener import Listener


class MessageListener(Listener):
    def __init__(self, 
        client: 'pyrogram.Client' = None,
        future: Future = None, 
        callback: Callable = None, 
        chat_id: Union[Union[int, str], List[Union[int, str]]] = None, 
        user_id: Union[Union[int, str], List[Union[int, str]]] = None, 
        custom_filters: Optional['filters.Filter'] = None
    ):
        _filters = filters.chat(chat_id)
        if user_id:
            _filters = _filters & filters.user(user_id)
        if custom_filters:
            _filters = _filters & custom_filters
        super().__init__(client, future, callback, _filters)