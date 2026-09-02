# Imaging Problem List exemplar

Synthetic patient data for the Imaging Problem List (IPL) framework paper: one patient, 15 imaging examinations from 2017 to 2024, 41 findings, and 223 observations. The `build_exemplar.py` script generates every data file in this repository.

## Contents

- `build_exemplar.py`: the specification of every finding and observation, and the rules that derive the data files.
- `efls/`: one Exam Finding List (EFL) per examination.
- `imaging_problem_list.json`: the aggregated Imaging Problem List.
- `swimlane_data.csv`: the observations of the tracked findings, for plotting.
- `finding_models/`: definitions for five of the finding codes.

## Regenerate the data

To regenerate the data files in place, run the script with Python 3:

```
python3 build_exemplar.py
```

The script uses only the standard library. It prints summary statistics and rewrites `efls/`, `imaging_problem_list.json`, and `swimlane_data.csv`.

## Data model

An observation is one documented assessment of a finding on one examination, recorded as the report stated it. Each observation carries the following fields:

- `presence`: `present` or `absent`.
- `measurement` and `characterization`: the measured value or descriptive terms as stated.
- `temporal_status`: the radiologist's stated comparison to prior imaging.
- `chronicity`: the radiologist's stated stage.
- `confidence`: the attributes the radiologist hedged.
- `text`: the report sentence.

An EFL lists the observations of one examination, with the examination's LOINC procedure code. Each finding carries an Open Imaging Finding Model (OIFM) code and its stated anatomic site.

The IPL groups observations by finding and anatomic site into entries. An entry holds its observation history and a `status` derived from that history:

- `excluded`: assessed and never present.
- `resolved`: present before, and absent on the most recent assessment.
- `active`: present, and either newly present or carrying a stated change on the most recent observation.
- `stable`: present and otherwise unchanged. A finding first documented as chronic or remote is stable from its first observation.

A distinct sequela of a resolved finding is its own entry, linked to the finding it succeeded by a `sequela_of` linkage.

## Codes

Finding codes are OIFM identifiers from the [Open Imaging Finding Models registry](https://github.com/openimagingdata/findingmodels). The definitions for the five codes in `finding_models/` follow the registry's schema. Procedure codes are LOINC codes.

## License

The code is licensed under the Apache License 2.0, in the `LICENSE` file. The data files are licensed under CC BY 4.0, in the `LICENSE-DATA` file.

## Citation

For the citation, see the `CITATION.cff` file.
