// IPL code systems, value sets, and extensions. SUSHI compiles this file with sushi-config.yaml beside it.

CodeSystem: IPLStatus
Id: ipl-status
Title: "IPL entry status"
Description: "The status an IPL entry derives from its observation history."
* ^status = #draft
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* #active "active" "The latest observation states the finding new or changed."
* #stable "stable" "The latest observation states the finding present and unchanged."
* #resolved "resolved" "The latest observation states the finding absent after it was present."
* #excluded "excluded" "Every observation states the finding absent."
* #closed "closed" "Every observation states the finding absent, and a finding of its type was later reported within its site."

CodeSystem: IPLStatusRule
Id: ipl-status-rule
Title: "IPL status rule"
Description: "The rule that set an IPL entry's status."
* ^status = #draft
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* #absent-never-present "absent never present" "The report states an absence, and no earlier report stated the finding present."
* #absent-after-present "absent after present" "The report states an absence after an earlier presence."
* #absent-after-resolved "absent after resolved" "The report states an absence after the entry has resolved."
* #stated-new "stated new" "The radiologist reported the finding new."
* #stated-change "stated change" "The radiologist stated a change."
* #stated-unchanged "stated unchanged" "The radiologist stated no change."
* #first-stated-old "first stated old" "The radiologist stated the finding chronic, remote, or healed at its first observation or when present after an absence."
* #first-observation "first observation" "The radiologist reported the finding for the first time, with no comparison wording and no stated age that predates the examination."
* #present-after-absence "present after absence" "The radiologist reported the finding present after an absence, including a recurrence after resolution, with no comparison wording and no stated age that predates the examination."
* #attribute-contradicts "attribute contradicts" "The radiologist wrote no comparison wording, and a stated attribute contradicts its last stated value."
* #nothing-contradicts "nothing contradicts" "The radiologist wrote no comparison wording, and no stated attribute contradicts its last stated value."
* #closed-by-subsequent-finding "closed by subsequent finding" "The entry holds only absences, and a radiologist reported a finding of its type present within its site after the last absence, so that finding's entry carries the status."

CodeSystem: IPLCertainty
Id: ipl-certainty
Title: "IPL certainty"
Description: "Whether the radiologist stated an element plainly or hedged it."
* ^status = #draft
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* #definite "definite" "The radiologist stated the element plainly."
* #hedged "hedged" "The radiologist hedged the element."

CodeSystem: IPLAttribute
Id: ipl-attribute
Title: "IPL attribute"
Description: "The OIDM report findings annotator's attributes, each with its values beneath it, its size attribute named measurement, plus the IPL's prior measurement, clinical context, and interpretation."
* ^status = #draft
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* ^hierarchyMeaning = #is-a
* #presence "presence" "Finding presence status (polarity only — which way the radiologist leans)"
  * #present "present"
  * #absent "absent"
* #certainty "certainty" "Assertion modality: which axes the radiologist hedged (omitted = definite)"
* #laterality "laterality" "Which side of the body"
  * #left "left"
  * #right "right"
  * #bilateral "bilateral"
* #temporal_status "change from prior" "How finding compares to prior studies"
  * #unchanged "unchanged"
  * #new "new"
  * #resolved "resolved"
  * #increased "increased"
  * #decreased "decreased"
* #chronicity "chronicity" "Time course or disease stage"
  * #acute "acute"
  * #subacute "subacute"
  * #chronic "chronic"
  * #remote "remote"
  * #evolving "evolving"
  * #resolving "resolving"
  * #healing "healing"
  * #healed "healed"
* #measurement "current measurement" "The values the report states for this examination"
* #prior_measurement "prior measurement" "The values the report states the finding had on an earlier examination"
* #severity "severity" "The stated grade: a severity or size word"
  * #small "small"
  * #mild "mild"
  * #mild_to_moderate "mild to moderate"
  * #moderate "moderate"
  * #moderate_to_severe "moderate to severe"
  * #severe "severe"
  * #large "large"
* #anatomic_site "anatomic site" "Compound anatomic terms"
* #features "features" "Finding-specific descriptive properties that cannot exist independently"
* #multiple "multiple" "The statement covers more than one finding of a type"
* #insertion_site "insertion site" "Where the device enters"
* #tip_location "tip location" "Where device tip terminates"
* #integrity "integrity" "Device structural integrity"
  * #intact "intact"
  * #discontinuous "discontinuous"
* #clinical_context "clinical context" "A cause or clinical state the radiologist named for the finding."
* #interpretation "interpretation" "A diagnosis or category the radiologist attached to the finding."

ValueSet: IPLStatusRuleValueSet
Id: ipl-status-rule
Title: "IPL status rule"
Description: "Every IPL status rule."
* ^status = #draft
* ^experimental = false
* include codes from system IPLStatusRule

ValueSet: IPLStatusValueSet
Id: ipl-status
Title: "IPL entry status"
Description: "Every IPL entry status."
* ^status = #draft
* ^experimental = false
* include codes from system IPLStatus

ValueSet: IPLPresenceValueSet
Id: ipl-presence
Title: "IPL presence"
Description: "The values of the presence attribute."
* ^status = #draft
* ^experimental = false
* include codes from system IPLAttribute where concept descendent-of #presence

ValueSet: IPLLateralityValueSet
Id: ipl-laterality
Title: "IPL laterality"
Description: "The values of the laterality attribute."
* ^status = #draft
* ^experimental = false
* include codes from system IPLAttribute where concept descendent-of #laterality

ValueSet: IPLTemporalStatusValueSet
Id: ipl-temporal-status
Title: "IPL change from prior"
Description: "The values of the change from prior attribute."
* ^status = #draft
* ^experimental = false
* include codes from system IPLAttribute where concept descendent-of #temporal_status

ValueSet: IPLChronicityValueSet
Id: ipl-chronicity
Title: "IPL chronicity"
Description: "The values of the chronicity attribute."
* ^status = #draft
* ^experimental = false
* include codes from system IPLAttribute where concept descendent-of #chronicity

ValueSet: IPLSeverityValueSet
Id: ipl-severity
Title: "IPL severity"
Description: "The values of the severity attribute."
* ^status = #draft
* ^experimental = false
* include codes from system IPLAttribute where concept descendent-of #severity

ValueSet: IPLIntegrityValueSet
Id: ipl-integrity
Title: "IPL integrity"
Description: "The values of the integrity attribute."
* ^status = #draft
* ^experimental = false
* include codes from system IPLAttribute where concept descendent-of #integrity

Extension: EntryStatusRule
Id: entry-status-rule
Title: "Entry status rule"
Description: "The rule that set an IPL entry's status, on the List entry whose flag carries the status."
* ^status = #draft
* ^experimental = false
* ^context[0].type = #element
* ^context[0].expression = "List.entry"
* value[x] only Coding
* valueCoding from IPLStatusRuleValueSet (required)

Extension: EntryClosedBy
Id: entry-closed-by
Title: "Entry closed by"
Description: "For an entry of only absences, the later observation of a finding of its type within its site that closed it."
* ^status = #draft
* ^experimental = false
* ^context[0].type = #element
* ^context[0].expression = "List.entry"
* value[x] only Reference(Observation)
