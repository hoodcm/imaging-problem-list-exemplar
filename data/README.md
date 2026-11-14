# Data

The synthetic exemplar's data. Nothing here describes a real patient.

## Raw files

Each raw file is kept as its source published it. The following table lists where each came from and its licence:

| Path | Source | Licence |
|---|---|---|
| `raw/anatomic_locations/` | Release 1.0.0 of the Anatomic Locations Index and its JSON Schema, from `talkasab/anatomiclocations.org` on GitHub, which codes every anatomic site | ISC, in `raw/anatomic_locations/LICENSE` |
| `raw/finding_models/` | Finding-model definitions written for the exemplar, for codes the Open Imaging Finding Models registry doesn't publish | CC BY 4.0, as the repository's data |
| `raw/oidm_annotator/attributes.json` | The attribute model of the OIDM report findings annotator, `hoodcm/oidm-report-findings-annotator` at commit `384d9fb`, whose values the schema's attribute value sets equal | Apache 2.0, in `raw/oidm_annotator/LICENSE` and `NOTICE` |
| `raw/fhir/` | The HL7 FHIR packages the field table and worked example are checked against: R5 core 5.0.0, R6 core 6.0.0-snapshot1, HL7 Terminology 7.5.0, and the Extensions Pack 5.4.0 for R5, from `packages.fhir.org` and `hl7.org` | CC0 1.0, as each package's `package.json` states |

The field table's DICOM SR concepts are checked against DICOM PS3.16 2026d, Content Mapping Resource, at https://dicom.nema.org/medical/dicom/current/source/docbook/part16/part16.xml. It carries third-party licensed content, so it isn't redistributed here.

## Derived files

`derived/` holds what the scripts write, so regenerate it with the commands in the repository's `README.md`, never by hand:

- `efls/`: one Exam Finding List per examination.
- `imaging_problem_list.json`: the Imaging Problem List.
- `field_table.md` and `field_table.tsv`: the field table.
- `fhir/definitions/`: the IPL code systems and extensions that SUSHI compiles.
- `fhir/aneurysm-example.json`: the worked FHIR example.
