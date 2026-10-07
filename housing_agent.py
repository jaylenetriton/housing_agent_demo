from openai import OpenAI
import json
from housing_tools import get_applications_needing_followup, get_application_details


client = OpenAI()

# Describe the function the model can request.
tools = [
    {
        "type": "function",
        "name": "get_applications_needing_followup",
        "description": (
            "Find incomplete housing applications due for follow-up "
            "on a specified date. An application is incomplete if its "
            "agreement or deposit is missing. Follow-up is due at least "
            "three days after the latest reminder, or after submission "
            "if no reminder exists. Returns application IDs, student "
            "names, emails, missing requirements, and reminder history."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "as_of_date": {
                    "type": "string",
                    "description": "Report date in YYYY-MM-DD format."
                }
            },
            "required": ["as_of_date"],
            "additionalProperties": False
        },
        "strict": True
    }
]

tools.append({
    "type": "function",
    "name": "get_application_details",
    "description": (
        "Look up one housing application by its application ID. "
        "Returns the student's details, missing requirements, "
        "reminder history, and next follow-up due date. "
        "Use this to explain an application's status, including "
        "applications that are not currently due for follow-up."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "application_id": {
                "type": "integer",
                "description": "The application ID, such as 2001."
            }
        },
        "required": ["application_id"],
        "additionalProperties": False
    },
    "strict": True
})

# question = "Which housing applications need follow-up as of October 6, 2026?"
question = input("Ask the housing assistant: ").strip()

if not question:
    raise SystemExit("Please enter a question.")

response = client.responses.create(
    model="gpt-4.1-mini",
    instructions=(
        "You assist staff with a fictional housing application demo. "
        "Use tools to retrieve application information; never invent records. "
        "Use get_applications_needing_followup to find applications due "
        "on a specified date. Ask for a date if none is provided. "
        "Use get_application_details to inspect a specific application. "
        "Ask for its application ID if none is provided; do not guess IDs. "
        "No reminders are sent by these tools."
    ),
    input=question,
    tools=tools,
    parallel_tool_calls=False,
    max_output_tokens=300
)

tool_outputs = []

for item in response.output:
    if item.type != "function_call":
        continue

    arguments = json.loads(item.arguments)

    print("Calling:", item.name)
    print("Arguments:", arguments)

    if item.name == "get_applications_needing_followup":
        results = get_applications_needing_followup(
            as_of_date=arguments["as_of_date"]
        )

    elif item.name == "get_application_details":
        results = get_application_details(
            application_id=arguments["application_id"]
        )

    else:
        raise ValueError(f"Unknown function requested: {item.name}")

    # print("\nDatabase results:")
    # print(json.dumps(results, indent=2))

    tool_outputs.append({
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(results)
    })

if tool_outputs:
    final_response = client.responses.create(
        model="gpt-4.1-mini",
        previous_response_id=response.id,
        instructions=(
            "Answer the user's question using only the returned tool data. "
            "Explain missing requirements, reminder history, or follow-up "
            "dates when relevant. If an application was not found, say so. "
            "A null next_followup_due means the application is complete "
            "under our demo rules. These are fictional records. "
            "No reminders have been sent by this program."
        ),
        input=tool_outputs,
        max_output_tokens=500
    )

    print("\nAssistant:")
    print(final_response.output_text)

else:
    print(response.output_text)

