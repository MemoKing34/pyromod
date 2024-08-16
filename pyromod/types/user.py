from typing import Union, List, Optional

import pyrogram
from pyrogram.filters import Filter

from ..client import Client
from ..utils import patch_into, should_patch
from ..enums import ListenerType


@patch_into(pyrogram.types.user_and_chats.user.User)
class User(pyrogram.types.user_and_chats.user.User):
    _client: Client

    @should_patch()
    async def listen(
        self,
        listener_type: ListenerType = ListenerType.MESSAGE,
        chat_id: Union[Union[int, str], List[Union[int, str]]] = None,
        chat_instance: Union[Union[int, str], List[Union[int, str]]] = None,
        message_id: Union[int, List[int]] = None,
        inline_message_id: Union[str, List[str]] = None,
        filters: Optional[Filter] = None,
        unallowed_click_text: str = "[pyromod] You're not expected to click this button.", 
        alert_it: bool = True,
        timeout: Optional[int] = None
    ):
        return await self._client.listen_chat(
            listener_type=listener_type,
            chat_id=chat_id,
            user_id=self.id,
            chat_instance=chat_instance,
            message_id=message_id,
            inline_message_id=inline_message_id,
            filters=filters,
            unallowed_click_text=unallowed_click_text,
            alert_it=alert_it,
            timeout=timeout
        )

    @should_patch()
    async def ask(
        self,
        text: str,
        listener_type: ListenerType = ListenerType.MESSAGE,
        chat_id: Union[Union[int, str], List[Union[int, str]]] = None,
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
        return await self._client.ask_to_chat(chat_id, text,
            listener_type=listener_type,
            user_id=self.id,
            chat_instance=chat_instance,
            message_id=message_id,
            inline_message_id=inline_message_id,
            filters=filters,
            unallowed_click_text=unallowed_click_text,
            alert_it=alert_it,
            timeout=timeout,
            *args, **kwargs
        )

    @should_patch()
    async def stop_listening(self, throw_exceptions: bool = False):
        return self._client.stop_listening(throw_exceptions)
