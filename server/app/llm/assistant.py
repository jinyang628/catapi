import asyncio
import json
import os
from typing import Optional

import aiohttp
from openai import AsyncOpenAI
from openai.types.beta.thread import Thread

client = AsyncOpenAI()

CAT_API_KEY = os.environ.get("CAT_API_KEY")
CAT_API_BASE_URL = "https://api.thecatapi.com/v1"
SEARCH_CAT_FUNCTION_NAME = "search_cats"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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
            instructions=f"You are a helpful assistant that helps users pick the most suitable cat picture given the user's description of the cat. You should terminate after getting the cat picture and not make any more requests. You should output the image URL in your response in markdown format. Here is the list of cats you can filter for where the id is the breed id which you must output:\n{json.load(open(f'{BASE_DIR}/breeds.json'))}",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": SEARCH_CAT_FUNCTION_NAME,
                        "description": "Search for cat pictures based on breed or temperament using the Cat API.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "breed": {
                                    "type": "string",
                                    "description": "The breed of the cat. Your output should be a 4 character id in the Cat API",
                                },
                            },
                            "required": [],
                        },
                    },
                }
            ],
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

        try:
            await client.beta.threads.messages.create(
                thread_id=self.thread_id, role="user", content=user_input
            )

            run = await client.beta.threads.runs.create(
                thread_id=self.thread_id, assistant_id=self.assistant.id
            )

            while True:
                run = await client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id, run_id=run.id
                )

                if run.status == "requires_action":
                    # Handle tool calls
                    tool_outputs = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        if tool_call.function.name == SEARCH_CAT_FUNCTION_NAME:
                            args = json.loads(tool_call.function.arguments)
                            cat_result = await self.search_cats(**args)
                            tool_outputs.append(
                                {"tool_call_id": tool_call.id, "output": json.dumps(cat_result)}
                            )

                    # Submit tool outputs
                    await client.beta.threads.runs.submit_tool_outputs(
                        thread_id=self.thread_id, run_id=run.id, tool_outputs=tool_outputs
                    )

                elif run.status == "completed":
                    # Get the latest message
                    messages = await client.beta.threads.messages.list(
                        thread_id=self.thread_id, order="desc", limit=1
                    )

                    if not messages.data:
                        return "No response generated. Please try again."

                    message = messages.data[0]
                    if not message.content:
                        return "Empty response received. Please try again."

                    content = message.content[0]
                    return content.text.value if hasattr(content, "text") else ""

                elif run.status in ["failed", "cancelled", "expired"]:
                    return f"Run failed with status: {run.status}"

                # Wait before checking again
                await asyncio.sleep(1)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return error_message

    async def search_cats(
        self,
        breed: Optional[str] = None,
    ) -> dict:
        """
        Search for cats using the CatAPI based on given criteria
        """
        if not breed:
            return {}
        try:
            params = {}
            if breed:
                params["breed_ids"] = breed

            headers = {"x-api-key": CAT_API_KEY}

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{CAT_API_BASE_URL}/images/search",
                    params=params,
                    headers={k: str(v) for k, v in headers.items() if v is not None},
                ) as response:
                    response.raise_for_status()
                    cats = await response.json()
                    return cats[0] if cats else {"error": "No cats found matching criteria"}

        except aiohttp.ClientError as e:
            return {"error": f"API request to Cat API failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error during cat search: {str(e)}"}
