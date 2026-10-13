---
id: "SYS-13"
question: "How do you manage database migrations and backwards compatibility?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 342
editorial_status: "reviewed"
---

# SYS-13

## Original interview question

How do you manage database migrations and backwards compatibility?

## What the interviewer evaluates

Coordinate Room schema migration with backend compatibility and rollout windows.

## Explanation in Arabic

Database migration محلية لا تكفي لو backend contract تغيرت: مستخدم ممكن يقفز من نسخة قديمة بعد شهور offline، أو app قديمة تكلم server جديد. نحفظ exported schemas، نختبر upgrade paths والبيانات، ونخلي API additive/versioned خلال rollout. تغييرات خطيرة تعمل expand → migrate/backfill → contract، مع feature flag وrollback plan؛ ما نستخدمش destructive fallback على user data.

## Practical walkthrough

مستخدم رجع بعد 6 شهور وفتح DB version 3 بينما الجديد 8؛ migration من 7→8 فقط مش كفاية. احتفظ exported schemas وfixtures من نسخ منشورة، اختبر كل upgrade path والبيانات المهمة، وماتستخدمش destructive migration لسجل لا يُستعاد. Backend في نفس الوقت لازم تقبل APK قديمة خلال window معلنة، فاعمل expand ثم migration ثم contract بعد قياس adoption.

## Why it matters and how it works

Room validates schema and migration paths, but semantic correctness needs row-level tests. Backend must support old clients for a defined window, or return a controlled upgrade requirement. For encrypted files, key/backup migration requires separate recovery. A staged rollout should monitor migration crash rate by source version.

## Worked example

Conceptual compatibility matrix; CI should populate it from shipped variants.

```kotlin
data class CompatibilityCase(
    val oldDbVersion: Int,
    val newDbVersion: Int,
    val oldApiContract: Int,
    val expectedRows: Int,
)
// CI upgrades a real old schema fixture and asserts data + API behavior.
```

## Trade-offs and decision criteria

Additive backend fields ease old-app compatibility but prolong server complexity. Forced upgrades simplify backend but harm offline users and require product policy. Large local migrations can delay startup; plan chunking/recovery where necessary.

## Failure modes

A rename deployed to server before old clients adapt can break them. A destructive Room fallback may wipe drafts. A migration tested only from immediately prior version misses long-offline users. Rolling back APK after one-way DB upgrade can fail.

## Production perspective

A healthcare app tests every supported DB version with encrypted and plaintext fixtures, deploys backward-compatible API first, then stages new client and monitors migration failures. Contract removal occurs only after old-client usage falls below agreed threshold.

## Interview answer — short

“I treat database and backend compatibility as one rollout. I test migrations from shipped schemas with real data, keep server contracts compatible during version skew, stage changes and plan rollback or forward recovery.”

## Interview answer — structured

“For a migration I inventory installed database versions, export schemas and test upgrades with representative rows. At the same time I keep backend changes additive or versioned so older APKs continue to work during rollout. A risky change follows expand, migrate and contract phases rather than deleting an old field on day one. I avoid destructive fallback for user data and monitor crashes by source version. If rollback cannot read the new schema, I plan forward fix or explicit recovery before deployment.”

## Interview answer — deep senior

“Mobile version skew is normal: users may be offline for months while the server changes weekly. I maintain a compatibility matrix across DB schema, API contract and app version. Room migration tests assert both structural validity and business values for each shipped source version. Backend deploys additive fields/endpoints first, client migrates and backfills, then old contract is removed only after usage data and support policy allow it. I plan for low storage, encryption key/backup behavior and interrupted migration. A staged rollout watches migration failure, ANR/startup time and data-loss signals. Rollback is not automatically safe after one-way schema migration, so I prepare a forward patch and preserve source data where feasible. I would keep migration fixtures from actual shipped schemas, including rows with nulls, pending outbox items and historical enum values. A test should verify business data survives, not only that Room accepts the new schema. On the server side, additive responses and dual-read periods let old APKs coexist with new code. I would observe adoption and error rates before contracting an old field. If a minimum version is required, the app needs a safe update path that does not discard unsent local work.”

## How to answer in the interview

- **Why:** users skip releases and backend deploys faster than apps.
- **How:** test old schema fixtures and stage additive API contracts before removal.
- **Trade-off:** compatibility windows increase temporary code and storage cost.
- **Failure case:** destructive migration deletes pending offline operations.
- **Production solution:** migration matrix, rollback plan, and adoption-based deprecation.

## Deep-dive talking points

Draw expand/migrate/contract sequence and old-app/new-server matrix.

## Follow-up questions

- [DAT-11](../dat-11/): How protect local data? **Answer:** exported schemas and upgrade tests from every supported version.
- [SYS-18](../sys-18/): How handle old clients? **Answer:** additive/versioned backend contracts during a defined window.

## Self-check rubric

Can I test old databases, support old APKs and explain rollback limits?

## References and reviewed-on date

- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — schema testing.
- [Android architecture guide](https://developer.android.com/topic/architecture) — persistent models.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
