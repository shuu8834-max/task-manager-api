import json
import urllib.request

url = "http://localhost:8080/api/tasks"

tasks_to_add = [
    {"title": "Complete Flask REST API training"},
    {"title": "Build a portfolio website"},
    {"title": "Practice SQL queries daily"},
]

print("🚀 Starting database population...")

for task in tasks_to_add:
    json_data = json.dumps(task).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            print(f"✅ Successfully added: '{task['title']}'")
    except Exception as e:
        print(f"❌ Error adding '{task['title']}': {e}")

print("\n🎉 Done! Refresh your browser to see the data.")

