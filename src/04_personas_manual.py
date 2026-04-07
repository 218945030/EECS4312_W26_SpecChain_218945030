"""automated persona generation pipeline"""
import re
from groq import Groq
import json
from pathlib import Path

client = Groq(api_key="")

# --- Load JSONL ---
project_root = Path(__file__).resolve().parent.parent
input_file = project_root / "data" / "reviews_clean.jsonl"
output_file = project_root / "data" / "review_groups_auto.json"

clean_data = []
with open(input_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        try:
            clean_data.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Error on line {i}: {e}")

def format_reviews(data):
    return "\n".join(
        f"{r['reviewId']}: {r['content'][:120]}"
        for r in data
    )

def split_data(data, size=25):

    for i in range (0, len(data), size):
        yield data[i:i + size]

def compress_review(review):

    return {
        "reviewId": review["reviewId"],
        "content": review["content"]
    }

def extract_json(text):
    if not text or not text.strip():
        raise ValueError("Empty response from model")

    # Extract first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response")

    json_str = match.group()

    return json.loads(json_str)

def get_completion(data, grouping_prompt, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0):

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

PROMPT_TEMPLATE = """
Group these by theme.

The response MUST start with '[' and end with ']'.

Output format: 
[
    curly brace 
      "group_id": "G1",
      "theme": ,
      "review_ids": [],
      "example_reviews": []
    curly brace
]

Return ONLY valid JSON

Rules: 
- Max 5 groups
- Max 3 examples per group 
- No explanations

Reviews: 
{data}
"""

MERGE_PROMPT = """
Please take this list of review groups and combine similar ones in order to reduce the amount to around 5 - 10.

Return the result as a json list of groups in the same format

Here are the list of groups to combine:
{data}
"""

result = []

for split in split_data(clean_data, 25):
    compressed_split = [compress_review(r) for r in split]
    format_split = format_reviews(compressed_split)
    response = get_completion(format_split, PROMPT_TEMPLATE)
    parsed = extract_json(response)
    result.append(parsed)
    print(response)

final_groups = get_completion(result, MERGE_PROMPT)

print(type(final_groups))
print(final_groups)

try:
    parsed = extract_json(final_groups)
except json.JSONDecodeError as e:
    print(e)
    raise

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)te(json.dumps(record, ensure_ascii=False) + "\n")
