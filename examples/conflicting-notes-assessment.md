**Saved example run · Fictional data · Conflicting-notes export**

This assessment was prepared from a saved validator run. It is available for the walkthrough; opening it does not run the agent. The companion file is `conflicting-notes-validation.json`.

### Handoff Readiness

**Needs Review.** The structured baseline is **Ready**, with no script-reported issues. Contextual review changes the result: CRM still shows an October 5 pilot, while the September 14 note records joint approval to move it to November 2. The same note says downstream milestones and measurement deadlines need replanning. [CRM O: `Implementation_Timeline__c`, `Success_Criteria__c`; Sales Notes N4–N5]

The change note explicitly replaces the earlier pilot agreement. Its relevance comes from the recorded approval and replacement, not simply its later date. The handoff still needs a reconciled plan. [Sales Notes N4–N5]

### Missing / Incomplete Information

- **Blocking fields:** None are blank or placeholders. [CRM O: `Executive_Sponsor__c`, `Implementation_Timeline__c`, `Success_Criteria__c`]
- **Review — current timeline:** CRM's pilot and SSO dates are stale. A replacement SSO date and revised venue rollout dates are Not Confirmed. The notes approve a November 2 pilot, but CRM has not caught up. [CRM O: `Implementation_Timeline__c`; CRM A: `Implementation_Notes__c`; Sales Notes N5]
- **Review — measurement deadlines:** Revised deadlines are Not Confirmed. The earlier numeric targets are documented, but their timing needs replanning. [CRM O: `Success_Criteria__c`; Sales Notes N4–N5]
- **Additional gaps:** Contact phone numbers and the implementation lead's personal identity are Not Confirmed. [CRM C1–C3: `Phone`; Sales Notes N4–N5]

### Customer Goals

Standardize security operations across six venues and improve executive visibility. The September 10 agreement specified six-venue dashboard coverage, at least 95% of priority alerts appearing within 15 minutes, and mean investigation time of at most 42 minutes against a 60-minute baseline. The original November 30 and December 18 deadlines cannot yet be relied on. [CRM A: `Customer_Goals__c`; CRM O: `Success_Criteria__c`; Sales Notes N4–N5]

### Key Stakeholders

- **Scarlet Begonia — VP, Information Security.** Decision Maker, sole primary contact, and explicit executive sponsor responsible for cross-team escalations. [CRM C1: name/title; CRM R1: `Role`, `IsPrimary`; CRM O: `Executive_Sponsor__c`; Sales Notes N4]
- **Casey Jones — Director, Security Engineering.** Technical Buyer and technical owner. [CRM C2: name/title; CRM R2: `Role`; CRM O: `Technical_Owner__c`; Sales Notes N4]
- **Jack Straw — Procurement Manager.** Procurement role; confirmed procurement is complete. [CRM C3: name/title; CRM R3: `Role`; Sales Notes N3]

The unnamed Wall of Sound implementation lead joined Scarlet and Casey in approving the pilot change. The unnamed CIO is a reporting audience; project ownership is Not Confirmed. [Sales Notes N3, N5]

### Commitments / Expectations

The September 10 agreement established an October 5 corporate pilot and November 2–30 venue rollout, with SSO required before broad rollout. The vendor lead accepted initial rollout-planning assistance. [CRM O: `Implementation_Timeline__c`; Sales Notes N4]

The September 14 change moves the pilot to November 2 because the identity team cannot support October 2 SSO validation. It supplies no replacement SSO date or venue schedule. CRM still assigns Casey kickoff scheduling by September 17 and identity-team notice by September 18; confirm how those actions fit the revised plan. [CRM O: `NextStep`; Sales Notes N5]

### Risks / Open Questions

- Reconcile the opportunity and account timeline with the approved change; confirm the replacement SSO validation date. [CRM O: `Implementation_Timeline__c`; CRM A: `Implementation_Notes__c`; Sales Notes N5]
- Agree new venue rollout milestones. The original venue start now falls on the revised pilot start. [CRM O: `Implementation_Timeline__c`; Sales Notes N4–N5]
- Reconfirm measurement dates and whether the agreed targets remain feasible. Do not assume deadlines shift automatically. [CRM O: `Success_Criteria__c`; Sales Notes N5]

### Handoff Summary

Terrapin Touring has confirmed ownership, goals, and measurable targets, but its handoff needs review. The notes approve moving the pilot to November 2 while CRM retains the old plan. Before the receiving team relies on the handoff, reconcile the dates and agree a new SSO schedule, venue rollout, and measurement deadlines. [CRM O: ownership, timeline, success criteria; Sales Notes N4–N5]

<details>
<summary>Source key — full record references</summary>

- **CRM O:** `Opportunity.csv`, `0065g00003OPP001AAH`.
- **CRM A:** `Account.csv`, `0015g00002ABCDeAAH`.
- **CRM C1:** `Contact.csv`, `0035g00004CON001AAH`; **C2:** `0035g00004CON002AAH`; **C3:** `0035g00004CON003AAH`. Name/title references use `FirstName`, `LastName`, and `Title`.
- **CRM R1:** `OpportunityContactRole.csv`, `00K5g00001OCR001AAH`; **R2:** `00K5g00001OCR002AAH`; **R3:** `00K5g00001OCR003AAH`.
- **Sales Notes N3:** `SalesNotes.csv`, `a0N5g00001NOTE03AAH`, 2026-09-04, Commercial Review.
- **Sales Notes N4:** `SalesNotes.csv`, `a0N5g00001NOTE04AAH`, 2026-09-10, Wall of Sound Handoff Plan Confirmed.
- **Sales Notes N5:** `SalesNotes.csv`, `a0N5g00001NOTE05AAH`, 2026-09-14, Wall of Sound Pilot Schedule Changed.

</details>
