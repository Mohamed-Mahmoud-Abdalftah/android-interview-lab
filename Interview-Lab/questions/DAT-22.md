---
id: "DAT-22"
question: "You must migrate encrypted and unencrypted local databases. How do you protect against data loss?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "C"
phase: 3
priority: "P1"
order: 279
editorial_status: "reviewed"
---

# DAT-22

## Original interview question

You must migrate encrypted and unencrypted local databases. How do you protect against data loss?

## What the interviewer evaluates

Migrate encrypted and plaintext databases with verified copy, key/backup recovery and no destructive fallback.

## Explanation in Arabic

نقل بيانات بين database مشفرة وغير مشفرة أخطر من schema migration عادية: لازم نعرف format/key لكل نسخة قديمة، نحافظ على الأصل لحد ما النسخة الجديدة تتعمل وتتحقق، وبعدها swap atomic قدر الإمكان مع recovery marker. ننفذ على نسخ اختبار من release قديمة، ونتعامل مع disk full وprocess kill، وما نمسحش الأصل لمجرد إن فتح الجديدة نجح مرة.

## Why it matters and how it works

Inventory supported file formats, keys, backup policies and migration paths. A safe protocol copies to a temporary destination, validates row counts/checksums and critical invariants, flushes/renames, and records completion so restart can resume or roll back. Key loss is a separate threat: do not silently replace unrecoverable user data with empty DB.

## Worked example

Conceptual migration state machine; actual database/encryption library APIs are project-specific and must be tested on device.

```kotlin
enum class MigrationStage { NOT_STARTED, COPYING, VERIFIED, SWITCHED }
interface DbMigrationJournal {
    suspend fun stage(): MigrationStage
    suspend fun mark(stage: MigrationStage)
}
// Keep source file until destination verification and safe switch complete.
```

## Practical walkthrough

encrypted/unencrypted DB migration فيها خطرين: data transform وkey availability. اعمل inventory للمستخدمين حسب old version ونوع DB، وخلي source file untouched لحد ما temporary destination تكتمل وتتراجع: row counts، FK integrity، business invariants، وربما checksums لحقول غير حساسة. state marker durable يحدد COPYING/VERIFYING/SWITCHED عشان crash يعيد بأمان؛ file switch/backup strategy لازم تناسب library/OS filesystem contract. Android Keystore key قد لا ينتقل مع backup، فلا تعد recovery تلقائيًا لو ciphertext وصلت بلا key؛ صمّم user re-auth/server rehydrate أو explicit failure UX. اختبر low storage، wrong key، process kill بكل stage، وترقية متعددة الإصدارات.

## Trade-offs and decision criteria

In-place migration is faster but risks irreversible loss; copy-and-swap needs extra storage and careful file handling. Encryption protects data at rest only under a sound key/backup threat model. Rolling back to an old app may not read new format, so rollout must plan compatibility.

## Failure modes

Backing up ciphertext without its Keystore key can create an unreadable restored DB. Deleting plaintext source before verifying encrypted copy loses drafts on disk-full or crash. A migration journal stored only in volatile memory cannot recover after process death.

## Production perspective

A health app migrates legacy plaintext records to encrypted storage in a staged release. It tests old fixtures, low storage, key invalidation, backup restore and kill at each stage. Metrics record only counts/status, never sensitive rows; support provides recovery guidance.

## Interview answer — short

“I inventory old formats and keys, copy into a temporary target, verify data and invariants, then switch with a durable recovery marker. I retain the source until verification and test low storage, process death and backup/key restoration.”

## Interview answer — structured

“An encrypted/unencrypted database migration is a file and key lifecycle problem. I first map shipped formats and backup behavior. I create a new destination, copy rows, verify counts and critical values, and only then switch the app to it. A durable journal lets restart detect whether it was copying, verified or switched. I do not use destructive fallback or delete the old file early. Tests include disk full, process kill after every stage, encryption-key unavailability and restore on a new device.”

## Interview answer — deep senior

I treat this as a transactional file migration under adversarial conditions. The source database remains untouched until a temporary destination has been fully populated and verified against row counts, checksums where appropriate, foreign keys and business invariants. A durable stage marker and safe rename/switch protocol make retries idempotent after crash. I separately design key management: Android Keystore keys may not migrate with backup, so restored ciphertext can be unreadable and needs a documented recovery path. Copy-and-swap costs disk space, which I check before starting; in-place conversion is faster but riskier. I run fixtures from every shipped version on target devices, simulate power loss/kill and low storage, stage rollout, and never log plaintext or silently erase user data.

I would run this as a recoverable data migration, not a one-shot copy followed by deletion. I classify installations by old schema and encryption state, keep the source database untouched, and write a temporary destination. Before switching, I verify row counts, foreign keys, and domain invariants; checksums can help where they do not expose sensitive contents. A durable stage marker makes crash retry idempotent. Encryption adds a separate key lifecycle: Keystore material may not be restored with backed-up ciphertext, so I need an explicit re-authentication or server rehydration plan rather than silently wiping data. I test low storage, wrong keys, interruption at each stage, and supported upgrade paths on devices.

## How to answer in the interview

- **Why:** Migration failure can destroy both data and decryptability.
- **How:** Classify source, copy to temporary destination, verify, switch with stage marker.
- **Trade-offs:** Keep source until validated; design key/backup recovery separately.
- **Failure cases:** Wrong key, low storage, mid-switch crash, silent destructive fallback.
- **Production solution:** Device tests for each stage and explicit recovery UX.

## Deep-dive talking points

Walk crash windows, key/backup mismatch, verification and rollout/rollback limits.

## Follow-up questions

- [DAT-11](../dat-11/): Why keep old schemas? **Answer:** every shipped version may be an upgrade source.
- [DAT-18](../dat-18/): Why release-only disappearance? **Answer:** variant migration, backup/key or serializer path could differ and needs evidence.

## Self-check rubric

Can I preserve original, verify copy, recover each crash stage and handle non-restorable keys?

## References and reviewed-on date

- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — upgrade testing.
- [Android backup guidance](https://developer.android.com/identity/data/backup) — backup/restore behavior.
- [Android Keystore guide](https://developer.android.com/privacy-and-security/keystore) — key storage.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
