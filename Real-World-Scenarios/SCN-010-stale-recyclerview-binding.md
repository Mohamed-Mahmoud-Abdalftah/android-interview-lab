---
id: SCN-010
lesson_id: UI-001
status: reviewed
code_verification: not_run
---
# SCN-010 — List row displays an older title after navigation

**Hypothetical Android UI investigation.** A note title changes in data state, but the list row sometimes shows its earlier title after the user navigates away and back. No app build, screenshot, stack trace, rate or AndroidX version is observed. Start with [UI-001](../05-Views-Compose/ui-001-views-recyclerview-and-fragment-binding.md).

<p dir="rtl" lang="ar">فيه فرضيات متعددة: <code dir="ltr">areContentsTheSame</code> تقارن ID فقط فتفوت title جديدة؛ نفس mutable list اتعدلت بعد submit؛ ViewHolder ما بتربطش كل fields عند reuse؛ أو Fragment observer بتعدل binding قديمة بعد <code dir="ltr">onDestroyView</code>. اجمع state قبل/بعد submit، callback outputs، view lifecycle timeline، وscreenshot من جهاز قبل إعلان root cause.</p>

## Reproduction and competing causes

1. Submit old row `n-1/old`, then a new list containing `n-1/new`. Assert item identity true and visible content equality false. The [JVM policy test](../projects/kotlin-jvm-labs/src/test/kotlin/academy/NoteRowTest.kt) covers this logic only.
2. Inspect whether caller mutated a submitted list instance or nested mutable fields. A new outer list is not enough when item internals mutate.
3. Scroll rows off and back on to force ViewHolder reuse; verify binding fills every field and click listener data.
4. Destroy/recreate Fragment view while a fake result is pending. Check old binding is cleared and new view receives current state.

## Correction and evidence limit

<p dir="rtl" lang="ar">استخدم stable domain ID، وقارن content المؤثرة على UI، وقدم snapshot جديدة عند كل تغيير. اربط تحديث view بـ <code dir="ltr">viewLifecycleOwner</code> ونظف binding عند <code dir="ltr">onDestroyView</code>. اختبر كل فرضية منفصلة؛ تغيير diff لا يصلح view leak، وتنظيف binding لا يصلح mutation للـ list.</p>

The [coding challenge](../Coding-Challenges/LAB-009-note-row-diff-policy.md) tests a pure comparator/snapshot. A real RecyclerView/ListAdapter and Fragment test are still needed. A staged rollout would monitor the exact wrong-title signature after an Android integration test; no rollout or measurement is claimed.

## Senior follow-ups

1. **Can an old submitList commit callback be relied on?** Not always; a newer list may overtake it, per the official ListAdapter API.
2. **Does same title imply the same note?** No. Stable identity comes from a domain key, possibly including tenant/account.
