import ollama

from retriever import retrieve_documents

LLM_MODEL = "qwen2.5:3b"


def rewrite_question(question, chat_history):
    """
    Convert a follow-up question into a standalone search query.
    """

    # No previous conversation? Use the original question.
    if not chat_history:
        return question

    messages = [
        {
            "role": "system",
            "content": """
            You rewrite follow-up questions into standalone search queries.

            Rules:
            1. Read the previous conversation carefully.
            2. Identify the main topic being discussed.
            3. Resolve references such as "it", "that", "those" and "what about".
            4. Preserve the exact topic and context from previous messages.
            5. Never remove important terms from the conversation.
            6. Do not answer the question.
            7. Return only one standalone search query.

            Example:

            Conversation:
            User: How many annual leave days do employees receive?
            Assistant: Employees receive 20 days per year.

            Follow-up:
            What about carry-forward?

            Correct rewrite:
            How many unused annual leave days can employees carry forward?

            Another example:

            Conversation:
            User: What is the annual leave carry-forward limit?

            Follow-up:
            When do those days expire?

            Correct rewrite:
            When do carried-forward annual leave days expire?
            """
        }
    ]

    # Include recent conversation for context
    messages.extend(chat_history[-6:])

    messages.append({
        "role": "user",
        "content": f"Rewrite this question for document search: {question}"
    })

    response = ollama.chat(
        model=LLM_MODEL,
        messages=messages,
        options={"temperature": 0}
    )

    return response["message"]["content"].strip()


def generate_answer(question, chat_history=None):
    """Retrieve documents and generate a context-aware answer."""

    if chat_history is None:
        chat_history = []

    # Step 1: Rewrite the question using conversation history
    search_query = rewrite_question(question, chat_history)

    print("\nSEARCH QUERY:", search_query)

    # Step 2: Retrieve relevant document chunks
    documents = retrieve_documents(search_query, top_k=2)

    if not documents:
        answer = "I couldn't find this information in the provided documents."
        return {"answer": answer, "sources": []}

    # Step 3: Prepare retrieved context
    context_parts = []

    for index, document in enumerate(documents, start=1):
        context_parts.append(
            f"""
            Source {index}:
            Document: {document['source']}
            Page: {document['page']}
            Content: {document['text']}
            """
        )

    context = "\n".join(context_parts)

    # Step 4: Construct the system prompt
    system_prompt = """
    You are an AI assistant that answers questions using provided documents.

    Follow these rules:
    1. Answer using only the provided document context.
    2. Do not invent facts or make unsupported assumptions.
    3. If the answer is not present in the context, say:
       "I couldn't find this information in the provided documents."
    4. Keep answers clear and concise.
    5. Do not write source labels such as Source 1 in your answer.
    6. Source references are displayed separately by the application.
    7. Use proper spacing and readable formatting.
    9. Do not combine rules from different policy sections unless the context explicitly connects them.
    10. Do not apply a policy rule to another category of leave, expense, or employee benefit.
    11. Every factual statement must be directly supported by the retrieved context.
    12. If only part of a question can be answered, clearly distinguish the supported information from what is unknown.
    """

    # Step 5: Build the messages for Qwen
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Add previous conversation
    messages.extend(chat_history[-6:])

    # Add the current question and retrieved context
    messages.append({
        "role": "user",
        "content": f"""
        Retrieved document context:

        {context}

        Original user question:
        {question}

        Answer using only the retrieved context.
        """
    })

    # Step 6: Generate the answer
    response = ollama.chat(
        model=LLM_MODEL,
        messages=messages,
        options={"temperature": 0.2}
    )

    answer = response["message"]["content"]

    # Step 7: Remove duplicate source/page combinations
    unique_sources = []
    seen_sources = set()

    for document in documents:
        source_key = (document["source"], document["page"])

        if source_key not in seen_sources:
            seen_sources.add(source_key)

            unique_sources.append({
                "source": document["source"],
                "page": document["page"]
            })

    # Hide citations when the model refuses to answer
    if "couldn't find this information" in answer.lower():
        unique_sources = []

    return {
        "answer": answer,
        "sources": unique_sources,
        "search_query": search_query
    }


if __name__ == "__main__":

    # Stores messages for this conversation
    chat_history = []

    print("Local RAG Assistant")
    print("Type 'exit' to end the conversation.")

    while True:

        question = input("\nYou: ").strip()

        if question.lower() in ["exit", "quit"]:
            print("Conversation ended.")
            break

        if not question:
            continue

        result = generate_answer(question, chat_history)

        print("\nAI:", result["answer"])

        print("\nSOURCES:")

        for source in result["sources"]:
            print(
                f"- {source['source']} | Page {source['page']}"
            )

        # Save the exchange for future questions
        chat_history.append({
            "role": "user",
            "content": question
        })

        chat_history.append({
            "role": "assistant",
            "content": result["answer"]
        })