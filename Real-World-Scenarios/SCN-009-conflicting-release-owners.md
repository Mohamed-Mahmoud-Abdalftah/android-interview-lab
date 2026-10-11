---
id: SCN-009
lesson_id: INT-004
status: reviewed
code_verification: not_applicable
---
# SCN-009 — Two teams disagree on release ownership

**Hypothetical leadership exercise, not the learner’s experience.** Android and backend teams disagree over who should own a late-response bug before a release. A delivery deadline is near, but no verified customer impact or incident rate is provided. Use [INT-004](../09-Leadership-English/int-004-senior-ownership-and-behavioral-star.md) to practice a truthful decision narrative.

<p dir="rtl" lang="ar">السؤال مش مين “كسب” النقاش. ابدأ بهدف مشترك: منع state خاطئة للمستخدم من غير إخفاء خطر الإصدار. اجمع trace redacted يبين request/response order، وثّق حدود Android guard وحدود backend cancellation، واختر owner للتجربة والقرار والمتابعة. لو البيانات غير كافية، اصنع reversible release decision بدل إعلان root cause متخيل.</p>

## Evidence, options and decision

1. **Evidence:** A minimal reproduced timeline, test showing out-of-order result, affected builds and known/unknown impact. Do not invent a crash percentage.
2. **Option A:** Android generation guard prevents stale response from replacing newer UI state. It may not stop server work or fix other clients.
3. **Option B:** Backend contract changes request identity or cancellation. It may take longer and still require client result ownership.
4. **Joint decision:** Define a release gate, named owners, a rollback route and follow-up review. The exact choice depends on the real evidence and constraints.

## STAR practice without fabricated credit

<p dir="rtl" lang="ar">استخدم الحالة دي لتعلم شكل الإجابة فقط. لا تقل “I led this release” إلا لو حصلت لك فعلًا. في <a dir="ltr" href="../09-Leadership-English/STAR-EVIDENCE-WORKSHEET.md">ورقة الأدلة</a> اكتب موقفك الحقيقي: دورك، مَن شارك، ما القرار، وما النتيجة التي تستطيع إثباتها. لو افتراض ناقص، قل “unknown”.</p>

**Failure modes:** Blaming one engineer, claiming a release metric before rollout, merging the guard without a test, or calling a decision “done” without an owner for follow-up. Google SRE’s [postmortem guidance](https://sre.google/workbook/postmortem-culture/) supports analysis of contributing conditions and actionable follow-up; it does not establish what happened in this hypothetical case.

## Senior follow-ups

1. **Who owns the final decision?** Name the DRI according to the organization’s process; distinguish that decision from each team’s implementation ownership.
2. **What if your preferred option loses?** Record the rationale, support the agreed plan, and define evidence that would reopen the decision.
