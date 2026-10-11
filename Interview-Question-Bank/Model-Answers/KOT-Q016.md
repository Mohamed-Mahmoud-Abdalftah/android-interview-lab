---
id: KOT-Q016-ANSWER
question_id: KOT-Q016
status: reviewed
---
# KOT-Q016 — Model answer

**Spoken answer:** “(String) -> Unit is a function value that accepts a String and returns Unit. A higher-order function receives or returns a function. Passing a lambda only gives the callee something it may invoke; the callee's contract determines whether it runs immediately, later, or on another thread.”

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> نوع <code dir="ltr">(String) -&gt; Unit</code> يعني function تستقبل نص وتعمل فعل من غير نتيجة مفيدة للـ caller. لو <code dir="ltr">registerClick { id -&gt; ... }</code>، اسم <code dir="ltr">registerClick</code> ممكن يسجل الـ lambda للمستقبل؛ لكن <code dir="ltr">runNow { ... }</code> ممكن يناديها فورًا. الأقواس وطريقة الكتابة لا تحدد وقت التنفيذ.</p>

**Mechanics:** Kotlin [functions](https://kotlinlang.org/docs/functions.html) and [lambdas](https://kotlinlang.org/docs/lambdas.html) document function types, higher-order arguments and trailing lambda syntax; checked 2026-10-10. The UI click example is conceptual. A real Android listener's thread/lifetime is its API contract, not the function type alone.

**Common wrong answer:** “A lambda starts a background thread.” Syntax does not schedule work. **Trade-off:** Passing behavior can separate UI event wiring from a domain action, but a tiny direct call is often clearer when no deferred behavior or substitution is needed.

**Follow-up 1:** Does a trailing lambda run later than a named lambda argument? **No.** Both are call syntax for passing a function value; the receiving implementation controls when it invokes it.

**Follow-up 2:** Can a function return another function? **Yes.** The Day 4 lab returns a no-argument callback that reads a provider on each invocation, which is a higher-order function boundary.

**Fair rubric (10):** 3 type meaning, 3 higher-order definition, 2 timing distinction, 2 UI ownership caveat.
