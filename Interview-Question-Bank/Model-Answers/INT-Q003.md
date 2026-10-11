---
id: INT-Q003-ANSWER
question_id: INT-Q003
status: reviewed
---
# INT-Q003 — Complete model answer

**Spoken answer:** “I would say the regression test passed and describe the release status accurately. I would not turn that into a claim that production incidents fell by a percentage. I would explain how I would measure the production outcome later.”

<p dir="rtl" lang="ar">اجتياز test دليل محدود. ما تقولش “خفضنا crashes” إلا لو فيه قياس بعد rollout وبـ baseline واضح. قول اللي اتثبت، واللي لسه مجهول.</p>

**Mechanics:** Separate implementation evidence, rollout evidence and user impact. A quantitative claim needs a source, comparison window and relevant denominator; otherwise give an observable narrower result. [Amazon STAR guidance](https://amazon.jobs/content/en/how-we-hire/interview-loop) and [Google SRE postmortem guidance](https://sre.google/workbook/postmortem-culture/) were checked 2026-10-10. The answer is a coaching model, not the learner’s personal history.

**Common wrong answer:** “Tests passed, so the bug was eliminated in production.” Tests cover only selected conditions.

**Follow-up 1:** Can you still give a strong result without a number? Yes. A verified rollback, accepted design decision, merged test or documented recovery can be a concrete result with its limit.

**Follow-up 2:** How do you avoid underselling a team result? State the team outcome and your exact part, then use any reliable evidence available without taking credit for unowned work.

**Rubric for self-review:** Keep the story truthful, identify individual and team actions separately, give evidence for the result, name uncertainty, and answer the follow-up without blaming people. This is visible practice, not a scored assessment.
