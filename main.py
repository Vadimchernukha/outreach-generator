"""
╔══════════════════════════════════════════════════════════╗
║         AI Cold Outreach Generator                      ║
║         Powered by Google Gemini 3.1 Pro                ║
╚══════════════════════════════════════════════════════════╝

USAGE:
  python main.py --client lionwood --input contacts.csv

  --client   Name of config file in clients/ folder (without .yaml)
  --input    Path to your CSV file
  --output   Output CSV path (default: results_{client}.csv)
  --delay    Seconds between API calls (default: 4)

SETUP:
  1. pip install google-generativeai pandas pyyaml openpyxl
  2. Copy .env.example to .env and add your Gemini API key
  3. Create/edit your client config in clients/
  4. Run!
"""

import os
import sys
import time
import argparse
import yaml
import google.generativeai as genai
from datetime import datetime

from core.csv_handler import load_contacts, get_field, build_dynamic_text, save_results, flatten_result
from core.generator  import generate_chain
from core.humanizer  import humanize


# ─── Load API key ────────────────────────────────────
def get_api_key() -> str:
    # Try .env file first
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY"):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    # Fallback to environment variable
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        print("ERROR: GEMINI_API_KEY not found.")
        print("  Option 1: Add to .env file:  GEMINI_API_KEY=your_key")
        print("  Option 2: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    return key


# ─── Load client config ──────────────────────────────
def load_config(client_name: str) -> dict:
    path = os.path.join(os.path.dirname(__file__), "clients", f"{client_name}.yaml")
    if not os.path.exists(path):
        print(f"ERROR: Client config not found: {path}")
        available = [f.replace(".yaml","") for f in os.listdir("clients") if f.endswith(".yaml")]
        print(f"Available clients: {available}")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─── Process single contact ──────────────────────────
def process_contact(model, row, dynamic_cols: list, config: dict, delay: float) -> dict:
    csv_mapping = config.get("csv_mapping", {})
    language    = config.get("language", "english")

    contact = {
        "person_name":    get_field(row, "person_name",    csv_mapping),
        "title":          get_field(row, "title",          csv_mapping),
        "company_name":   get_field(row, "company_name",   csv_mapping),
        "website":        get_field(row, "website",        csv_mapping),
        "industry":       get_field(row, "industry",       csv_mapping),
        "company_size":   get_field(row, "company_size",   csv_mapping),
        "company_country":get_field(row, "company_country",csv_mapping),
        "company_city":   get_field(row, "company_city",   csv_mapping),
        "dynamic_fields": build_dynamic_text(row, dynamic_cols),
    }

    print(f"  -> {contact['person_name']} | {contact['title']} @ {contact['company_name']}")

    # Step 1: Generate raw chain
    try:
        chain = generate_chain(model, contact, config)
    except Exception as e:
        print(f"     ERROR generating: {e}")
        return {"error": str(e), "messages": []}

    time.sleep(delay)

    # Step 2: Humanize each message
    humanized_messages = []
    for msg in chain.get("messages", []):
        step = msg.get("step", "?")
        print(f"     Humanizing message {step}...")
        try:
            human_text = humanize(model, msg["text"], language)
        except Exception as e:
            print(f"     ERROR humanizing step {step}: {e}")
            human_text = msg["text"]

        humanized_messages.append({
            "step":           msg.get("step", ""),
            "send_after":     msg.get("send_after", ""),
            "angle":          msg.get("angle", ""),
            "original_text":  msg.get("text", ""),
            "humanized_text": human_text,
        })
        time.sleep(delay / 2)

    return {
        "strategy_rationale": chain.get("strategy_rationale", ""),
        "messages": humanized_messages,
    }


# ─── Main ────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True,  help="Client name (matches clients/NAME.yaml)")
    parser.add_argument("--input",  required=True,  help="Path to input CSV")
    parser.add_argument("--output", default=None,   help="Path to output CSV")
    parser.add_argument("--delay",  type=float, default=4.0)
    args = parser.parse_args()

    output_path = args.output or f"results_{args.client}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    print("=" * 60)
    print(f"  OUTREACH GENERATOR  |  Client: {args.client}")
    print("=" * 60)

    # Load config + init Gemini
    config = load_config(args.client)
    print(f"  Company: {config.get('company_name')}")
    print(f"  Language: {config.get('language', 'english')}")

    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.1-pro-preview")
    print(f"  Model: Gemini 3.1 Pro Preview\n")

    # Load contacts
    df, dynamic_cols = load_contacts(args.input, config)

    # Process
    all_rows = []
    total = len(df)

    for idx, row in df.iterrows():
        print(f"\n[{idx + 1}/{total}]")
        result  = process_contact(model, row, dynamic_cols, config, args.delay)
        rows    = flatten_result(row, result, config.get("csv_mapping", {}))
        all_rows.extend(rows)
        print(f"     Done: {len(result.get('messages', []))} messages")
        time.sleep(args.delay)

    save_results(all_rows, output_path)

    print("=" * 60)
    print(f"  Contacts processed : {total}")
    print(f"  Total message rows : {len(all_rows)}")
    print(f"  Output file        : {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
