import logging

from fastapi import APIRouter, HTTPException
from httpx import codes

from app.models.messages import MessagePayload
from app.services.messages import MessagesService

log = logging.getLogger(__name__)


class MessagesController:
    def __init__(self, service: MessagesService):
        self.router = APIRouter()
        self.service = service
        self.setup_routes()

    def setup_routes(self):
        router = self.router

        @router.post(
            "",
            response_model=MessagePayload,
        )
        async def message(input: MessagePayload) -> MessagePayload:
            try:
                log.info("Sending message...")
                response: MessagePayload = await self.service.message(payload=input)
                log.info("Response returned %s", response.message.content)
                return response
            except Exception as e:
                log.error("Unexpected error occurred when sending message: %s", str(e))
                raise HTTPException(
                    status_code=codes.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
                ) from e
