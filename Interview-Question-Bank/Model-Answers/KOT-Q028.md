---
id: KOT-Q028-ANSWER
question_id: KOT-Q028
status: reviewed
---
# KOT-Q028 — Complete model answer

<p dir="rtl" lang="ar">Big-O بتوصف asymptotic growth بالنسبة لحجم input وبتتجاهل constants والحدود الأقل. عشان كده تقدر تقول إن nested scan أسوأ حالاتها تكبر بشكل quadratic، لكن ما تقدرش تستنتج latency على جهاز محدد. الزمن الفعلي يتأثر بالـinput distribution، allocations، GC، cache behavior، warmup، compiler/runtime، الجهاز والـbuild variant. operation count ممكن يثبت control flow؛ benchmark مضبوط يجاوب على latency للسيناريو المقاس.</p>

**Spoken answer:** “Big-O describes how resource use grows with input size. It does not include constants, allocation cost, cache effects, warmup, device hardware or build configuration. I use complexity to reject poor scaling, deterministic counts to verify an implementation path, and a controlled benchmark for device-specific latency.”

**Common wrong answer:** `O(n)` is always faster than `O(n²)` for every input and device.

**Follow-up 1:** Why are microbenchmarks easy to misread? Dead-code elimination, warmup, unrealistic data and timing noise can measure a different workload from the production path.

**Follow-up 2:** Can best-case O(1) make a nested search constant time? It describes only favorable inputs; capacity planning and general contracts still need expected or worst-case behavior.

**Rubric:** Explain growth, omitted constants, environment factors, deterministic counts and controlled measurement.
