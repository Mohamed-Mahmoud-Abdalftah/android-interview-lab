---
id: "CIC-05"
question: "Compare git reset --soft versus --hard."
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 424
editorial_status: "reviewed"
---

# CIC-05

## Original interview question

Compare git reset --soft versus --hard.

## What the interviewer evaluates

- Index/worktree effects of soft versus hard reset.
- Commit movement and data-loss boundary.

## Explanation in Arabic

`git reset --soft <commit>` يرجّع HEAD للcommit المطلوب ويترك index وworking tree كما هما؛ تغييرات commits الملغاة تبقى staged. `git reset --hard <commit>` يرجّع HEAD ويطابق index وworking tree للهدف، فممكن يضيّع uncommitted changes. الاتنين يغيروا branch history لو branch منشور، فلا تستخدمهم على main المشترك بدون تنسيق.

### Practical walkthrough in Egyptian Arabic

`git reset --soft HEAD~1` يرجّع مؤشر HEAD خطوة لكنه يترك تغييرات الـcommit في staging، مناسب لو بتعيد صياغة commit محلي. `git reset --hard HEAD~1` يغيّر HEAD والـindex والـworking tree، وقد يزيل شغل غير محفوظ؛ استخدمه فقط وأنت عارف حالة الفرع والملفات. في shared release branch، بدل reset لcommit منشور استخدم `revert` بحيث يبقى سبب التراجع ظاهرًا. قبل أي reset اعرض `git status` و`git log` وخذ نسخة لو فيه تغييرات مهمة.

## Why it matters and how it works

Reset moves the current branch ref (or HEAD). Soft leaves staged snapshots available for recommit. Hard writes target tree into index/worktree and discards tracked local changes; untracked files are a separate concern. Reflog may help recover commit objects but should not be a substitute for caution.

## Worked example

After two local experimental commits, use `git reset --soft HEAD~2` to combine changes into one reviewed commit. If abandoning a disposable local branch, `git reset --hard origin/main` is possible only after inspecting status and preserving anything needed.

## Trade-offs and decision criteria

Soft is useful for rewriting local commit boundaries. Hard can restore a known tree quickly but risks irreversible local loss and shared-branch divergence. Prefer revert for already published bad commits.

## Failure modes

Running hard reset in a dirty workspace loses tracked edits. Confirm `git status`, target SHA and branch before executing; use a backup/stash when appropriate. Do not assume reset deletes untracked build files.

## Production perspective

Team rules protect main from force-push and document recovery with reflog. CI release artifacts always point to immutable commit SHA.

## Interview answer — short

“Soft reset moves HEAD while keeping changes staged; hard reset moves HEAD and makes index/worktree match the target, discarding tracked local changes. Neither is the normal rollback for shared main.”

## Interview answer — structured

“I use `--soft` when I want to rewrite local commits but keep their contents ready to recommit. `--hard` also replaces the index and tracked working files with the target tree, so I inspect status and target first. Both can rewrite published branch history; for a shared or released commit I make a revert commit instead. Reflog can sometimes recover commits, but it does not justify careless destructive resets.”

## Interview answer — deep senior

“I explain reset in terms of three places: HEAD, the index and the working tree. `git reset --soft <commit>` moves HEAD while leaving the index and working tree intact, so the changes from removed local commits remain staged. `git reset --hard <commit>` moves HEAD and makes the index and tracked working-tree files match the target; it can discard uncommitted tracked work. Neither operation is a safe way to erase an already published commit from a protected shared branch. For a private commit I may use soft reset to split it into reviewable pieces, after checking `git status` and the target commit. I use hard reset only when I have deliberately chosen to discard that local state and have preserved anything valuable. For a production regression I add a revert commit and run the release gate, retaining the audit trail. I also remember that untracked files are a separate concern, so I do not describe hard reset as a universal filesystem cleanup command.”

## How to answer in the interview

- **Why:** reset changes which work is retained.
- **How:** name HEAD, index and working-tree effects.
- **Trade-off:** local cleanup versus loss of work.
- **Failure case:** hard reset discards tracked edits.
- **Production solution:** inspect status and use revert for shared history.

## Deep-dive talking points

Prompt for three trees, staged result, tracked loss, untracked caveat and shared history.

## Follow-up questions

- [CIC-06](../cic-06/): Why use revert on main? **Answer:** it adds auditable history without moving public refs backward.
- [CIC-04](../cic-04/): What does rebase change? **Answer:** commit identities along the rewritten branch.

## Self-check rubric

Given three local commits, predict HEAD, index and working tree after reset --soft versus --hard. Explain why a hard reset on a shared branch can discard work and confuse collaborators.

## References and reviewed-on date

- [Git reset documentation](https://git-scm.com/docs/git-reset) — mode effects.
- [Android app publishing](https://developer.android.com/studio/publish) — released artifact context.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
