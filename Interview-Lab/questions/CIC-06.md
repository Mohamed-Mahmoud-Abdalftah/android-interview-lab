---
id: "CIC-06"
question: "When is revert safer than reset on shared branches?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 425
editorial_status: "reviewed"
---

# CIC-06

## Original interview question

When is revert safer than reset on shared branches?

## What the interviewer evaluates

- Shared-history rollback and auditability.
- Limits of revert for migrations and later dependent commits.

## Explanation in Arabic

لماذا يعتبر أمر `git revert` أكثر أماناً من `git reset` على الفروع المشتركة (Shared Branches)؟

1. جوهر المشكلة في الفروع المشتركة:
   - الفروع المشتركة (مثل `main`, `develop`, `release/*`) يقوم بسحبها (Pull) والعمل عليها عشرات المهندسين وسيرفرات الـ CI/CD.
   - إذا استخدمت `git reset` لمسح كوميت سبب مشكلة، فأنت **تغير تاريخ الفرع إلى الوراء**.
   - لرفع هذا التغيير للـ Remote، ستضطر لاستخدام `git push --force`، وهو ما يكسر تزامن كل المهندسين الآخرين.

2. كوارث الـ `git reset` على الفروع المشتركة:
   - **تكرار الكوميتات وتضاربها**: عندما يقوم زملاؤك بعمل `git pull`، سيرى Git أن فرعهم المحلي يملك الكوميت الذي حذفته، فيقوم بدمجه مرة أخرى (Re-merge)، ويعود الخطأ الذي حذفته إلى الحياة!
   - **فقدان التدقيق (Audit Trail)**: مسح الكوميت يحذف الدليل على من كتب الكود ومتى ظهرت المشكلة.

3. لماذا `git revert` هو الخيار الاحترافي؟:
   - **تاريخ تطلعي للأمام (Forward-only)**: ينشئ كوميت جديد تماماً يقوم بعكس التغييرات (Inverse Diff).
   - **دفع عادي دون Force**: يرفع للـ Remote باستخدام `git push` الطبيعي دون الحاجة لـ `--force`.
   - **تزامن سلس**: عندما يقوم الزملاء بعمل `git pull`، يتحدث كودهم بسلاسة دون تعارضات أو كسر لفروعهم.

## Practical walkthrough

مقارنة عملية توضح الفرق في سيناريو إصلاح خطأ إنتاجي على الفرع المشترك:
```bash
# ❌ السيناريو الخاطئ والخطير (Reset على فرع مشترك):
git checkout main
git reset --hard HEAD~1
git push origin main --force # ⚠️ خطر كارثي: يمسح كوميتات الزملاء ويعطل الـ CI!

# ✅ السيناريو الهندسي الآمن والصحيح (Revert على فرع مشترك):
git checkout main
git pull origin main

# 1. فحص الـ log لتحديد الـ hash للكوميت المعيب:
# e.g., commit 9a8b7c6 "feat: add experimental payment sdk"

# 2. إنشاء كوميت عكسي يلغي التغييرات مع رسالة واضحة:
git revert 9a8b7c6 -m 1 # (إذا كان merge commit نحدد الـ parent برقم 1)

# 3. دفع التغيير للأمام بسلاسة وبدون أي force:
git push origin main
# النتيجة: تم التراجع عن الخطأ، مع الحفاظ على سجل التدقيق وتزامن الزملاء.
```

## Why it matters and how it works

A revert applies inverse patch against current tree, so it may conflict or produce semantic problems when subsequent commits changed the same code. Git history remains append-only, preserving CI and release references. A revert of a merge requires choosing a mainline parent.

## Worked example

A bad payment validation commit is on main and included in internal build. Create a revert PR, resolve a conflict with a later UI change, run payment tests and release a new artifact. Do not reset main to yesterday because another team already based work on it.

## Trade-offs and decision criteria

Revert is safer for collaboration but can require repair and a new release; reset is suitable for disposable local branch cleanup. A backend feature flag may reduce live risk faster while the revert builds.

## Failure modes

Reverting a database migration source does not reverse schemas already applied on user devices. Plan compatible forward migration or fix-forward. Verify the deployed state, not just Git diff.

## Production perspective

Incident runbook records commit, revert SHA, artifact version, schema compatibility and rollout status. Branch protection prevents force-push to release branches.

## Interview answer — short

Git revert is safer on shared branches because it creates a new forward-moving commit that inverts the target changes without rewriting history. Git reset rewrites history and requires force-pushing, which corrupts teammates' branches, causes ghost commit re-merges, and destroys audit logs.

## Interview answer — structured

On shared branches like `main` or release stabilization branches, `git revert` is the only safe undo mechanism for three core reasons.

First, **Forward-Only History (No Force-Push Required)**. Next, `git revert <sha>` records a new commit containing the exact inverse diff of the flawed commit. Because the branch tip advances forward linearly, it can be pushed with a standard `git push` without requiring destructive force pushes (`git push --force`).
**Teammate Synchronization & Ghost Merges**. If you use `git reset` and force-push to a shared branch, any collaborator whose local clone still has the erased commit will unknowingly re-introduce it the next time they pull or merge, causing ghost bug resuscitations and severe merge conflicts.
**Compliance and Auditability**. Finally, enterprise compliance frameworks (such as SOC2 or ISO 27001) mandate an immutable audit trail. `git revert` transparently documents that a feature was committed, caused an issue, and was subsequently rolled back, preserving full attribution.


## Interview answer — deep senior

Handling reverts on complex merge commits presents an architectural challenge that senior engineers must navigate.

First, with Reverting Merge Commits (`git revert -m 1`), when reverting a merge commit, Git does not know which of the two parents represents the mainline. Passing `-m 1` specifies that the first parent (the target branch, like `main`) is the baseline. This reverts the changes introduced by the feature branch. Next, a The Re-Merge Dilemma is a critical nuance occurs when re-introducing the feature later. If you simply re-merge the original feature branch after reverting it, Git sees that the commits are already in history and **will not re-apply the reverted code**! To re-introduce the feature, you must execute `git revert <revert-commit-sha>` (reverting the revert) before merging new fixes.
Finally, with Branch Protection Enforcements, mature teams configure branch protection rules in GitHub or GitLab that strictly disallow `git push --force` or `--force-with-lease` on `main`, enforcing `git revert` by operational policy.


## How to answer in the interview

- **Why:** shared refs already depend on published commits.
- **How:** revert with a reviewed compensating commit.
- **Trade-off:** auditability versus extra history.
- **Failure case:** later commits may rely on reverted API.
- **Production solution:** run release checks on the resulting branch.

## Deep-dive talking points

Prompt for public commit references, inverse patch conflict, released migration, feature gate.

## Follow-up questions

- **Interviewer:** "What happens if you try to merge a feature branch that was previously reverted on main?"
  **Answer:** "Git will not re-apply the feature diff because it considers those commits already in history; you must revert the revert commit first."

- **Interviewer:** "Why is the `-m` flag required when reverting a merge commit?"
  **Answer:** "Because a merge commit has multiple parents, so `-m 1` explicitly designates the mainline parent to calculate the reverse diff against."

## Self-check rubric

Explain why revert adds a new inverse commit without rewriting shared history; identify a case where reverting an old commit conflicts with later changes and how you would verify the result.

## References and reviewed-on date

- [Git revert documentation](https://git-scm.com/docs/git-revert) — inverse commit semantics.
- [Android Room migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — shipped schema considerations.

Technically reviewed against primary documentation on 2026-10-13.
