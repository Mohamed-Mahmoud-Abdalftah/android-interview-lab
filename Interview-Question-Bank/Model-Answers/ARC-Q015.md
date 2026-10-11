---
id: ARC-Q015-ANSWER
question_id: ARC-Q015
status: reviewed
---
# ARC-Q015 — Complete model answer

<p dir="rtl" lang="ar">أختبر DAO transaction للentity/outbox، restart بعد كل نقطة، worker مرتين بنفس mutation، network ينجح والرد يضيع، responses بترتيب معكوس، version conflict، migration، وUI stream بعد refresh failure. API fake/server test تثبت idempotency؛ unit in-memory وحدها لا تثبت durability.</p>

**Spoken answer:** “I inject crashes and duplicate execution around the local transaction and remote call, then verify one durable user intent, stable idempotency identity, preserved conflicts, and a local stream that remains consistent.”

**Common wrong answer:** Testing only that a mocked repository returns cached data when a Boolean `isOnline` is false.

**Follow-up 1:** Why test a lost response after server success? It creates the critical retry case where the client is uncertain but the remote effect already exists.

**Follow-up 2:** What does WorkManager success prove? It proves that worker invocation completed under its result contract, not that every business mutation is correct without repository assertions.

**Rubric:** Include transactions, restart, duplicate execution, lost response, ordering, conflict, migration, UI observation, and API idempotency.
