---
id: "SEC-23"
question: "What are the threats of insecure backup and local database files?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 320
editorial_status: "reviewed"
---

# SEC-23

## Original interview question

What are the threats of insecure backup and local database files?

## What the interviewer evaluates

- Backup and database-file exposure despite normal sandboxing.
- Android-version-specific extraction rules and Keystore restore mismatch.

## Explanation in Arabic

App-private database محمية بالـsandbox أثناء التشغيل العادي، لكن backup/device transfer/debug build أو exported provider ممكن يفتح طريق تاني. حساسية المحتوى هي اللي تحدد هل نخزن أصلًا، نمنع backup، أو نحتاج app encryption. لو database مشفّرة بمفتاح Keystore، نسخها لجهاز تاني غالبًا مش هيفكها؛ لازم recovery واضح.

## Why it matters and how it works

Android Auto Backup may include app data by default; rules differ for Android 12+ target behavior versus older backup XML. Database files and WAL/journal files should be reviewed together. File encryption and backup exclusion are separate controls, and `allowBackup`/data extraction configuration must be tested on supported versions.

## Worked example

A POS app stores only masked card display data and transaction operation IDs in Room. It excludes token/ciphertext files from cloud backup, restores transaction history from the backend, and tests device transfer. If it stores an encrypted local queue, the queue’s recovery rules must not assume its Keystore key follows it.

## Trade-offs and decision criteria

Backup improves user recovery, while exclusion limits exposure and avoids undecryptable restores. Server resync may be preferable for financial records; offline queues need durable local data plus a recovery and reconciliation strategy.

## Failure modes

An app excludes the main DB but leaves a WAL or export file containing sensitive rows, or backs up ciphertext without its key. Inventory all files and run backup/restore tests across API versions; do not infer behavior from one manifest flag.

## Production perspective

Production security review inspects database schema, cache files, WAL, exports and backup rules, and verifies a real restore. Account/session data is reauthenticated, while authoritative payment history is obtained from the server.

## Interview answer — short

“Sandboxing does not settle backup risk. I minimize sensitive local rows, configure and test backup/device-transfer rules, and plan for Keystore ciphertext that cannot be decrypted after restore.”

## Interview answer — structured

“Internal databases are private by default under the Android sandbox, but backup, transfer, debug access or exported components can create other paths. I inventory the database and associated files, configure version-appropriate backup exclusions for secrets, and test restore. If ciphertext depends on a device Keystore key, I do not expect it to decrypt elsewhere. For financial history, I prefer authoritative server resync; for an offline queue, I define a separate durable recovery strategy. The mechanics matter. Android Auto Backup may include app data by default; rules differ for Android 12+ target behavior versus older backup XML. Database files and WAL/journal files should be reviewed together. File encryption and backup exclusion are separate controls, and `allowBackup`/data extraction configuration must be tested on supported versions.”

## Interview answer — deep senior

“I would perform a data-flow and file inventory, including Room database, WAL, journal, cache, attachments and SDK files. I validate Android 12+ data-extraction-rules and legacy full-backup-content on the supported matrix, then run a backup and restore drill. Excluding everything can harm usability, while backing up credentials can create both exposure and unusable ciphertext after key loss. I keep payment truth on the backend, store minimal offline state with explicit retention, and re-authenticate after restore. A compromised rooted device can still inspect local files at runtime, so file controls are defense in depth. Consider a concrete case. A POS app stores only masked card display data and transaction operation IDs in Room. It excludes token/ciphertext files from cloud backup, restores transaction history from the backend, and tests device transfer. If it stores an encrypted local queue, the queue’s recovery rules must not assume its Keystore key follows it. A failure case illustrates the risk. An app excludes the main DB but leaves a WAL or export file containing sensitive rows, or backs up ciphertext without its key. Inventory all files and run backup/restore tests across API versions; do not infer behavior from one manifest flag.”

## Deep-dive talking points

Prompt for WAL/journal inventory, Android 12+ rules, restore drill, Keystore mismatch and backend resync.

## Follow-up questions

- [SEC-13](../sec-13/): Why can encrypted backup fail? **Answer:** the original Keystore key may not transfer.
- [PAY-07](../pay-07/): Why must an offline reversal queue be durable? **Answer:** power loss must not erase an obligation.

## Self-check rubric

Can I identify database side files, backup rules, restore behavior and authoritative history recovery?

## References and reviewed-on date

- [Android Auto Backup](https://developer.android.com/identity/data/autobackup) — inclusion/exclusion and API behavior.
- [OWASP backup test](https://mas.owasp.org/MASTG/tests/android/MASVS-STORAGE/MASTG-TEST-0216/) — sensitive backup exposure.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
