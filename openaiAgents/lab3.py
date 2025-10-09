import asyncio

from dotenv import load_dotenv
import os
from agents import Agent, OpenAIChatCompletionsModel, function_tool, Runner, GuardrailFunctionOutput, input_guardrail
from openai import AsyncOpenAI
import sendgrid
from pydantic import BaseModel
from sendgrid import Email, To, Content
from sendgrid.helpers.mail import Mail


load_dotenv(override=True)

sales_manager_instructions = """
   You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.

   Follow these steps carefully:
   1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.

   2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
   You can use the tools multiple times if you're not satisfied with the results from the first try.

   3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. The Email Manager will take care of formatting and sending.

   Crucial Rules:
   - You must use the sales agent tools to generate the drafts — do not write them yourself.
   - You must hand off exactly ONE email to the Email Manager — never more than one.
   """


def setupAll():
    router_apiKey = os.getenv("OPENROUTER_API_KEY")
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    groq_api_key = os.getenv('GROQ_API_KEY')
    rcerebras_api_key = os.getenv('CEREBRAS_API_KEY')

    instructions1 = "You are a sales agent working for ComplAI, \
    a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
    You write professional, serious cold emails."

    instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
    a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
    You write witty, engaging cold emails that are likely to get a response."

    instructions3 = "You are a busy sales agent working for ComplAI, \
    a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
    You write concise, to the point cold emails."

    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
    OLLAMA_BASE_URL="http://localhost:11434/v1"
    CEREBRAS_BASE_URL="https://api.cerebras.ai/v1"

    deepseek_model="z-ai/glm-4.5-air:free"
    ollama_model="z-ai/glm-4.5-air:free"
    groq_model_name = "z-ai/glm-4.5-air:free"
    general_model_name="z-ai/glm-4.5-air:free"
    model_name = "qwen2.5-coder:3b"
    cerebras_model="llama-4-scout-17b-16e-instruct"

    deepseek_client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key=deepseek_api_key)
    ollama_client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key=deepseek_api_key)
    groq_client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key=deepseek_api_key)
    cerebras_client = AsyncOpenAI(base_url=CEREBRAS_BASE_URL, api_key=rcerebras_api_key)

    deepseek_model_obj=OpenAIChatCompletionsModel(model=cerebras_model,openai_client=cerebras_client)
    ollama_model_obj = OpenAIChatCompletionsModel(model=cerebras_model, openai_client=cerebras_client)
    groq_model_obj = OpenAIChatCompletionsModel(model=cerebras_model, openai_client=cerebras_client)
    general_model_obj = OpenAIChatCompletionsModel(model=cerebras_model, openai_client=cerebras_client)

    sales_agent1 = Agent(name="Deepseak sales agent", instructions=instructions1, model=deepseek_model_obj)
    sales_agent2 =  Agent(name="Ollama Sales Agent", instructions=instructions2, model=ollama_model_obj)
    sales_agent3  = Agent(name="Groq Sales Agent",instructions=instructions3,model=groq_model_obj)

    description = "Write a cold sales email"

    tool1= sales_agent1.as_tool(tool_name="sales Agent1", tool_description=description)
    tool2 = sales_agent2.as_tool(tool_name="Sales Agent2", tool_description=description)
    tool3 = sales_agent3.as_tool(tool_name="sales Agent3", tool_description=description)

    subject_instructions = "You can write a subject for a cold sales email. \
    You are given a message and you need to write a subject for an email that is likely to get a response."

    html_instructions = "You can convert a text email body to an HTML email body. \
    You are given a text email body which might have some markdown \
    and you need to convert it to an HTML email body with simple, clear, compelling layout and design."

    subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model=general_model_obj)
    subject_tool = subject_writer.as_tool(tool_name="subject_writer",
                                          tool_description="Write a subject for a cold sales email")

    html_converter = Agent(name="HTML email body converter", instructions=html_instructions, model=general_model_obj)
    html_tool = html_converter.as_tool(tool_name="html_converter",
                                       tool_description="Convert a text email body to an HTML email body")

    email_tools = [subject_tool, html_tool, send_html_email]

    instructions = "You are an email formatter and sender. You receive the body of an email to be sent. \
    You first use the subject_writer tool to write a subject for the email, then use the html_converter tool to convert the body to HTML. \
    Finally, you use the send_html_email tool to send the email with the subject and HTML body."

    emailer_agent = Agent(
        name="Email Manager",
        instructions=instructions,
        tools=email_tools,
        model=general_model_obj,
        handoff_description="Convert an email to HTML and send it")

    tools = [tool1, tool2, tool3]
    handoffs = [emailer_agent]


    sales_manager = Agent(
        name="Sales Manager",
        instructions=sales_manager_instructions,
        tools=tools,
        handoffs=handoffs,
        model=general_model_obj)

    careful_sales_manager = Agent(
        name="Sales Manager",
        instructions=sales_manager_instructions,
        tools=tools,
        handoffs=[emailer_agent],
        model="gpt-4o-mini",
        input_guardrails=[guardrail_against_name]
    )

    return careful_sales_manager


@function_tool
def send_html_email(subject: str, html_body: str) -> dict[str, str]:
    """ Send out an email with the given subject and HTML body to all sales prospects """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("sachinbhute23nov@gmail.com")  # Change to your verified sender
    to_email = To("sachinbbhute@gmail.com")  # Change to your recipient
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}



async def runner():
    guardrailAgent()
    message = "Send out a cold sales email addressed to Dear CEO from Alice"
    await Runner.run(setupAll(),message)

async def runner2():
    message = "Send out a cold sales email addressed to Dear CEO from Alice"
    result = await Runner.run(setupAll(), message)

class NameCheckOutput(BaseModel):
    is_name_in_message: bool
    name: str


def guardrailAgent():
    OLLAMA_BASE_URL = "http://localhost:11434/v1"
    deepseek_model = "z-ai/glm-4.5-air:free"
    model_name = "qwen2.5-coder:3b"
    ollama_client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key=None)
    general_model_obj = OpenAIChatCompletionsModel(model=model_name, openai_client=ollama_client)
    guardrail_agent = Agent(
        name="Name check",
        instructions="Check if the user is including someone's personal name in what they want you to do.",
        output_type=NameCheckOutput,
        model=general_model_obj
    )
    return guardrail_agent

@input_guardrail
async def guardrail_against_name(ctx, agent, message):
    result = await Runner.run(guardrailAgent(), message, context=ctx.context)
    is_name_in_message = result.final_output.is_name_in_message
    return GuardrailFunctionOutput(output_info={"found_name": result.final_output},tripwire_triggered=is_name_in_message)


if __name__ == "__main__":
    asyncio.run(runner2())




