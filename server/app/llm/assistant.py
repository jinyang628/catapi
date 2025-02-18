import asyncio
from threading import Thread
from typing import Optional

from openai import AsyncAssistantEventHandler, AsyncOpenAI
from openai.types.beta.thread import Thread

client = AsyncOpenAI()


class AsyncCatAssistant:
    thread_id: Optional[str] = None

    def __init__(self, thread_id: Optional[str] = None):
        self.assistant = None
        self.thread_id = thread_id

    @classmethod
    async def create(cls, thread_id: Optional[str] = None):
        instance = cls(thread_id)
        instance.assistant = await client.beta.assistants.create(
            name="Cat Picker",
            instructions="You are a helpful assistant that helps users pick the most suitable cat picture.",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4o-mini",
        )
        if not instance.thread_id:
            thread: Thread = await client.beta.threads.create()
            instance.thread_id = thread.id
        return instance

    async def run(self, user_input: str):
        if not self.thread_id:
            raise ValueError("Thread ID is not set")
        if not self.assistant:
            raise ValueError("Assistant is not set")
        await client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=user_input
        )

        event_handler = AsyncAssistantEventHandler()

        async with client.beta.threads.runs.stream(
            thread_id=self.thread_id,
            assistant_id=self.assistant.id,
            instructions="Please address the user as Jane Doe. The user has a premium account.",
            event_handler=event_handler,
        ) as stream:
            await stream.until_done()

        final_response = await event_handler.get_final_messages()
        print(final_response)
        return final_response
