**Saved example run · Fictional data · Default export**

This assessment was prepared from a saved validator run. It is available for the walkthrough; opening it does not run the agent. The companion file is `blocked-validation.json`.

### Handoff Readiness

**Blocked.** The structured baseline and final assessment agree. Three required CRM fields are blank: executive sponsor, implementation timeline, and success criteria. Notes provide useful context, but do not fill those CRM gaps. [CRM O: `Executive_Sponsor__c`, `Implementation_Timeline__c`, `Success_Criteria__c`]

### Missing / Incomplete Information

- **Blocking — executive sponsor:** Not Confirmed. Scarlet is a Decision Maker and primary contact; neither establishes executive sponsorship. [CRM O: `Executive_Sponsor__c`; CRM R1: `Role`, `IsPrimary`]
- **Blocking — implementation timeline:** Not Confirmed. Early October is the customer's desired start, not an agreed schedule. [CRM O: `Implementation_Timeline__c`; Sales Notes N1]
- **Blocking — success criteria:** Not Confirmed. The commercial note explicitly says specific metrics were not finalized. [CRM O: `Success_Criteria__c`; Sales Notes N3]
- **Additional CRM gaps:** Account implementation notes and all three contact phone numbers are blank. Kickoff scheduling is the next step, but its owner and date are Not Confirmed. [CRM A: `Implementation_Notes__c`; CRM C1–C3: `Phone`; CRM O: `NextStep`]

**Context recovered from notes:** Casey owns the technical rollout. The customer wants a corporate-first phase, requires SSO before broad rollout, and needs at least two weeks' notice for identity-team configuration. These details remain note evidence. [Sales Notes N1–N2]

### Customer Goals

Standardize security operations across six acquired venues and improve executive reporting. Scarlet wants one operating model and a monthly view of security posture, with measurable progress to show the CIO before the end of Q4. No measurable acceptance criteria are confirmed. [CRM A: `Customer_Goals__c`; CRM O: `Primary_Business_Problem__c`; Sales Notes N1, N3]

### Key Stakeholders

- **Scarlet Begonia — VP, Information Security.** Decision Maker and sole primary contact. Executive sponsorship is Not Confirmed. [CRM C1: name/title; CRM R1: `Role`, `IsPrimary`; CRM O: `Executive_Sponsor__c`]
- **Casey Jones — Director, Security Engineering.** Technical Buyer and confirmed technical owner. [CRM C2: name/title; CRM R2: `Role`; CRM O: `Technical_Owner__c`; Sales Notes N1]
- **Jack Straw — Procurement Manager.** Procurement role; confirmed procurement is complete. [CRM C3: name/title; CRM R3: `Role`; Sales Notes N3]

The CIO is an unnamed reporting audience. Their project ownership is Not Confirmed. [Sales Notes N3]

### Commitments / Expectations

The customer would like deployment to begin in early October and expects the Wall of Sound implementation team to help plan the rollout. A vendor commitment to that assistance is Not Confirmed. Casey requires SSO before broad rollout and at least two weeks' notice for identity-team configuration. Q4 progress is a desired outcome, not a Q4 completion promise. [Sales Notes N1–N3]

### Risks / Open Questions

- Who will explicitly accept executive sponsorship and escalation responsibility? [CRM O: `Executive_Sponsor__c`]
- What timeline can both teams agree, including identity-team notice, SSO validation, the corporate phase, and venue expansion? [CRM O: `Implementation_Timeline__c`; Sales Notes N1–N2]
- What metrics, baselines, targets, and measurement dates will define success? [CRM O: `Success_Criteria__c`; Sales Notes N3]
- Who will schedule kickoff, by when, and what planning help will the vendor provide? [CRM O: `NextStep`; Sales Notes N2]

### Handoff Summary

Terrapin Touring wants consistent security operations across six venues and clearer executive reporting. Casey is the technical owner; Scarlet is the primary decision maker. The handoff remains blocked until executive sponsorship, an agreed timeline, and measurable success criteria are documented. Before kickoff, resolve the SSO dependency, identity-team notice, and expected planning support. [CRM O: sponsor, timeline, success criteria, technical owner; CRM R1; Sales Notes N1–N3]

<details>
<summary>Source key — full record references</summary>

- **CRM O:** `Opportunity.csv`, `0065g00003OPP001AAH`.
- **CRM A:** `Account.csv`, `0015g00002ABCDeAAH`.
- **CRM C1:** `Contact.csv`, `0035g00004CON001AAH`; **C2:** `0035g00004CON002AAH`; **C3:** `0035g00004CON003AAH`. Name/title references use `FirstName`, `LastName`, and `Title`.
- **CRM R1:** `OpportunityContactRole.csv`, `00K5g00001OCR001AAH`; **R2:** `00K5g00001OCR002AAH`; **R3:** `00K5g00001OCR003AAH`.
- **Sales Notes N1:** `SalesNotes.csv`, `a0N5g00001NOTE01AAH`, 2026-08-18, Discovery Call.
- **Sales Notes N2:** `SalesNotes.csv`, `a0N5g00001NOTE02AAH`, 2026-08-27, Technical Validation.
- **Sales Notes N3:** `SalesNotes.csv`, `a0N5g00001NOTE03AAH`, 2026-09-04, Commercial Review.

</details>
