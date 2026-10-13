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

## Practical walkthrough

لو غيرت alias من `session-v1` إلى `session-v2`، اعمل تشفير نسخة جديدة ثم verify فكّها قبل ما تغيّر pointer النشط. لو crash حصل بين الخطوتين، لازم النسخة القديمة تفضل قابلة للقراءة. بعد uninstall أو restore، Keystore key ممكن ما ترجعش؛ لو السر مجرد session token، امسح ciphertext غير القابل للفتح واطلب login، أما بيانات لا تُستعاد تحتاج سياسة backup مختلفة من البداية.

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

“I version key aliases and ciphertext so a rotation can read the old record, write a new one, verify it, then switch atomically. A crash before the switch must leave one readable version. Backup and reinstall may restore ciphertext without its Keystore key, so I distinguish replaceable session tokens from irreplaceable offline data. The former can trigger sign-in; the latter needs a recovery architecture from the start. I test both migration and key-loss paths.”

## Interview answer — deep senior

“I separate routine rotation from key loss. During rotation, I keep the old alias readable, write a new versioned ciphertext record, verify a round trip, then atomically switch the active pointer. A crash before that switch must still leave the old record usable. Backup and reinstall are different: Keystore keys may be absent when ciphertext returns on another installation. For a refresh token I can clear the unusable record and reauthenticate; irreplaceable offline data needs a recovery architecture planned in advance. I would test invalidation, restore, process death at each migration step, and rollback before claiming this is reliable. The migration protocol should have a committed active-version marker so startup can distinguish an interrupted write from a completed cutover. I would keep only a bounded number of old aliases and remove them after telemetry shows migration success. For biometric-bound keys I would explicitly test enrollment changes and authentication policy; those failures differ from an attacker-modified ciphertext tag. Support messages should ask for reauthentication without exposing raw crypto exceptions.”

## How to answer in the interview

- **Why:** key lifecycle outlives a single encryption call.
- **How:** version aliases and ciphertext, migrate atomically, then retire old keys.
- **Trade-off:** keeping old readers supports rollback but extends key exposure.
- **Failure case:** partial migration or backup without Keystore key.
- **Production solution:** exercise reinstall, restore, invalidation, and crash recovery tests.

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

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
