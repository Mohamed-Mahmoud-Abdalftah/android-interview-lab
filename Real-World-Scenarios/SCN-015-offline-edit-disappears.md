---
id: SCN-015
lesson_id: ARC-003
status: reviewed
code_verification: not_run
---
# SCN-015 — Offline edit disappears after reconnect

**Hypothetical investigation.** A user edits a note offline, sees it briefly, reconnects, and the older server title overwrites it.

<p dir="rtl" lang="ar">اجمع local entity version، pending mutation ID، outbox rows، sync start/result، remote version، وترتيب writes. فرضيات: refresh كتب server snapshot فوق dirty row، entity اتخزنت من غير outbox، worker باعت payload قديمة، أو conflict policy last-write-wins بclock جهاز غلط.</p>

## Reproduce and fix

1. Seed server version 3, disconnect, save a local edit with base version 3.
2. Change server to version 4 on another client.
3. Reconnect and deliver remote snapshot before pending push.
4. Assert the local draft remains visible and conflict evidence is retained.

<p dir="rtl" lang="ar">الإصلاح يكتب entity/outbox atomically، ويمنع refresh من مسح dirty intent، ويرسل base version. server ترجع conflict بدل overwrite؛ repository تحفظ النسختين وتطبق product policy. rollout راقب pending age، conflict rate، dropped mutation count، وtime-to-sync من غير محتوى note.</p>

[LAB-014](../Coding-Challenges/LAB-014-offline-note-repository.md) covers an in-memory version only; Room/process death/API tests remain required.

## Senior follow-ups

1. **Can you simply prefer the local value?** Only if the domain defines client authority; otherwise you may erase a valid remote change.
2. **What is the rollback?** Pause destructive sync and preserve outboxes; do not roll back to silent overwrite.
