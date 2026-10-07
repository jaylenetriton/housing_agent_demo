from openai import OpenAI

# Automatically reads OPENAI_API_KEY from your environment.
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Reply with one short sentence confirming you are ready to help with a housing demo.",
    max_output_tokens=100,
)

print(response.output_text)