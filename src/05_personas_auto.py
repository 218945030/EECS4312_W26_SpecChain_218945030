"""automated persona generation pipeline"""
from groq import Groq
from pathlib import Path
import re
import json

client = Groq(api_key="")

# --- Load JSONL ---
project_root = Path(__file__).resolve().parent.parent
input_file = project_root / "data" / "review_groups_auto.json"
output_file = project_root / "personas" / "personas_auto.json"


with open(input_file, "r", encoding="utf-8") as f:
    group_data = json.load(f)

groups = group_data.get("groups", [])

def get_completion(data, grouping_prompt, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=1):

    prompt = grouping_prompt.format(data=data)

    response = client.chat.completions.create(
        model=model,
        messages=[ {"role": "user", "content": prompt} ],
        temperature=temperature,
        max_completion_tokens=800,
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
Given 5 groups of related review types, create 5 personas that represent users of the reviewed app. 

Output format: 

curly brace
    "personas": [
     curly brace
      "id": "P1",
      "name": ,
      "description": ,
      "goals": [ ],
      "pain_points": [ ],
      "context": [ ],
      "constraints": [ ],
      "evidence_reviews": [ ]
     curly brace
    ]
curly brace

Return ONLY a valid JSON

Rules: 
- Maximum 5 personas 
- Maximum 3 evidence reviews per group 
- No explanations

Groups: 
{data}
"""

personas_raw = get_completion(groups, PROMPT_TEMPLATE)

print(type(personas_raw))
print(personas_raw)

try:
    parsed = extract_json(personas_raw)
except json.JSONDecodeError as e:
    print(e)
    raise

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)
