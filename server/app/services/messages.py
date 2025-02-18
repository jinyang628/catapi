from app.llm.assistant import AsyncCatAssistant
from app.models.messages import Message, MessagePayload, Role


class MessagesService:
    async def message(self, payload: MessagePayload) -> MessagePayload:
        assistant = await AsyncCatAssistant.create(thread_id=payload.thread_id)
        response: str = await assistant.run(user_input=payload.message.content)
        return MessagePayload(
            thread_id=assistant.thread_id,
            message=Message(role=Role.ASSISTANT, content=response),
        )
