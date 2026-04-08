"""generates tests from specs"""
import re
from groq import Groq
from pathlib import Path
import json
import sys

client = Groq(api_key=sys.argv[1])

# --- Load JSONL ---
project_root = Path(__file__).resolve().parent.parent
input_file = project_root / "spec" / "spec_auto.md"
output_file = project_root / "tests" / "tests_auto.json"

requirements = []
with open(input_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        requirements.append(line)

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

def extract_json(text):
    if not text or not text.strip():
        raise ValueError("Empty response from model")

    # Extract first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response")

    json_str = match.group()

    return json.loads(json_str)

PROMPT_TEMPLATE = """ 
Given 10 requirements, create validation tests for the system.

Example output in JSON form: 
curly brace
  "tests": [
    curly brace
      "test_id": "T_auto_1",
      "requirement_id": "FR_auto_1",
      "scenario": "Logging a workout without crashing",
      "steps": [
        "Open the workout logging screen",
        "Enter workout details",
        "Submit the workout"
      ],
      "expected_result": "The workout is saved successfully and the application remains stable."
    curly brace
  ]
curly brace

Return ONLY a valid JSON

Rules: 
- Each requirement must link to at least one test
- Every test references a requirement ID
- The expected result must reflect the requirement being validated
- No explanations


Personas:
{data}
"""

tests = get_completion(requirements, PROMPT_TEMPLATE)

print(type(tests))
print(tests)

try:
    parsed = extract_json(tests)
except json.JSONDecodeError as e:
    print(e)
    raise

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)
