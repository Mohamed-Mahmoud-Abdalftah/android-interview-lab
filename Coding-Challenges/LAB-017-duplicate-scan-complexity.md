---
id: LAB-017
lesson_id: KOT-006
status: reviewed
code_verification: tested
---
# LAB-017 — Duplicate scan complexity

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> نفّذ نسختين ترجع أول value تتكرر حسب ترتيب input: نسخة nested comparison، ونسخة تستخدم set. رجّع كمان probe count deterministic: عدد المقارنات في الأولى وعدد محاولات الإضافة في الثانية. الـcount أداة تعليمية للـcontrol flow، مش timer.</p>

**Contract:** Empty and single inputs return no duplicate. Preserve the caller's `IntArray`. For `[9, 4, 4, 9]`, return `4` because its second occurrence appears first. The nested unique case performs `n(n-1)/2` comparisons; the set version attempts one insertion per visited value.

<p dir="rtl" lang="ar"><strong>ابدأ بالاختبارات:</strong> شغّل <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/DuplicateScanTest.kt">DuplicateScanTest</a> قبل فتح <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/DuplicateScan.kt">reference implementation</a>. الاختبارات تغطي empty/single، first repeated semantics، unique worst case، early exit، Int boundaries، no mutation، وحدود معنى probes.</p>

**Complexity:** Nested worst-case time is `O(n²)` and extra space is `O(1)`. Hash-set expected time is `O(n)` and extra space is `O(n)`, assuming suitable hash behavior. Do not claim measured Android speed from the operation counts.

**Verification:** Run `./gradlew test --tests academy.DuplicateScanTest --no-daemon`, then the full `./gradlew clean test check run --no-daemon`. The JVM suite does not inspect DEX or benchmark ART.

**Optional extension:** Compare a sorted-copy solution. Preserve original-order semantics by carrying indices, calculate its copy and sorting costs, and explain why extra complexity may not beat the set contract.
