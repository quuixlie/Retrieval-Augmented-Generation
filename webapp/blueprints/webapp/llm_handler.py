import json
import os
from dotenv import load_dotenv
from os import getenv

import requests

# OPENROUTER_API_KEY = getenv("OPENROUTER_API_KEY")

load_dotenv()



import requests

def llm(endpoint: str, prompt: str):
    api = os.getenv("OPENROUTER_API_KEY")
    headers = {
        'Authorization': f'Bearer {api}',
        'Content-Type': 'application/json',
    }
    payload = {
        "model": endpoint,
        "messages": [{"role": "user", "content": prompt}]
    }
    print(headers)
    print(payload)

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": "Request to LLM API failed"}

    except (KeyError, IndexError) as e:
        print(f"Unexpected response format: {e}")
        return {"error": "Unexpected API response"}


def create_prompt(query: str, relevant_documents: list):
    """
    Create a prompt for the LLM based on the query and relevant documents.
    :param query: The user's query
    :param relevant_documents:
    :return: Formatted prompt string
    """
    prompt = f"Question: {query}\n\n"
    prompt += "Relevant documents:\n"
    for i, doc in enumerate(relevant_documents):
        prompt += f"\n================= Document {i + 1} =================\n, {doc}"

    return prompt
