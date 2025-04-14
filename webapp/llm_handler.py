import os
from dotenv import load_dotenv
import requests

from appconfig import AppConfig


def llm(endpoint: str, prompt: str):
    headers = {
        'Authorization': f'Bearer {AppConfig.OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        "model": endpoint,
        "messages": [{"role": "user", "content": prompt}]
    }
    # print(headers)
    # print(payload)

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


def create_prompt(query: str, relevant_documents_formatted: str) -> str:
    """
    Create a prompt for the LLM based on the query and relevant documents.
    :param query: The user's query
    :param relevant_documents:
    :return: Formatted prompt string
    """
    prompt = f"Question: {query}\n\n"
    prompt += "Relevant documents:\n"
    prompt += relevant_documents_formatted

    return prompt


def format_relevant_documents(relevant_documents: list) -> str:
    """
    Format the relevant documents for the prompt.
    :param relevant_documents: List of relevant documents
    :return: Formatted string of relevant documents
    """
    formatted_docs = ""
    for i, doc in enumerate(relevant_documents):
        formatted_docs += f"\n================= Document {i + 1} =================\n{doc}"

    return formatted_docs


def format_response(response: str, relevant_documents_formatted: str) -> str:
    """
    Format the LLM response.
    :param response: The LLM response
    :param relevant_documents_formatted: The formatted relevant documents
    :return: Formatted string of the response
    """
    formatted_response = f"Response:\n{response}\n\n"
    formatted_response += "Relevant documents:\n"
    formatted_response += relevant_documents_formatted

    return formatted_response
