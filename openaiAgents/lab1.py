# The imports
import asyncio

from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv
from agents import Agent, Runner, trace
import os

from lazy_object_proxy.utils import await_
from litellm import completion


def myRun():
    base_url="https://openrouter.ai/api/v1"
    api_key=os.getenv("OPENROUTER_API_KEY")
    model ="openrouter/openai/gpt-4"

    load_dotenv(override=True)

    # response = completion(
    #     model="openrouter/openai/gpt-4",
    #     messages=[{"role":"system","content":"You are a joke teller"},{"role":"user","content":"Tell a joke about Autonomous AI Agents"}]
    # )
    # print(f"litellm response {response}")

    agent = Agent(name="Jokester",instructions="You are a joke teller",model=LitellmModel(model=model, api_key=api_key))

    asyncio.run(runner(agent))
    #result = await Runner.run(agent, "Tell a joke about Autonomous AI Agents")


async def runner(agent):
    result = await Runner.run(agent, "Tell a joke about Autonomous AI Agents")
    print(f"2nd output {result.final_output}")

if __name__ == "__main__":
    myRun()

