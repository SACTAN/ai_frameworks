import openai
from IPython.display import Markdown, display
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv(override=True)

# GEMINI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
# google_api_key=os.getenv("GOOGLE_API_KEY")
# gemini=OpenAI(base_url=GEMINI_BASE_URL,api_key=google_api_key)
# response = gemini.chat.completions.create(model="gemini-2.5-flash-preview-05-20",messages=[{"role":"user","content":"What we celebrate 2 Oct in india"}])
# print(response.choices[0].message.content)

# ollama = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
# model_name = "qwen2.5-coder:3b"
#
# response = ollama.chat.completions.create(model=model_name, messages=[{"role":"user","content":"What we celebrate on 2 Oct in india"}])
# answer = response.choices[0].message.content
#
# display(Markdown(answer))
groq_base_url="https://api.groq.com/openai/v1"
groq_api_key=os.getenv("GROQ_API_KEY")

model_name = "llama-3.3-70b-versatile"

#groq = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
# response = groq.chat.completions.create(model=model_name, messages=[{"role":"user","content":"What we celebrate on 2 Oct in india"}])
# answer = response.choices[0].message.content
# print(answer)
# display(Markdown(answer))
#
question="Please propose a hard, challenging question to assess someone's IQ. Respond only with the question."
messages=[{"role":"user","content":question}]


groqTwo = OpenAI(api_key=groq_api_key, base_url=groq_base_url)
answer = groqTwo.chat.completions.create(model=model_name,messages=messages)
myResponse = answer.choices[0].message.content
#print(myResponse)

display(Markdown(myResponse))