import asyncio

import sendgrid
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
from openai.types.responses import ResponseTextDeltaEvent
from sendgrid.helpers.mail import Email, To, Content, Mail
from dotenv import load_dotenv
import sendgrid
import os


load_dotenv(override=True)

base_url="https://openrouter.ai/api/v1"
api_key=os.getenv("OPENROUTER_API_KEY")
model ="openrouter/openai/gpt-4"
sales_agents=[]


def send_test_email():
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    from_email = Email("meredostchutyahai@gmail.com")  # Change to your verified sender
    to_email = To("sachinbhute23nov@gmail.com")  # Change to your recipient
    content = Content("text/plain", "This is an important test email")
    mail = Mail(from_email, to_email, "Test email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    #response = sg.send(mail)
    print(response.status_code)

#send_test_email()

def setupAll():
    instructions1 = "You are a sales agent working for ComplAI, \
    a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
    You write professional, serious cold emails."

    instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
    a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
    You write witty, engaging cold emails that are likely to get a response."

    instructions3 = "You are a busy sales agent working for ComplAI, \
    a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
    You write concise, to the point cold emails."

    sales_Agent1= Agent(name="Professional Email Agent", instructions=instructions1, model=LitellmModel(model=model, api_key=api_key))
    sales_agents.append(sales_Agent1)

    sales_Agent2 = Agent(name="Professional Sales Agent", instructions=instructions2, model=LitellmModel(model=model,api_key=api_key))
    sales_agents.append(sales_Agent2)
    sales_Agent3 = Agent(name="Professional busy Sales Agent", instructions=instructions3,model=LitellmModel(model=model,api_key=api_key))
    sales_agents.append(sales_Agent3)
    return sales_agents


async def events():
    result = Runner.run_streamed(sales_agents[0], input="Write a cold sales email")
    #print(result)
    async for event in result.stream_events():
       # print(event)
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


async def asyncioGather():
    message = "Write a cold sales email"
    results = await asyncio.gather(
            Runner.run(sales_agent[0], message),
            Runner.run(sales_agent[1], message),
            Runner.run(sales_agent[2], message),
        )
    outputs = [result.final_output for result in results]
    for output in outputs: print(output + "\n\n")

sales_picker = Agent(
    name="sales_picker",
    instructions="You pick the best cold sales email from the given options. \
Imagine you are a customer and pick the one you are most likely to respond to. \
Do not give an explanation; reply with the selected email only.",
    model=LitellmModel(model=model,api_key=api_key)
)

async def pickBest():
    message = "Write a cold sales email"
    results = await asyncio.gather(
            Runner.run(sales_agent[0], message),
            Runner.run(sales_agent[1], message),
            Runner.run(sales_agent[2], message),
        )
    outputs = [result.final_output for result in results]
    emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)
    best = await Runner.run(sales_picker, emails)
    print(f"Best sales email:\n{best.final_output}")


if __name__ == "__main__":
    sales_agent = setupAll()
    #asyncio.run(events())
    #asyncio.run(asyncioGather())
    asyncio.run(pickBest())



