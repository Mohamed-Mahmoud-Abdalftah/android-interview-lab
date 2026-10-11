---
id: SCN-006
lesson_id: ARC-001
status: reviewed
code_verification: not_run
---
# SCN-006 — The note appears saved but vanishes

**Hypothetical production investigation.** A screen shows “Saved” after tapping Save, yet the note is absent on relaunch. The app version, storage adapter, offline state, process history, logs and reproduction rate are unknown. Start with [ARC-001](../04-Architecture-DI/arc-001-solid-and-useful-patterns.md).

<p dir="rtl" lang="ar">ما نفترضش إن المشكلة UI فقط. ممكن UI تعرض success حتى لو exception اتبلعت، أو adapter ترجع قبل durable write، أو read path تستخدم source مختلفة. اجمع event timeline بالـ ID بعد تنقيته من بيانات حساسة: ضغط Save، validation، استدعاء repository، نتيجة transaction، state المعروضة، ثم إعادة فتح التطبيق.</p>

## Competing hypotheses and evidence

1. **Swallowed failure:** Search for broad catch blocks that emit success. Force fake writer to throw, assert the screen does not report success, and preserve a redacted error.
2. **False durability promise:** If writer returns before a queued write commits, test process termination between acknowledgement and commit. Decide whether “Saved” means persisted locally or merely accepted for later sync.
3. **Different source of truth:** Compare write/read keys, tenant, database instance and normalization. A write to one account and read from another can look like data loss.
4. **Sync conflict:** Inspect server/local conflict policy separately; a successful local upsert might later be overwritten.

## Correction and verification

<p dir="rtl" lang="ar">خلّي contract واضحة: validation error، persist result، وsync status حالات مختلفة. الـ UI تعرض الحالة اللي تحققت فعلاً. الـ use case تفوض لـ port صغيرة، والـ adapter تضمن أو تصرح بمعنى نجاحها. اختبار <a dir="ltr" href="../Coding-Challenges/LAB-006-save-note-port.md">LAB-006</a> يثبت إن writer failure لا تتحول إلى نجاح، لكنه لا يثبت durability. أضف اختبار قاعدة بيانات وتكامل process restart لما تتوفر Android toolchain.</p>

**Tempting wrong fixes:** Add a delay before success, catch all exceptions, or retry every failure without idempotency. Each hides or duplicates the real effect. A staged rollout would monitor the exact missing-note signature and roll back if data loss appears; no rollout or measured incidence is claimed.

## Senior follow-ups

1. **Does an interface make the storage implementation correct?** No. It exposes a contract; an adapter must meet it and be tested with real persistence.
2. **Would one giant repository fix the boundary?** Not necessarily. The writer path needs a clear success/failure contract; unrelated methods add coupling without repairing that contract.
