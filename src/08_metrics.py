"""computes metrics: coverage/traceability/ambiguity/testability"""
import re
from groq import Groq
from pathlib import Path
import json

client = Groq(api_key="")

# --- Load JSONL ---
project_root = Path(__file__).resolve().parent.parent
reviews_file = project_root / "data" / "reviews_clean.jsonl"
groups_file = project_root / "data" / "review_groups_auto.json"
personas_file = project_root / "personas" / "personas_auto.json"
requirements_file = project_root / "spec" / "spec_auto.md"
tests_file = project_root / "tests" / "tests_auto.json"
output_file = project_root / "metrics" / "metrics_auto.json"

def read_file(input_file):
    file_data = []
    with open(input_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            file_data.append(line)
    return file_data

def read_json(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)

def read_reviews(input_file):
    file_data = []
    with open(input_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            try:
                file_data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error on line {i}: {e}")
    return file_data

def extract_json(text):
    if not text or not text.strip():
        raise ValueError("Empty response from model")

    # Extract first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response")

    json_str = match.group()

    return json.loads(json_str)

def split_data(data, size=50):

    for i in range (0, len(data), size):
        yield data[i:i + size]

def compress_review(review):

    return {
        "reviewId": review["reviewId"],
        "content": review["content"]
    }

def format_reviews(data):
    return [r["content"][:80] for r in data]

def get_completion(dataset, personas, requirements, tests, grouping_prompt):

    prompt = grouping_prompt.format(dataset=dataset, personas=personas, requirements=requirements, tests=tests)

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[ {"role": "user", "content": prompt} ],
        temperature=0,
        max_completion_tokens=400,
        top_p=1,
        stop=None
    )
    return response.choices[0].message.content

PROMPT_TEMPLATE = """ 
Compute metrics based on the given data

Output format: 
curly brace
  "pipeline": "automated",
  "dataset_size": Number of reviews in Dataset,
  "persona_count": Number of personas in Personas,
  "requirements_count": Number of requirements in Requirements,
  "tests_count": Number of tests in Tests,
  "traceability_links": The number of explicit traceable relationships between artifacts in the pipeline,
  "review_coverage": The ratio (0-1) of reviews that have been covered by the personas generated ,
  "traceability_ratio": The proportion of requirements that can be traced back to a persona through an explicit reference in the specification ,
  "testability_rate": The proportion of requirements that have at least one associated validation test scenario, 
  "ambiguity_ratio": The proportion of requirements whose descriptions or acceptance criteria contain ambiguous or non-measurable language (e.g., vague terms such as fast, easy, better, user-friendly, etc.) that lead to multiple interpretations during testing.
curly brace

Return ONLY a valid JSON

NO explanations

Dataset: {dataset}
Personas: {personas}
Requirements: {requirements}
Tests: {tests}
"""

MERGE_PROMPT = """
Given the list of metrics, please combine and compute the finalized metrics for the entire dataset.

Output format: 
curly brace
  "pipeline": "automated",
  "dataset_size": Sum of dataset sizes across all Metrics
  "persona_count": Average number of personas across Metrics,
  "requirements_count": Average number of requirements across Metrics,
  "tests_count": Average number of tests across Metrics,
  "traceability_links": Sun of all traceability links in all Metrics,
  "review_coverage": Average of all review coverage ratios (0 - 1) ,
  "traceability_ratio": Average of all traceability ratios (0 - 1),
  "testability_rate": Average of all testability rates (0 - 1), 
  "ambiguity_ratio": Average of all of ambiguity ratios (0 - 1)
curly brace

Only return a valid JSON 

NO explanations

Metrics: {dataset}
"""

reviews = read_reviews(reviews_file)
groups = read_json(groups_file)
personas = read_json(personas_file)
requirements = read_file(requirements_file)
tests = read_json(tests_file)

metric = []
for split in split_data(reviews, 50):
    compressed_split = [compress_review(r) for r in split]
    format_split = format_reviews(compressed_split)
    response = get_completion(json.dumps(format_split, separators=(",", ":")), personas, requirements, tests, PROMPT_TEMPLATE)
    parsed = extract_json(response)
    metric.append(parsed)
    print(response)

metric_final = get_completion(json.dumps(metric, separators=(",", ":")), personas, requirements, tests, MERGE_PROMPT)

print(type(metric_final))
print(metric_final)

try:
    parsed = extract_json(metric_final)
except json.JSONDecodeError as e:
    print(e)
    raise

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)
