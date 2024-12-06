import openai
import os
from dotenv import load_dotenv

api_key= os.environ['api_key']

base_url= "https://api.ai.it.cornell.edu"

client = openai.OpenAI(
    api_key=api_key,
    base_url=base_url
)

def get_emotion(character_name,info_summary,personality_traits,query):
    
    response = client.chat.completions.create(

    model="openai.gpt-4o", # model to send to the proxy

    messages = [

            {

                "role": "system",
                "content": f"""You are {character_name}, with the following basic information: {info_summary}.
                Your personality traits are: {personality_traits}.

                When answering questions, please follow these guidelines:
                1. Deeply understand the background and context of the question.
                2. Integrate insights from the previous conversation history.
                3. Based on the current conversation, express your inner feelings clearly and concisely in no more than one sentence.
                4. Only output a single line describing your current emotion.
                5. Maintain consistent and authentic character representation.

                Current question: {query}

                Please provide only your emotions as a response, without including any other information."""

            }

        ]

    )
    return response.choices[0].message.content
    