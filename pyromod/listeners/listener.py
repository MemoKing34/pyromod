import inspect
from typing import Callable, Union, Optional
from asyncio import Future
import asyncio

import pyrogram

from pyromod.helpers.helpers import seperate_filter

class Listener(pyrogram.handlers.handler.Handler):
    def __init__(self, 
        client: 'pyrogram.Client' = None,
        future: Future = None, 
        callback: Callable = None, 
        filters: Optional['pyrogram.filters.Filter'] = None
    ):
        if not (asyncio.isfuture(future) or callable(callback)):
            raise ValueError("Listener must have either a future or a callback")
        self.future = future
        self._callback = callback
        self.filters = filters
        self._client = client
       
    
    async def callback(self, client: 'pyrogram.Client', update: Union['pyrogram.types.Message', 'pyrogram.types.CallbackQuery']):
        if asyncio.isfuture(self.future) and not self.future.done():
            return self.future.set_result(update)
        if callable(self._callback):
            return await self._execute_callback(self._callback, update)
        
    async def _execute_callback(self, callback, *args):
        if inspect.iscoroutinefunction(callback):
            await listener.callback(self._client, *args)
        else:
            await self._client.loop.run_in_executor(
                self._client.executor, callback,
                self._client, *args
            )
    