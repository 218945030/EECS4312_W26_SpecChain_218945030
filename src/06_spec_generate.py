"""generates structured specs from personas"""
from groq import Groq
from pathlib import Path
import json
import sys

client = Groq(api_key=sys.argv[1])

# --- Load JSONL ---
project_root = Path(__file__).resolve().parent.parent
input_file = project_root / "personas" / "personas_auto.json"
output_file = project_root / "spec" / "spec_auto.md"


with open(input_file, "r", encoding="utf-8") as f:
    persona_data = json.load(f)

personas = persona_data.get("personas", [])

def get_completion(data, grouping_prompt, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=1):

    prompt = grouping_prompt.format(data=data)

    response = client.chat.completions.create(
        model=model,
        messages=[ {"role": "user", "content": prompt} ],
        temperature=temperature,
        max_completion_tokens=1024,
        top_p=1,
        stop=None
    )
    return response.choices[0].message.content

PROMPT_TEMPLATE = """ 
Given 5 personas, I need to create structured system requirements.

Example output: 
# Requirement ID: FR_auto_1
- Description: [The system shall allow users to log workouts without application crashes.]

- Source Persona: [Active Fitness Tracker]
- Traceability: [Derived from review group A1]
- Acceptance Criteria:[Given the user logs a workout, When the logging process completes, Then the application must remain stable, and the workout must be saved successfully.]

Output should be formated for a .md file

Rules: 
- Maximum 10 requirements 
- Each persona must create 2 requirements 
- No explanations

Personas:
{data}
"""

requirements = get_completion(personas, PROMPT_TEMPLATE)

print(type(requirements))
print(requirements)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(requirements)
