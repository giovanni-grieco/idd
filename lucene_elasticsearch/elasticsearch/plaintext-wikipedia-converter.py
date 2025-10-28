import json
import argparse
import pathlib





def main(import_path: str, export_path: str):
    print(f"Importing from {import_path} and exporting to {export_path}")
    # Move in import path
    # List all current files
    # for each file, parse file and create new plain text single file and save file in export path
    import_dir = pathlib.Path(import_path)
    export_dir = pathlib.Path(export_path)
    export_dir.mkdir(parents=True, exist_ok=True)
    for file_path in import_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for entry in data:
            title = entry.get("title", "untitled").replace("/", "_")
            text = entry.get("text", "")
            id = entry.get("id", "unknown")
            output_file_path = export_dir / f"{title}.txt"
            with open(output_file_path, "w", encoding="utf-8") as out_f:
                out_f.write(text)
        print(f"Processed file: {file_path.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Wikipedia plaintext dump to JSONL format.")
    parser.add_argument("--import_path", type=str, required=True, help="Path to the input folder where all the JSON Wikipedia files are located.")
    parser.add_argument("--export_path", type=str, required=True, help="Path to the output folder where all the single files will be created.")
    args = parser.parse_args()
    main(args.import_path, args.export_path)