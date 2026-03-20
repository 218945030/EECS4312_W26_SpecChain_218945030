"""imports or reads your raw dataset; if you scraped, include scraper here"""
from google_play_scraper import reviews, Sort
import json
from pathlib import Path

app_id = "com.getsomeheadspace.android"
count = 2500

project_root = Path(__file__).resolve().parent.parent
output_file = project_root / "data" / "reviews_raw.jsonl"

app_reviews_list = []
continuation_token = None

while len(app_reviews_list) < count:

    batch_size = min(200, count - len(app_reviews_list))
    result, continuation_token = reviews(
        app_id,
        lang='en',
        country='ca',
        sort=Sort.NEWEST,
        count=batch_size,
        continuation_token=continuation_token
    )
    if not result:
        break

    app_reviews_list.extend(result)

    if continuation_token is None: break

with open(output_file, "w", encoding="utf-8") as f:
    for review in app_reviews_list:
        f.write(json.dumps(review,ensure_ascii=False, default=str) + "\n")
