"""runs the full pipeline end-to-end"""
import subprocess
from pathlib import Path

key = ""

project_root = Path(__file__).resolve().parent.parent
src = project_root / "src" 

#Start of pipeline 
#Validates that all required folders and required files exist
#No files produced 
subprocess.run(["python", src / "00_validate_repo.py"])

#Pipeline Part 1
#Gathers raw review data for Headspace
#Produces file data/reviews_raw.jsonl 
subprocess.run(["python", src / "01_collect_or_import.py"])

#Pipeline Part 2
#Cleans raw review data
#Produces file data/reviews_clean.jsonl 
subprocess.run(["python", src / "02_clean.py"])

#Pipeline Part 3
#Groups reviews from clean data
#Produces file data/review_groups_auto.json 
subprocess.run(["python", src / "04_personas_manual.py", key])

#Pipeline Part 4
#Creates personas based on generated groups
#Produces file personas/personas_auto.json 
subprocess.run(["python", src / "05_personas_auto.py", key])

#Pipeline Part 5
#Creates specifications based on generated personas
#Produces file spec/spec_auto.md 
subprocess.run(["python", src / "06_spec_generate.py", key])

#Pipeline Part 6
#Creates tests based on generated requirements
#Produces file tests/tests_auto.json 
subprocess.run(["python", src / "07_tests_generate.py", key])

#Pipeline Part 7
#Calculates metrics of the automatic pipeline
#Produces file metrics/metrics_auto.json
subprocess.run(["python", src / "08_metrics.py", key])
