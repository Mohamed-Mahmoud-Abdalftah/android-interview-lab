---
id: MOCK-005
status: reviewed
---
# MOCK-005 — Production and security

**Recommended time:** 75 minutes. **Default:** Learning Mode; scoring is optional and self-reported. Read the rubric before starting.

## Question-only interview

1. **PRO-Q001:** How would you threat-model a payment return link before writing code?
2. **PRO-Q002:** Why is checking whether a URL contains your domain insecure, and what should a strict parser validate?
3. **PRO-Q003:** Why is an intent filter not a security boundary, and how do you protect a privileged Android component?
4. **PRO-Q004:** A verified App Link contains `status=success`. Why must the backend still authorize and confirm the payment?
5. **PRO-Q005:** Which tests would you require before claiming a deep-link payment flow is secure enough to release?
6. **PRO-Q006:** How do you decide whether application data belongs in Room or DataStore?
7. **PRO-Q007:** A Room upgrade works from version 3 to 4 but crashes for users on version 1. How do you investigate and fix it?
8. **PRO-Q008:** Review code that writes a local entity, calls the network inside a Room transaction, and then inserts an outbox row. What would you change?
9. **PRO-Q009:** Design the migration verification strategy for a large Android app with several supported installed versions.
10. **PRO-Q010:** What tests and production evidence distinguish migration failure, database corruption, lock contention, and DataStore read failure?
11. **PRO-Q011:** A senior review exposes this failure: عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين. Explain Timeout taxonomy, choose a correction, and name evidence that would prove or falsify it.
12. **PRO-Q012:** A senior review exposes this failure: عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين. Explain Retry safety, choose a correction, and name evidence that would prove or falsify it.

## Answer key

1. **PRO-Q001:** I identify assets, actors, entry points, and trust boundaries, then list concrete abuse cases. Each mitigation gets evidence at the right layer: parser tests, device routing tests, and backend authorization tests. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q001.md)
2. **PRO-Q002:** I parse the URL structurally and compare an exact allowed origin and path. I reject duplicate or unknown fields and convert accepted values to constrained types. Parsing still does not authorize the operation. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q002.md)
3. **PRO-Q003:** Intent filters route messages; they do not authorize callers. I minimize exported components and enforce permission, input, and business authorization checks at the component boundary. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q003.md)
4. **PRO-Q004:** Domain verification protects link routing, not payment authority. The backend checks the authenticated user's ownership and the provider-backed order state, then returns the source-of-truth result. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q004.md)
5. **PRO-Q005:** I require evidence across the full boundary chain: parser tests, Android routing and component tests, domain verification on a signed build, and API authorization and idempotency tests. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q005.md)
6. **PRO-Q006:** I choose from the data contract. Relational, queryable state with multi-row invariants belongs in Room. Small application settings that are read and updated as one value fit DataStore. I also define ownership, migration, and corruption behavior instead of choosing solely by API convenience. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q006.md)
7. **PRO-Q007:** I reproduce from an exported version-one database, not a fresh install. I inspect the registered migration graph and execute the full path with representative rows. The fix is a tested forward migration with data and constraint assertions, followed by a staged rollout and version-specific monitoring. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q007.md)
8. **PRO-Q008:** I atomically persist the local state and durable outbox, then close the transaction. A worker performs the remote call outside the database lock. A second short transaction conditionally applies the response using mutation or version identity, which also rejects stale completions. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q008.md)
9. **PRO-Q009:** My release gate is a matrix from every supported installed schema to the target. Each path runs against an exported file with representative data and verifies both Room schema validation and business invariants. I add staged rollout telemetry and a forward recovery plan because binary rollback may be schema-incompatible. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q009.md)
10. **PRO-Q010:** I classify failures before recovery. Version-specific open errors point to migration logic, integrity failures point toward corruption, and timing plus transaction traces reveal contention. DataStore I/O and corruption follow separate policies. Tests reproduce each boundary, while telemetry records versions, duration, and typed outcomes without user content. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q010.md)
11. **PRO-Q011:** Connect, read, call, and application deadlines have different meanings and ownership. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q011.md)
12. **PRO-Q012:** Retry only classified transient failures and only when operation semantics are safe or idempotent. [Complete answer](../Interview-Question-Bank/Model-Answers/PRO-Q012.md)

## Published rubric

Score each answer 0–4: **0** absent/unsafe, **1** definition only, **2** correct core contract, **3** mechanism plus failure/test, **4** senior trade-off, evidence boundary, and clear communication. Coding questions also require compiling logic, boundary tests, and honest complexity. The score is practice evidence, never a hiring guarantee.

## Debrief

Record three items: the first wrong assumption, the slowest explanation, and the missing test. Return to linked lessons before repeating this pack. Do not memorize the answer key wording.
