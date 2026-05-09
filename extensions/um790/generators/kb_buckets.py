from __future__ import annotations

import json

from schemas.vocabulary import Vocabulary

NAME = "kb_buckets"
INPUTS = ["vocabulary:lifecycle_categories"]
OUTPUTS = ["/opt/stack/services/gdrive-projects/Projects/Current/Atlas/40-OUTPUT/KB Buckets.json"]

HEADER = "# AUTO-GENERATED from atlas-store/vocabularies/lifecycle_categories.yaml - do not hand-edit"


def _generate_payload(vocab: Vocabulary) -> dict:
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


def generate(store: dict) -> dict[str, str]:
    vocab_store = store.get("vocabulary", {})
    vocab = vocab_store.get("lifecycle_categories")
    if not isinstance(vocab, Vocabulary):
        raise ValueError("Missing vocabulary:lifecycle_categories in store")

    payload = _generate_payload(vocab)
    content = f"{HEADER}\n{json.dumps(payload, indent=2, sort_keys=True)}\n"
    return {"-": content}
