import json

json_files = [
    "db_part1.json",
    "db_part2.json",
    "db_part3.json",
    "db_part4.json",
    "db_part5.json",
    "db_part6.json"
]

merged = []

for file in json_files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict):
            data = list(data.values())
        elif isinstance(data, str):
            data = [{"text": data}]
        elif isinstance(data, list):
            new_data = []
            for entry in data:
                if isinstance(entry, dict):
                    new_data.append(entry)
                else:
                    new_data.append({"text": str(entry)})
            data = new_data
        merged.extend(data)

# ✅ No deduplication → keep all rows
output_path = "fssai_regulations.json"
with open(output_path, "w", encoding="utf-8") as out:
    json.dump(merged, out, indent=2, ensure_ascii=False)

print(f"✅ Merged {len(merged)} entries into {output_path}")
