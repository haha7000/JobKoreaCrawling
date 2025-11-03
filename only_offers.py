import json
from pathlib import Path


def extract_offer_messages(input_file: str, output_file: str = "output/only_offers.json"):
    """
    Extract position offer messages from JSON file and save as list

    Args:
        input_file: input JSON file path
        output_file: output JSON file path
    """
    # Check input file
    if not Path(input_file).exists():
        print(f"File not found: {input_file}")
        return

    # Load JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total {len(data)} data loaded")

    # Extract offer messages
    offer_messages = []
    for item in data:
        offer_msg = item.get('포지션제안문구')
        if offer_msg:
            offer_messages.append(offer_msg)

    print(f"Extracted {len(offer_messages)} offer messages")

    # Save result
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(offer_messages, f, ensure_ascii=False, indent=2)

    print(f"Saved: {output_file}")

    # Sample output
    if offer_messages:
        print(f"\nSample (first 3):")
        for idx, msg in enumerate(offer_messages[:3], 1):
            preview = msg[:100] if len(msg) > 100 else msg
            print(f"  {idx}. {preview}...")

    return offer_messages


def main():
    input_file = "/Users/gimdonghun/Documents/apiTEst/output/kspac2022_with_offers.json"
    output_file = "output/only_offers.json"

    extract_offer_messages(input_file, output_file)


if __name__ == "__main__":
    main()
