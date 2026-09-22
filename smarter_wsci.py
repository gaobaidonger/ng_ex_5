from pathlib import Path
from ollama import chat
import json


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""


# -------------------------
# SELECT
# -------------------------

def select_context(question):
    question = question.lower()

    selected_files = []

    if (
        "wi-fi" in question
        or "wifi" in question
        or "eduroam" in question
        or "network" in question
    ):
        selected_files.append("knowledge/wifi_setup.txt")

    if (
        "password" in question
        or "credential" in question
        or "login" in question
    ):
        selected_files.append("knowledge/password_changes.txt")

    if (
        "connect" in question
        or "works" in question
        or "status" in question
    ):
        selected_files.append("knowledge/service_status.txt")

    if "email" in question or "mail" in question:
        selected_files.append("knowledge/email_setup.txt")

    if "vpn" in question:
        selected_files.append("knowledge/vpn.txt")

    if "print" in question or "printer" in question:
        selected_files.append("knowledge/printing.txt")

    if (
        "projector" in question
        or "display" in question
        or "hdmi" in question
    ):
        selected_files.append("knowledge/classroom_projectors.txt")

    return selected_files


selected_files = select_context(question)

print("Selected files:")
print(selected_files)


# -------------------------
# READ SELECTED CONTEXT
# -------------------------

context = ""

for file in selected_files:
    context += Path(file).read_text()
    context += "\n\n"

print(
    "Selected context characters:",
    len(context)
)


# -------------------------
# COMPRESS
# -------------------------

def compress_context(context, question):

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": f"""
The student's question is:

{question}

Below is university IT support information:

{context}

Extract only the information that is directly relevant
to answering the student's question.

Do not add any information that is not in the context.
"""
            }
        ]
    )

    return response.message.content


compressed_context = compress_context(
    context,
    question
)

print(
    "Compressed context characters:",
    len(compressed_context)
)


# -------------------------
# WRITE INITIAL STATE
# -------------------------

state = {
    "diagnostic_context": {
        "problem": question.strip(),
        "device": "Windows laptop",
        "wifi_status": "operational",
        "selected_files": selected_files,
        "compressed_context": compressed_context
    },

    "report_context": {
        "exercise": "WSCI Framework",
        "status": "in progress"
    }
}


with open(
    "state.json",
    "w"
) as file:

    json.dump(
        state,
        file,
        indent=2
    )


# -------------------------
# READ STATE
# -------------------------

with open(
    "state.json",
    "r"
) as file:

    state = json.load(file)


# -------------------------
# ISOLATE
# -------------------------

diagnostic_context = state[
    "diagnostic_context"
]


# -------------------------
# FINAL QWEN CALL
# -------------------------

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": f"""
You are a university IT support assistant.

Use only the diagnostic context below.

Diagnostic context:

{json.dumps(diagnostic_context, indent=2)}

Answer the student's problem.

Return the answer as JSON using exactly this structure:

{{
    "likely_cause": "...",
    "evidence": [
        "...",
        "..."
    ],
    "steps": [
        "...",
        "...",
        "..."
    ],
    "escalation": "..."
}}
"""
        }
    ]
)


print(response.message.content)


# -------------------------
# WRITE FINAL RESULT
# -------------------------

state[
    "diagnostic_context"
][
    "result"
] = response.message.content

state[
    "report_context"
][
    "status"
] = "completed"


with open(
    "state.json",
    "w"
) as file:

    json.dump(
        state,
        file,
        indent=2
    )


print("State written to state.json")