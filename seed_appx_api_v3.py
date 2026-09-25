# STEP 1: Pehle is poori cell ko ek Colab cell me paste karke run karo.
# Ye tumse ek file select karne ko kahega — us waqt "appxapis.json" file select karo
# (jo neeche di gayi hai, use pehle apne phone me download kar lo).

# Cell 1 me ye run karo pehle:
# !pip install motor pymongo -q

from google.colab import files
import json
import asyncio
import motor.motor_asyncio
from pymongo import UpdateOne

DB_URL = "mongodb+srv://alexkrishna:alex6387901aspTHaap@cluster0.icuhraj.mongodb.net/?appName=Cluster0"
DB_NAME = "APPX_API"
COLLECTION_NAME = "appx_api"

print("Ab appxapis.json file select karo jo upload hui hai...")
uploaded = files.upload()

filename = list(uploaded.keys())[0]
with open(filename, 'r', encoding='utf-8') as f:
    APPS_DATA = json.load(f)

print(f"Loaded {len(APPS_DATA)} apps from {filename}")

async def upload_apis():
    client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f"Connected. Uploading {len(APPS_DATA)} apps...")

    operations = []
    for item in APPS_DATA:
        name = item.get("name")
        api = item.get("api")
        if name and api:
            operations.append(
                UpdateOne(
                    {"api": api},
                    {"$set": {"name": name, "api": api}},
                    upsert=True
                )
            )

    if operations:
        BATCH_SIZE = 200
        total_upserted = 0
        total_modified = 0
        total_matched = 0
        for i in range(0, len(operations), BATCH_SIZE):
            chunk = operations[i:i + BATCH_SIZE]
            result = await collection.bulk_write(chunk)
            total_upserted += result.upserted_count
            total_modified += result.modified_count
            total_matched += result.matched_count
            print(f"Batch {i // BATCH_SIZE + 1}: uploaded {i + len(chunk)}/{len(operations)}")
        print("-" * 30)
        print(f"Inserted (New): {total_upserted}")
        print(f"Modified (Updated): {total_modified}")
        print(f"Matched (Existing): {total_matched}")
        count = await collection.count_documents({})
        print(f"Total documents in collection now: {count}")
        print("-" * 30)
        print("DONE! Ab bot me 'Add Batch' try karo.")
    else:
        print("No valid data found.")

await upload_apis()
