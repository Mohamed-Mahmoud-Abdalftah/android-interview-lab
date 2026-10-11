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

“For a migration I inventory installed database versions, export schemas and test upgrades with representative rows. At the same time I keep backend changes additive or versioned so older APKs continue to work during rollout. A risky change follows expand, migrate and contract phases rather than deleting an old field on day one. I avoid destructive fallback for user data and monitor crashes by source version. If rollback cannot read the new schema, I plan forward fix or explicit recovery before deployment. Additive backend fields ease old-app compatibility but prolong server complexity. Forced upgrades simplify backend but harm offline users and require product policy. Large local migrations can delay startup; plan chunking/recovery where necessary. A healthcare app tests every supported DB version with encrypted and plaintext fixtures, deploys backward-compatible API first, then stages new client and monitors migration failures.”

## Interview answer — deep senior

“Mobile version skew is normal: users may be offline for months while the server changes weekly. I maintain a compatibility matrix across DB schema, API contract and app version. Room migration tests assert both structural validity and business values for each shipped source version. Backend deploys additive fields/endpoints first, client migrates and backfills, then old contract is removed only after usage data and support policy allow it. I plan for low storage, encryption key/backup behavior and interrupted migration. A staged rollout watches migration failure, ANR/startup time and data-loss signals. Rollback is not automatically safe after one-way schema migration, so I prepare a forward patch and preserve source data where feasible. Room validates schema and migration paths, but semantic correctness needs row-level tests. Backend must support old clients for a defined window, or return a controlled upgrade requirement. For encrypted files, key/backup migration requires separate recovery. A staged rollout should monitor migration crash rate by source version. A rename deployed to server before old clients adapt can break them. A destructive Room fallback may wipe drafts. A migration tested only from immediately prior version misses long-offline users. Rolling back APK after one-way DB upgrade can fail. A healthcare app tests every supported DB version with encrypted and plaintext fixtures, deploys backward-compatible API first, then stages new client and monitors migration failures.”

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

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
