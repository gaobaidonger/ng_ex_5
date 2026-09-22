from pathlib import Path
from ollama import chat

question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

selected_files = [
    "knowledge/password_changes.txt",
    "knowledge/service_status.txt",
    "knowledge/wifi_setup.txt"
]

context = ""

for file in selected_files:
    context += Path(file).read_text()
    context += "\n\n"

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": f"""
Use the following university IT support knowledge to answer the student's question.

Context:
{context}

Question:
{question}
"""
        }
    ]
)

print(
    "Context characters:",
    len(context)
)

print(response.message.content)