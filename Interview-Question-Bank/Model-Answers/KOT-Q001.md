---
id: KOT-Q001-ANSWER
question_id: KOT-Q001
status: reviewed
---
# KOT-Q001 — Model answer

**Spoken answer:** “`String` expresses a non-null Kotlin contract, while `String?` requires a null-aware branch. For null, the safe call yields null and Elvis returns zero; for `Ada`, it returns three. Zero is only right when the product contract treats absence as zero.”

<p dir="rtl" lang="ar"><strong>الشرح بالمصري:</strong> <code dir="ltr">String?</code> بتقول إن القيمة ممكن تغيب، فلازم تفحصها. لو <code dir="ltr">s = null</code>، <code dir="ltr">s?.length</code> نتيجتها null وبعدين <code dir="ltr">?:</code> يختار صفر. لو <code dir="ltr">s = &quot;Ada&quot;</code> فالطول 3. اختيار صفر هنا قرار منتج، مش قانون في Kotlin.</p>

**Mechanics:** Kotlin's null safety is checked at compile time for ordinary Kotlin values. `?.` skips `.length` when the receiver is null. `?:` takes the right expression only if the left result is null. This says nothing about whether a missing name is valid business data. [Kotlin null safety](https://kotlinlang.org/docs/null-safety.html), checked 2026-10-10.

**Common wrong answer:** “Kotlin makes NPE impossible.” Java platform types and `!!` can still fail. **When not to use it:** A fallback zero would conceal a required field; return a domain error instead.

**Follow-up 1:** Can `String?` contain `""`? **Yes.** Nullable only models absence; blank validation is separate.

**Follow-up 2:** Does `s?.length ?: 0` evaluate `s` twice? **No in this expression.** The receiver is evaluated for the safe call, then the resulting nullable length feeds Elvis. Do not extrapolate this to two separate reads of a mutable property.

**Fair rubric (10):** 4 nullability distinction, 3 both trace outcomes, 2 domain fallback choice, 1 caveat. Version caveat: stable Kotlin language behavior; no Android dependency.
