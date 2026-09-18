#!/usr/bin/env python3
"""Build the synthetic exemplar patient for the Imaging Problem List framework paper.

Every finding's observation sequence, and the report sentence for each
observation, is authored here. From this one source the script derives the
per-examination Exam Finding Lists (efls/), the aggregated Imaging Problem List
(imaging_problem_list.json), and the Figure 2 data (swimlane_data.csv).

All data are synthetic. Each observation records what the report stated:
presence, any measurement or characterization, the radiologist's stated
comparison (temporal_status), the stated time course (chronicity), and any hedge
(confidence). The entry status in the IPL is derived from the observation
history and never authored.
"""

import json
import os
from collections import defaultdict

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
EFL_DIR = os.path.join(OUTPUT_DIR, "efls")
os.makedirs(EFL_DIR, exist_ok=True)

# ============================================================
# Patient
# ============================================================

patient = {
    "id": "IPL-EXEMPLAR-001",
    "name": "Synthetic Patient 001",
    "age_at_start": 64,
    "clinical_profile": "MASH cirrhosis with portal hypertension, abdominal aortic aneurysm under surveillance",
    "surgical_history": ["Appendectomy (remote)", "Left total hip arthroplasty (2014)"],
}

# ============================================================
# Exams
# ============================================================

exams = [
    {"id": "E01", "date": "2017-03-14", "type": "US Abdomen",                              "modality": "US",  "body_region": "ABDOMEN",       "setting": "Outpatient", "indication": "Cirrhosis surveillance"},
    {"id": "E02", "date": "2018-02-06", "type": "CT Abdomen/Pelvis with contrast",          "modality": "CT",  "body_region": "ABDOMEN_PELVIS","setting": "Outpatient", "indication": "Elevated AFP, hepatic lesion workup"},
    {"id": "E03", "date": "2018-05-22", "type": "MRI Abdomen with contrast (LI-RADS)",      "modality": "MRI", "body_region": "ABDOMEN",       "setting": "Outpatient", "indication": "Hepatic lesion characterization"},
    {"id": "E04", "date": "2019-09-12", "type": "CXR (PA and lateral)",                     "modality": "XR",  "body_region": "CHEST",         "setting": "Urgent care","indication": "Cough and fever, rule out pneumonia"},
    {"id": "E05", "date": "2019-10-29", "type": "CXR (PA and lateral)",                     "modality": "XR",  "body_region": "CHEST",         "setting": "Outpatient", "indication": "Follow-up pneumonia"},
    {"id": "E06", "date": "2020-06-18", "type": "CTA Abdomen/Pelvis",                       "modality": "CT",  "body_region": "ABDOMEN_PELVIS","setting": "Outpatient", "indication": "Abdominal aortic aneurysm surveillance, cirrhosis follow-up"},
    {"id": "E07", "date": "2021-03-09", "type": "MRI Abdomen with contrast (LI-RADS)",      "modality": "MRI", "body_region": "ABDOMEN",       "setting": "Outpatient", "indication": "Hepatic lesion follow-up, >2 yr from initial"},
    {"id": "E08", "date": "2021-07-22", "type": "CT Abdomen/Pelvis with contrast",          "modality": "CT",  "body_region": "ABDOMEN_PELVIS","setting": "Outpatient", "indication": "Cirrhosis follow-up, worsening LFTs"},
    {"id": "E09", "date": "2022-01-15", "type": "XR Chest (portable, supine)",              "modality": "XR",  "body_region": "CHEST",         "setting": "ED",         "indication": "Fall, trauma screening"},
    {"id": "E10", "date": "2022-01-15", "type": "XR Pelvis (AP)",                           "modality": "XR",  "body_region": "PELVIS",        "setting": "ED",         "indication": "Fall, trauma screening"},
    {"id": "E11", "date": "2022-01-15", "type": "CT Chest/Abdomen/Pelvis with contrast",    "modality": "CT",  "body_region": "CHEST_ABDOMEN_PELVIS", "setting": "ED",  "indication": "Fall, trauma workup"},
    {"id": "E12", "date": "2022-01-15", "type": "CT Head without contrast",                 "modality": "CT",  "body_region": "HEAD",          "setting": "ED",         "indication": "Fall, rule out intracranial hemorrhage"},
    {"id": "E13", "date": "2022-04-10", "type": "US Abdomen with Doppler",                  "modality": "US",  "body_region": "ABDOMEN",       "setting": "Outpatient", "indication": "Cirrhosis surveillance, portal vein assessment"},
    {"id": "E14", "date": "2023-03-28", "type": "CT Abdomen/Pelvis with contrast",          "modality": "CT",  "body_region": "ABDOMEN_PELVIS","setting": "Outpatient", "indication": "Abdominal aortic aneurysm and cirrhosis surveillance"},
    {"id": "E15", "date": "2024-07-16", "type": "CTA Abdomen/Pelvis",                       "modality": "CT",  "body_region": "ABDOMEN_PELVIS","setting": "Outpatient", "indication": "Abdominal aortic aneurysm pre-surgical evaluation"},
]

exam_map = {e["id"]: e for e in exams}

# LOINC procedure code per exam type.
PROCEDURE_CODES = {
    "US Abdomen":                            ("24558-9", "US Abdomen"),
    "US Abdomen with Doppler":               ("24558-9", "US Abdomen"),
    "CT Abdomen/Pelvis with contrast":       ("36813-4", "CT Abdomen and Pelvis W contrast IV"),
    "CTA Abdomen/Pelvis":                    ("87854-6", "CT Abdomen and Pelvis and CT angiogram Abdominal aorta W contrast IV"),
    "CT Chest/Abdomen/Pelvis with contrast": ("72254-6", "CT Chest and Abdomen and Pelvis W contrast IV"),
    "CT Head without contrast":              ("30799-1", "CT Head WO contrast"),
    "MRI Abdomen with contrast (LI-RADS)":   ("36134-5", "MR Abdomen W contrast IV"),
    "CXR (PA and lateral)":                  ("42272-5", "XR Chest PA and Lateral"),
    "XR Chest (portable, supine)":           ("36589-0", "Portable XR Chest AP single view"),
    "XR Pelvis (AP)":                        ("37622-8", "XR Pelvis AP"),
}

# Open Imaging Finding Model code per finding.
FINDING_CODES = {
    "F01": ("OIFM_MSFT_134126", "abdominal aortic aneurysm"),
    "F02": ("OIFM_OIDM_160831", "hepatic lesion"),
    "F03": ("OIFM_GMTS_000480", "ascites"),
    "F04": ("OIFM_GMTS_035534", "portal vein thrombosis"),
    "F05": ("OIFM_MGB_774223", "IPMN"),
    "F06": ("OIFM_CDE_000076", "pneumonia"),
    "F07": ("OIFM_MGB_944849", "rib fracture"),
    "F08": ("OIFM_CDE_000230", "vertebral compression fracture"),
    "F09": ("OIFM_GMTS_000249", "esophageal varices"),
    "F10": ("OIFM_GMTS_022460", "cirrhosis"),
    "F11": ("OIFM_GMTS_003565", "splenomegaly"),
    "F12": ("OIFM_GMTS_022482", "gallstone"),
    "F13": ("OIFM_GMTS_016773", "cystic renal mass"),
    "F14": ("OIFM_OIDM_319506", "kidney stone"),
    "F15": ("OIFM_OIDM_675673", "degenerative change of the thoracic spine"),
    "F16": ("OIFM_OIDM_481402", "lumbar spine degenerative change"),
    "F17": ("OIFM_OIDM_847217", "aortic calcification"),
    "F18": ("OIFM_GMTS_017620", "enlarged prostate"),
    "F19": ("OIFM_MGB_169189", "total hip arthroplasty"),
    "F20": ("OIFM_MGB_285678", "prior appendectomy"),
    "F21": ("OIFM_OIDM_251340", "lacunar infarct"),
    "F22": ("OIFM_OIDM_093125", "cerebral small vessel disease"),
    "F23": ("OIFM_OIDM_444719", "medial orbital wall fracture"),
    "F24": ("OIFM_CDE_000254", "pleural effusion"),
    "F25": ("OIFM_CDE_000195", "pulmonary nodule"),
    "F26": ("OIFM_GMTS_022537", "cardiomegaly"),
    "F27": ("OIFM_GMTS_023339", "pneumothorax"),
    "F28": ("OIFM_OIDM_874812", "hydronephrosis"),
    "F29": ("OIFM_GMTS_005226", "dilated bile ducts"),
    "F30": ("OIFM_GMTS_002674", "dilated pancreatic duct"),
    "F31": ("OIFM_OIDM_160831", "hepatic lesion"),
    "F32": ("OIFM_GMTS_003106", "abdominal lymphadenopathy"),
    "F33": ("OIFM_GMTS_022484", "intestinal obstruction"),
    "F34": ("OIFM_CDE_000228", "pneumoperitoneum"),
    "F35": ("OIFM_CDE_000194", "acute intracranial hemorrhage"),
    "F36": ("OIFM_OIDM_119725", "intracranial mass"),
    "F37": ("OIFM_MGB_987895", "solid organ injury"),
    "F38": ("OIFM_MGB_437803", "pelvic fracture"),
    "F39": ("OIFM_MGB_969524", "sternal fracture"),
    "F40": ("OIFM_MGB_735619", "thoracic spine fracture"),
    "F41": ("OIFM_OIDM_745898", "pulmonary scar"),
}


def procedure_code(exam):
    code, display = PROCEDURE_CODES[exam["type"]]
    return {"system": "LOINC", "code": code, "display": display}


def finding_code(finding):
    code, display = FINDING_CODES[finding["id"]]
    return {"system": "OIFM", "code": code, "display": display}

# ============================================================
# Helper
# ============================================================

def obs(exam_id, presence, **kwargs):
    """Create an observation dict."""
    return {"exam_id": exam_id, "presence": presence, **kwargs}

# ============================================================
# Findings and observations
# ============================================================

findings = []

# --------------------------------------------------
# SHOWCASE FINDINGS
# --------------------------------------------------

findings.append({
    "id": "F01",
    "name": "Abdominal aortic aneurysm",
    "anatomic_site": "infrarenal aorta",
    "body_region": "Abdomen",
    "category": "showcase",
    "trajectory_type": "Progressive measurement toward surgical threshold",
    "observations": [
        obs("E01", "present", measurement="3.2 cm", text="The infrarenal aorta measures 3.2 cm, mildly dilated."),
        obs("E02", "present", measurement="3.5 cm", temporal_status="increased", text="Infrarenal abdominal aortic aneurysm measuring 3.5 cm, mildly increased compared to 3.2 cm on the prior ultrasound from March 2017."),
        obs("E06", "present", measurement="3.9 cm", temporal_status="increased", text="Known infrarenal AAA now measures 3.9 cm, previously 3.5 cm. No evidence of rupture or dissection."),
        obs("E08", "present", measurement="4.3 cm", temporal_status="increased", text="Infrarenal aortic aneurysm measures 4.3 cm, increased from 3.9 cm on the prior CTA."),
        obs("E11", "present", measurement="4.5 cm", temporal_status="increased", text="There is a 4.5 cm infrarenal abdominal aortic aneurysm, slightly increased from 4.3 cm on July 2021 CT. No surrounding stranding to suggest contained leak."),
        obs("E13", "present", measurement="4.5 cm", temporal_status="stable", text="Infrarenal AAA measures 4.5 cm, unchanged compared to the recent CT from January."),
        obs("E14", "present", measurement="4.8 cm", temporal_status="increased", text="Interval increase in the infrarenal aortic aneurysm, now measuring 4.8 cm compared to 4.5 cm previously."),
        obs("E15", "present", measurement="5.1 cm", temporal_status="increased", text="Infrarenal abdominal aortic aneurysm has increased to 5.1 cm from 4.8 cm on the 2023 study. Approaching surgical threshold."),
    ],
})

findings.append({
    "id": "F02",
    "name": "Hepatic lesion",
    "anatomic_site": "hepatic segment 6",
    "body_region": "Abdomen",
    "category": "showcase",
    "trajectory_type": "Reclassification after temporal stability (LR-3 → LR-2)",
    "observations": [
        obs("E01", "absent", text="No focal hepatic lesion."),
        obs("E02", "present", measurement="1.8 cm", characterization="LR-3", text="1.8 cm arterially enhancing segment 6 lesion. LI-RADS 3. MRI recommended."),
        obs("E03", "present", measurement="1.8 cm", characterization="LR-3", text="1.8 cm segment 6 lesion with arterial phase hyperenhancement, no washout or capsule appearance. LI-RADS 3, unchanged."),
        obs("E06", "present", measurement="1.7 cm", temporal_status="stable", text="Segment 6 hepatic lesion measures 1.7 cm, stable."),
        obs("E07", "present", measurement="1.7 cm", characterization="LR-2", temporal_status="stable", text="Segment 6 lesion 1.7 cm, stable >2 years. Downgraded to LI-RADS 2."),
        obs("E08", "present", measurement="1.7 cm", characterization="LR-2", temporal_status="stable", text="Segment 6 lesion stable at 1.7 cm. LI-RADS 2."),
        obs("E11", "present", measurement="1.7 cm", temporal_status="stable", text="Known hepatic segment 6 lesion, stable at 1.7 cm."),
        obs("E13", "present", measurement="1.7 cm", temporal_status="stable", text="Segment 6 hepatic lesion measures 1.7 cm, stable."),
        obs("E14", "present", measurement="1.6 cm", characterization="LR-2", temporal_status="stable", text="Segment 6 hepatic lesion measures 1.6 cm, stable. LI-RADS 2."),
        obs("E15", "present", measurement="1.6 cm", temporal_status="stable", text="Segment 6 lesion stable at 1.6 cm."),
    ],
})

findings.append({
    "id": "F03",
    "name": "Ascites",
    "anatomic_site": "peritoneal cavity",  # SNOMED CT 83670000 (coarse site; the report stated none)
    "body_region": "Abdomen",
    "category": "showcase",
    "trajectory_type": "Waxing and waning (lifecycle transitions)",
    "observations": [
        obs("E01", "absent", text="No ascites."),
        obs("E02", "absent", text="No free fluid."),
        obs("E03", "absent", text="No ascites."),
        obs("E06", "present", characterization="small volume", text="Small volume ascites in the pelvis and perihepatic space, new."),
        obs("E07", "present", characterization="small volume", text="Small volume ascites, similar to prior."),
        obs("E08", "present", characterization="moderate", temporal_status="increased", text="Moderate ascites, increased from prior."),
        obs("E11", "present", characterization="moderate", text="Moderate abdominal ascites."),
        obs("E13", "present", characterization="small volume", temporal_status="decreased", text="Small volume ascites, decreased from prior."),
        obs("E14", "absent", text="Ascites has resolved."),
        obs("E15", "present", characterization="trace", text="Trace perihepatic ascites, recurrent."),
    ],
})

findings.append({
    "id": "F04",
    "name": "Portal vein thrombus",
    "anatomic_site": "main portal vein",
    "body_region": "Abdomen",
    "category": "showcase",
    "trajectory_type": "Acute → organizing → chronic",
    "observations": [
        obs("E01", "absent", text="Portal vein is patent with hepatopetal flow."),
        obs("E02", "absent", text="Portal vein is patent."),
        obs("E06", "absent", text="Patent portal vein."),
        obs("E08", "absent", text="Portal vein is patent."),
        obs("E11", "present", characterization="acute, non-occlusive", text="New non-occlusive thrombus in the main portal vein, hypodense, acute."),
        obs("E13", "present", characterization="organizing", text="Portal vein thrombus with peripheral enhancement, organizing. Flow maintained around thrombus."),
        obs("E14", "present", characterization="chronic, stable", text="Chronic non-occlusive portal vein thrombus, stable."),
        obs("E15", "present", characterization="chronic, stable", text="Chronic portal vein thrombus, unchanged."),
    ],
})

findings.append({
    "id": "F05",
    "name": "Side-branch IPMN",
    "anatomic_site": "pancreatic body",
    "body_region": "Abdomen",
    "category": "showcase",
    "trajectory_type": "Stable incidentaloma (unchanged across all follow-ups)",
    "observations": [
        obs("E02", "present", measurement="1.2 cm", text="1.2 cm pancreatic body cyst communicating with main pancreatic duct, side-branch IPMN."),
        obs("E06", "present", measurement="1.2 cm", temporal_status="stable", text="Pancreatic body IPMN measures 1.2 cm, stable."),
        obs("E07", "present", measurement="1.2 cm", temporal_status="stable", text="Known side-branch IPMN in the pancreatic body, 1.2 cm, stable."),
        obs("E08", "present", measurement="1.2 cm", temporal_status="stable", text="Pancreatic body IPMN stable at 1.2 cm."),
        obs("E11", "present", measurement="1.2 cm", temporal_status="stable", text="Stable 1.2 cm pancreatic body IPMN."),
        obs("E13", "present", confidence={"presence": "hedged"}, text="Probable side-branch IPMN in the pancreatic body, incompletely evaluated due to overlying bowel gas."),
        obs("E14", "present", measurement="1.2 cm", temporal_status="stable", text="Pancreatic body IPMN measures 1.2 cm, unchanged."),
        obs("E15", "present", measurement="1.2 cm", temporal_status="stable", text="Stable 1.2 cm side-branch IPMN, pancreatic body."),
    ],
})

findings.append({
    "id": "F06",
    "name": "Pneumonia",
    "anatomic_site": "right lower lobe",
    "body_region": "Chest",
    "category": "showcase",
    "trajectory_type": "Acute → resolved",
    "observations": [
        obs("E04", "present", characterization="consolidation", text="Right lower lobe consolidation, pneumonia."),
        obs("E05", "absent", text="Prior right lower lobe consolidation has resolved. Lungs clear."),
    ],
})

findings.append({
    "id": "F07",
    "name": "Rib fractures",
    "anatomic_site": "left 7th and 8th ribs, posterior axillary line",
    "body_region": "Chest",
    "category": "showcase",
    "trajectory_type": "State evolution within one entity: acute → healed",
    "observations": [
        obs("E09", "present", characterization="acute", text="Acute nondisplaced fractures of the left 7th and 8th ribs along the posterior axillary line."),
        obs("E11", "present", characterization="acute", text="Acute fractures of the left 7th and 8th ribs, confirmed. Minimal displacement."),
        obs("E14", "present", characterization="healed with callus", chronicity="healed", text="Previously acute left 7th and 8th rib fractures are now healed with callus formation."),
        obs("E15", "present", characterization="healed", temporal_status="stable", text="Healed left 7th and 8th rib fractures, unchanged."),
    ],
})

findings.append({
    "id": "F08",
    "name": "Compression fracture",
    "anatomic_site": "L4 superior endplate",
    "body_region": "Spine",
    "category": "showcase",
    "trajectory_type": "State evolution within one entity: acute → healed deformity",
    "observations": [
        obs("E10", "present", characterization="acute", measurement="20% height loss", text="Acute L4 superior endplate compression fracture, approximately 20% height loss."),
        obs("E11", "present", characterization="acute", measurement="20% height loss", text="Acute superior endplate compression fracture of L4 with approximately 20% height loss."),
        obs("E14", "present", characterization="healed, chronic deformity", measurement="20% height loss", chronicity="healed", text="Previously acute L4 compression fracture is now healed, with chronic superior endplate deformity and stable 20% height loss."),
        obs("E15", "present", characterization="chronic deformity", measurement="20% height loss", temporal_status="stable", text="Chronic L4 compression deformity, stable."),
    ],
})

findings.append({
    "id": "F09",
    "name": "Esophageal varices",
    "anatomic_site": "distal esophagus",
    "body_region": "Abdomen",
    "category": "showcase",
    "trajectory_type": "Progressive (portal hypertension)",
    "observations": [
        obs("E02", "present", characterization="small", text="Small esophageal varices."),
        obs("E03", "present", characterization="small", temporal_status="stable", text="Small esophageal varices, unchanged."),
        obs("E06", "present", characterization="small", temporal_status="stable", text="Small esophageal varices, unchanged."),
        obs("E07", "present", characterization="small", temporal_status="stable", text="Small esophageal varices, stable."),
        obs("E08", "present", characterization="moderate", temporal_status="increased", text="Esophageal varices, now moderate, increased from small on prior."),
        obs("E11", "present", characterization="moderate", text="Moderate esophageal varices."),
        obs("E14", "present", characterization="large", temporal_status="increased", text="Large esophageal varices, increased."),
        obs("E15", "present", characterization="large", temporal_status="stable", text="Large esophageal varices, stable."),
    ],
})

# --------------------------------------------------
# CHRONIC SEQUELA (a genuinely distinct entity succeeding a resolved
# acute finding — linked by an explicit succession relation, not merged.
# The fracture findings, by contrast, are the SAME physical entity
# evolving through stages and live in single entries above.)
# --------------------------------------------------

findings.append({
    "id": "F41",
    "name": "Residual scarring",
    "anatomic_site": "right lower lobe",
    "body_region": "Chest",
    "category": "showcase",
    "permanent": True,
    "sequela_of": "F06",
    "trajectory_type": "Chronic sequela of resolved pneumonia",
    "observations": [
        obs("E11", "present", characterization="linear", text="Linear scarring in the right lower lobe, sequela of prior pneumonia."),
        obs("E14", "present", temporal_status="stable", text="Right lower lobe scarring, unchanged."),
        obs("E15", "present", temporal_status="stable", text="Right lower lobe scarring, stable."),
    ],
})

# --------------------------------------------------
# BACKGROUND / CHRONIC FINDINGS
# --------------------------------------------------

findings.append({
    "id": "F10",
    "name": "Cirrhotic liver morphology",
    "anatomic_site": "liver",
    "body_region": "Abdomen",
    "category": "chronic",
    "trajectory_type": "Chronic, present on every abdominal exam",
    "observations": [
        obs("E01", "present", text="Coarsened echotexture with nodular liver surface, cirrhosis."),
        obs("E02", "present", text="Nodular liver contour and capsular retraction, cirrhosis."),
        obs("E03", "present", text="Cirrhotic liver morphology with nodular contour."),
        obs("E06", "present", text="Cirrhotic liver morphology, unchanged."),
        obs("E07", "present", text="Cirrhotic liver morphology."),
        obs("E08", "present", text="Cirrhotic liver, unchanged."),
        obs("E11", "present", text="Cirrhotic liver morphology."),
        obs("E13", "present", text="Coarsened echotexture, nodular surface. Known cirrhosis."),
        obs("E14", "present", text="Cirrhotic liver morphology, stable."),
        obs("E15", "present", text="Cirrhotic liver, unchanged."),
    ],
})

findings.append({
    "id": "F11",
    "name": "Splenomegaly",
    "anatomic_site": "spleen",
    "body_region": "Abdomen",
    "category": "chronic",
    "trajectory_type": "Chronic, slowly progressive",
    "observations": [
        obs("E01", "present", measurement="13.2 cm", text="Spleen measures 13.2 cm, mildly enlarged."),
        obs("E02", "present", measurement="13.8 cm", text="Splenomegaly, 13.8 cm."),
        obs("E03", "present", measurement="14.0 cm", text="Splenomegaly, 14.0 cm."),
        obs("E06", "present", measurement="14.5 cm", temporal_status="increased", text="Splenomegaly, now 14.5 cm, mildly increased."),
        obs("E07", "present", measurement="14.8 cm", text="Splenomegaly, 14.8 cm."),
        obs("E08", "present", measurement="15.0 cm", text="Splenomegaly, 15.0 cm, mildly increased."),
        obs("E11", "present", measurement="15.2 cm", text="Splenomegaly, 15.2 cm."),
        obs("E13", "present", measurement="15.4 cm", text="Spleen measures 15.4 cm, enlarged."),
        obs("E14", "present", measurement="15.8 cm", text="Splenomegaly, 15.8 cm."),
        obs("E15", "present", measurement="16.1 cm", temporal_status="increased", text="Splenomegaly, 16.1 cm, increased."),
    ],
})

findings.append({
    "id": "F12",
    "name": "Cholelithiasis",
    "anatomic_site": "gallbladder",
    "body_region": "Abdomen",
    "category": "chronic",
    "trajectory_type": "Chronic, stable",
    "observations": [
        obs("E01", "present", text="Cholelithiasis."),
        obs("E02", "present", measurement="largest 8 mm", text="Cholelithiasis, largest stone 8 mm. No gallbladder wall thickening."),
        obs("E03", "present", text="Cholelithiasis, noted."),
        obs("E06", "present", text="Cholelithiasis, unchanged."),
        obs("E07", "present", text="Cholelithiasis, unchanged."),
        obs("E08", "present", text="Cholelithiasis."),
        obs("E11", "present", text="Cholelithiasis."),
        obs("E13", "present", text="Multiple gallstones, unchanged."),
        obs("E14", "present", text="Cholelithiasis, stable."),
        obs("E15", "present", text="Cholelithiasis."),
    ],
})

findings.append({
    "id": "F13",
    "name": "Simple renal cysts",
    "anatomic_site": "bilateral kidneys",
    "body_region": "Abdomen",
    "category": "chronic",
    "trajectory_type": "Chronic, stable",
    "observations": [
        obs("E01", "present", measurement="left 1.4 cm, right 0.8 cm", text="Simple cysts in bilateral kidneys, largest left 1.4 cm, right 0.8 cm."),
        obs("E02", "present", measurement="left 1.5 cm, right 0.8 cm", text="Simple renal cysts bilaterally, largest left 1.5 cm, right 0.8 cm."),
        obs("E06", "present", measurement="left 1.5 cm, right 0.9 cm", text="Bilateral simple renal cysts, stable."),
        obs("E08", "present", measurement="left 1.6 cm, right 0.9 cm", text="Bilateral renal cysts, stable."),
        obs("E11", "present", text="Bilateral simple renal cysts, stable."),
        obs("E13", "present", measurement="left 1.6 cm, right 0.9 cm", text="Bilateral simple renal cysts, stable."),
        obs("E14", "present", measurement="left 1.6 cm, right 1.0 cm", text="Bilateral simple renal cysts, unchanged."),
        obs("E15", "present", text="Stable bilateral simple renal cysts."),
    ],
})

findings.append({
    "id": "F14",
    "name": "Nephrolithiasis",
    "anatomic_site": "left kidney lower pole",
    "body_region": "Abdomen",
    "category": "chronic",
    "trajectory_type": "Chronic, slowly increasing",
    "observations": [
        obs("E01", "present", measurement="punctate", text="Punctate left lower pole calculus."),
        obs("E02", "present", measurement="2 mm", text="2 mm left lower pole renal calculus."),
        obs("E06", "present", measurement="2 mm", temporal_status="stable", text="2 mm left lower pole renal calculus, stable."),
        obs("E08", "present", measurement="3 mm", temporal_status="increased", text="Left lower pole calculus now measures 3 mm, slightly increased."),
        obs("E11", "present", measurement="3 mm", temporal_status="stable", text="3 mm left renal calculus, stable."),
        obs("E13", "present", measurement="3 mm", temporal_status="stable", text="Left lower pole renal calculus, 3 mm, stable."),
        obs("E14", "present", measurement="3 mm", temporal_status="stable", text="Left lower pole renal calculus, 3 mm, stable."),
        obs("E15", "present", measurement="4 mm", temporal_status="increased", text="Left renal calculus now 4 mm, mildly increased."),
    ],
})

findings.append({
    "id": "F15",
    "name": "Degenerative changes",
    "anatomic_site": "thoracic spine",
    "body_region": "Spine",
    "category": "chronic",
    "permanent": True,
    "trajectory_type": "Chronic, stable",
    "observations": [
        obs("E11", "present", text="Multilevel degenerative changes of the thoracic spine with anterior osteophytes."),
        obs("E14", "present", text="Degenerative changes of the thoracic spine, stable."),
        obs("E15", "present", text="Thoracic spine degenerative changes, unchanged."),
    ],
})

findings.append({
    "id": "F16",
    "name": "Degenerative changes",
    "anatomic_site": "lumbar spine",
    "body_region": "Spine",
    "category": "chronic",
    "permanent": True,
    "trajectory_type": "Chronic, stable",
    "observations": [
        obs("E02", "present", text="Multilevel lumbar degenerative disc disease and facet arthropathy."),
        obs("E06", "present", text="Lumbar degenerative changes, unchanged."),
        obs("E08", "present", text="Degenerative changes of the lumbar spine."),
        obs("E10", "present", text="Degenerative changes of the lumbar spine."),
        obs("E11", "present", text="Multilevel lumbar degenerative changes, chronic."),
        obs("E14", "present", text="Lumbar degenerative changes, stable."),
        obs("E15", "present", text="Degenerative lumbar spine changes, unchanged."),
    ],
})

findings.append({
    "id": "F17",
    "name": "Atherosclerotic calcification",
    "anatomic_site": "aorta",
    "body_region": "Abdomen",
    "category": "chronic",
    "permanent": True,
    "trajectory_type": "Chronic, stable",
    "observations": [
        obs("E02", "present", text="Atherosclerotic calcifications of the abdominal aorta."),
        obs("E04", "present", text="Atherosclerotic aortic calcifications."),
        obs("E05", "present", text="Aortic calcifications, unchanged."),
        obs("E06", "present", text="Atherosclerotic calcification of the aorta."),
        obs("E08", "present", text="Aortic atherosclerotic disease."),
        obs("E09", "present", text="Atherosclerotic aortic calcifications."),
        obs("E11", "present", text="Atherosclerotic calcifications of the thoracic and abdominal aorta."),
        obs("E14", "present", text="Aortic atherosclerotic calcifications."),
        obs("E15", "present", text="Atherosclerotic calcifications, aorta, stable."),
    ],
})

findings.append({
    "id": "F18",
    "name": "Enlarged prostate",
    "anatomic_site": "prostate",
    "body_region": "Pelvis",
    "category": "chronic",
    "trajectory_type": "Chronic, stable",
    "observations": [
        obs("E02", "present", measurement="4.5 cm", text="Enlarged prostate, 4.5 cm."),
        obs("E06", "present", measurement="4.6 cm", text="Prostatomegaly, 4.6 cm."),
        obs("E08", "present", measurement="4.7 cm", text="Enlarged prostate, 4.7 cm."),
        obs("E11", "present", measurement="4.8 cm", text="Enlarged prostate, 4.8 cm."),
        obs("E14", "present", measurement="4.8 cm", temporal_status="stable", text="Enlarged prostate, 4.8 cm, stable."),
        obs("E15", "present", measurement="4.9 cm", text="Prostatomegaly, 4.9 cm."),
    ],
})

findings.append({
    "id": "F19",
    "name": "Total hip arthroplasty",
    "anatomic_site": "left hip",
    "body_region": "MSK",
    "category": "surgical_history",
    "permanent": True,
    "trajectory_type": "Surgical history, present on every relevant exam",
    "observations": [
        obs("E02", "present", text="Left total hip arthroplasty in expected position."),
        obs("E06", "present", text="Left total hip arthroplasty, unchanged."),
        obs("E08", "present", text="Left total hip arthroplasty in place."),
        obs("E10", "present", text="Left total hip arthroplasty, stable positioning. No periprosthetic fracture."),
        obs("E11", "present", text="Left total hip arthroplasty, stable."),
        obs("E14", "present", text="Left total hip arthroplasty, unchanged."),
        obs("E15", "present", text="Left total hip arthroplasty, stable positioning."),
    ],
})

findings.append({
    "id": "F20",
    "name": "Status post appendectomy",
    "anatomic_site": "right lower quadrant",
    "body_region": "Abdomen",
    "category": "surgical_history",
    "permanent": True,
    "trajectory_type": "Surgical history, present on every relevant exam",
    "observations": [
        obs("E02", "present", text="Prior appendectomy."),
        obs("E06", "present", text="Post-appendectomy changes."),
        obs("E08", "present", text="Status post appendectomy."),
        obs("E11", "present", text="Prior appendectomy."),
        obs("E14", "present", text="Status post appendectomy."),
        obs("E15", "present", text="Post-appendectomy changes."),
    ],
})

# --------------------------------------------------
# HEAD CT FINDINGS (E12 only)
# --------------------------------------------------

findings.append({
    "id": "F21",
    "name": "Lacunar infarcts",
    "anatomic_site": "bilateral basal ganglia",
    "body_region": "Head",
    "category": "chronic",
    "permanent": True,
    "trajectory_type": "Chronic, single observation",
    "observations": [
        obs("E12", "present", characterization="chronic", text="Chronic lacunar infarcts in bilateral basal ganglia."),
    ],
})

findings.append({
    "id": "F22",
    "name": "Small vessel ischemic disease",
    "anatomic_site": "periventricular white matter",
    "body_region": "Head",
    "category": "chronic",
    "permanent": True,
    "trajectory_type": "Chronic, single observation",
    "observations": [
        obs("E12", "present", characterization="chronic, moderate", text="Moderate periventricular and subcortical white matter hypodensities, chronic small vessel ischemic disease."),
    ],
})

findings.append({
    "id": "F23",
    "name": "Orbital wall fracture",
    "anatomic_site": "right medial orbital wall",
    "body_region": "Head",
    "category": "chronic",
    "permanent": True,
    "trajectory_type": "Remote history, single observation",
    "observations": [
        obs("E12", "present", characterization="old, corticated margins", text="Old right medial orbital wall fracture with smooth corticated margins."),
    ],
})

# --------------------------------------------------
# PERTINENT NEGATIVES
# --------------------------------------------------

# Chest
findings.append({
    "id": "F24",
    "name": "Pleural effusion",
    "anatomic_site": "pleural cavity",  # SNOMED CT 91381003 (coarse site; the report stated none)
    "body_region": "Chest",
    "category": "excluded",
    "trajectory_type": "Assessed on chest exams, consistently absent",
    "observations": [
        obs("E04", "absent", text="No pleural effusion."),
        obs("E05", "absent", text="No pleural effusion."),
        obs("E09", "absent", text="No pleural effusion."),
        obs("E11", "absent", text="No pleural effusion."),
    ],
})

findings.append({
    "id": "F25",
    "name": "Pulmonary nodule",
    "anatomic_site": "both lungs",  # SNOMED CT 74101002 (coarse site; the report stated none)
    "body_region": "Chest",
    "category": "excluded",
    "trajectory_type": "Assessed on chest exams, consistently absent",
    "observations": [
        obs("E04", "absent", text="No pulmonary nodule."),
        obs("E05", "absent", text="No pulmonary nodule."),
        obs("E11", "absent", text="No pulmonary nodule."),
    ],
})

findings.append({
    "id": "F26",
    "name": "Cardiomegaly",
    "anatomic_site": "heart",
    "body_region": "Chest",
    "category": "excluded",
    "trajectory_type": "Assessed on chest exams, consistently absent",
    "observations": [
        obs("E04", "absent", text="Normal heart size."),
        obs("E05", "absent", text="Normal cardiac silhouette."),
        obs("E09", "absent", text="Normal heart size, limited on supine film."),
        obs("E11", "absent", text="Normal heart size."),
    ],
})

findings.append({
    "id": "F27",
    "name": "Pneumothorax",
    "anatomic_site": "pleural cavity",  # SNOMED CT 91381003 (coarse site; the report stated none)
    "body_region": "Chest",
    "category": "excluded",
    "trajectory_type": "Assessed on chest exams, absent",
    "observations": [
        obs("E04", "absent", text="No pneumothorax."),
        obs("E09", "absent", text="No pneumothorax."),
        obs("E11", "absent", text="No pneumothorax."),
    ],
})

# Abdomen
findings.append({
    "id": "F28",
    "name": "Hydronephrosis",
    "anatomic_site": "bilateral kidneys",
    "body_region": "Abdomen",
    "category": "excluded",
    "trajectory_type": "Assessed on abdominal exams, consistently absent",
    "observations": [
        obs("E01", "absent", text="No hydronephrosis bilaterally."),
        obs("E02", "absent", text="No hydronephrosis."),
        obs("E06", "absent", text="No hydronephrosis."),
        obs("E08", "absent", text="No hydronephrosis bilaterally."),
        obs("E11", "absent", text="No hydronephrosis."),
        obs("E13", "absent", text="No hydronephrosis."),
        obs("E14", "absent", text="No hydronephrosis."),
        obs("E15", "absent", text="No hydronephrosis."),
    ],
})

findings.append({
    "id": "F29",
    "name": "Biliary ductal dilation",
    "anatomic_site": "biliary tree",
    "body_region": "Abdomen",
    "category": "excluded",
    "trajectory_type": "Assessed on abdominal exams, consistently absent",
    "observations": [
        obs("E01", "absent", measurement="common bile duct 4 mm", text="Common bile duct 4 mm, normal. No biliary dilation."),
        obs("E02", "absent", measurement="common bile duct 4 mm", text="No intrahepatic or extrahepatic biliary dilation. Common bile duct 4 mm."),
        obs("E06", "absent", text="No biliary dilation."),
        obs("E08", "absent", text="Bile ducts are normal in caliber."),
        obs("E11", "absent", text="No biliary dilation."),
        obs("E13", "absent", measurement="common bile duct 5 mm", text="Common bile duct 5 mm, normal. No biliary dilation."),
        obs("E14", "absent", text="No biliary ductal dilation."),
        obs("E15", "absent", text="Biliary tree is normal."),
    ],
})

findings.append({
    "id": "F30",
    "name": "Pancreatic ductal dilation",
    "anatomic_site": "main pancreatic duct",
    "body_region": "Abdomen",
    "category": "excluded",
    "trajectory_type": "Assessed on abdominal CTs, consistently absent",
    "observations": [
        obs("E02", "absent", text="Main pancreatic duct is normal in caliber."),
        obs("E06", "absent", text="No pancreatic ductal dilation."),
        obs("E08", "absent", text="Main pancreatic duct is normal."),
        obs("E11", "absent", text="No pancreatic ductal dilation."),
        obs("E14", "absent", text="Pancreatic duct normal in caliber."),
        obs("E15", "absent", text="No pancreatic ductal dilation."),
    ],
})

findings.append({
    "id": "F31",
    "name": "Hepatic mass (other than segment 6 lesion)",
    "anatomic_site": "liver",
    "body_region": "Abdomen",
    "category": "excluded",
    "trajectory_type": "Assessed on abdominal exams, consistently absent (important in cirrhosis surveillance)",
    "observations": [
        obs("E01", "absent", text="No focal hepatic lesion."),
        obs("E02", "absent", text="No other focal hepatic lesion."),
        obs("E03", "absent", text="No additional hepatic lesion."),
        obs("E06", "absent", text="No new hepatic lesion."),
        obs("E07", "absent", text="No new hepatic lesion."),
        obs("E08", "absent", text="No new focal hepatic lesion."),
        obs("E11", "absent", text="No new hepatic mass."),
        obs("E13", "absent", text="No new focal hepatic lesion."),
        obs("E14", "absent", text="No new hepatic lesion."),
        obs("E15", "absent", text="No new focal hepatic lesion."),
    ],
})

findings.append({
    "id": "F32",
    "name": "Lymphadenopathy",
    "anatomic_site": "abdomen",
    "body_region": "Abdomen",
    "category": "excluded",
    "trajectory_type": "Assessed on abdominal CTs, consistently absent",
    "observations": [
        obs("E02", "absent", text="No pathologic abdominal lymphadenopathy."),
        obs("E06", "absent", text="No lymphadenopathy."),
        obs("E08", "absent", text="No pathologic lymphadenopathy."),
        obs("E11", "absent", text="No abdominal lymphadenopathy."),
        obs("E14", "absent", text="No lymphadenopathy."),
        obs("E15", "absent", text="No pathologic lymphadenopathy."),
    ],
})

findings.append({
    "id": "F33",
    "name": "Bowel obstruction",
    "anatomic_site": "intestines",  # SNOMED CT 113276009 (coarse site; the report stated none)
    "body_region": "Abdomen",
    "category": "excluded",
    "trajectory_type": "Assessed on abdominal CTs, consistently absent",
    "observations": [
        obs("E02", "absent", text="No bowel obstruction."),
        obs("E06", "absent", text="No small or large bowel obstruction."),
        obs("E08", "absent", text="No bowel obstruction."),
        obs("E11", "absent", text="No bowel obstruction or perforation."),
        obs("E14", "absent", text="No bowel obstruction."),
        obs("E15", "absent", text="No obstruction."),
    ],
})

findings.append({
    "id": "F34",
    "name": "Free air",
    "anatomic_site": "peritoneal cavity",  # SNOMED CT 83670000 (coarse site; the report stated none)
    "body_region": "Abdomen",
    "category": "excluded",
    "trajectory_type": "Assessed on abdominal CTs, consistently absent",
    "observations": [
        obs("E02", "absent", text="No pneumoperitoneum."),
        obs("E06", "absent", text="No free air."),
        obs("E08", "absent", text="No pneumoperitoneum."),
        obs("E11", "absent", text="No free air."),
        obs("E14", "absent", text="No pneumoperitoneum."),
        obs("E15", "absent", text="No free air."),
    ],
})

# Head CT pertinent negatives
findings.append({
    "id": "F35",
    "name": "Intracranial hemorrhage",
    "anatomic_site": "intracranial",  # SNOMED CT 128319008 (coarse site; the report stated none)
    "body_region": "Head",
    "category": "excluded",
    "trajectory_type": "Assessed on head CT, absent (primary indication)",
    "observations": [
        obs("E12", "absent", text="No acute intracranial hemorrhage."),
    ],
})

findings.append({
    "id": "F36",
    "name": "Acute intracranial mass or mass effect",
    "anatomic_site": "intracranial",  # SNOMED CT 128319008 (coarse site; the report stated none)
    "body_region": "Head",
    "category": "excluded",
    "trajectory_type": "Assessed on head CT, absent",
    "observations": [
        obs("E12", "absent", text="No mass, midline shift, or hydrocephalus."),
    ],
})

# Trauma pertinent negatives
findings.append({
    "id": "F37",
    "name": "Solid organ injury",
    "anatomic_site": "abdominal viscera",  # SNOMED CT 361295005 (coarse site; the report stated none)
    "body_region": "Abdomen",
    "category": "excluded",
    "trajectory_type": "Assessed on trauma CT, absent",
    "observations": [
        obs("E11", "absent", text="No solid organ laceration or active hemorrhage."),
    ],
})

findings.append({
    "id": "F38",
    "name": "Pelvic fracture",
    "anatomic_site": "pelvis",
    "body_region": "Pelvis",
    "category": "excluded",
    "trajectory_type": "Assessed on pelvis XR and trauma CT, absent",
    "observations": [
        obs("E10", "absent", text="No pelvic fracture. Bones are diffusely osteopenic."),
        obs("E11", "absent", text="No pelvic fracture."),
    ],
})

findings.append({
    "id": "F39",
    "name": "Sternal fracture",
    "anatomic_site": "sternum",
    "body_region": "Chest",
    "category": "excluded",
    "trajectory_type": "Assessed on trauma CT, absent",
    "observations": [
        obs("E11", "absent", text="No sternal fracture."),
    ],
})

findings.append({
    "id": "F40",
    "name": "Thoracic spine fracture",
    "anatomic_site": "thoracic spine",
    "body_region": "Spine",
    "category": "excluded",
    "trajectory_type": "Assessed on trauma CT, absent",
    "observations": [
        obs("E11", "absent", text="No acute thoracic spine fracture."),
    ],
})


# ============================================================
# Build EFLs (per-exam finding lists)
# ============================================================

def build_efls():
    """Build EFL JSON files matching the repo structure."""
    for exam in exams:
        efl = {
            "report_metadata": {
                "patient_id": patient["id"],
                "study_date": exam["date"],
                "modality": exam["modality"],
                "body_region": exam["body_region"],
                "exam_type": exam["type"],
                "procedure_code": procedure_code(exam),
                "setting": exam["setting"],
                "indication": exam["indication"],
            },
            "findings": [],
        }

        for f in findings:
            for o in f["observations"]:
                if o["exam_id"] == exam["id"]:
                    finding_entry = {
                        "finding_name": f["name"],
                        "finding_id": f["id"],
                        "finding_code": finding_code(f),
                        "anatomic_site": f.get("anatomic_site"),
                        "attributes": {
                            "presence": o["presence"],
                            "temporal_status": o.get("temporal_status"),
                            "chronicity": o.get("chronicity"),
                            "characterization": o.get("characterization"),
                            "measurement": o.get("measurement"),
                            "confidence": o.get("confidence"),
                        },
                        "text": o.get("text", ""),
                    }
                    # Remove None values from attributes
                    finding_entry["attributes"] = {
                        k: v for k, v in finding_entry["attributes"].items() if v is not None
                    }
                    efl["findings"].append(finding_entry)

        # Sort: present findings first, then absent
        efl["findings"].sort(key=lambda x: (0 if x["attributes"]["presence"] == "present" else 1, x["finding_name"]))

        filename = f"EFL_{exam['id']}_{exam['date']}_{exam['modality']}.json"
        filepath = os.path.join(EFL_DIR, filename)
        with open(filepath, "w") as fh:
            json.dump(efl, fh, indent=2)

    print(f"EFL files written to: {EFL_DIR}/")


# ============================================================
# Build aggregated IPL
# ============================================================

def build_ipl():
    """Build the aggregated IPL JSON matching the repo structure."""
    ipl_entries = []

    for f in findings:
        obs_list = f["observations"]

        presence_values = [o["presence"] for o in obs_list]
        present_count = sum(1 for p in presence_values if p == "present")
        absent_count = sum(1 for p in presence_values if p == "absent")

        # Derive the entity status (matches manuscript definitions).
        # Status is a downstream derivation from the observation history,
        # never a stored/faithful field:
        #   excluded — assessed and never present (a tracked pertinent negative)
        #   resolved — previously present, absent on the most recent assessment
        #   active   — present now, and new or changing
        #   stable   — present now, unchanged
        # "permanent": True marks findings whose stated language is chronic/
        # remote at first documentation, so a single observation derives
        # stable rather than active.
        CHANGE_WORDS = {"increased", "decreased", "new"}
        last = obs_list[-1]
        if present_count == 0:
            status = "excluded"
        elif last["presence"] == "absent":
            status = "resolved"
        else:
            prev = obs_list[-2] if len(obs_list) > 1 else None
            changing = last.get("temporal_status") in CHANGE_WORDS
            newly_present = (prev is None or prev["presence"] == "absent") and not f.get("permanent", False)
            status = "active" if (changing or newly_present) else "stable"

        # Build observation records with exam metadata
        ipl_observations = []
        for o in obs_list:
            ex = exam_map[o["exam_id"]]
            ipl_obs = {
                "exam_date": ex["date"],
                "exam_type": ex["type"],
                "exam_modality": ex["modality"],
                "finding_name": f["name"],
                "anatomic_site": f.get("anatomic_site"),
                "attributes": {
                    "presence": o["presence"],
                },
                "text": o.get("text", ""),
                "source_exam": o["exam_id"],
            }
            # Add optional attributes ("confidence" is the per-axis hedge map,
            # e.g. {"presence": "hedged"}; an axis absent from the map is definite)
            for attr in ("temporal_status", "chronicity", "characterization", "measurement", "confidence"):
                if o.get(attr):
                    ipl_obs["attributes"][attr] = o[attr]
            ipl_observations.append(ipl_obs)

        dates = [exam_map[o["exam_id"]]["date"] for o in obs_list]
        modalities = list(set(exam_map[o["exam_id"]]["modality"] for o in obs_list))

        entry = {
            "ipl_key": f"{f['id']}:{f['name']}",
            "finding_id": f["id"],
            "canonical_name": f["name"],
            "finding_code": finding_code(f),
            "anatomic_site": f.get("anatomic_site"),
            "body_region": f["body_region"],
            "category": f["category"],
            "status": status,
            "total_observations": len(obs_list),
            "present_count": present_count,
            "absent_count": absent_count,
            "first_observed": min(dates),
            "last_observed": max(dates),
            "modalities": sorted(modalities),
            "presence_timeline": [
                {"exam_date": exam_map[o["exam_id"]]["date"], "presence": o["presence"]}
                for o in obs_list
            ],
            "observations": ipl_observations,
        }
        # Succession linkage: a genuinely distinct sequela entity is linked to
        # the resolved entry it succeeded (a typed relation, not a parent field)
        if f.get("sequela_of"):
            entry["linkages"] = [{"relation": "sequela_of", "target_finding_id": f["sequela_of"]}]
        ipl_entries.append(entry)

    output = {
        "metadata": {
            "patient": patient,
            "compiled_date": "2026-03-18",
            "total_examinations": len(exams),
            "total_ipl_entries": len(ipl_entries),
            "total_observations": sum(e["total_observations"] for e in ipl_entries),
            "date_range": {"first": exams[0]["date"], "last": exams[-1]["date"]},
            "modalities": sorted(set(e["modality"] for e in exams)),
        },
        "exams": [{**e, "procedure_code": procedure_code(e)} for e in exams],
        "ipl": ipl_entries,
    }

    filepath = os.path.join(OUTPUT_DIR, "imaging_problem_list.json")
    with open(filepath, "w") as fh:
        json.dump(output, fh, indent=2)
    print(f"IPL written to: {filepath}")

    return output


# ============================================================
# Compute and print statistics
# ============================================================

def print_statistics():
    total_obs = sum(len(f["observations"]) for f in findings)
    total_present = sum(1 for f in findings for o in f["observations"] if o["presence"] == "present")
    total_absent = sum(1 for f in findings for o in f["observations"] if o["presence"] == "absent")
    total_hedged = sum(1 for f in findings for o in f["observations"] if o.get("confidence"))
    total_findings = len(findings)

    multi_exam = sum(1 for f in findings if len(f["observations"]) > 1)

    status_changes = 0
    for f in findings:
        presences = set(o["presence"] for o in f["observations"])
        if len(presences) > 1:
            status_changes += 1

    obs_per_exam = defaultdict(lambda: {"total": 0, "present": 0, "absent": 0})
    for f in findings:
        for o in f["observations"]:
            obs_per_exam[o["exam_id"]]["total"] += 1
            obs_per_exam[o["exam_id"]][o["presence"]] += 1

    cat_counts = defaultdict(lambda: {"findings": 0, "observations": 0})
    for f in findings:
        cat_counts[f["category"]]["findings"] += 1
        cat_counts[f["category"]]["observations"] += len(f["observations"])

    modality_map = {e["id"]: e["modality"] for e in exams}
    modalities_per_finding = []
    for f in findings:
        mods = set(modality_map[o["exam_id"]] for o in f["observations"])
        modalities_per_finding.append(len(mods))

    cross_modality = sum(1 for m in modalities_per_finding if m > 1)

    print("=" * 65)
    print("EXEMPLAR PATIENT STATISTICS")
    print("=" * 65)
    print(f"Total examinations: {len(exams)}")
    print(f"  CT: {sum(1 for e in exams if e['modality'] == 'CT')}")
    print(f"  US: {sum(1 for e in exams if e['modality'] == 'US')}")
    print(f"  MRI: {sum(1 for e in exams if e['modality'] == 'MRI')}")
    print(f"  XR: {sum(1 for e in exams if e['modality'] == 'XR')}")
    print(f"Date range: {exams[0]['date']} to {exams[-1]['date']}")
    print()
    print(f"Total unique IPL entities (findings): {total_findings}")
    print(f"Total observations: {total_obs}")
    print(f"  Present: {total_present}")
    print(f"  Absent: {total_absent}")
    print(f"  Hedged (confidence axis): {total_hedged}")
    print(f"Consolidation ratio: {total_obs / total_findings:.1f}:1")
    print()
    print(f"Findings tracked across multiple exams: {multi_exam} of {total_findings}")
    print(f"Findings with presence changes: {status_changes}")
    print(f"Findings observed across multiple modalities: {cross_modality}")
    print(f"Avg modalities per finding: {sum(modalities_per_finding)/len(modalities_per_finding):.1f}")
    print()
    print("By category:")
    for cat, counts in sorted(cat_counts.items()):
        print(f"  {cat}: {counts['findings']} findings, {counts['observations']} observations")
    print()
    print("Observations per exam:")
    for e in exams:
        eid = e["id"]
        counts = obs_per_exam[eid]
        print(f"  {eid} ({e['date']}, {e['modality']:>3} {e['type'][:40]:<40}): {counts['total']:>3} obs ({counts['present']:>2} pres, {counts['absent']:>2} abs)")


# ============================================================
# Generate Figure 2 data: Swimlane timeline (CSV for plotting)
# ============================================================

def build_swimlane_data():
    """Output CSV data for a swimlane timeline figure."""
    import csv as csv_mod
    filepath = os.path.join(OUTPUT_DIR, "swimlane_data.csv")
    with open(filepath, "w", newline="") as fh:
        writer = csv_mod.writer(fh)
        writer.writerow(["finding_id", "finding_name", "body_region", "category",
                         "exam_id", "exam_date", "modality", "presence",
                         "confidence", "measurement", "characterization"])
        for f in findings:
            # Skip excluded findings (pertinent negatives) for the swimlane — too noisy
            if f["category"] == "excluded":
                continue
            for o in f["observations"]:
                ex = exam_map[o["exam_id"]]
                writer.writerow([
                    f["id"], f["name"], f["body_region"], f["category"],
                    o["exam_id"], ex["date"], ex["modality"], o["presence"],
                    "hedged" if o.get("confidence") else "",
                    o.get("measurement", ""), o.get("characterization", ""),
                ])
    print(f"Swimlane CSV written to: {filepath}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print_statistics()
    print()
    build_efls()
    build_ipl()
    build_swimlane_data()
    print("\nDone.")
