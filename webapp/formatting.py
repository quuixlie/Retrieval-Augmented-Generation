
def format_response(response: str, relevant_contexts: str) -> str:
    """
    Format the LLM response.
    :param response: The LLM response
    :param relevant_documents_formatted: The formatted relevant documents
    :return: Formatted string of the response
    """

    formatted_docs = ""

    for i, doc in enumerate(relevant_contexts):
        formatted_docs += f"\n================= Fragment {i + 1} =================\n{doc}"

    formatted_response = f"Response:\n{response}\n\n"
    formatted_response += "Relevant documents:\n"
    formatted_response += formatted_docs

    return formatted_response
