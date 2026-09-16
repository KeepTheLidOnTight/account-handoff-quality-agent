# Account Handoff Quality Agent

A practical check before sales hands a deal to implementation.

**CSV exports -> Python checks -> Skill review -> Handoff brief**

## Why I built it

A Closed Won deal can still leave the implementation team guessing. The sponsor is missing, the rollout plan is buried in notes, or a customer request reads like an agreed commitment. I built this skill to pull those details into a short, sourced handoff brief. The intended benefit is less kickoff preparation and fewer missed expectations. I have not measured time savings, revenue impact, or customer outcomes.

## What I assumed

The user is a post-sale teammate preparing for kickoff. For this prototype, a documented executive sponsor, implementation timeline, and success criteria are core requirements: any missing one means Blocked. Smaller gaps mean Needs Review. These are business assumptions to validate with the receiving team, not universal Salesforce rules. The five Salesforce-style CSV exports are the external data source; this version does not require a live Salesforce connection.

## How I split the work

Python reads Account, Opportunity, Contact, OpportunityContactRole, and SalesNotes. It selects the Closed Won deal, checks fields and record links, and preserves the evidence. If several deals qualify, the user chooses. The skill then compares CRM fields with notes and produces seven sections covering readiness, gaps, goals, stakeholders, expectations, risks, and a short summary. I kept repeatable checks in code and contextual judgment in the skill. Version one does not update CRM records, contact customers, or run automatically when a deal closes.

## The example I would show

Terrapin Touring Co.'s incomplete handoff is Blocked. A complete version passes the structured checks as Ready. In a third version, CRM still says the corporate pilot starts October 5, but a note records an approved move to November 2 and says other milestones need re-planning. The skill returns Needs Review, cites both sources, and asks for reconciliation. Filled fields alone are not enough.

## Where AI helped, and needed checking

I used AI to draft the skill, validator, and fictional data, then asked it to review its own assumptions and test failure cases. The initial validator could select the wrong deal, accept TBD as complete, and hide broken contact links. Those findings drove the revisions. The package now passes 27 automated tests across the validator's behavior and includes five demo fixtures. A separate agent checked two exports without seeing their expected outcomes. That is useful evidence, but a small check, not proof of reliable judgment across real deals.

## What I would change for production

I would agree on the handoff policy with sales and implementation, add read-only CRM access with least-privilege permissions, and limit who can see or retain customer data. For reliability, I would monitor failed runs, validate export freshness, and make retries safe. At scale, I would fetch only the relevant records and handle API limits. For accuracy, I would evaluate labeled real-world cases, review contradictions with a person, and track missed gaps and false alarms. Any future writeback would need human approval and an audit trail.

*Demo data is entirely fictional and Grateful Dead themed. It contains no real customer records, band biographies, or lyrics.*
