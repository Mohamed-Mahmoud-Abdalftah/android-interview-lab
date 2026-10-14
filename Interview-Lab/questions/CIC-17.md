---
id: "CIC-17"
question: "A production hotfix is needed while feature branches have diverged. Explain your Git strategy."
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "C"
phase: 4
priority: "P2"
order: 436
editorial_status: "reviewed"
---

# CIC-17

## Original interview question

A production hotfix is needed while feature branches have diverged. Explain your Git strategy.

## What the interviewer evaluates

- Hotfix from deployed base with branch divergence.
- Propagation, compatibility and release provenance.

## Explanation in Arabic

حدث كراش حرج في الإنتاج بينما فرع التطوير الرئيسي (`main`) ابتعد وتضمن ميزات جديدة غير جاهزة للإطلاق. ما هي استراتيجيتك الدقيقة في Git والـ CI؟

1. توصيف المأزق الهندسي:
   - التطبيق الحي في المتجر هو الإصدار `v2.4.0`.
   - فرع `main` يحتوي على 40 كوميت لميزات جديدة للإصدار `v2.5.0` ما زالت قيد التطوير والاختبار، وبالتالي **يستحيل تجميع أو إطلاق `main` للإنتاج فوراً**.

2. استراتيجية الإصلاح العاجل (Hotfix Branching Strategy):
   - **1. التفريع من تاج الإنتاج (Branch from Tag)**: إنشاء فرع جديد مشتق مباشرة من التاج الدقيق للإصدار الإنتاجي: `git checkout -b hotfix/2.4.1 v2.4.0`.
   - **2. الإصلاح الجراحي (Surgical Fix)**: كتابة أقل قدر ممكن من الكود لحل العطل الحرج فقط، مع كتابة Unit Test يثبت المشكلة ويتحقق من حلها.
   - **3. بناء واختبار وتوزيع الـ Hotfix**: رفع الـ Hotfix وتجميع نسخة `v2.4.1` مع زيادة الـ `versionCode`، وتوزيعها لمسار الإنتاج مع Staged Rollout.
   - **4. وسم الإصدار (Tagging)**: عمل Tag جديد على الكوميت: `git tag v2.4.1`.
   - **5. إعادة الدمج في الفرع الرئيسي (Backporting)**: دمج أو انتقاء (`cherry-pick`) كوميت الإصلاح إلى فرع `main` فوراً؛ لضمان عدم عودة الكراش للظهور عند إطلاق التحديث الكبير القادم `v2.5.0`.

## Practical walkthrough

تسلسل أوامر Git خطوة بخطوة للتعامل مع الـ Hotfix وإعادة الدمج:
```bash
# 1. إنشاء فرع الـ hotfix انطلاقاً من Tag النسخة الحالية في الإنتاج:
git fetch --tags
git checkout -b hotfix/2.4.1 tags/v2.4.0

# 2. كتابة كود الإصلاح الجراحي واختبارات الوحدة:
# ... تعديل الكود واختباره محلياً ...
git commit -am "fix(checkout): resolve NPE during 3DS biometric challenge (#451)"

# 3. تجميع واختبار الـ release bundle ورفعه للإنتاج عبر CI:
git push origin hotfix/2.4.1
# بعد اكتمال النشر والتأكد من استقرار الإصدار:
git tag -a v2.4.1 -m "Release hotfix 2.4.1"
git push origin v2.4.1

# 4. نقل الإصلاح إلى فرع التطوير الرئيسي (Backporting):
git checkout main
git pull origin main
git cherry-pick tags/v2.4.1^{commit} -x
git push origin main
# النتيجة: تم حل مشكلة الإنتاج دون سحب أي كود غير جاهز، وتم تأمين الفرع الرئيسي.
```

## Why it matters and how it works

Hotfix source should match deployed artifact provenance, including mapping and dependencies. Cherry-picking replays a patch with new hash and may need dependent changes. Release branch and main each need tests in their own context.

## Worked example

Production `2.3.1` has token crash; main contains unfinished checkout refactor. Branch from `v2.3.1`, fix token handling, run release tests, ship `2.3.2` staged. Then apply equivalent change to main, possibly with a different implementation due to refactor.

## Trade-offs and decision criteria

Minimal patch lowers regression risk but may leave technical debt for main. Fix-forward on main could be faster if divergence is small and safe; choose based on deployed risk and test evidence.

## Failure modes

Blind cherry-pick compiles on release branch but breaks new main architecture. Review semantics and run both test suites. Never reset shared main or tag a build from an unknown dirty tree.

## Production perspective

Incident log maps deployed version, hotfix SHA, main follow-up and rollout state. Feature gates can contain impact while Play propagation occurs.

## Interview answer — short

Branch immediately from the production release tag (e.g., git checkout -b hotfix/2.4.1 v2.4.0). Apply a surgical fix with a regression test, increment versionCode, build and deploy v2.4.1 to production. Once verified, tag the hotfix and backport the commit to main via git cherry-pick -x or merge to prevent bug regression in future releases.

## Interview answer — structured

Executing a production hotfix when the mainline has diverged requires a strict, audited protocol.

First, **Isolate the Baseline via Release Tag**. Next, check out a dedicated hotfix branch directly from the production release Git tag (`git checkout -b hotfix/2.4.1 tags/v2.4.0`). Never attempt to hotfix directly from `main` or develop, as unverified features will leak into production.
**Surgical Implementation & Regression Testing**. Write the minimal atomic fix necessary to resolve the crash. Accompany it with a failing unit test that reproduces the incident to confirm the fix.
**Version Bump & Production Deployment**. Increment `versionCode` and update `versionName` to `"2.4.1"`. Trigger the CI pipeline to compile, sign, and upload the hotfix AAB to Google Play production via staged rollout.
**Audit Tagging & Backporting to Mainline**. Tag the release commit (`git tag -a v2.4.1`).
Finally, backport the hotfix commit into `main` using `git cherry-pick -x` or by merging the hotfix branch into `main`. The `-x` flag records the original commit hash, guaranteeing that the fix survives into subsequent major releases.


## Interview answer — deep senior

From an operational and incident management perspective, hotfixes carry hidden risks.

First, a The 'Forgot to Backport' Trap is the most frequent failure in hotfix workflows is deploying the hotfix, celebrating the fix, and forgetting to merge it back into `main`. Three weeks later, `v2.5.0` ships and re-introduces the identical crash, causing severe reputational damage. Enforce automated CI bots or branch policies that require a PR merging the hotfix branch back into `main` before closing the incident. Next, with Database Migration Clashes, if the hotfix touches Room or SQLite database schemas, handle versioning cautiously. If `v2.4.0` was on db version 4, the hotfix `v2.4.1` might introduce db version 5. If `main` already introduced a different migration for db version 5, a merge collision occurs that can corrupt user databases upon future updates. Backport migrations must reconcile schema version numbers carefully.
Finally, with Expedited Store Review, alert Google Play Developer Support or use expedited review requests in Play Console if the hotfix addresses a catastrophic revenue or data-loss incident.


## How to answer in the interview

- **Why:** hotfix must match shipped code.
- **How:** branch from production tag and forward-port fix.
- **Trade-off:** isolation speed versus duplicate integration.
- **Failure case:** patch applies but behavior differs on main.
- **Production solution:** test release variant and every destination branch.

## Deep-dive talking points

Prompt for deployed artifact base, minimal scope, branch propagation, compatibility and staged rollout.

## Follow-up questions

- **Interviewer:** "Why is branching from the production release tag safer than fixing on `main`?"
  **Answer:** "Because `main` contains incomplete, unverified feature code; branching from the tag guarantees binary parity with production, containing only the surgical fix."

- **Interviewer:** "What is the danger of not backporting a hotfix into the mainline development branch?"
  **Answer:** "The bug will resurface in the next scheduled feature release, causing a regression."

## Self-check rubric

Branch the hotfix from the production tag, cherry-pick only the fix, test and release a higher version, then merge or cherry-pick the fix forward into diverged branches.

## References and reviewed-on date

- [Git cherry-pick documentation](https://git-scm.com/docs/git-cherry-pick) — patch replay.
- [Android publishing](https://developer.android.com/studio/publish) — release process.

Technically reviewed against primary documentation on 2026-10-13.
