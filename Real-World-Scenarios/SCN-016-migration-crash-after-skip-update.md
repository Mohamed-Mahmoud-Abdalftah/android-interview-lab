---
id: SCN-016
lesson_id: PRO-001
status: reviewed
code_verification: not_run
---
# SCN-016 — Database opens fail after users skip releases

**Hypothetical investigation.** Release v4 works for fresh installs and upgrades from v3, but some long-inactive users crash while opening the database.

<p dir="rtl" lang="ar">ابدأ من evidence: installed app version قبل التحديث، database user_version، exception chain، schema export، migrations المسجلة، ومدة الفتح. الفرضية الأقوى إن الفريق اختبر 3→4 فقط ونسي path من1 أو2. فرضيات أخرى: default غير صالح لrows قديمة، index unique يفشل بسبب duplicates، SQL تعتمد على column لسه متعملتش، أو downgrade بعد rollback.</p>

## Reproduce and repair

1. Create file databases from every supported exported schema and seed edge-case rows.
2. Open each database with the v4 build and run integrity plus business-data assertions.
3. Reproduce the exact missing edge or invalid transform; do not switch to destructive migration.
4. Ship a corrective forward migration and stage rollout while monitoring open failures and duration.

<p dir="rtl" lang="ar">الإصلاح مش مجرد إضافة edge عشان schema validation تعدي. لو unique index الجديدة تقابل duplicates، لازم product rule تحدد merge/reject/archive قبل إنشاء index. migration تبقى deterministic وممكن إعادة اختبارها. rollback للAPK القديمة خطر لو schema اتحولت، فجهز hotfix forward واتفاق compatibility قبل rollout.</p>

## Senior follow-ups

1. **What evidence separates a missing path from corrupt storage?** Version-specific open failures and missing graph edges point to compatibility; integrity checks and unrelated page errors support corruption.
2. **What do you monitor without leaking user data?** Start/target schema versions, migration duration, typed failure category, app version, device/storage class, and success rate.
3. **What does LAB-015 prove?** Only declared graph coverage; Android file migration tests must prove SQL, rows, indexes, and Room validation.

[LAB-015](../Coding-Challenges/LAB-015-migration-coverage-planner.md) provides the release graph audit.
