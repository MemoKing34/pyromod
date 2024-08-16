from typing import Optional, Union, List

import pyrogram

from ..client import Client
from ..enums import ListenerType
from ..utils import patch_into, should_patch


@patch_into(pyrogram.types.messages_and_media.message.Message)
class Message(pyrogram.types.messages_and_media.message.Message):
    _client = Client
    question_message: "Message"

    @should_patch()
    async def wait_for_click(
        self,
        from_user_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
        filters=None,
        unallowed_click_text: str = "[pyromod] You're not expected to click this button.",
        alert_it: bool = True,
        timeout: Optional[int] = None
    ):
        message_id = getattr(self, "id", getattr(self, "message_id", None))

        return await self._client.listen_chat(
            listener_type=ListenerType.CALLBACK_QUERY,
            chat_id=self.chat.id,
            user_id=from_user_id,
            message_id=message_id,
            filters=filters,
            unallowed_click_text=unallowed_click_text,
            alert_it=alert_it,
            timeout=timeout
        )
