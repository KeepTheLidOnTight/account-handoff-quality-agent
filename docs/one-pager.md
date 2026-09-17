# Baton

## Why I built it

When an account moves between internal teams, the next owner needs a quick, reliable view of the customer: what was sold, what matters now, and what still needs a decision. Baton turns that handoff into one account deck so the new team can start with the right context and open work.

## Simple assumptions

Someone starts a handoff when an account changes owner or team. They provide the date, the outgoing team, and the incoming team. Baton uses the CRM export and call notes as the shared record for the deck.

## A concrete example

Terrapin Touring Co. moves from Sales to Product Onboarding on September 16. The handoff deck captures the customer goal, key contacts, and the work Sales promised. When the account moves again, Baton adds the new handoff to the same deck and keeps the earlier record in place. The current owner can quickly see what is still open, who owns it, and when it is due.

## How Baton works

1. A person triggers a handoff when an owner or team changes.
2. Baton reads the account records and notes, checks for key handoff details, and creates or updates that account's deck.
3. The team reviews the deck, completes the open items, and leaves feedback so the next handoff gets better.

## Human in the loop

AI helps organize the information and point out missing details. A person reviews the deck before using it, confirms what is true, and decides what should happen next.

## What I would add in production

I would connect Baton to Apollo's API so it can pull the right account context when a handoff starts. I would keep the manual trigger, add simple feedback on every deck, and use that feedback to improve the handoff checks over time. Teams could also set their own required fields and notification rules.

*All names, records, dates, and results in this demo are fictional.*
