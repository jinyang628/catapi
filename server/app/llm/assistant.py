import json
import os
from threading import Thread
from typing import Optional

import aiohttp
from openai import AsyncAssistantEventHandler, AsyncOpenAI
from openai.types.beta.thread import Thread

client = AsyncOpenAI()

CAT_API_KEY = os.environ.get("CAT_API_KEY")
CAT_API_BASE_URL = "https://api.thecatapi.com/v1"


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
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "search_cats",
                        "description": "Search for cat pictures based on breed, temperament, or size.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "breed": {"type": "string", "description": "The breed of the cat."},
                                "temperament": {
                                    "type": "string",
                                    "description": "The temperament of the cat.",
                                },
                                "size": {"type": "string", "description": "The size of the cat."},
                            },
                            "required": [],
                        },
                    },
                }
            ],
            model="gpt-4",
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

        # Add the user's message to the thread
        await client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=user_input
        )

        event_handler = AsyncAssistantEventHandler()

        async with client.beta.threads.runs.stream(
            thread_id=self.thread_id,
            assistant_id=self.assistant.id,
            event_handler=event_handler,
        ) as stream:
            async for event in stream:
                if event.event == "thread.run.requires_action":
                    # The assistant is requesting to call a function
                    run_id = event.data.get("run_id")
                    tool_calls = (
                        event.data.get("required_action", {})
                        .get("submit_tool_outputs", {})
                        .get("tool_calls", [])
                    )

                    tool_outputs = []
                    for tool_call in tool_calls:
                        if tool_call["function"]["name"] == "search_cats":
                            # Parse the arguments and call the CatAPI
                            args = json.loads(tool_call["function"]["arguments"])
                            cat_result = await self.search_cats(**args)

                            # Submit the function output back to the assistant
                            tool_outputs.append(
                                {"tool_call_id": tool_call["id"], "output": json.dumps(cat_result)}
                            )

                    # Submit the tool outputs back to the assistant
                    await client.beta.threads.runs.submit_tool_outputs(
                        thread_id=self.thread_id, run_id=run_id, tool_outputs=tool_outputs
                    )

            await stream.until_done()

        # Retrieve the final response from the assistant
        final_response = await event_handler.get_final_messages()
        print(final_response)
        content = final_response[0].content[0]
        if hasattr(content, "text"):
            return content.text.value
        elif hasattr(content, "image_file"):
            return content.image_file.url
        elif hasattr(content, "image_url"):
            return content.image_url.url
        else:
            return str(content)

    async def search_cats(
        self,
        breed: Optional[str] = None,
        temperament: Optional[str] = None,
        size: Optional[str] = None,
    ) -> dict:
        """
        Search for cats using the CatAPI based on given criteria
        """
        params = {}
        if breed:
            params["breed_ids"] = breed

        headers = {"x-api-key": CAT_API_KEY}

        async with aiohttp.ClientSession() as session:
            # First get breed information if needed
            if temperament or size:
                async with session.get(
                    f"{CAT_API_BASE_URL}/breeds",
                    headers={k: str(v) for k, v in headers.items() if v is not None},
                ) as response:
                    breeds = await response.json()

                    # Filter breeds based on temperament and size
                    if temperament:
                        breeds = [
                            b
                            for b in breeds
                            if temperament.lower() in b.get("temperament", "").lower()
                        ]
                    if size:
                        breeds = [b for b in breeds if b.get("size", "").lower() == size.lower()]

                    if breeds:
                        params["breed_ids"] = ",".join([b["id"] for b in breeds])

            async with session.get(
                f"{CAT_API_BASE_URL}/images/search",
                params=params,
                headers={k: str(v) for k, v in headers.items() if v is not None},
            ) as response:
                cats = await response.json()
                return cats[0] if cats else {}
