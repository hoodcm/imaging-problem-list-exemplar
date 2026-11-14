#!/usr/bin/env python3
"""Build the worked FHIR example of the aneurysm entry.

The script reads entry F01 from data/derived/imaging_problem_list.json, its
reports from data/derived/efls/, and the attribute displays from the IPL code
system SUSHI compiles into data/derived/fhir/definitions/, and writes a FHIR R5 Bundle of type collection
to data/derived/fhir/aneurysm-example.json. Each report gets a DiagnosticReport,
a BodyStructure that holds the site as that report gave it, and an Observation
that references the BodyStructure. The entry's Tracking UID ties the
BodyStructures together, and an anchor BodyStructure stands for the entry on the
patient's List. The review history is illustrative, because no model read the
synthetic reports: a model extracts each observation, a radiologist affirms the
2024 observation, rejects the model's 2023 reading of 4.5 cm, and enters 4.8 cm.
The model's reading takes the prior value as the current one and records no
prior measurement.

Usage: python3 scripts/fhir_example.py
"""

import glob
import json
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED_DIR = os.path.join(PROJECT_DIR, "data", "derived")
ATTRIBUTE_CODE_SYSTEM = os.path.join(DERIVED_DIR, "fhir", "definitions", "fsh-generated", "resources",
                                     "CodeSystem-ipl-attribute.json")
BASE = "https://github.com/hoodcm/imaging-problem-list-exemplar"
FULL_URL = "http://example.org/fhir"
SYSTEMS = {
    "OIFM": f"{BASE}/CodeSystem/oifm",
    "Anatomic Locations Index 1.0.0": f"{BASE}/CodeSystem/anatomic-locations",
    "LOINC": "http://loinc.org",
}
ATTRIBUTE = f"{BASE}/CodeSystem/ipl-attribute"
SNOMED, UCUM, DCM = "http://snomed.info/sct", "http://unitsofmeasure.org", "http://dicom.nema.org/resources/ontology/DCM"
LIFECYCLE = "http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle"
PARTICIPANT = "http://terminology.hl7.org/CodeSystem/provenance-participant-type"
ILLUSTRATIVE = "Illustrative: no model read the synthetic reports, so this review history shows the structure only."
REJECTED_EXAM, AFFIRMED_EXAM, MISREAD_CM = "E14", "E15", 4.5


def attribute_displays():
    """-> {code: display} for every code in the compiled IPL attribute code system."""
    def walk(concepts):
        for c in concepts:
            yield c["code"], c["display"]
            yield from walk(c.get("concept", []))
    with open(ATTRIBUTE_CODE_SYSTEM) as fh:
        return dict(walk(json.load(fh)["concept"]))


DISPLAYS = attribute_displays()


def attribute(code):
    """-> a Coding from the IPL attribute code system, with its compiled display."""
    return {"system": ATTRIBUTE, "code": code, "display": DISPLAYS[code]}


def coding(c):
    """-> a FHIR Coding from one of the IPL files' codings."""
    return {"system": SYSTEMS[c["system"]], "code": c["code"], "display": c["display"]}


def concept(*codings):
    return {"coding": list(codings)}


def ref(kind, rid):
    return {"reference": f"{kind}/{rid}"}


def narrative(text):
    return {"status": "generated", "div": f'<div xmlns="http://www.w3.org/1999/xhtml">{text}</div>'}


def resource(kind, rid, text, **body):
    return {"resourceType": kind, "id": rid, "text": narrative(text), **body}


def body_structure(rid, entry_like, uid, site_words, text):
    site = entry_like["anatomic_site"]
    structure = concept(coding(site), *([{"system": SNOMED, "code": site["snomed"]}] if site["snomed"] else []))
    return resource("BodyStructure", rid, text,
                    identifier=[{"type": concept({"system": DCM, "code": "112040", "display": "Tracking Unique Identifier"}),
                                 "system": "urn:dicom:uid", "value": f"urn:oid:{uid}"}],
                    morphology=concept(coding(entry_like["finding_code"])),
                    includedStructure=[{"structure": structure}],
                    **({"description": site_words} if site_words else {}),
                    patient=ref("Patient", "patient"))


def observation(o, rid, text, status="final", replaces=None):
    a = o["attributes"]
    components = []
    for key in ("measurement", "prior_measurement"):
        for m in a.get(key, []):
            assert "property" not in m, f"{o['observation_id']}: the worked example gives a measurement's property no form"
            components.append({"code": concept(attribute(key)),
                               "valueQuantity": {"value": m["value"], "unit": m["unit"], "system": UCUM, "code": m["unit"]}})
    for word in a.get("temporal_status", []):
        components.append({"code": concept(attribute("temporal_status")), "valueCodeableConcept": concept(attribute(word))})
    detected = {"system": SNOMED, "code": "260373001", "display": "Detected"}
    return resource("Observation", rid, text,
                    **({"extension": [{"url": "http://hl7.org/fhir/StructureDefinition/observation-replaces",
                                       "valueReference": ref("Observation", replaces)}]} if replaces else {}),
                    status=status, code=concept(coding(o["finding_code"])), subject=ref("Patient", "patient"),
                    effectiveDateTime=o["exam_date"], valueCodeableConcept=concept(detected),
                    note=[{"text": o["text"]}], bodyStructure=ref("BodyStructure", f"{o['exam_id']}-F01"),
                    component=components)


def provenance(rid, activity, targets, agent, agent_type, text, entities=(), recorded="2026-11-13T00:00:00Z"):
    return resource("Provenance", rid, f"{text} {ILLUSTRATIVE}",
                    target=[ref(*t) for t in targets], recorded=recorded,
                    activity=concept({"system": LIFECYCLE, "code": activity}),
                    agent=[{"type": concept({"system": PARTICIPANT, "code": agent_type}), "who": ref(*agent)}],
                    **({"entity": [{"role": role, "what": ref(*what)} for role, what in entities]} if entities else {}))


def bundle(ipl, reports):
    """-> the worked example as a Bundle of type collection."""
    entry = next(e for e in ipl["entries"] if e["finding_id"] == "F01")
    uid, patient = entry["tracking_uid"], ipl["patient"]
    out = [resource("Patient", "patient", "The synthetic exemplar patient.",
                    identifier=[{"value": patient["id"]}], name=[{"text": patient["name"]}]),
           resource("Device", "extraction-model", f"The example extraction model. {ILLUSTRATIVE}",
                    name=[{"value": "example extraction model", "type": "user-friendly-name"}], version=[{"value": "1.0"}]),
           resource("Device", "ipl-compiler", "The IPL compiler, scripts/build_exemplar.py.",
                    name=[{"value": "IPL compiler", "type": "user-friendly-name"}]),
           resource("Practitioner", "radiologist", f"The reviewing radiologist. {ILLUSTRATIVE}", name=[{"text": "Reviewing radiologist"}]),
           body_structure("F01", entry, uid, None, "The anchor that stands for the aneurysm entry on the patient's List.")]
    rejected_id, extracted = f"F01.{REJECTED_EXAM}.model", []
    for o in entry["observations"]:
        exam, report = o["exam_id"], reports[o["exam_id"]]["report"]
        result = [ref("Observation", o["observation_id"])]
        if exam == REJECTED_EXAM:
            misread = {k: v for k, v in o["attributes"].items() if k != "prior_measurement"}
            misread["measurement"] = [{"value": MISREAD_CM, "unit": "cm"}]
            out.append(observation({**o, "attributes": misread}, rejected_id,
                                   f"The model's reading of the {o['exam_date'][:4]} sentence as {MISREAD_CM} cm, rejected. {ILLUSTRATIVE}",
                                   status="entered-in-error"))
            out.append(observation(o, o["observation_id"],
                                   f"The radiologist's replacement, {o['attributes']['measurement'][0]['value']} cm. {ILLUSTRATIVE}", replaces=rejected_id))
            result.insert(0, ref("Observation", rejected_id))
            extracted.append(rejected_id)
        else:
            out.append(observation(o, o["observation_id"], f"The aneurysm as the {o['exam_date']} report states it."))
            extracted.append(o["observation_id"])
        out.append(body_structure(f"{exam}-F01", o, uid, o["provenance"]["site_words"], f"The aneurysm's site as the {o['exam_date']} report gives it."))
        out.append(resource("DiagnosticReport", f"report-{exam}", f"The {o['exam_date']} report.",
                            identifier=[{"value": report["report_id"]}], status="final",
                            code=concept(coding(report["procedure_code"])), subject=ref("Patient", "patient"),
                            effectiveDateTime=report["date"], result=result))
    for oid in extracted:
        exam = oid.split(".")[1]
        out.append(provenance(f"extract-{exam}", "transform", [("Observation", oid)], ("Device", "extraction-model"), "transformer",
                              f"The model extracts the {exam} observation.", entities=[("source", ("DiagnosticReport", f"report-{exam}"))]))
    report_structures = [("BodyStructure", f"{o['exam_id']}-F01") for o in entry["observations"]]
    out.append(provenance("match", "link", report_structures, ("Device", "ipl-compiler"), "assembler",
                          "The IPL compiler matches the reports' BodyStructures and writes the Tracking UID into each."))
    out.append(provenance("affirm", "verify", [("Observation", f"F01.{AFFIRMED_EXAM}")], ("Practitioner", "radiologist"), "verifier",
                          "The radiologist affirms the 2024 observation."))
    out.append(provenance("reject", "deprecate", [("Observation", rejected_id)], ("Practitioner", "radiologist"), "verifier",
                          "The radiologist rejects the model's 2023 reading."))
    out.append(provenance("replace", "amend", [("Observation", f"F01.{REJECTED_EXAM}")], ("Practitioner", "radiologist"), "verifier",
                          "The radiologist enters the 2023 measurement the report states.", entities=[("revision", ("Observation", rejected_id))]))
    out.append(resource("List", "ipl", "The patient's Imaging Problem List, holding the aneurysm entry.",
                        status="current", mode="working", title="Imaging Problem List", subject=[ref("Patient", "patient")],
                        date=ipl["compiled_date"],
                        entry=[{"extension": [{"url": f"{BASE}/StructureDefinition/entry-status-rule",
                                               "valueCoding": {"system": f"{BASE}/CodeSystem/ipl-status-rule", "code": entry["status_rule"]}}],
                                "flag": concept({"system": f"{BASE}/CodeSystem/ipl-status", "code": entry["status"]}),
                                "item": ref("BodyStructure", "F01")}]))
    return {"resourceType": "Bundle", "id": "aneurysm-example", "type": "collection",
            "entry": [{"fullUrl": f"{FULL_URL}/{r['resourceType']}/{r['id']}", "resource": r} for r in out]}


if __name__ == "__main__":
    with open(os.path.join(DERIVED_DIR, "imaging_problem_list.json")) as fh:
        ipl = json.load(fh)
    reports = {}
    for path in glob.glob(os.path.join(DERIVED_DIR, "efls", "EFL_*.json")):
        with open(path) as fh:
            efl = json.load(fh)
        reports[efl["report"]["exam_id"]] = efl
    os.makedirs(os.path.join(DERIVED_DIR, "fhir"), exist_ok=True)
    path = os.path.join(DERIVED_DIR, "fhir", "aneurysm-example.json")
    with open(path, "w") as fh:
        json.dump(bundle(ipl, reports), fh, indent=2, ensure_ascii=False)
    print(f"Worked example written to {path}")
