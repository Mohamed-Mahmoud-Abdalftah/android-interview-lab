---
id: "DAT-18"
question: "A transaction is saved but disappears after restart in release builds only. What should you investigate?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "C"
phase: 3
priority: "P1"
order: 275
editorial_status: "reviewed"
---

# DAT-18

## Original interview question

A transaction is saved but disappears after restart in release builds only. What should you investigate?

## What the interviewer evaluates

Investigate release-only disappearance of saved transaction across persistence, R8, encryption and backup paths.

## Explanation in Arabic

لو transaction اتسجلت واختفت بعد restart في release بس، نثبت أولًا هل write commit حصل فعلًا ولا UI عرضت optimistic state فقط. نقارن debug/release database path, user/account, migrations, destructive fallback, R8 serialization/reflective model rules, encryption key availability وbackup/restore. ما نفترضش R8 السبب؛ نجمع logs, DB evidence وreproduction من signed release artifact.

## Why it matters and how it works

Build a timeline: local transaction commit, process death, reopen, query, session filter and sync overwrite. Inspect release variant schema/version, shrinker mapping, manifest, encryption key/backup configuration and server reconciliation. Preserve evidence and redact financial data. A local row disappearing may reflect wrong account partition, sync deletion or database reset.

## Worked example

Conceptual diagnostic check; app DAO/model are product types, and telemetry should log IDs/status only.

```kotlin
suspend fun verifyAfterSave(dao: TransactionDao, id: String) {
    dao.insertPending(id)
    val observed = dao.findById(id)
    check(observed != null) { "pending row missing after local insert: $id" }
}
// Repeat read after force-stop/relaunch with the signed release variant.
```

## Trade-offs and decision criteria

Instrumented release tests with minification catch variant-only behavior but cost more CI time. A migration test catches schema/data loss, while R8 mapping/retrace helps diagnose reflective failures. Do not disable shrinking as a permanent unexplained workaround.

## Failure modes

Optimistic UI can show Saved before the DAO transaction commits. A destructive migration can silently wipe rows on upgrade. A restore can bring encrypted DB without its key, or logout can delete account partition. A release-only serializer failure can map the wrong columns/payload.

## Production perspective

A payments app logs stable operation IDs and local state transitions, reproduces a signed release upgrade/force-stop, inspects DB and reconciles server state. It freezes destructive cleanup until root cause is known and tests each suspected boundary.

## Interview answer — short

“I trace commit versus display, then reopen the signed release database after process restart. I check variant config, migration, account filters, sync overwrite, R8/serialization and encryption/backup before claiming a cause.”

## Interview answer — structured

“I start with an exact reproduction: same transaction ID, signed release build, force-stop and reopen. I verify that the DAO transaction committed before UI said Saved and check the row directly after restart. Then I compare debug/release database names, schema versions, migrations, minification-sensitive serializers, account filtering, sync deletion and encryption key restoration. I use mapping files to read release stack traces and avoid disabling R8 blindly. For money, I reconcile server status so no user-facing balance is inferred from a possibly missing local row. Instrumented release tests with minification catch variant-only behavior but cost more CI time. A migration test catches schema/data loss, while R8 mapping/retrace helps diagnose reflective failures. Do not disable shrinking as a permanent unexplained workaround. A payments app logs stable operation IDs and local state transitions, reproduces a signed release upgrade/force-stop, inspects DB and reconciles server state.”

## Interview answer — deep senior

“The symptom spans multiple boundaries, so I build an evidence timeline. Did the local transaction actually commit, or was the UI only optimistic? Did process death happen before fsync/acknowledgement? On reopen, is the same database file, schema and account selected? Could migration fallback clear data, a background sync delete it, or backup restore ciphertext without the original key? Release minification may break reflective serialization, so I inspect retraced exceptions and packaged keep rules. I reproduce with the exact signed release artifact and old database fixture, log only non-sensitive operation IDs, and query authoritative payment state. I add regression tests for the proven cause rather than accepting a broad `-keep` or disabling R8 without explanation. Build a timeline: local transaction commit, process death, reopen, query, session filter and sync overwrite. Inspect release variant schema/version, shrinker mapping, manifest, encryption key/backup configuration and server reconciliation. Preserve evidence and redact financial data. A local row disappearing may reflect wrong account partition, sync deletion or database reset. Optimistic UI can show Saved before the DAO transaction commits. A destructive migration can silently wipe rows on upgrade. A restore can bring encrypted DB without its key, or logout can delete account partition. A release-only serializer failure can map the wrong columns/payload.”

## Deep-dive talking points

Trace write/commit/reopen/filter/sync steps and distinguish release variant causes by evidence.

## Follow-up questions

- [DAT-11](../dat-11/): Could migration erase data? **Answer:** yes if destructive fallback or faulty path is used.
- [BLD-08](../bld-08/): How inspect release-only crash? **Answer:** use signed release reproduction and retrace mapping.

## Self-check rubric

Can I prove commit, inspect exact release artifact and rule causes in/out without guessing?

## References and reviewed-on date

- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — migration data preservation.
- [Android R8 overview](https://developer.android.com/build/shrink-code) — release shrinking behavior.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
