import os
import json

import openai
from dotenv import load_dotenv
from openai import OpenAI
from IPython.display import Markdown, display

load_dotenv(override=True)

request = "Please come up with a challenging, nuanced question that I can ask a number of LLMs to evaluate their intelligence. "
request += "Answer only with the question, no explanation."
messages = [{"role": "user", "content": request}]

groq_base_url="https://api.groq.com/openai/v1"
groq_api_key=os.getenv("GROQ_API_KEY")
model_name = "llama-3.3-70b-versatile"

groq = OpenAI(base_url=groq_base_url, api_key=groq_api_key)
answer = groq.chat.completions.create(model=model_name, messages=messages)
question = answer.choices[0].message.content
print(question)


competitors = []
answers=[]
messages =[{"role":"user", "content":question}]

# ollama = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
# model_name = "qwen2.5-coder:3b"
#
# response = ollama.chat.completions.create(model=model_name, messages=messages)
# answer = response.choices[0].message.content
#
# display(Markdown(answer))
# competitors.append(model_name)
# answers.append(answer)

routerClient = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
answer = routerClient.chat.completions.create(model="agentica-org/deepcoder-14b-preview:free",messages=messages)
deepcoderAns = answer.choices[0].message.content
print("Answer from chat GPT "+ deepcoderAns)
competitors.append("agentica-org/deepcoder-14b-preview:free")
answers.append(deepcoderAns)

routerClient = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
answer = routerClient.chat.completions.create(model="mistralai/mistral-small-3.2-24b-instruct:free",messages=messages)
mistralAns = answer.choices[0].message.content
print("Answer from chat GPT "+ mistralAns)
competitors.append("mistralai/mistral-small-3.2-24b-instruct:free")
answers.append(mistralAns)

groq = OpenAI(base_url=groq_base_url, api_key=groq_api_key)
answer = groq.chat.completions.create(model=model_name, messages=messages)
groqAnswer = answer.choices[0].message.content
print("Answer from chat GPT "+ groqAnswer)
competitors.append(model_name)
answers.append(groqAnswer)
print("==================================================================")
for ans in zip(competitors,answers):
    print(ans)

together = ""
for index, answer in enumerate(answers):
    together += f"# Response from competitor {index+1}\n\n"
    together += answer + "\n\n"
print(together)

judge = f"""You are judging a competition between {len(competitors)} competitors.
Each model has been given this question:

{question}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
Respond with JSON, and only JSON, with the following format:
{{"results": ["best competitor number", "second best competitor number", "third best competitor number", ...]}}

Here are the responses from each competitor:

{together}

Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks."""

judge_message = [{"role": "user", "content":judge}]

finalResp = routerClient.chat.completions.create(model="qwen/qwen3-235b-a22b:free",messages=judge_message)
fresults = finalResp.choices[0].message.content
print(fresults)

result_dict= json.loads(fresults)
ranks =result_dict["results"]
for index, result in enumerate(ranks):
    competitor = competitors[int(result)-1]
    print(f"Rank {index+1}: {competitor}")





