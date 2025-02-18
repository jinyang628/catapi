from app.llm.assistant import AsyncCatAssistant
from app.models.messages import MessagePayload


class MessagesService:
    async def message(self, payload: MessagePayload) -> MessagePayload:
        assistant = await AsyncCatAssistant.create(thread_id=payload.thread_id)
        response = await assistant.run(user_input=payload.message.content)
        return MessagePayload(thread_id=payload.thread_id, message=payload.message)
