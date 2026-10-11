---
id: SCN-007
lesson_id: AND-001
status: reviewed
code_verification: not_run
---
# SCN-007 — Old Fragment view receives a late update

**Hypothetical Android incident.** A user navigates away from a profile Fragment and later returns. A delayed result updates an old view binding, or a memory trace suggests that the old view remains retained. The specific app, Fragment version, stack trace, heap evidence and frequency are unknown. Start with [AND-001](../03-Android-Internals/and-001-activity-fragment-and-view-lifecycle.md).

<p dir="rtl" lang="ar">الفرضية الأولى إن observer مربوطة بعمر Fragment مع إنها بتعدل view؛ الـ Fragment ممكن تفضل بعد <code dir="ltr">onDestroyView</code>. فرضية تانية إن callback احتفظت بـ binding في singleton. فرضية ثالثة إن view اتفصلت صح، لكن response قديمة غيرت state الجديدة. فرّق بين leak وstale state بدل جمعهم تحت اسم lifecycle bug.</p>

## Evidence and reproducer

1. Record redacted navigation and lifecycle timestamps: request start, onDestroyView, result arrival, new onViewCreated and render. Do not log full profile data.
2. Inspect owner passed to LiveData/Flow collection and references to binding after onDestroyView. A heap retention trace, if available, can support a leak claim; no such trace exists in this exercise.
3. Release a controlled fake result after view destruction. Assert old view receives no render; separately assert a new view renders the current state.
4. If state still shows an older profile, test request generations or cancellation independently from view cleanup.

## Correction and limits

<p dir="rtl" lang="ar">استخدم <code dir="ltr">viewLifecycleOwner</code> للشغل الذي يلمس view، ونظف binding ومراجع adapter عند <code dir="ltr">onDestroyView</code>. لا تعالجها بـ delay. لو business result لازمة بعد إعادة بناء view، خزّن state عند owner مناسبة واعرضها على view الجديدة، مع حماية من response قديمة. <a dir="ltr" href="https://developer.android.com/guide/fragments/lifecycle">Fragment lifecycle source</a>، اتراجع 2026-10-10.</p>

The [JVM challenge](../Coding-Challenges/LAB-007-view-session-owner.md) tests detach/rebind logic only. Android FragmentScenario, rotation, back stack, process recreation and leak inspection remain unexecuted because no Android SDK is installed. A staged rollout and measurement plan would follow a real reproducer; none is claimed here.

## Senior follow-ups

1. **Does clearing binding cancel the network?** No. It releases view references; cancellation and stale-response ownership are separate concerns.
2. **Could a Fragment observer be correct?** Yes for work with Fragment lifetime that never touches a destroyed view; choose the owner by the work's lifetime.
