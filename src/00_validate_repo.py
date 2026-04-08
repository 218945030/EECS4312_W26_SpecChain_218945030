"""checks required files/folders exist"""
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

print("Checking repository structure...")

data = ["dataset_metadata.json", "review_groups_auto.json", "review_groups_hybrid.json", "review_groups_manual.json", "reviews_clean.jsonl", "reviews_raw.jsonl"]
if (project_root / "data").exists(): 
    print("data found")
    for i in range(len(data)): 
        if (project_root / "data" / data[i]).exists:
            print("data/" + data[i] + " found") 


metrics = ["metrics_auto.json", "metrics_hybrid.json", "metrics_manual.json", "metrics_summary.json"]
if (project_root / "metrics").exists(): 
    print("metircs found")
    for i in range(len(metrics)): 
        if (project_root / "metircs" / metrics[i]).exists:
            print("metrics/" + metrics[i] + " found") 

personas = ["personas_auto.json", "personas_hybrid.json", "personas_manual.json"]
if (project_root / "personas").exists(): 
    print("personas found")
    for i in range(len(personas)): 
        if (project_root / "personas" / personas[i]).exists:
            print("personas/"  + personas[i] + " found") 

spec = ["spec_auto.json", "spec_hybrid.json", "spec_manual.json"]
if (project_root / "spec").exists(): 
    print("spec found")
    for i in range(len(spec)): 
        if (project_root / "spec" / spec[i]).exists:
            print("spec/"  + spec[i] + " found") 

tests = ["tests_auto.json", "tests_hybrid.json", "tests_manual.json"]
if (project_root / "tests").exists(): 
    print("tests found")
    for i in range(len(tests)): 
        if (project_root / "tests" / tests[i]).exists:
            print("tests/"  + tests[i] + " found") 

print("Repository validation complete")
