import asyncio
from inspect import iscoroutinefunction
from typing import Optional, Callable, Dict, List, Union

import pyrogram
from pyrogram.filters import Filter

from .listeners import MessageListener, CallbackQueryListener
from .listeners.listener import Listener
from .exceptions import ListenerTimeout, ListenerStopped
from .utils import should_patch, patch_into
from .enums import ListenerType
from .dispatcher import Dispatcher


@patch_into(pyrogram.client.Client)
class Client(pyrogram.client.Client):
    old__init__: Callable
    
    @should_patch()
    def __init__(self, *args, **kwargs):
        self.old__init__(*args, **kwargs)
        self.dispatcher = Dispatcher(self)
    
    
    @should_patch()
    def _add_listener(self, listener, listener_type):
        self.dispatcher.add_listener(listener, listener_type)
        return listener, listener_type
        
    @should_patch()
    def _remove_listener(self, listener, listener_type):
        self.dispatcher.remove_listener(listener, listener_type)
        return listener, listener_type

    @should_patch()
    async def listen_chat(
        self,
        listener_type: ListenerType = ListenerType.MESSAGE,
        chat_id: Union[Union[int, str], List[Union[int, str]]] = None,
        user_id: Union[Union[int, str], List[Union[int, str]]] = None,
        chat_instance: Union[Union[int, str], List[Union[int, str]]] = None,
        message_id: Union[int, List[int]] = None,
        inline_message_id: Union[str, List[str]] = None,
        filters: Optional[Filter] = None,
        unallowed_click_text: str = "[pyromod] You're not expected to click this button.", 
        alert_it: bool = True,
        timeout: Optional[int] = None
    ):
        future = self.loop.create_future()
        
        if listener_type == ListenerType.MESSAGE:
            listener = MessageListener(
                client=self,
                future=future,
                chat_id=chat_id,
                user_id=user_id,
                custom_filters=filters
            )
        else:
            listener = CallbackQueryListener(
                client=self,
                future=future,
                chat_instance=chat_instance,
                chat_id=chat_id,
                user_id=user_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                custom_filters=filters,
                unallowed_click_text=unallowed_click_text,
                alert_it=alert_it
            )
        
        self._add_listener(listener, listener_type)

        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.exceptions.TimeoutError:
            self.stop_listener(listener, listener_type, False)
            raise ListenerTimeout(timeout)

    @should_patch()
    async def ask_to_chat(
        self,
        chat_id: Union[Union[int, str], List[Union[int, str]]],
        text: str,
        listener_type: ListenerType = ListenerType.MESSAGE,
        user_id: Union[Union[int, str], List[Union[int, str]]] = None,
        chat_instance: Union[Union[int, str], List[Union[int, str]]] = None,
        message_id: Union[int, List[int]] = None,
        inline_message_id: Union[str, List[str]] = None,
        filters: Optional[Filter] = None,
        unallowed_click_text: str = "[pyromod] You're not expected to click this button.",
        alert_it: bool = True,
        timeout: Optional[int] = None,
        *args,
        **kwargs
    ):
        chat_to_ask = chat_id[0] if isinstance(chat_id, list) else chat_id
        question_message = await self.send_message(chat_to_ask, text, *args, **kwargs)

        response = await self.listen_chat(
            listener_type=listener_type,
            chat_id=chat_id,
            user_id=user_id,
            chat_instance=chat_instance,
            message_id=message_id,
            inline_message_id=inline_message_id,
            filters=filters,
            unallowed_click_text=unallowed_click_text,
            alert_it=alert_it,
            timeout=timeout
        )
        if response:
            response.question_message = question_message
        return response



    @should_patch()
    async def stop_listening(self, throw_exceptions: bool = False):
        for listener_type, listeners in self.dispatcher.listeners.items():
            for listener in listeners:
                self.stop_listener(listener, listener_type, throw_exceptions)

    @should_patch()
    def stop_listener(self, listener: Listener, listener_type: ListenerType, throw_exception: bool = True):
        self._remove_listener(listener, listener_type)

        if listener.future.done():
            return

        if throw_exception:
            listener.future.set_exception(ListenerStopped())
        else:
            listener.future.cancel()
        

    @should_patch()
    def register_next_step_handler(
        self,
        callback: Callable,
        listener_type: ListenerType = ListenerType.MESSAGE,
        chat_id: Union[Union[int, str], List[Union[int, str]]] = None,
        user_id: Union[Union[int, str], List[Union[int, str]]] = None,
        chat_instance: Union[Union[int, str], List[Union[int, str]]] = None,
        message_id: Union[int, List[int]] = None,
        inline_message_id: Union[str, List[str]] = None,
        filters: Optional[Filter] = None,
        unallowed_click_text: str = "[pyromod] You're not expected to click this button.",
        alert_it: bool = True,
    ):
        if listener_type == ListenerType.MESSAGE:
            listener = MessageListener(
                callback=callback,
                chat_id=chat_id,
                user_id=user_id,
                custom_filters=filters
            )
        else:
            listener = CallbackQueryListener(
                callback=callback,
                chat_instance=chat_instance,
                user_id=user_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                unallowed_click_text=unallowed_click_text,
                alert_it=alert_it
            )
