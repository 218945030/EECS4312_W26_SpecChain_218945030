# EECS4312_W26_SpecChain

Application: [Headspace]

Dataset:
- reviews_raw.jsonl contains the collected reviews.
- reviews_clean.jsonl contains the cleaned dataset.
- The cleaned dataset contains 2572 reviews.

Repository Structure:
- data/ contains datasets and review groups
- personas/ contains persona files
- spec/ contains specifications
- tests/ contains validation tests
- metrics/ contains all metric files
- src/ contains executable Python scripts
- reflection/ contains the final reflection

How to Run:
1. Create Groq api key at https://console.groq.com/keys
2. Paste key into src/run_all.py 
3. Run python script src/run_all.py
4. Open metrics/metrics_summary.json for comparison results

