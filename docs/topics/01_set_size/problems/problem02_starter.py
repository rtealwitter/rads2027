import requests
import math

# Increase samples to get enough collisions
m = 100000
batch_size = 500
titles = []

URL = "https://en.wikipedia.org/w/api.php"
headers = {"User-Agent": "WikiSizeEstimator/1.0"}

print(f"Fetching {m} random URLs (this will take a few minutes)...")

while len(titles) < m:
    params = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnlimit": batch_size,
        "rnnamespace": 0
    }

    try:
        response = requests.get(url=URL, params=params, headers=headers)
        data = response.json()

        if "query" in data:
            for page in data["query"]["random"]:
                titles.append(page['id']) # Use ID, it's safer/faster than title strings
        else:
            print("Retrying...")

    except Exception:
        pass
