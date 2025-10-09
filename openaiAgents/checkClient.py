import os
from cerebras.cloud.sdk import Cerebras

client = Cerebras(
  api_key="csk-hwhe9kth28w44nv2ppj8h9drfy26tht3dr6pvpd5hkpdkhkx",
)

chat_completion = client.chat.completions.create(
  messages=[
  {"role": "user", "content": "Why is fast inference important?",}
],
  model="llama-4-scout-17b-16e-instruct",
)

print(chat_completion.choices[0].message.content)