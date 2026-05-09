#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schemas.vocabulary import Vocabulary

HEADER = "# AUTO-GENERATED from atlas-store/vocabularies/lifecycle_categories.yaml - do not hand-edit"


def generate_payload(vocab: Vocabulary) -> dict:
    values = [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "physical_location": item.physical_location,
        }
        for item in vocab.values
        if not item.deprecated
    ]

    return {
        "vocabulary_id": vocab.id,
        "vocabulary_name": vocab.name,
        "extension_policy": vocab.extension_policy,
        "values": values,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate lifecycle category payload for future knowledge-server integration")
    parser.add_argument("--write", type=Path, default=None, help="optional output file path")
    args = parser.parse_args()

    repo_root = REPO_ROOT
    source_path = repo_root / "vocabularies" / "lifecycle_categories.yaml"

    data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    vocab = Vocabulary.model_validate(data)
    payload = generate_payload(vocab)

    output = f"{HEADER}\n{json.dumps(payload, indent=2, sort_keys=True)}\n"

    print(output, end="")

    if args.write is not None:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(output, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
