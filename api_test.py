import openai
import os
from dotenv import load_dotenv

api_key= os.environ['api_key']

base_url= "https://api.ai.it.cornell.edu"

client = openai.OpenAI(
    api_key=api_key,
    base_url=base_url
)

response = client.chat.completions.create(

    model="openai.gpt-4o", # model to send to the proxy

    messages = [

        {

            "role": "user",

            "content": "How are you"

        }

    ]

)

print(response.choices[0].message.content)