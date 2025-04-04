import json
from os import getenv

import requests

OPENROUTER_API_KEY = getenv("OPENROUTER_API_KEY")

models = {
    "Gemini2.0F" : {
        "name": "Gemini 2.0",
        "md_name":"Gemini 2\.0",
        "emoji" : '♊️',
        'is_free' : True,
        'api_key': OPENROUTER_API_KEY,
        'endpoint': "google/gemini-2.0-flash-exp:free",
    }
}


async def llm(prompt: str, initial_prompt) -> str:
    return await get_openrouter_response(prompt, initial_prompt)



async def get_openrouter_response(prompt: str, initial_prompt:str) -> str:
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
    }
    json_data = json.dumps({
    "model": models['Gemini2.0F']['endpoint'], #default model
    "messages": [
      {
        "role": "user",
        "content": prompt,
       }
    ]
  })
    response = requests.post(url="https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json_data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']
