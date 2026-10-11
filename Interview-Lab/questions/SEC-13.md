---
id: "SEC-13"
question: "How do you handle key invalidation, key rotation, backups, and reinstall?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 310
editorial_status: "reviewed"
---

# SEC-13

## Original interview question

How do you handle key invalidation, key rotation, backups, and reinstall?

## What the interviewer evaluates

- Key invalidation and rotation as explicit data-lifecycle events.
- Backup/reinstall behavior and replaceable versus irreplaceable data.

## Explanation in Arabic

Key ممكن تبقى unavailable بعد uninstall/reinstall، restore على جهاز تاني، أو invalidation مرتبط بإعدادات authentication حسب key policy. Rotation مش مجرد alias جديد؛ لازم تعرف تقرأ البيانات القديمة ثم تعيد تشفيرها بأمان، وتتعامل مع crash في النص. بيانات قابلة للإصدار من server زي token ممكن تتمسح ويُطلب sign-in؛ بيانات غير قابلة للاسترجاع تحتاج recovery مستقل.

## Why it matters and how it works

Persist a ciphertext format version and key identifier. While the old key works, decrypt and write the new envelope atomically before deleting old data. If the old key no longer works, no local algorithm can reconstruct plaintext. Android backup policy must align with Keystore non-transferability.

## Worked example

When upgrading a token store, read old token, encrypt under alias `session-v2`, verify decryption, then switch the persisted active version. If process death occurs before switch, keep the old record readable. If neither key works, delete only the unusable token and require authenticated renewal.

## Trade-offs and decision criteria

Keeping old keys supports gradual migration but extends exposure and complicates cleanup. Eager rotation simplifies final state but can lengthen startup and fail mid-migration. Reissuable tokens are easier than locally created data without a server copy.

## Failure modes

Silently replacing a failed decrypt with an empty token hides corruption and may loop on refresh. Blindly restoring encrypted preferences to a new install can strand data. Surface a safe re-authentication state and record redacted diagnostics.

## Production perspective

For a finance app, test fresh install, reinstall, cloud restore, device transfer, biometric enrollment changes where auth-bound keys are used, and interrupted migration. Backend sessions can be revoked and reissued; payment history is recovered from server records.

## Interview answer — short

“I version ciphertext and key aliases, migrate atomically while the old key works, and design recovery for invalidation. Backup or reinstall may leave ciphertext without its Keystore key, so replaceable tokens trigger re-authentication.”

## Interview answer — structured

“Rotation needs a readable old key, a new key, a versioned storage format and crash-safe switch. I write and verify the new ciphertext before deleting the old one. On invalidation I classify the data: a session token can be cleared and reissued, but irreplaceable data needs an independent recovery method. Device-bound Keystore keys should not be assumed to transfer with Auto Backup. I test restore and process death, not just the happy path. Rotation must be crash-safe: keep the old readable envelope until the new ciphertext has been written and verified, then switch the active version. Backups and reinstall may restore data without the device-bound key. I classify data before choosing recovery; tokens can be reissued, but irreplaceable files need a separate plan.”
## Interview answer — deep senior

“I would define an explicit state machine: old readable, migration pending, new verified, old retired, and unrecoverable. The storage update is atomic, and a crash can restart from either old or new valid envelope. I never pretend an invalidated key can be recreated to decrypt existing ciphertext. Authentication-bound keys can have additional invalidation conditions, so tests follow the exact KeyGenParameterSpec policy. Backup rules exclude device-bound ciphertext or provide a separate recovery design. Financial truth and payment records remain on the backend; local session material can be safely discarded with server-aware logout. I would model key migration as states rather than one blind rewrite: old format readable, new alias created, new envelope verified, active pointer changed and old material retired. Each step must survive process death without leaving ambiguous ciphertext. If the old key is invalidated, generating another key cannot decrypt the old bytes; a token store should clear unusable session material and use authenticated sign-in, while unrecoverable user data requires a recovery design prepared earlier. Authentication-bound keys may have additional invalidation behavior depending on their parameters and device, so I test that exact policy. I also run backup/device-transfer drills and avoid backing up ciphertext that assumes a nontransferable Keystore key. Server payment history remains the source of truth.”
## Deep-dive talking points

Build a decision table for key invalidation, biometric enrollment changes, backup restore and reinstall; separate revocable tokens from irreplaceable user data.

## Follow-up questions

- [SEC-11](../sec-11/): Why version an encrypted envelope? **Answer:** it identifies the key and format during migration.
- [SEC-23](../sec-23/): How does backup affect ciphertext? **Answer:** restored bytes may lack the original key.

## Self-check rubric

Can I explain rotation ordering, crash recovery, invalidation, backup/reinstall and data-class-specific recovery?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key behavior.
- [Android Auto Backup](https://developer.android.com/identity/data/autobackup) — restore and exclusion rules.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
