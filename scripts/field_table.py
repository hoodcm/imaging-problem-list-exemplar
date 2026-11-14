#!/usr/bin/env python3
"""Render the field table from the JSON Schema.

The script walks scripts/spec/observation.schema.json, efl.schema.json, and
ipl.schema.json and writes one row per property to data/derived/field_table.md
and data/derived/field_table.tsv: the element, what it means, its cardinality,
its binding, its FHIR R5 and R6 paths, its DICOM SR concept, and how FHIR
represents it.

Usage: python3 scripts/field_table.py
"""

import csv
import json
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_DIR = os.path.join(PROJECT_DIR, "scripts", "spec")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "data", "derived")
COLUMNS = ["Element", "Meaning", "Cardinality", "Binding", "FHIR R5", "FHIR R6", "DICOM SR", "Representation"]
CODINGS = {"oifm_coding": "OIFM, a Coding", "site_coding": "Anatomic Locations Index 1.0.0, a Coding"}


def binding(node):
    """-> what values a property takes: a value set, a code system, a pattern, or a type."""
    if "$ref" in node:
        name = node["$ref"].rsplit("/", 1)[-1]
        return CODINGS.get(name, f"an {name.removesuffix('.schema.json')}")
    if "enum" in node:
        return ", ".join(str(v) for v in node["enum"])
    if "const" in node:
        return str(node["const"]).lower() if isinstance(node["const"], bool) else node["const"]
    if node.get("type") == "array":
        return "list of " + binding(node["items"])
    if "propertyNames" in node:
        return f"{', '.join(node['propertyNames']['enum'])}, each {node['additionalProperties']['const']}"
    if "pattern" in node:
        return f"text matching {node['pattern']}" + (", or null" if "null" in node.get("type", []) else "")
    if node.get("format") == "date":
        return "date, YYYY-MM-DD"
    kind = node.get("type", "object")
    return " or ".join(kind) if isinstance(kind, list) else kind


def cardinality(node, required):
    low = 1 if required else 0
    if node.get("type") == "array":
        return f"{min(low, node.get('minItems', 0)) if required else 0}..*"
    return f"{low}..1"


def rows(schema_name, node, path, required, out):
    """Append a row for node, then for each property below it."""
    if "x-representation" in node:
        out.append([f"{schema_name}: {path}", node["description"], cardinality(node, required), binding(node),
                    node["x-fhir-r5"], node["x-fhir-r6"], node["x-dicom-sr"], node["x-representation"]])
    body = node.get("items", node) if node.get("type") == "array" else node
    for name, sub in body.get("properties", {}).items():
        rows(schema_name, sub, f"{path}.{name}" if path else name, name in body.get("required", []), out)


def table():
    """-> every schema property as a row, in schema order."""
    out = []
    for schema_name in ("observation", "efl", "ipl"):
        with open(os.path.join(SPEC_DIR, f"{schema_name}.schema.json")) as fh:
            schema = json.load(fh)
        for name, sub in schema.get("$defs", {}).items():
            rows(schema_name, sub, name, True, out)
        rows(schema_name, schema, "", True, out)
    return out


if __name__ == "__main__":
    out = table()
    with open(os.path.join(OUTPUT_DIR, "field_table.tsv"), "w", newline="") as fh:
        csv.writer(fh, delimiter="\t").writerows([COLUMNS] + out)
    cell = lambda v: v.replace("|", "\\|")
    with open(os.path.join(OUTPUT_DIR, "field_table.md"), "w") as fh:
        fh.write("| " + " | ".join(COLUMNS) + " |\n|" + "---|" * len(COLUMNS) + "\n")
        fh.writelines("| " + " | ".join(cell(v) for v in r) + " |\n" for r in out)
    print(f"{len(out)} rows written to {OUTPUT_DIR}/field_table.md and field_table.tsv")
