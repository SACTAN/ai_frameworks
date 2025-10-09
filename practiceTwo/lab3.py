from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from pydantic import BaseModel
import os
import gradio as gr

load_dotenv(override=True)

base_url="https://openrouter.ai/api/v1"
api_key=os.getenv("OPENROUTER_API_KEY")
model ="mistralai/mistral-small-3.2-24b-instruct:free"
reader = PdfReader("me/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

print(linkedin)

with open("me/summary.text","r",encoding="utf-8") as f:
    summary= f.read()

name ="Sachin Bhute"

system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer, say so."

system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."

def chat(message, history):
    messages=[{"role":"system","content":system_prompt},{"role":"user","content":message}]
    myllmRouter = OpenAI(base_url=base_url,api_key=api_key)
    answerS =myllmRouter.chat.completions.create(model=model, messages=messages)
    finalAns = answerS.choices[0].message.content
    return finalAns

gr.ChatInterface(chat, type="messages").launch()

# Create a Pydantic model for the Evaluation


class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
The Agent is playing the role of {name} and is representing {name} on their website. \
The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
The Agent has been provided with context on {name} in the form of their summary and LinkedIn details. Here's the information:"

evaluator_system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
evaluator_system_prompt += f"With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."

def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt


def evaluate(reply, message, history) -> Evaluation:
    routerTwo=OpenAI(base_url=base_url,api_key=api_key)
    messagesAll = [{"role":"system", "content":evaluator_system_prompt},{"role":"user","content":evaluator_user_prompt(reply, message, history)}]
    endResponse = routerTwo.chat.completions.create(model="gentica-org/deepcoder-14b-preview:free",messages=messagesAll,response_format=Evaluation)
    return endResponse.choices[0].message.parsed

messages = [{"role": "system", "content": system_prompt}] + [{"role": "user", "content": "do you hold a Bachlor of enginnering dgree?"}]
routerTwo=OpenAI(base_url=base_url,api_key=api_key)
response = routerTwo.chat.completions.create(model="mistralai/mistral-small-3.2-24b-instruct:free", messages=messages)
reply = response.choices[0].message.content

print(reply)

evaluate(reply,"from which college you completed your Bachlor of engineering",messages[:1])


def rerun(reply, message, history, feedback):
    updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    routerThree = OpenAI(base_url=base_url, api_key=api_key)
    response = routerThree.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
    return response.choices[0].message.content


def chat(message, history):
    system = system_prompt
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": message}]
    routerfour = OpenAI(base_url=base_url, api_key=api_key)
    response = routerfour.chat.completions.create(model="mistralai/mistral-small-3.2-24b-instruct:free", messages=messages)
    reply = response.choices[0].message.content

    evaluation = evaluate(reply, message, history)

    if evaluation.is_acceptable:
        print("Passed evaluation - returning reply")
    else:
        print("Failed evaluation - retrying")
        print(evaluation.feedback)
        reply = rerun(reply, message, history, evaluation.feedback)
    return reply

gr.ChatInterface(chat, type="messages").launch()










