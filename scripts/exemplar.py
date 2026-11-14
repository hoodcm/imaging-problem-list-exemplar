"""What the exemplar's reports say.

This module holds the synthetic patient, the examinations, the finding
concepts, and every finding's observations as its report sentences state them,
in the attribute model of the OIDM report findings annotator. Every finding code
names a concept in an Imaging Findings Workbench taxonomy, and every anatomic
site is an entry of the Anatomic Locations Index 1.0.0. All data are synthetic.
scripts/build_exemplar.py turns this module into the Exam Finding Lists and the
Imaging Problem List.
"""

# ============================================================
# Patient and examinations
# ============================================================

patient = {
    "id": "IPL-EXEMPLAR-001",
    "name": "Synthetic Patient 001",
    "age_at_start": 64,
    "clinical_profile": "MASH cirrhosis with portal hypertension, abdominal aortic aneurysm under surveillance",
    "surgical_history": ["Appendectomy (remote)", "Left total hip arthroplasty (2014)"],
}

exams = [
    {"id": "E01", "date": "2017-03-14", "time": "09:40", "type": "US Abdomen",                              "modality": "US",  "body_region": "ABDOMEN",       "setting": "Outpatient", "indication": "Cirrhosis surveillance"},
    {"id": "E02", "date": "2018-02-06", "time": "10:15", "type": "CT Abdomen/Pelvis with contrast",          "modality": "CT",  "body_region": "ABDOMEN_PELVIS","setting": "Outpatient", "indication": "Elevated AFP, hepatic lesion workup"},
    {"id": "E03", "date": "2018-05-22", "time": "13:30", "type": "MRI Abdomen with contrast (LI-RADS)",      "modality": "MRI", "body_region": "ABDOMEN",       "setting": "Outpatient", "indication": "Hepatic lesion characterization"},
    {"id": "E04", "date": "2019-09-12", "time": "16:20", "type": "CXR (PA and lateral)",                     "modality": "XR",  "body_region": "CHEST",         "setting": "Urgent care","indication": "Cough and fever, rule out pneumonia"},
    {"id": "E05", "date": "2019-10-29", "time": "11:05", "type": "CXR (PA and lateral)",                     "modality": "XR",  "body_region": "CHEST",         "setting": "Outpatient", "indication": "Follow-up pneumonia"},
    {"id": "E06", "date": "2020-06-18", "time": "08:50", "type": "CTA Abdomen/Pelvis",                       "modality": "CT",  "body_region": "ABDOMEN_PELVIS","setting": "Outpatient", "indication": "Abdominal aortic aneurysm surveillance, cirrhosis follow-up"},
    {"id": "E07", "date": "2021-03-09", "time": "14:10", "type": "MRI Abdomen with contrast (LI-RADS)",      "modality": "MRI", "body_region": "ABDOMEN",       "setting": "Outpatient", "indication": "Hepatic lesion follow-up, >2 yr from initial"},
    {"id": "E08", "date": "2021-07-22", "time": "09:25", "type": "CT Abdomen/Pelvis with contrast",          "modality": "CT",  "body_region": "ABDOMEN_PELVIS","setting": "Outpatient", "indication": "Cirrhosis follow-up, worsening LFTs"},
    {"id": "E09", "date": "2022-01-15", "time": "14:05", "type": "XR Chest (portable, supine)",              "modality": "XR",  "body_region": "CHEST",         "setting": "ED",         "indication": "Fall, trauma screening"},
    {"id": "E10", "date": "2022-01-15", "time": "14:12", "type": "XR Pelvis (AP)",                           "modality": "XR",  "body_region": "PELVIS",        "setting": "ED",         "indication": "Fall, trauma screening"},
    {"id": "E11", "date": "2022-01-15", "time": "14:40", "type": "CT Chest/Abdomen/Pelvis with contrast",    "modality": "CT",  "body_region": "CHEST_ABDOMEN_PELVIS", "setting": "ED",  "indication": "Fall, trauma workup"},
    {"id": "E12", "date": "2022-01-15", "time": "14:55", "type": "CT Head without contrast",                 "modality": "CT",  "body_region": "HEAD",          "setting": "ED",         "indication": "Fall, rule out intracranial hemorrhage"},
    {"id": "E13", "date": "2022-04-10", "time": "10:30", "type": "US Abdomen with Doppler",                  "modality": "US",  "body_region": "ABDOMEN",       "setting": "Outpatient", "indication": "Cirrhosis surveillance, portal vein assessment"},
    {"id": "E14", "date": "2023-03-28", "time": "08:45", "type": "CT Abdomen/Pelvis with contrast",          "modality": "CT",  "body_region": "ABDOMEN_PELVIS","setting": "Outpatient", "indication": "Abdominal aortic aneurysm and cirrhosis surveillance"},
    {"id": "E15", "date": "2024-07-16", "time": "11:20", "type": "CTA Abdomen/Pelvis",                       "modality": "CT",  "body_region": "ABDOMEN_PELVIS","setting": "Outpatient", "indication": "Abdominal aortic aneurysm pre-surgical evaluation"},
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

# ============================================================
# Finding vocabulary
# ============================================================
# Each concept is a row of an Imaging Findings Workbench taxonomy: the
# ct.chest-abdomen-pelvis taxonomy, which also serves the ultrasound and MRI
# examinations, ct.head, xr.chest, and xr.msk. "path" lists the concept's
# ancestors in that taxonomy, general to specific.
#
# The OIFM code source is "registry" for a model in the Open Imaging Finding
# Model registry, "minted" for a model whose definition is in
# data/raw/finding_models/, and "assigned" for a code given to the concept for
# this exemplar only, which no registry or definition file holds.

def C(path, oifm, source):
    """One concept: its ancestors' names, its OIFM code, and that code's source."""
    return {"path": tuple(path.split(" > ")) if path else (), "oifm": oifm, "source": source}


CONCEPTS = {
    # Vascular
    "aortic_aneurysm":                  C("vascular_abnormality > vascular_aneurysm > arterial_aneurysm", "OIFM_GMTS_014057", "registry"),
    "aortic_dilation":                  C("vascular_abnormality > vascular_dilation > arterial_dilation", "OIFM_OIDM_787784", "registry"),
    "aortic_rupture":                   C("vascular_abnormality > arterial_abnormality", "OIFM_MGB_989055", "assigned"),
    "aortic_dissection":                C("vascular_abnormality > arterial_abnormality > arterial_dissection", "OIFM_MSFT_573630", "registry"),
    "arterial_calcification":           C("vascular_abnormality > arterial_abnormality", "OIFM_GMTS_022512", "registry"),
    "aortic_atherosclerosis":           C("vascular_abnormality > arterial_abnormality > arterial_atherosclerosis", "OIFM_MGB_650866", "registry"),
    "arterial_contrast_extravasation":  C("vascular_abnormality > arterial_abnormality", "OIFM_MGB_672036", "assigned"),
    "fat_stranding":                    C("extravisceral_abnormality", "OIFM_MGB_168543", "assigned"),
    # Liver, biliary, pancreas, spleen
    "hepatic_lesion":                   C("hepatobiliary_abnormality > liver_abnormality", "OIFM_OIDM_160831", "registry"),
    "cirrhotic_liver_morphology":       C("hepatobiliary_abnormality > liver_abnormality", "OIFM_MGB_433540", "assigned"),
    "nodular_liver_contour":            C("hepatobiliary_abnormality > liver_abnormality", "OIFM_MGB_816014", "assigned"),
    "hepatic_capsular_retraction":      C("hepatobiliary_abnormality > liver_abnormality", "OIFM_MGB_137592", "assigned"),
    "cirrhosis":                        C("hepatobiliary_abnormality > liver_abnormality", "OIFM_GMTS_022460", "registry"),
    "hepatic_laceration":               C("hepatobiliary_abnormality > liver_abnormality", "OIFM_MGB_122996", "assigned"),
    "portal_vein_thrombus":             C("hepatobiliary_abnormality > liver_abnormality > hepatic_vascular_abnormality", "OIFM_MGB_425154", "assigned"),
    "cholelithiasis":                   C("hepatobiliary_abnormality > gallbladder_abnormality", "OIFM_GMTS_022482", "registry"),
    "gallbladder_wall_thickening":      C("hepatobiliary_abnormality > gallbladder_abnormality > gallbladder_wall_abnormality", "OIFM_MGB_410256", "assigned"),
    "biliary_ductal_dilation":          C("hepatobiliary_abnormality > bile_duct_abnormality", "OIFM_GMTS_005226", "registry"),
    "pancreatic_cystic_lesion":         C("pancreatic_abnormality > pancreatic_lesion", "OIFM_MGB_588034", "assigned"),
    "branch_duct_intraductal_papillary_mucinous_neoplasm":
                                        C("pancreatic_abnormality > pancreatic_lesion > pancreatic_neoplasm > intraductal_papillary_mucinous_neoplasm", "OIFM_MGB_219857", "assigned"),
    "pancreatic_ductal_dilation":       C("pancreatic_abnormality > pancreatic_ductal_abnormality", "OIFM_GMTS_002674", "registry"),
    "splenomegaly":                     C("splenic_abnormality", "OIFM_GMTS_003565", "registry"),
    "splenic_laceration":               C("splenic_abnormality", "OIFM_MGB_834584", "assigned"),
    # Peritoneum, bowel, lymph nodes
    "ascites":                          C("peritoneal_abnormality > peritoneal_cavity_abnormality", "OIFM_GMTS_000480", "registry"),
    "pneumoperitoneum":                 C("peritoneal_abnormality > peritoneal_cavity_abnormality", "OIFM_CDE_000228", "registry"),
    "esophageal_varices":               C("gastrointestinal_tract_abnormality > esophageal_abnormality", "OIFM_GMTS_000249", "registry"),
    "small_bowel_obstruction":          C("gastrointestinal_tract_abnormality > bowel_abnormality > small_bowel_abnormality > small_bowel_caliber_abnormality", "OIFM_CDE_000178", "registry"),
    "large_bowel_obstruction":          C("gastrointestinal_tract_abnormality > bowel_abnormality > large_bowel_abnormality > large_bowel_caliber_abnormality", "OIFM_MGB_183080", "assigned"),
    "hollow_viscus_perforation":        C("gastrointestinal_tract_abnormality", "OIFM_MGB_068585", "assigned"),
    "lymph_node_enlargement":           C("lymphatic_abnormality > lymph_node_abnormality", "OIFM_MGB_391371", "assigned"),
    "appendectomy":                     C("gastrointestinal_tract_postsurgical_change > bowel_postsurgical_change > large_bowel_postsurgical_change > appendiceal_postsurgical_change", "OIFM_MGB_285678", "minted"),
    # Urinary and reproductive
    "simple_renal_cyst":                C("urinary_abnormality > renal_abnormality > renal_lesion > renal_cyst", "OIFM_MGB_210162", "assigned"),
    "renal_calculus":                   C("urinary_abnormality > renal_abnormality", "OIFM_OIDM_319506", "registry"),
    "hydronephrosis":                   C("urinary_abnormality > renal_abnormality", "OIFM_OIDM_874812", "registry"),
    "prostate_enlargement":             C("male_reproductive_abnormality > prostatic_abnormality", "OIFM_GMTS_017620", "registry"),
    # Chest
    "consolidation":                    C("lung_abnormality > airspace_opacity", "OIFM_OIDM_628702", "registry"),
    "pneumonia":                        C("lung_abnormality > pulmonary_infection", "OIFM_CDE_000076", "registry"),
    "pulmonary_scarring":               C("lung_abnormality", "OIFM_OIDM_745898", "registry"),
    "pulmonary_nodule":                 C("lung_abnormality > pulmonary_lesion", "OIFM_CDE_000195", "registry"),
    "pleural_effusion":                 C("pleural_abnormality", "OIFM_CDE_000254", "registry"),
    "pneumothorax":                     C("pleural_abnormality", "OIFM_GMTS_023339", "registry"),
    "cardiomegaly":                     C("cardiac_abnormality", "OIFM_GMTS_022537", "registry"),
    # Bones and joints
    "fracture":                         C("osseous_abnormality", "OIFM_OIDM_739317", "registry"),
    "rib_fracture":                     C("osseous_abnormality > fracture", "OIFM_MGB_944849", "registry"),
    "vertebral_compression_fracture":   C("osseous_abnormality > fracture > compression_fracture", "OIFM_CDE_000230", "registry"),
    "pelvic_fracture":                  C("osseous_abnormality > fracture", "OIFM_MGB_437803", "minted"),
    "sternal_fracture":                 C("osseous_abnormality > fracture", "OIFM_MGB_969524", "registry"),
    "periprosthetic_fracture":          C("osseous_abnormality > fracture > perihardware_fracture", "OIFM_MGB_117059", "assigned"),
    "osteopenia":                       C("osseous_abnormality > metabolic_bone_abnormality", "OIFM_MGB_391931", "assigned"),
    "spinal_degeneration":              C("spinal_abnormality", "OIFM_MGB_873240", "assigned"),
    "total_hip_arthroplasty":           C("hardware > arthroplasty > total_joint_arthroplasty", "OIFM_MGB_169189", "minted"),
    # Head
    "lacunar_infarct":                  C("brain_parenchymal_abnormality > ischemic_disease > infarct", "OIFM_OIDM_251340", "registry"),
    "hypoattenuation":                  C("brain_parenchymal_abnormality", "OIFM_OIDM_381117", "registry"),
    "small_vessel_ischemic_disease":    C("brain_parenchymal_abnormality > ischemic_disease", "OIFM_MGB_693165", "assigned"),
    "medial_orbital_wall_fracture":     C("osseous_abnormality > fracture > facial_bone_fracture > orbital_fracture", "OIFM_OIDM_444719", "registry"),
    "intracranial_hemorrhage":          C("brain_parenchymal_abnormality", "OIFM_OIDM_797056", "registry"),
    "mass_effect":                      C("brain_parenchymal_abnormality", "OIFM_OIDM_113253", "registry"),
    "hydrocephalus":                    C("ventricular_abnormality", "OIFM_GMTS_007816", "registry"),
    # Examination quality
    "limited_examination":              C("image_quality_issue", "OIFM_MGB_299896", "assigned"),
}

# Codes that name one finding at different asserted severities, least to most
# severe. A step between them within one entry is a change, as along the
# aortic caliber spectrum from dilation to aneurysm.
SPECTRA = [("aortic_dilation", "aortic_aneurysm")]

# ============================================================
# Authoring helpers
# ============================================================

def obs(exam_id, presence, text, **attrs):
    """One observation as its report sentences state it.

    text is the sentence or sentences the observation comes from. Optional
    attributes: code (a concept other than the entry's), site (a RadLex id
    other than the entry's), words (the site as this sentence states it, where
    it differs from the entry's), laterality, temporal (str or list), chronicity
    (str or list), measurement (list of (value, unit) or (value, unit,
    property)), prior_measurement (the same, for a prior examination's value),
    severity, extent, distribution, aggregate, features (list), hedged (list of
    axes), position_status, interp (list of interpretations, each a concept
    name, ("concept", "hedged"), or ("LI-RADS", category)), and context (list of
    stated causes, each a concept name or ("concept", "hedged")).
    """
    return {"exam_id": exam_id, "presence": presence, "text": text, **attrs}


findings = []


def finding(fid, code, site_id, words, status, observations, laterality=None):
    """Add one entry.

    Args:
        fid: the entry's id.
        code: its finding concept.
        site_id: its Anatomic Locations Index site.
        words: the words its sentences use to state the site, which an
            observation's own words override.
        status: the status the entry is meant to derive, which the build checks.
        observations: its observations in examination order.
        laterality: its side, where the finding has one.
    """
    findings.append({"id": fid, "code": code, "site": site_id, "words": words, "status": status,
                     "laterality": laterality, "observations": observations})
    when = [(exam_map[o["exam_id"]]["date"], exam_map[o["exam_id"]]["time"]) for o in observations]
    assert when == sorted(set(when)), f"{fid}: observations out of examination order"

# ============================================================
# Findings and observations
# ============================================================
# --------------------------------------------------
# SHOWCASE FINDINGS
# --------------------------------------------------

finding("F01", "aortic_aneurysm", "RID905", "infrarenal abdominal aortic", "active", [
    obs("E01", "present", "Infrarenal abdominal aortic aneurysm measuring 3.2 cm.", measurement=[(3.2, "cm")]),
    obs("E02", "present", "Infrarenal abdominal aortic aneurysm measuring 3.5 cm, mildly increased compared to 3.2 cm on the prior ultrasound from March 2017.",
        measurement=[(3.5, "cm")], prior_measurement=[(3.2, "cm")], temporal="larger"),
    obs("E06", "present", "Infrarenal abdominal aortic aneurysm measures 3.9 cm, increased from 3.5 cm.",
        measurement=[(3.9, "cm")], prior_measurement=[(3.5, "cm")], temporal="larger"),
    obs("E08", "present", "Infrarenal aortic aneurysm measures 4.3 cm, increased from 3.9 cm on the prior CTA.", words="infrarenal aortic",
        measurement=[(4.3, "cm")], prior_measurement=[(3.9, "cm")], temporal="larger"),
    obs("E11", "present", "There is a 4.5 cm infrarenal abdominal aortic aneurysm, slightly increased from 4.3 cm on July 2021 CT.",
        measurement=[(4.5, "cm")], prior_measurement=[(4.3, "cm")], temporal="larger"),
    obs("E13", "present", "Infrarenal AAA measures 4.5 cm, unchanged compared to the recent CT from January.", words="infrarenal",
        measurement=[(4.5, "cm")], temporal="unchanged"),
    obs("E14", "present", "Infrarenal abdominal aortic aneurysm measures 4.8 cm, increased from 4.5 cm.",
        measurement=[(4.8, "cm")], prior_measurement=[(4.5, "cm")], temporal="larger"),
    obs("E15", "present", "Infrarenal abdominal aortic aneurysm has increased to 5.1 cm from 4.8 cm on the 2023 study.",
        measurement=[(5.1, "cm")], prior_measurement=[(4.8, "cm")], temporal="larger"),
])

LR = "LI-RADS"
finding("F02", "hepatic_lesion", "RID33242", "segment 6", "stable", [
    obs("E02", "present", "1.8 cm arterially enhancing segment 6 lesion. LI-RADS 3.",
        measurement=[(1.8, "cm")], features=["arterial phase hyperenhancement"], interp=[(LR, "LR-3")]),
    obs("E03", "present", "1.8 cm segment 6 lesion with arterial phase hyperenhancement, unchanged, without washout or capsule appearance. LI-RADS 3.",
        measurement=[(1.8, "cm")], temporal="unchanged",
        features=["arterial phase hyperenhancement", "no washout", "no capsule appearance"], interp=[(LR, "LR-3")]),
    obs("E06", "present", "Segment 6 hepatic lesion measures 1.7 cm, stable.", measurement=[(1.7, "cm")], temporal="unchanged"),
    obs("E07", "present", "Segment 6 lesion 1.7 cm, stable >2 years. Downgraded to LI-RADS 2.",
        measurement=[(1.7, "cm")], temporal="unchanged", interp=[(LR, "LR-2")]),
    obs("E08", "present", "Segment 6 lesion stable at 1.7 cm. LI-RADS 2.",
        measurement=[(1.7, "cm")], temporal="unchanged", interp=[(LR, "LR-2")]),
    obs("E11", "present", "Segment 6 hepatic lesion, stable at 1.7 cm.", measurement=[(1.7, "cm")], temporal="unchanged"),
    obs("E13", "present", "Segment 6 hepatic lesion measures 1.7 cm, stable.", measurement=[(1.7, "cm")], temporal="unchanged"),
    obs("E14", "present", "Segment 6 hepatic lesion measures 1.6 cm, stable. LI-RADS 2.",
        measurement=[(1.6, "cm")], temporal="unchanged", interp=[(LR, "LR-2")]),
    obs("E15", "present", "Segment 6 lesion stable at 1.6 cm.", measurement=[(1.6, "cm")], temporal="unchanged"),
])

finding("F03", "ascites", "RID397", "ascites", "active", [
    obs("E01", "absent", "No ascites."),
    obs("E02", "absent", "No ascites."),
    obs("E03", "absent", "No ascites."),
    obs("E06", "present", "Mild ascites, new.", severity="mild", temporal="new"),
    obs("E07", "present", "Mild ascites, similar to prior.", severity="mild", temporal="unchanged"),
    obs("E08", "present", "Moderate ascites, increased from prior.", severity="moderate", temporal="increased_extent"),
    obs("E11", "present", "Moderate ascites.", severity="moderate"),
    obs("E13", "present", "Mild ascites, decreased from prior.", severity="mild", temporal="decreased_extent"),
    obs("E14", "absent", "Ascites has resolved.", temporal="resolved"),
    obs("E15", "present", "Mild ascites, new.", severity="mild", temporal="new"),
])

finding("F04", "portal_vein_thrombus", "RID1208", "portal vein", "stable", [
    obs("E01", "absent", "No portal vein thrombus."),
    obs("E02", "absent", "No portal vein thrombus."),
    obs("E06", "absent", "No portal vein thrombus."),
    obs("E08", "absent", "No portal vein thrombus."),
    obs("E11", "present", "New acute non-occlusive portal vein thrombus.",
        temporal="new", chronicity="acute", features=["non-occlusive"]),
    obs("E13", "present", "Non-occlusive portal vein thrombus, unchanged.",
        temporal="unchanged", features=["non-occlusive"]),
    obs("E14", "present", "Chronic non-occlusive portal vein thrombus.",
        chronicity="chronic", features=["non-occlusive"]),
    obs("E15", "present", "Chronic portal vein thrombus, unchanged.", temporal="unchanged", chronicity="chronic"),
])

IPMN = "branch_duct_intraductal_papillary_mucinous_neoplasm"
finding("F05", "pancreatic_cystic_lesion", "RID174", "pancreatic body", "stable", [
    obs("E02", "present", "1.2 cm pancreatic body cyst communicating with main pancreatic duct, side-branch IPMN.",
        measurement=[(1.2, "cm")], features=["communicates with main pancreatic duct"], interp=[IPMN]),
    obs("E06", "present", "Pancreatic body cystic lesion measures 1.2 cm, stable, side-branch IPMN.",
        measurement=[(1.2, "cm")], temporal="unchanged", interp=[IPMN]),
    obs("E07", "present", "1.2 cm pancreatic body cystic lesion, stable, side-branch IPMN.",
        measurement=[(1.2, "cm")], temporal="unchanged", interp=[IPMN]),
    obs("E08", "present", "Pancreatic body cystic lesion stable at 1.2 cm, likely side-branch IPMN.",
        measurement=[(1.2, "cm")], temporal="unchanged", interp=[(IPMN, "hedged")]),
    obs("E11", "present", "Stable 1.2 cm pancreatic body cyst, side-branch IPMN.",
        measurement=[(1.2, "cm")], temporal="unchanged", interp=[IPMN]),
    obs("E13", "present", "Probable pancreatic body cyst, incompletely evaluated due to overlying bowel gas.",
        hedged=["presence"]),
    obs("E14", "present", "Pancreatic body cystic lesion measures 1.2 cm, unchanged, side-branch IPMN.",
        measurement=[(1.2, "cm")], temporal="unchanged", interp=[IPMN]),
    obs("E15", "present", "Stable 1.2 cm side-branch IPMN cyst, pancreatic body.",
        measurement=[(1.2, "cm")], temporal="unchanged", interp=[IPMN]),
])

finding("F06", "consolidation", "RID1315", "right lower lobe", "resolved", [
    obs("E04", "present", "Right lower lobe consolidation, pneumonia.", interp=["pneumonia"]),
    obs("E05", "absent", "Prior right lower lobe consolidation has resolved.", temporal="resolved"),
])

# The report sentences describe the left 7th and 8th rib fractures together.
# They are two fractures, so they are two entries: each sentence yields one
# observation for each rib, and both observations keep the whole sentence.
RIB_SENTENCES = [
    ("E09", "Acute nondisplaced fractures of the left 7th and 8th ribs.",
     dict(chronicity="acute", features=["nondisplaced"], words="left 7th and 8th ribs")),
    ("E11", "Acute nondisplaced left 7th and 8th rib fractures.",
     dict(chronicity="acute", features=["nondisplaced"])),
    ("E14", "Healed left 7th and 8th rib fractures with callus formation.",
     dict(chronicity="healed", features=["callus"])),
    ("E15", "Healed left 7th and 8th rib fractures, unchanged.",
     dict(chronicity="healed", temporal="unchanged")),
]
for rib_id, ordinal, site_id in (("F07", "7th", "RID28591_RID6157_RID5824"), ("F42", "8th", "RID28591_RID6158_RID5824")):
    finding(rib_id, "rib_fracture", site_id, "left 7th and 8th rib", "stable",
            [obs(e, "present", t, laterality="left", **a) for e, t, a in RIB_SENTENCES], laterality="left")

finding("F08", "vertebral_compression_fracture", "RID29196", "L4", "stable", [
    obs("E11", "present", "Acute L4 compression fracture with 20% height loss.",
        chronicity="acute", measurement=[(20, "%", "height loss")]),
    obs("E14", "present", "Healed L4 compression fracture with 20% height loss.",
        chronicity="healed", measurement=[(20, "%", "height loss")]),
    obs("E15", "present", "Healed L4 compression fracture with 20% height loss, unchanged.",
        chronicity="healed", temporal="unchanged", measurement=[(20, "%", "height loss")]),
])

finding("F09", "esophageal_varices", "RID95", "esophageal", "stable", [
    obs("E02", "present", "Small esophageal varices.", extent="small", aggregate=True),
    obs("E03", "present", "Small esophageal varices, unchanged.", extent="small", temporal="unchanged", aggregate=True),
    obs("E06", "present", "Small esophageal varices, unchanged.", extent="small", temporal="unchanged", aggregate=True),
    obs("E07", "present", "Small esophageal varices, stable.", extent="small", temporal="unchanged", aggregate=True),
    obs("E08", "present", "Medium-sized esophageal varices, increased from small.", extent="medium", temporal="larger", aggregate=True),
    obs("E11", "present", "Medium-sized esophageal varices.", extent="medium", aggregate=True),
    obs("E14", "present", "Large esophageal varices, increased.", extent="large", temporal="larger", aggregate=True),
    obs("E15", "present", "Large esophageal varices, stable.", extent="large", temporal="unchanged", aggregate=True),
])

# --------------------------------------------------
# A DIFFERENT KIND OF FINDING AFTER A RESOLVED ONE: the scarring is its own
# entry, since it is not the consolidation in another phase, as each fracture
# above is one fracture in two phases. The cause the radiologist named stays on
# the observation as clinical context, and no link joins the two entries.
# --------------------------------------------------

finding("F41", "pulmonary_scarring", "RID1315", "right lower lobe", "stable", [
    obs("E11", "present", "Chronic linear scarring in the right lower lobe, sequela of prior pneumonia.",
        chronicity="chronic", features=["linear"], context=["pneumonia"]),
    obs("E14", "present", "Right lower lobe scarring, unchanged.", temporal="unchanged"),
    obs("E15", "present", "Right lower lobe scarring, stable.", temporal="unchanged"),
])

# --------------------------------------------------
# BACKGROUND AND CHRONIC FINDINGS
# --------------------------------------------------

# Each liver observation the reports state is its own entry, each interpreted as
# cirrhosis.
finding("F10", "cirrhotic_liver_morphology", "RID58", "liver", "stable", [
    obs("E03", "present", "Cirrhotic liver morphology with nodular contour and capsular retraction.", interp=["cirrhosis"]),
    obs("E06", "present", "Cirrhotic liver morphology, unchanged.", temporal="unchanged", interp=["cirrhosis"]),
    obs("E07", "present", "Cirrhotic liver morphology.", interp=["cirrhosis"]),
    obs("E08", "present", "Cirrhotic liver morphology, unchanged.", temporal="unchanged", interp=["cirrhosis"]),
    obs("E11", "present", "Cirrhotic liver morphology.", interp=["cirrhosis"]),
    obs("E14", "present", "Cirrhotic liver morphology, stable.", temporal="unchanged", interp=["cirrhosis"]),
    obs("E15", "present", "Cirrhotic liver morphology, unchanged.", temporal="unchanged", interp=["cirrhosis"]),
])

finding("F44", "nodular_liver_contour", "RID58", "liver", "stable", [
    obs("E01", "present", "Nodular liver surface, cirrhosis.", interp=["cirrhosis"]),
    obs("E02", "present", "Nodular liver contour and capsular retraction, cirrhosis.", interp=["cirrhosis"]),
    obs("E03", "present", "Cirrhotic liver morphology with nodular contour and capsular retraction.", interp=["cirrhosis"]),
    obs("E13", "present", "Nodular liver surface, unchanged, consistent with cirrhosis.",
        temporal="unchanged", interp=["cirrhosis"]),
])

finding("F45", "hepatic_capsular_retraction", "RID58", "liver", "stable", [
    obs("E02", "present", "Nodular liver contour and capsular retraction, cirrhosis.", interp=["cirrhosis"]),
    obs("E03", "present", "Cirrhotic liver morphology with nodular contour and capsular retraction.", interp=["cirrhosis"]),
])

finding("F11", "splenomegaly", "RID86", "splenomegaly", "active", [
    obs("E01", "present", "Spleen measures 13.2 cm, mildly enlarged.", words="spleen", measurement=[(13.2, "cm")], severity="mild"),
    obs("E02", "present", "Splenomegaly, 13.8 cm.", measurement=[(13.8, "cm")]),
    obs("E03", "present", "Splenomegaly, 14.0 cm.", measurement=[(14.0, "cm")]),
    obs("E06", "present", "Splenomegaly, 14.5 cm, mildly increased.", measurement=[(14.5, "cm")], temporal="larger"),
    obs("E07", "present", "Splenomegaly, 14.8 cm.", measurement=[(14.8, "cm")]),
    obs("E08", "present", "Splenomegaly, 15.0 cm, mildly increased.", measurement=[(15.0, "cm")], temporal="larger"),
    obs("E11", "present", "Splenomegaly, 15.2 cm.", measurement=[(15.2, "cm")]),
    obs("E13", "present", "Spleen measures 15.4 cm, enlarged.", words="spleen", measurement=[(15.4, "cm")]),
    obs("E14", "present", "Splenomegaly, 15.8 cm.", measurement=[(15.8, "cm")]),
    obs("E15", "present", "Splenomegaly, 16.1 cm, increased.", measurement=[(16.1, "cm")], temporal="larger"),
])

# A collection keeps the size of its largest member on the collection's entry.
finding("F12", "cholelithiasis", "RID187", "cholelithiasis", "stable", [
    obs("E01", "present", "Cholelithiasis.", aggregate=True),
    obs("E02", "present", "Cholelithiasis, largest stone 8 mm.", measurement=[(8, "mm", "largest member")], aggregate=True),
    obs("E03", "present", "Cholelithiasis.", aggregate=True),
    obs("E06", "present", "Cholelithiasis, unchanged.", temporal="unchanged", aggregate=True),
    obs("E07", "present", "Cholelithiasis, unchanged.", temporal="unchanged", aggregate=True),
    obs("E08", "present", "Cholelithiasis.", aggregate=True),
    obs("E11", "present", "Cholelithiasis.", aggregate=True),
    obs("E13", "present", "Multiple gallstones, unchanged.", words="gallstones", temporal="unchanged", aggregate=True),
    obs("E14", "present", "Cholelithiasis, stable.", temporal="unchanged", aggregate=True),
    obs("E15", "present", "Cholelithiasis.", aggregate=True),
])

# The kidneys are paired, so the bilateral cysts are one entry per side.
RENAL_CYST_SENTENCES = [
    ("E01", "Simple cysts in bilateral kidneys, largest left 1.4 cm, right 0.8 cm.", "simple_renal_cyst", None, (1.4, 0.8)),
    ("E02", "Simple renal cysts bilaterally, largest left 1.5 cm, right 0.8 cm.", "simple_renal_cyst", None, (1.5, 0.8)),
    ("E06", "Bilateral simple renal cysts, stable.", "simple_renal_cyst", "unchanged", None),
    ("E08", "Bilateral simple renal cysts, stable.", "simple_renal_cyst", "unchanged", None),
    ("E11", "Bilateral simple renal cysts, stable.", "simple_renal_cyst", "unchanged", None),
    ("E13", "Bilateral simple renal cysts, stable.", "simple_renal_cyst", "unchanged", None),
    ("E14", "Bilateral simple renal cysts, unchanged.", "simple_renal_cyst", "unchanged", None),
    ("E15", "Stable bilateral simple renal cysts.", "simple_renal_cyst", "unchanged", None),
]
for cyst_id, side, site_id, i in (("F13", "left", "RID29663", 0), ("F43", "right", "RID29662", 1)):
    cyst_obs = []
    for e, t, code, temporal, sizes in RENAL_CYST_SENTENCES:
        a = {"code": code, "laterality": side, "aggregate": True, **({"words": "kidneys"} if e == "E01" else {})}
        if temporal:
            a["temporal"] = temporal
        if sizes:
            a["measurement"] = [(sizes[i], "cm", "largest member")]
        cyst_obs.append(obs(e, "present", t, **a))
    finding(cyst_id, "simple_renal_cyst", site_id, "renal", "stable", cyst_obs, laterality=side)

finding("F14", "renal_calculus", "RID29663", "left renal", "active", [
    obs("E01", "present", "Punctate left renal calculus.", laterality="left", features=["punctate"]),
    obs("E02", "present", "2 mm left renal calculus.", laterality="left", measurement=[(2, "mm")]),
    obs("E06", "present", "2 mm left renal calculus, stable.", laterality="left", measurement=[(2, "mm")], temporal="unchanged"),
    obs("E08", "present", "Left renal calculus measures 3 mm, slightly increased.", laterality="left", measurement=[(3, "mm")], temporal="larger"),
    obs("E11", "present", "3 mm left renal calculus, stable.", laterality="left", measurement=[(3, "mm")], temporal="unchanged"),
    obs("E13", "present", "Left renal calculus, 3 mm, stable.", laterality="left", measurement=[(3, "mm")], temporal="unchanged"),
    obs("E14", "present", "Left renal calculus, 3 mm, stable.", laterality="left", measurement=[(3, "mm")], temporal="unchanged"),
    obs("E15", "present", "Left renal calculus measures 4 mm, mildly increased.", laterality="left", measurement=[(4, "mm")], temporal="larger"),
], laterality="left")

finding("F15", "spinal_degeneration", "RID34572", "thoracic spine", "stable", [
    obs("E11", "present", "Degenerative changes of the thoracic spine."),
    obs("E14", "present", "Degenerative changes of the thoracic spine, stable.", temporal="unchanged"),
    obs("E15", "present", "Thoracic spine degenerative changes, unchanged.", temporal="unchanged"),
])

finding("F16", "spinal_degeneration", "RID34573", "lumbar", "stable", [
    obs("E02", "present", "Lumbar degenerative changes."),
    obs("E06", "present", "Lumbar degenerative changes, unchanged.", temporal="unchanged"),
    obs("E08", "present", "Degenerative changes of the lumbar spine."),
    obs("E11", "present", "Lumbar degenerative changes, chronic.", chronicity="chronic"),
    obs("E14", "present", "Lumbar degenerative changes, stable.", temporal="unchanged"),
    obs("E15", "present", "Degenerative lumbar spine changes, unchanged.", temporal="unchanged"),
])

ATH = "aortic_atherosclerosis"
finding("F17", "arterial_calcification", "RID905", "abdominal aorta", "stable", [
    obs("E02", "present", "Atherosclerotic calcifications of the abdominal aorta.", aggregate=True, interp=[ATH]),
    obs("E06", "present", "Atherosclerotic calcifications of the abdominal aorta.", aggregate=True, interp=[ATH]),
    obs("E08", "present", "Atherosclerotic calcifications of the abdominal aorta.", aggregate=True, interp=[ATH]),
    obs("E11", "present", "Atherosclerotic calcifications of the abdominal aorta.", aggregate=True, interp=[ATH]),
    obs("E14", "present", "Abdominal aortic atherosclerotic calcifications.", words="abdominal aortic", aggregate=True, interp=[ATH]),
    obs("E15", "present", "Atherosclerotic calcifications of the abdominal aorta, stable.", temporal="unchanged", aggregate=True, interp=[ATH]),
])

finding("F18", "prostate_enlargement", "RID343", "prostate", "stable", [
    obs("E02", "present", "Enlarged prostate, 4.5 cm.", measurement=[(4.5, "cm")]),
    obs("E06", "present", "Enlarged prostate, 4.6 cm.", measurement=[(4.6, "cm")]),
    obs("E08", "present", "Enlarged prostate, 4.5 cm.", measurement=[(4.5, "cm")]),
    obs("E11", "present", "Enlarged prostate, 4.6 cm.", measurement=[(4.6, "cm")]),
    obs("E14", "present", "Enlarged prostate, 4.6 cm, stable.", measurement=[(4.6, "cm")], temporal="unchanged"),
    obs("E15", "present", "Enlarged prostate, 4.6 cm.", measurement=[(4.6, "cm")]),
])

finding("F19", "total_hip_arthroplasty", "RID2640_RID5824", "hip", "stable", [
    obs("E02", "present", "Left total hip arthroplasty in expected position.", laterality="left", position_status="satisfactory"),
    obs("E06", "present", "Left total hip arthroplasty, unchanged.", laterality="left", temporal="unchanged"),
    obs("E08", "present", "Left total hip arthroplasty in place.", laterality="left", position_status="satisfactory"),
    obs("E10", "present", "Left total hip arthroplasty, unchanged.", laterality="left", temporal="unchanged"),
    obs("E11", "present", "Left total hip arthroplasty, stable.", laterality="left", temporal="unchanged"),
    obs("E14", "present", "Left total hip arthroplasty, unchanged.", laterality="left", temporal="unchanged"),
    obs("E15", "present", "Left total hip arthroplasty, unchanged.", laterality="left", temporal="unchanged"),
], laterality="left")

finding("F20", "appendectomy", "RID168", "appendectomy", "stable", [
    obs("E02", "present", "Status post appendectomy."),
    obs("E06", "present", "Status post appendectomy."),
    obs("E08", "present", "Status post appendectomy."),
    obs("E11", "present", "Status post appendectomy."),
    obs("E14", "present", "Status post appendectomy."),
    obs("E15", "present", "Status post appendectomy."),
])

# Head CT findings (E12 only)
finding("F21", "lacunar_infarct", "RID6537", "bilateral basal ganglia", "stable", [
    obs("E12", "present", "Chronic lacunar infarcts in bilateral basal ganglia.",
        laterality="bilateral", chronicity="chronic", aggregate=True),
], laterality="bilateral")

finding("F22", "hypoattenuation", "RID13857", "periventricular white matter", "stable", [
    obs("E12", "present", "Moderate chronic periventricular white matter hypodensities, compatible with small vessel ischemic disease.",
        chronicity="chronic", severity="moderate", aggregate=True, interp=["small_vessel_ischemic_disease"]),
])

finding("F23", "medial_orbital_wall_fracture", "RID9573_RID5825", "right medial orbital wall", "stable", [
    obs("E12", "present", "Old right medial orbital wall fracture with smooth corticated margins.",
        laterality="right", chronicity="remote", features=["smooth corticated margins"]),
], laterality="right")

# Statements about the examination's quality describe one examination, not the
# patient, so each stays in its EFL and no IPL entry aggregates it.
examination_statements = [
    ("L01", "limited_examination", "RID170",
     obs("E13", "present", "Probable pancreatic body cyst, incompletely evaluated due to overlying bowel gas.",
         words="pancreatic body")),
]

finding("F56", "osteopenia", "RID13209", "osteopenia", "stable", [
    obs("E10", "present", "Bones are diffusely osteopenic.", words="bones", distribution="diffuse"),
    obs("E11", "present", "Diffuse osteopenia.", distribution="diffuse"),
])

# --------------------------------------------------
# FINDINGS STATED ONLY AS ABSENT
# --------------------------------------------------

# Chest
finding("F24", "pleural_effusion", "RID1362", "pleural", "excluded", [
    obs("E04", "absent", "No pleural effusion."),
    obs("E05", "absent", "No pleural effusion."),
    obs("E09", "absent", "No pleural effusion."),
    obs("E11", "absent", "No pleural effusion."),
])

finding("F25", "pulmonary_nodule", "RID1301", "pulmonary", "excluded", [
    obs("E04", "absent", "No pulmonary nodule."),
    obs("E05", "absent", "No pulmonary nodule."),
    obs("E11", "absent", "No pulmonary nodule."),
])

finding("F26", "cardiomegaly", "RID1385", "heart", "excluded", [
    obs("E04", "absent", "Normal heart size."),
    obs("E05", "absent", "Normal heart size."),
    obs("E09", "absent", "Normal heart size."),
    obs("E11", "absent", "Normal heart size."),
])

finding("F27", "pneumothorax", "RID1362", "pneumothorax", "excluded", [
    obs("E04", "absent", "No pneumothorax."),
    obs("E09", "absent", "No pneumothorax."),
    obs("E11", "absent", "No pneumothorax."),
])

# Abdomen
finding("F28", "hydronephrosis", "RID205", "hydronephrosis", "excluded", [
    obs("E01", "absent", "No hydronephrosis."),
    obs("E02", "absent", "No hydronephrosis."),
    obs("E06", "absent", "No hydronephrosis."),
    obs("E08", "absent", "No hydronephrosis."),
    obs("E11", "absent", "No hydronephrosis."),
    obs("E13", "absent", "No hydronephrosis."),
    obs("E14", "absent", "No hydronephrosis."),
    obs("E15", "absent", "No hydronephrosis."),
])

finding("F29", "biliary_ductal_dilation", "RID33652", "biliary", "excluded", [
    obs("E01", "absent", "No biliary ductal dilation."),
    obs("E02", "absent", "No biliary ductal dilation."),
    obs("E06", "absent", "No biliary ductal dilation."),
    obs("E08", "absent", "Bile ducts are normal in caliber.", words="bile ducts"),
    obs("E11", "absent", "No biliary ductal dilation."),
    obs("E13", "absent", "No biliary ductal dilation."),
    obs("E14", "absent", "No biliary ductal dilation."),
    obs("E15", "absent", "No biliary ductal dilation."),
])

finding("F30", "pancreatic_ductal_dilation", "RID177", "pancreatic ductal", "excluded", [
    obs("E02", "absent", "Main pancreatic duct is normal in caliber.", words="main pancreatic duct"),
    obs("E06", "absent", "No pancreatic ductal dilation."),
    obs("E08", "absent", "Main pancreatic duct is normal in caliber.", words="main pancreatic duct"),
    obs("E11", "absent", "No pancreatic ductal dilation."),
    obs("E14", "absent", "Pancreatic duct normal in caliber.", words="pancreatic duct"),
    obs("E15", "absent", "No pancreatic ductal dilation."),
])

# A negation scoped to new lesions is its own entry and never matches the named
# segment VI lesion.
finding("F31", "hepatic_lesion", "RID58", "hepatic", "excluded", [
    obs("E06", "absent", "No new hepatic lesion.", temporal="new"),
    obs("E07", "absent", "No new hepatic lesion.", temporal="new"),
    obs("E08", "absent", "No new focal hepatic lesion.", temporal="new"),
    obs("E11", "absent", "No new hepatic lesion.", temporal="new"),
    obs("E13", "absent", "No new focal hepatic lesion.", temporal="new"),
    obs("E14", "absent", "No new hepatic lesion.", temporal="new"),
    obs("E15", "absent", "No new focal hepatic lesion.", temporal="new"),
])

finding("F32", "lymph_node_enlargement", "RID28854", "abdominal", "excluded", [
    obs("E02", "absent", "No abdominal lymphadenopathy."),
    obs("E06", "absent", "No abdominal lymphadenopathy."),
    obs("E08", "absent", "No abdominal lymphadenopathy."),
    obs("E11", "absent", "No abdominal lymphadenopathy."),
    obs("E14", "absent", "No abdominal lymphadenopathy."),
    obs("E15", "absent", "No abdominal lymphadenopathy."),
])

finding("F33", "small_bowel_obstruction", "RID132", "small bowel", "excluded", [
    obs("E02", "absent", "No small bowel obstruction."),
    obs("E06", "absent", "No small or large bowel obstruction.", words="small or large bowel"),
    obs("E08", "absent", "No small bowel obstruction."),
    obs("E11", "absent", "No small bowel obstruction or perforation."),
    obs("E14", "absent", "No small bowel obstruction."),
    obs("E15", "absent", "No small bowel obstruction."),
])

finding("F57", "large_bowel_obstruction", "RID152", "large bowel", "excluded", [
    obs("E06", "absent", "No small or large bowel obstruction."),
])

finding("F55", "hollow_viscus_perforation", "RID94", "perforation", "excluded", [
    obs("E11", "absent", "No small bowel obstruction or perforation."),
])

finding("F34", "pneumoperitoneum", "RID397", "pneumoperitoneum", "excluded", [
    obs("E02", "absent", "No pneumoperitoneum."),
    obs("E06", "absent", "No pneumoperitoneum."),
    obs("E08", "absent", "No pneumoperitoneum."),
    obs("E11", "absent", "No pneumoperitoneum."),
    obs("E14", "absent", "No pneumoperitoneum."),
    obs("E15", "absent", "No pneumoperitoneum."),
])

finding("F51", "gallbladder_wall_thickening", "RID187", "gallbladder", "excluded", [
    obs("E02", "absent", "No gallbladder wall thickening."),
])

# Aorta, at the surveillance CTs
finding("F46", "aortic_rupture", "RID905", "rupture", "excluded", [
    obs("E06", "absent", "No evidence of rupture or dissection."),
])

finding("F47", "aortic_dissection", "RID905", "dissection", "excluded", [
    obs("E06", "absent", "No evidence of rupture or dissection."),
])

finding("F48", "fat_stranding", "RID431", "periaortic", "excluded", [
    obs("E11", "absent", "No periaortic fat stranding."),
])

# Head CT
finding("F35", "intracranial_hemorrhage", "RID6383_RID9080", "intracranial", "excluded", [
    obs("E12", "absent", "No intracranial hemorrhage."),
])

finding("F36", "mass_effect", "RID6383_RID9080", "mass effect", "excluded", [
    obs("E12", "absent", "No mass effect or hydrocephalus."),
])

finding("F58", "hydrocephalus", "RID6383_RID9080", "hydrocephalus", "excluded", [
    obs("E12", "absent", "No mass effect or hydrocephalus."),
])

# Trauma
finding("F37", "hepatic_laceration", "RID58", "hepatic", "excluded", [
    obs("E11", "absent", "No hepatic or splenic laceration."),
])

finding("F59", "splenic_laceration", "RID86", "splenic", "excluded", [
    obs("E11", "absent", "No hepatic or splenic laceration."),
])

finding("F60", "arterial_contrast_extravasation", "RID56", "extravasation", "excluded", [
    obs("E11", "absent", "No active contrast extravasation."),
])

finding("F38", "pelvic_fracture", "RID2507", "pelvic", "excluded", [
    obs("E10", "absent", "No pelvic fracture."),
    obs("E11", "absent", "No pelvic fracture."),
])

finding("F53", "periprosthetic_fracture", "RID2640_RID5824", "periprosthetic", "excluded", [
    obs("E10", "absent", "No periprosthetic fracture.", laterality="left"),
], laterality="left")

finding("F39", "sternal_fracture", "RID2473", "sternal", "excluded", [
    obs("E11", "absent", "No sternal fracture."),
])

finding("F40", "fracture", "RID34572", "thoracic spine", "excluded", [
    obs("E11", "absent", "No thoracic spine fracture."),
])
