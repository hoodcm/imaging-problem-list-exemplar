#!/usr/bin/env python3
"""Build the exemplar's Exam Finding Lists and Imaging Problem List.

The script reads what the reports say from exemplar.py and writes one Exam
Finding List per examination to data/derived/efls/ and the Imaging Problem List
to data/derived/imaging_problem_list.json. The rules that group observations
into entries and derive each entry's status are all in this file, so an entry's
status can be traced from its observations here: stated_values() and
contradiction() compare an observation with the entry's last stated values,
derive_status() walks the observations in order, and close_negations() closes an
entry of only absences.

Usage: python3 scripts/build_exemplar.py
"""

import json
import os
import re
import sys
import uuid
from collections import defaultdict
from functools import cache

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from exemplar import (CONCEPT_DISPLAY, CONCEPTS, PROCEDURE_CODES, SITE_DISPLAY, SPECTRA, exam_map, examination_statements, exams,
                      findings, patient)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "data", "derived")
EFL_DIR = os.path.join(OUTPUT_DIR, "efls")
SPEC_DIR = os.path.join(PROJECT_DIR, "scripts", "spec")
ANATOMIC_LOCATIONS = os.path.join(PROJECT_DIR, "data", "raw", "anatomic_locations",
                                  "anatomic-locations-1.0.0.json")

# The date the record was compiled, fixed so a rebuild reproduces its output.
COMPILED_DATE = "2026-11-13"

# The version of the JSON Schema in scripts/spec/ that the files follow.
SCHEMA_VERSION = "1.0.0"

# Tracking UIDs are DICOM UIDs under the 2.25 root, derived from a UUID per
# entry, so the same entry gets the same UID on every build.
UID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/hoodcm/imaging-problem-list-exemplar")

def procedure_code(exam):
    """-> the LOINC coding of an examination's procedure."""
    code, display = PROCEDURE_CODES[exam["type"]]
    return {"system": "LOINC", "code": code, "display": display}


def report_id(exam_id):
    """-> the identifier of an examination's report."""
    return f"{patient['id']}-{exam_id}"


def concept_code(name):
    """-> the OIFM coding of a concept, with the source of its code."""
    c = CONCEPTS[name]
    return {"system": "OIFM", "code": c["oifm"], "display": CONCEPT_DISPLAY.get(name, name.replace("_", " ")), "source": c["source"]}


def on_one_path(a, b):
    """True when one concept is the other or an ancestor of it."""
    return a == b or a in CONCEPTS[b]["path"] or b in CONCEPTS[a]["path"]


def same_spectrum(a, b):
    """True when two concepts name one finding at different severities."""
    return any(a in sp and b in sp for sp in SPECTRA)


CODE_CONCEPT = {c["oifm"]: name for name, c in CONCEPTS.items()}
exam_order = {e["id"]: i for i, e in enumerate(exams)}

# ============================================================
# Anatomic sites
# ============================================================

with open(ANATOMIC_LOCATIONS) as fh:
    _al = json.load(fh)
assert _al["$version"] == "1.0.0", _al["$version"]
AL = {b["radlexId"]: b for b in _al["bodyParts"]}


def site(radlex_id):
    """-> the Anatomic Locations Index coding of a site, with its SNOMED CT code."""
    b = AL[radlex_id]
    snomed = next((c["code"] for c in b.get("codes", []) if c["system"] == "SNOMED"), None)
    return {"system": "Anatomic Locations Index 1.0.0", "code": radlex_id,
            "display": SITE_DISPLAY.get(radlex_id, b["description"]), "snomed": snomed}


def site_within(inner, outer):
    """True when outer is inner or contains it by the index's containment or part-of links."""
    seen, todo = set(), [inner]
    while todo:
        r = todo.pop()
        if r == outer:
            return True
        if r in seen or r not in AL:
            continue
        seen.add(r)
        todo += [AL[r].get("containedById"), AL[r].get("partOfId"), AL[r].get("unsidedId")]
    return False


# ============================================================
# Structured observations
# ============================================================

def as_list(v):
    """-> v as a list, empty for None."""
    if v is None:
        return []
    return list(v) if isinstance(v, (list, tuple)) else [v]


def measurement_record(t):
    """-> a stated measurement as value, unit, and, where the sentence states it, what it measures."""
    value, unit = t[0], t[1]
    rec = {"value": value, "unit": unit}
    if len(t) > 2:
        rec["measured_quantity"] = t[2]
    return rec


def interpretation_record(i):
    """-> an interpretation as a coded concept, with its hedge."""
    name, hedged = (i, False) if isinstance(i, str) else (i[0], i[1] == "hedged")
    rec = {"code": concept_code(name)}
    if hedged:
        rec["hedged"] = True
    return rec


def attributes(o):
    """The annotator's attribute model, omitting what the sentence does not state."""
    a = {"presence": o["presence"]}
    if o.get("hedged"):
        a["certainty"] = {axis: "hedged" for axis in o["hedged"]}
    for key in ("laterality", "severity"):
        if o.get(key):
            a[key] = o[key]
    if o.get("temporal"):
        a["temporal_status"] = as_list(o["temporal"])
    if o.get("chronicity"):
        a["chronicity"] = as_list(o["chronicity"])
    if o.get("measurement"):
        a["measurement"] = [measurement_record(t) for t in o["measurement"]]
    if o.get("prior_measurement"):
        a["prior_measurement"] = [measurement_record(t) for t in o["prior_measurement"]]
    if o.get("multiple"):
        a["multiple"] = True
    if o.get("features"):
        a["features"] = list(o["features"])
    if o.get("context"):
        causes = [c if isinstance(c, tuple) else (c, None) for c in o["context"]]
        a["clinical_context"] = [concept_code(name) for name, _ in causes]
        if any(h == "hedged" for _, h in causes):
            a.setdefault("certainty", {})["clinical_context"] = "hedged"
    return a

# ============================================================
# Entry status
# ============================================================
# The rules classify what the radiologist stated about the finding. The
# radiologist's comparison wording sets the status. Without it, a stated
# attribute that contradicts that attribute's last stated value for the entry is
# a change. A first observation takes its status from the age the radiologist
# stated. Hedging records doubt about a statement, not a change in the finding,
# so it never sets the status. Each rule has a short key the status decision
# table cites.

CHANGE_WORDS = {"new", "resolved", "increased", "decreased"}
NO_CHANGE_WORDS = {"unchanged"}

# The stage each stated time-course word names, the annotator's chronicity
# values. A step between any two of the four stages contradicts.
TIME_COURSE_STAGES = {"acute": "acute", "subacute": "subacute",
                      "evolving": "evolving", "healing": "evolving", "resolving": "evolving",
                      "chronic": "old", "remote": "old", "healed": "old"}
# Time-course words that state the finding predates the examination.
STATED_OLD = {w for w, stage in TIME_COURSE_STAGES.items() if stage == "old"}

# Reports give sizes to the nearest millimetre, so lengths 1 mm apart or closer
# do not contradict. Another measurement compares only
# with one in the same unit of the same measured quantity, and contradicts when the two
# differ by more than one step of the coarser stated digit.
SIZE_PRECISION_MM = 1.0
MM_PER_UNIT = {"mm": 1.0, "cm": 10.0}  # a fixed fact of the units

# Grade words on one ordinal scale of four severity bands. The model records
# every grade word, a severity or a size word, as severity. A value naming a
# range covers the whole span, and two grades contradict only when their spans
# are disjoint.
GRADE_BANDS = {"small": {1}, "mild": {2}, "mild_to_moderate": {2, 3}, "moderate": {3},
               "moderate_to_severe": {3, 4}, "severe": {4}, "large": {4}}

# Descriptors that cannot describe one finding at once, in declared sets. Two
# descriptions contradict when each names exactly one member
# of a set and the members differ. A plain member's pattern refuses the
# prefixes that make it another member, hyphenated or spaced, so "part solid"
# and "non occlusive" name one member each.
DESCRIPTOR_SETS = [
    ("nodule composition", {"solid": r"(?<![-\w])(?<!part )(?<!semi )(?<!non )solid\b", "part-solid": r"\bpart[- ]?solid\b|\bsemi[- ]?solid\b",
                            "ground-glass": r"\bground[- ]?glass\b|\bnon[- ]?solid\b"}),
    ("shape", {"round or oval": r"\bround\b|\boval\b", "irregular": r"\birregular\b"}),
    ("margin", {"smooth": r"\bsmooth\b|\bwell[- ]circumscribed\b", "lobulated": r"\blobulated\b",
                "irregular or spiculated": r"\birregular\b|\bspiculated\b"}),
    ("calcification", {"calcified": r"(?<![-\w])(?<!non )calcified\b", "noncalcified": r"\bnon[- ]?calcified\b"}),
    ("occlusion", {"occlusive": r"(?<![-\w])(?<!non )occlu(?:sive|ding)\b", "nonocclusive": r"\bnon[- ]?occlusive\b"}),
    ("zone", {"upper": r"\bupper(?: lobe| lung| zone)?[- ]predominan",
              "lower": r"\b(?:lower(?: lobe| lung| zone)?|basilar|basal)[- ]predominan"}),
    ("number", {"one": r"\b(?:single|solitary)\b", "several": r"\b(?:multiple|several|numerous|innumerable)\b"}),
]

STATUS_RULES = {
    "absent-never-present": ("excluded", "The report states an absence, and no earlier report stated the finding present."),
    "absent-after-present": ("resolved", "The report states an absence after an earlier presence."),
    "absent-after-resolved": ("resolved", "The report states an absence after the entry has resolved."),
    "stated-new": ("active", "The radiologist reported the finding new."),
    "stated-change": ("active", "The radiologist stated a change."),
    "stated-unchanged": ("stable", "The radiologist stated no change."),
    "first-stated-old": ("stable", "The radiologist stated the finding chronic, remote, or healed at its first observation or when present after an absence."),
    "first-observation": ("active", "The radiologist reported the finding for the first time, with no comparison wording and no stated age that predates the examination."),
    "present-after-absence": ("active", "The radiologist reported the finding present after an absence, including a recurrence after resolution, with no comparison wording and no stated age that predates the examination."),
    "attribute-contradicts": ("active", "The radiologist wrote no comparison wording, and a stated attribute contradicts its last stated value."),
    "nothing-contradicts": ("stable", "The radiologist wrote no comparison wording, and no stated attribute contradicts its last stated value."),
    "closed-by-subsequent-finding": ("closed", "The entry holds only absences, and a radiologist reported a finding of its type present within "
                                           "its site after the last absence, so that finding's entry carries the status."),
}


def _lengths_mm(a):
    """-> {measured quantity: sorted lengths in mm}, so lengths of different quantities never compare."""
    lengths = defaultdict(list)
    for s in a.get("measurement", []):
        if s["unit"] in MM_PER_UNIT:
            lengths[s.get("measured_quantity")].append(s["value"] * MM_PER_UNIT[s["unit"]])
    return {prop: tuple(sorted(v)) for prop, v in lengths.items()}


def _stated_step(value):
    """-> one step of the last digit the value was stated to, 1 for 20 and 0.1 for 1.2."""
    text = repr(value)
    return 10.0 ** -len(text.split(".")[1]) if "." in text else 1.0


def _grade_band(a):
    return GRADE_BANDS.get(a.get("severity"), set())


def _descriptor_conflict(now, was):
    for name, members in DESCRIPTOR_SETS:
        ma = {m for m, pat in members.items() if re.search(pat, now, re.IGNORECASE)}
        mb = {m for m, pat in members.items() if re.search(pat, was, re.IGNORECASE)}
        if len(ma) == 1 and len(mb) == 1 and ma != mb:
            return name
    return None


def stated_values(o):
    """The attribute values an observation states, in the form the contradiction check compares."""
    a = o["attributes"]
    vals = {"code": o["finding_code"]["code"]}
    for prop, lengths in _lengths_mm(a).items():
        vals[("size", prop)] = lengths
    for s in a.get("measurement", []):
        if s["unit"] not in MM_PER_UNIT:
            vals[("measure", s["unit"], s.get("measured_quantity"))] = (s["value"], _stated_step(s["value"]))
    if _grade_band(a):
        vals["grade"] = _grade_band(a)
    if a.get("features"):
        vals["features"] = ", ".join(a["features"])
    if a.get("chronicity"):
        vals["stage"] = {TIME_COURSE_STAGES[w] for w in a["chronicity"]}
    return vals


def contradiction(now, carried):
    """-> the first attribute whose stated value contradicts its last stated value, or None.

    Only an attribute stated on both sides can contradict, since a dropped
    attribute is silence and an added one is new information.
    """
    if now["code"] != carried["code"] and same_spectrum(CODE_CONCEPT[now["code"]], CODE_CONCEPT[carried["code"]]):
        return "a step between codes on one severity spectrum"
    if "features" in now and "features" in carried:
        conflict = _descriptor_conflict(now["features"], carried["features"])
        if conflict:
            return conflict
    if "stage" in now and "stage" in carried and not (now["stage"] & carried["stage"]):
        return "time-course stage"
    if "grade" in now and "grade" in carried and not (now["grade"] & carried["grade"]):
        return "grade"
    shared = [k for k in now if isinstance(k, tuple) and k in carried]
    for key in [k for k in shared if k[0] == "measure"]:
        (x, step_x), (y, step_y) = now[key], carried[key]
        if round(abs(x - y), 6) > max(step_x, step_y):
            return f"{key[2] or 'measurement'} in {key[1]}"
    for key in [k for k in shared if k[0] == "size"]:
        a, b = now[key], carried[key]
        pairs = zip(a, b) if len(a) == len(b) else [(max(a), max(b))]
        if any(round(abs(x - y), 1) > SIZE_PRECISION_MM for x, y in pairs):
            return "size" if key[1] is None else f"size, {key[1]}"
    return None


def _same_measurement(a, b):
    """True when two comparable measurements agree within the tolerance the contradiction rule uses."""
    if a["unit"] in MM_PER_UNIT and b["unit"] in MM_PER_UNIT:
        diff = abs(a["value"] * MM_PER_UNIT[a["unit"]] - b["value"] * MM_PER_UNIT[b["unit"]])
        return round(diff, 1) <= SIZE_PRECISION_MM
    return round(abs(a["value"] - b["value"]), 6) <= max(_stated_step(a["value"]), _stated_step(b["value"]))


def _comparable(a, b):
    return a.get("measured_quantity") == b.get("measured_quantity") and (
        a["unit"] == b["unit"] or {a["unit"], b["unit"]} <= set(MM_PER_UNIT))


def prior_measurement_check(o, previous):
    """-> how the prior measurement an observation states compares with the entry's previous observation.

    "matches" when each stated prior value agrees with a measurement the
    previous observation records, within the tolerance contradiction() uses, "differs" when one doesn't, and "no-prior" when the
    previous observation records nothing to compare it with. The result is
    written on the record for review and never sets the status, since the
    record makes no clinical determination.
    """
    earlier = previous["attributes"].get("measurement", []) if previous else []
    results = []
    for stated in o["attributes"]["prior_measurement"]:
        candidates = [e for e in earlier if _comparable(stated, e)]
        results.append("no-prior" if not candidates
                       else "matches" if any(_same_measurement(stated, e) for e in candidates) else "differs")
    return "differs" if "differs" in results else "no-prior" if "no-prior" in results else "matches"


def derive_status(entry_observations):
    """Walk the observations in order and set each one's derived status.

    An observation a radiologist rejected stays in the history and sets no
    status, so the entry derives from the observations around it.

    Returns:
        The entry's status and the rule that set it.
    """
    status, rule, carried, previous = None, None, None, None
    for o in entry_observations:
        if rejected(o):
            o.pop("derived", None)
            continue
        a = o["attributes"]
        words = set(a.get("temporal_status", []))
        contra = None
        if a["presence"] == "absent":
            rule = {None: "absent-never-present", "excluded": "absent-never-present",
                    "resolved": "absent-after-resolved"}.get(status, "absent-after-present")
            carried = None
        else:
            now = stated_values(o)
            if "new" in words:
                rule = "stated-new"
            elif words & CHANGE_WORDS:
                rule = "stated-change"
            elif words & NO_CHANGE_WORDS:
                rule = "stated-unchanged"
            elif carried is None:
                if set(a.get("chronicity", [])) & STATED_OLD:
                    rule = "first-stated-old"
                else:
                    rule = "first-observation" if status is None else "present-after-absence"
            else:
                contra = contradiction(now, carried)
                rule = "attribute-contradicts" if contra else "nothing-contradicts"
            carried = {**(carried or {}), **now}
        status = STATUS_RULES[rule][0]
        o["derived"] = {"status": status, "rule": rule}
        if contra:
            o["derived"]["contradicting_attribute"] = contra
        if a.get("prior_measurement"):
            o["derived"]["prior_measurement_check"] = prior_measurement_check(o, previous)
        previous = o
    return status, rule

def rejected(o):
    """True when a radiologist rejected the observation, so it sets no status."""
    return o["provenance"]["review_status"] == "rejected"


def _sides_agree(a, b):
    return not ({a, b} <= {"left", "right"} and a != b)


def closing_observation(negation, entries):
    """-> the earliest observation that closes an entry of only absences, or None.

    A finding of the negation's type or a narrower one, reported present at a
    site within the negation's site after its last absence, closes it. A
    rejected observation counts on neither side. The two hierarchies relate the
    findings, so neither history changes.
    """
    finding_type = CODE_CONCEPT[negation["finding_code"]["code"]]
    region = negation["anatomic_site"]["code"]
    absences = [o for o in negation["observations"] if not rejected(o)]
    last = max(exam_order[o["exam_id"]] for o in absences)
    hits = []
    for e in entries:
        if e is negation:
            continue
        for o in e["observations"]:
            if rejected(o):
                continue
            a, code = o["attributes"], CODE_CONCEPT[o["finding_code"]["code"]]
            if (a["presence"] == "present" and exam_order[o["exam_id"]] > last
                    and (code == finding_type or finding_type in CONCEPTS[code]["path"])
                    and site_within(o["anatomic_site"]["code"], region)
                    and _sides_agree(a.get("laterality"), negation.get("laterality"))):
                hits.append(o)
    return min(hits, key=lambda o: exam_order[o["exam_id"]]) if hits else None


def close_negations(entries):
    """Close each excluded entry that a later finding within its site closes."""
    for e in entries:
        if e["status"] != "excluded":
            continue
        o = closing_observation(e, entries)
        if o:
            e["status"], e["status_rule"] = STATUS_RULES["closed-by-subsequent-finding"][0], "closed-by-subsequent-finding"
            e["closed"] = {"observation_id": o["observation_id"], "exam_id": o["exam_id"]}


# ============================================================
# Build
# ============================================================

def tracking_uid(fid):
    """-> the entry's Tracking UID, the same on every build."""
    return "2.25." + str(uuid.uuid5(UID_NAMESPACE, f"{patient['id']}/{fid}").int)


def report_sentences():
    """-> {exam_id: [sentence, ...]}: each exam's report, its sentences in authoring order, without repeats."""
    reports = defaultdict(list)
    for o in [o for f in findings for o in f["observations"]] + [s[3] for s in examination_statements]:
        for s in split_sentences(o["text"]):
            if s not in reports[o["exam_id"]]:
                reports[o["exam_id"]].append(s)
    return reports


def split_sentences(text):
    """-> the sentences in text, split at each period that ends one."""
    parts, cur = [], ""
    for i, ch in enumerate(text):
        cur += ch
        if ch == "." and (i + 1 == len(text) or text[i + 1] == " "):
            parts.append(cur.strip())
            cur = ""
    if cur.strip():
        parts.append(cur.strip())
    return parts


def validate():
    """Fail the build when an authored finding breaks an identity or negation rule."""
    ids = [f["id"] for f in findings]
    assert len(ids) == len(set(ids)), "duplicate entry id"
    for f in findings:
        assert f["code"] in CONCEPTS, f["id"]
        exams_seen = set()
        for o in f["observations"]:
            assert o["exam_id"] not in exams_seen, f"{f['id']}: two observations on {o['exam_id']}"
            exams_seen.add(o["exam_id"])
            code = o.get("code", f["code"])
            assert on_one_path(code, f["code"]) or same_spectrum(code, f["code"]), \
                f"{f['id']} {o['exam_id']}: {code} is off the path of {f['code']}"
            assert site_within(o.get("site", f["site"]), f["site"]), f"{f['id']} {o['exam_id']}: site outside the entry's"
            for i in as_list(o.get("interp")):
                name = i[0] if isinstance(i, tuple) else i
                assert name in CONCEPTS, f"{f['id']}: unknown interpretation {name}"
            for c in as_list(o.get("context")):
                assert (c[0] if isinstance(c, tuple) else c) in CONCEPTS, f"{f['id']}: unknown clinical context {c}"
            # The contradiction rule reads a value's stated digit from the typed
            # number, so each number must be typed as its sentence writes it.
            for key in ("measurement", "prior_measurement"):
                for value, *_ in o.get(key, []):
                    assert re.search(rf"(?<![\d.]){re.escape(repr(value))}(?![\d])", o["text"]), \
                        f"{f['id']} {o['exam_id']}: {value!r} is not written in its sentence as typed"
            # A negation joins only an entry of its own type at its own site, never a narrower one.
            assert o["presence"] == "present" or code == f["code"] or code not in CONCEPTS[f["code"]]["path"], \
                f"{f['id']} {o['exam_id']}: a negation of {code} is broader than the entry's {f['code']}"
        orders = [exam_order[o["exam_id"]] for o in f["observations"]]
        assert orders == sorted(orders), f"{f['id']}: observations out of order"
    for sid, code, site_id, o in examination_statements:
        assert code in CONCEPTS and "image_quality_issue" in CONCEPTS[code]["path"], sid
        assert site_id in AL, sid
    codes = [c["oifm"] for c in CONCEPTS.values()]
    assert len(codes) == len(set(codes)), "two concepts share an OIFM code"


def stated_site_words(text, words):
    """-> the span of text that states the site, as the sentence writes it."""
    m = re.search(r"\b" + re.escape(words) + r"\b", text, re.IGNORECASE)
    assert m, f"site words {words!r} are not in {text!r}"
    return m.group(0)


def structured_observation(f, o, sentence_numbers):
    """-> one observation as the EFL and IPL files record it."""
    ex = exam_map[o["exam_id"]]
    return {
        "observation_id": f"{f['id']}.{o['exam_id']}",
        "exam_id": o["exam_id"],
        "report_id": report_id(o["exam_id"]),
        "exam_date": ex["date"],
        "exam_modality": ex["modality"],
        "finding_code": concept_code(o.get("code", f["code"])),
        "anatomic_site": site(o.get("site", f["site"])),
        "attributes": attributes(o),
        "interpretations": [interpretation_record(i) for i in as_list(o.get("interp"))],
        "text": o["text"],
        "provenance": {
            "source": "specification",
            "report_id": report_id(o["exam_id"]),
            "sentences": sentence_numbers,
            "site_words": stated_site_words(o["text"], o.get("words", f.get("words", ""))),
            "review_status": "unreviewed",
            "reviews": [],
        },
    }


def build():
    """-> the IPL entries, the examination statements, and each report's sentences."""
    validate()
    reports = report_sentences()

    def numbers(o):
        return [reports[o["exam_id"]].index(s) + 1 for s in split_sentences(o["text"])]

    entries = []
    for f in findings:
        structured = [structured_observation(f, o, numbers(o)) for o in f["observations"]]
        status, rule = derive_status(structured)
        entry = {
            "finding_id": f["id"],
            "tracking_uid": tracking_uid(f["id"]),
            "finding_code": concept_code(f["code"]),
            "anatomic_site": site(f["site"]),
            "status": status,
            "status_rule": rule,
            "observations": structured,
            "corrections": [],
        }
        if f["laterality"]:
            entry["laterality"] = f["laterality"]
        entries.append(entry)
    close_negations(entries)
    for f, e in zip(findings, entries):
        assert e["status"] == f["status"], f"{f['id']} derives {e['status']}, specified {f['status']}"
    statements = [structured_observation({"id": sid, "code": code, "site": site_id}, o, numbers(o))
                  for sid, code, site_id, o in examination_statements]
    return entries, statements, reports


@cache
def schema_validator(name):
    """-> a validator for one of the schemas in scripts/spec/, with the others it references."""
    schemas = {}
    for f in ("observation", "efl", "ipl"):
        with open(os.path.join(SPEC_DIR, f"{f}.schema.json")) as fh:
            schemas[f] = json.load(fh)
    registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas.values())
    return Draft202012Validator(schemas[name], registry=registry, format_checker=Draft202012Validator.FORMAT_CHECKER)


def write_valid(files):
    """Write each (record, schema, path) as JSON once every record validates.

    The build exits nonzero on the first failure before it writes anything, so
    a failing build leaves the last build's files as they were.
    """
    for record, schema, path in files:
        error = next(iter(schema_validator(schema).iter_errors(record)), None)
        if error:
            sys.exit(f"{os.path.basename(path)} fails {schema}.schema.json at {error.json_path}: {error.message}")
    for record, _, path in files:
        with open(path, "w") as fh:
            json.dump(record, fh, indent=2, ensure_ascii=False)


def efl_files(entries, statements, reports):
    """-> one Exam Finding List per examination, as (record, schema, path)."""
    by_exam = defaultdict(list)
    for e in entries:
        for o in e["observations"]:
            by_exam[o["exam_id"]].append({k: v for k, v in o.items() if k != "derived"})
    for s in statements:
        by_exam[s["exam_id"]].append(s)
    files = []
    for exam in exams:
        observations = sorted(by_exam[exam["id"]],
                              key=lambda r: (0 if r["attributes"]["presence"] == "present" else 1, r["observation_id"]))
        efl = {
            "report": {
                "report_id": report_id(exam["id"]),
                "patient_id": patient["id"],
                "exam_id": exam["id"],
                "date": exam["date"],
                "modality": exam["modality"],
                "procedure_code": procedure_code(exam),
                "indication": exam["indication"],
            },
            "sentences": [{"number": i + 1, "text": s} for i, s in enumerate(reports[exam["id"]])],
            "observations": observations,
        }
        files.append((efl, "efl", os.path.join(EFL_DIR, f"EFL_{exam['id']}_{exam['date']}_{exam['modality']}.json")))
    return files


def ipl_file(entries):
    """-> the Imaging Problem List, as (record, schema, path)."""
    output = {"schema_version": SCHEMA_VERSION, "compiled_date": COMPILED_DATE, "patient": patient,
              "entries": entries}
    return output, "ipl", os.path.join(OUTPUT_DIR, "imaging_problem_list.json")


def remove_stale_efls(files):
    """Remove each EFL file a previous build wrote that this build did not."""
    written = {os.path.basename(path) for _, _, path in files}
    for old in os.listdir(EFL_DIR):
        if old.startswith("EFL_") and old.endswith(".json") and old not in written:
            os.remove(os.path.join(EFL_DIR, old))


if __name__ == "__main__":
    entries, statements, reports = build()
    os.makedirs(EFL_DIR, exist_ok=True)
    efls = efl_files(entries, statements, reports)
    write_valid(efls + [ipl_file(entries)])
    remove_stale_efls(efls)
    n_obs = sum(len(e["observations"]) for e in entries)
    print(f"{len(entries)} entries and {n_obs} observations from {len(exams)} examinations, "
          f"{len(statements)} examination statement{'' if len(statements) == 1 else 's'} kept in the EFLs, "
          f"written to {OUTPUT_DIR}/")
