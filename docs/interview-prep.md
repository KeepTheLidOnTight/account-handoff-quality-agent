# Interview prep

Use these as speaking notes. The goal is to explain your decisions comfortably,
not memorize every sentence. The statements below describe this project; add
personal experience only if it is something you actually did.

## Your 30-second introduction

I built Baton, a skill for the point where a deal moves from
sales to implementation or customer success. It reads CRM-style records and
sales notes, checks what's missing, and gives the receiving team a brief with
the context and questions they need before kickoff. Python handles the record
checks. The model handles the language in the notes. I used a fictional customer
so I could test different handoff problems without using employer data.

## 1. Why does this matter to a revenue team?

**Your answer**

A signed deal can leave a lot of unanswered questions for the team that takes
over. They need to know what the customer is trying to achieve, who owns the
work, and what sales led the customer to expect. That information is often split
between CRM fields and call notes. I wanted to reduce the time spent piecing it
together and make gaps visible before kickoff. I haven't measured the savings
yet, so I'd treat that as a hypothesis to test with the receiving team.

**Show:** the default Terrapin handoff. It has three missing core fields, but
the notes still contain useful details about SSO and identity-team notice.

**If they ask how you'd measure value:** compare preparation time and the number
of clarification requests on similar handoffs. Also track missed commitments
and whether reviewers agree with the agent's findings. A longer-term measure
could be time to the first agreed customer outcome; don't attribute every change
in onboarding speed to this tool.

## 2. What did you assume?

**Your answer**

I assumed the deal is already Closed Won and the receiving team is preparing
for kickoff. For this version, the sponsor, implementation timeline, and success
criteria have to be documented in the CRM. I assumed stakeholders belong to the
same account as the deal. Those are choices for the demo, not rules every company
uses. I'd validate them with sales and the receiving team before rolling this out.

**Be ready to explain:** missing next steps or a technical owner require review
in this version. Some teams would make those blocking requirements too. The
field priorities should follow the actual handoff process.

**If they ask why CSVs:** the exercise accepts structured files. CSVs let me
prove the workflow with repeatable inputs and no credentials. The current
integration reads files; it does not connect to Salesforce. The object names
and relationships are Salesforce-style, with a mock notes export and custom fields.

## 3. Why a skill plus a script?

**Your answer**

Some of this work should behave the same way every time. Selecting the right
opportunity, checking whether a field is empty, and verifying contact links are
good jobs for a script. Understanding whether a customer requested a date or
actually agreed to it needs context. The skill tells the model how to review
that evidence, cite its sources, and return the same useful structure each time.

**The data flow:** five CSV files feed the Python validator. It returns the
selected account and opportunity, the linked stakeholders, and the notes with
their IDs. The model uses that evidence to write the handoff assessment.

**Why not just paste everything into a model?** Record selection and joins would
be harder to verify, and repeated runs could make different choices. The script
makes those steps explicit and testable.

**Why not just a script?** A nonblank field can still be wrong. In the conflict
example, CRM says the pilot starts October 5. A note records an approved move
to November 2 and says the remaining dates need replanning. Python preserves
both sources. The skill explains why the handoff still needs review.

**Why not MCP?** MCP could provide live data. It would not replace the handoff
policy or the need to interpret evidence. I started with files to test those
decisions before adding authentication and integration failure modes.

**What you left out:** a custom UI, automatic CRM updates, a live connector,
and a numerical quality score. The three statuses are easier to explain for
this small demo.

## 4. Where did AI help, and where didn't you trust it?

**Your answer**

I used AI to help draft the skill, the validator, the mock data, and the tests.
I also used it to review the first version. That review found real problems:
the script picked the first opportunity, accepted placeholders like TBD, and
could hide a broken contact link. I had those behaviors corrected and tested.
For the notes, I want the model to extract context, but every important claim
needs a source and uncertainty needs to stay visible.

**Your strongest example:** the original rule blocked a handoff only when two
fields were empty. The current rule treats any missing core prerequisite as
blocking. This was a business-policy change, not just a coding fix.

**Know exactly what was checked:**

- 27 automated tests cover the Python behavior, including invalid inputs and
  evidence preservation. They do not measure model accuracy.
- Five fixture sets demonstrate different outcomes.
- An independent agent reviewed two unnamed exports without the expected answers.
  It returned Ready for the complete case and Needs Review for the conflicting case.
  That is a small behavioral check, not a production evaluation.

**Avoid saying:** "The tests prove the AI is accurate," "I wrote all the code
myself," or "I manually checked every test." Explain the actual AI-assisted process.

**If they ask about hallucination:** a Decision Maker is not automatically an
executive sponsor. A CIO mentioned in a note is not automatically a project owner.
The skill requires those distinctions and keeps unsupported details Not Confirmed.
Those instructions reduce risk; they don't guarantee perfect model behavior.

## 5. What would you harden for production?

**Your answer**

First I'd agree on the handoff requirements and test a larger set of real,
appropriately protected examples with the receiving team. Then I'd add a live
connector with limited permissions, clear error handling, and logs so we can
explain each result. I'd keep a person responsible for resolving contradictions
and approving any CRM changes. I wouldn't turn the demo's assumptions into a
company-wide gate without that work.

| Area | Concrete next step |
| --- | --- |
| Reliability | Validate changing schemas, handle API failures and retries, and make repeat runs safe. |
| Security | Use least-privilege access, protect customer notes, set retention rules, and treat note text as untrusted input. |
| Scale | Process the selected deal and related records instead of validating a whole CSV export each time. Trigger runs from the real handoff process. |
| Accuracy | Build labeled examples with edge cases, measure missed gaps and false alarms, and review model or prompt changes against that set. |

## Questions they may push on

**Why block a handoff if the answer is in the notes?**

That's the conservative policy I chose for this POC. The tool surfaces the note
so a person can confirm it and update the record. It keeps "we found something
useful" separate from "the required handoff field is complete." A different
team might choose another policy, but it should be an explicit choice.

**Does Ready mean the implementation can start?**

It means the supplied evidence is ready for handoff under these rules.
Dependencies like SSO still need to be completed on the agreed schedule.

**What happens when the script says Ready but the model finds a conflict?**

The final result becomes Needs Review, with both sources cited. The model cannot
lower a blocking or review result by pretending a note filled a CRM field.

**What if the data is broken?**

The script returns an input error and no assessment. A broken join is different
from a legitimate deal that is missing handoff information.

**How do you know the newest note is right?**

A later date alone isn't enough. The conflict example explicitly records joint
approval of a schedule change. Even then, the CRM and downstream milestones
still need reconciliation. The agent explains the disagreement; it doesn't
silently choose a source and update the record.

## Rehearse in this order

1. Explain the business problem in 30 seconds without mentioning Python.
2. Walk through the CSV-to-script-to-skill flow in one minute.
3. Show the conflicting-dates example and explain the two readiness results.
4. Name one concrete defect found in the first version and how it was tested.
5. Give one production improvement in each of the four areas above.

If you can't explain a line of code or a rule, say what you understand and inspect
it. A clear account of the tradeoffs is more useful than trying to sound fluent
in implementation details you haven't learned yet.
