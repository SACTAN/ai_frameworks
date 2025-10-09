from openai import OpenAI
import gradio as gr

from practiceTwo.lab3 import system_prompt, base_url, api_key, evaluate, rerun


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

gr.ChatInterface(chat, type="messages").launch(share=True)