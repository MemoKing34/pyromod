import asyncio

class ListenerTimeout(asyncio.exceptions.TimeoutError):
    def __init__(self, timeout: int):
        try:
            self.timeout = int(timeout)
        except (ValueError, TypeError):
            self.timeout = timeout
        super().__init__(timeout)
