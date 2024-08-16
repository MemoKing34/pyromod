import inspect
import logging
import asyncio

import pyrogram
from pyrogram import handlers

log = logging.getLogger(__name__)


from .listeners.listener import Listener
from .enums import ListenerType
from .utils import patch_into, should_patch
from .exceptions import ListenerStopped


@patch_into(pyrogram.dispatcher.Dispatcher)
class Dispatcher(pyrogram.dispatcher.Dispatcher):
    LISTENER_HANDLER = {
        handlers.MessageHandler: ListenerType.MESSAGE,
        handlers.CallbackQueryHandler: ListenerType.CALLBACK_QUERY
    }
    should_patch(LISTENER_HANDLER)
    
    @should_patch()
    def __init__(self, client: "pyrogram.Client"):
        self.old__init__(client)
        self.listeners = {listener_type: set() for listener_type in ListenerType}
    
    @should_patch()
    def add_listener(self, listener: Listener, listener_type: ListenerType):
        self.listeners[listener_type].add(listener)
    
    @should_patch()
    def remove_listener(self, listener: Listener, listener_type: ListenerType):
        self.listeners[listener_type].discard(listener)

    
    @should_patch()
    async def stop(self):
        await self.oldstop()
        await self.client.stop_listening()
        
    @should_patch()
    async def handler_worker(self, lock):
        while True:
            packet = await self.updates_queue.get()

            if packet is None:
                break

            try:
                update, users, chats = packet
                parser = self.update_parsers.get(type(update), None)

                parsed_update, handler_type = (
                    await parser(update, users, chats)
                    if parser is not None
                    else (None, type(None))
                )

                async with lock:
                    if handler_type in self.LISTENER_HANDLER:
                        for listener in self.listeners[self.LISTENER_HANDLER[handler_type]]:
                            try:
                                if await listener.check(self.client, parsed_update):
                                    await listener.callback(self.client, parsed_update)
                                    raise pyrogram.StopPropagation
                            except pyrogram.StopPropagation:
                                self.remove_listener(listener, self.LISTENER_HANDLER[handler_type])
                                raise
                            except pyrogram.ContinuePropagation:
                                raise pyrogram.StopPropagation
                            except Exception as e:
                                log.exception(e)
                    
                    for group in self.groups.values():
                        for handler in group:
                            args = None

                            if isinstance(handler, handler_type):
                                try:
                                    if await handler.check(self.client, parsed_update):
                                        args = (parsed_update,)
                                except Exception as e:
                                    log.exception(e)
                                    continue

                            elif isinstance(handler, handlers.RawUpdateHandler):
                                args = (update, users, chats)

                            if args is None:
                                continue

                            try:
                                if inspect.iscoroutinefunction(handler.callback):
                                    await handler.callback(self.client, *args)
                                else:
                                    await self.loop.run_in_executor(
                                        self.client.executor,
                                        handler.callback,
                                        self.client, *args
                                    )
                            except pyrogram.StopPropagation:
                                raise
                            except pyrogram.ContinuePropagation:
                                continue
                            except Exception as e:
                                log.exception(e)
                            break
            except pyrogram.StopPropagation:
                pass
            except Exception as e:
                log.exception(e)