---
id: LAB-011
lesson_id: PRO-003
status: reviewed
code_verification: tested
---
# LAB-011 — Parse a trusted payment return shape

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> اكتب parser ترجع typed result فقط للرابط <code dir="ltr">https://pay.example.com/payment/return</code> ومعه <code dir="ltr">orderId</code> و<code dir="ltr">status</code> مرة واحدة. ارفض HTTP، host شبيه، user-info، port، fragment، path زيادة، duplicate أو unknown fields، encoding خارج العقد، وقيم ناقصة أو طويلة. ابدأ من الاختبارات قبل <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/TrustedReturnLink.kt">reference</a>.</p>

**Acceptance:** [Six JUnit tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/TrustedReturnLinkTest.kt) cover accepted and hostile shapes. Then explain why accepted parsing does not authorize payment and sketch the backend lookup.

<p dir="rtl" lang="ar"><strong>حدود المعمل:</strong> لا يوجد Android Intent أو manifest أو App Links verification أو server. ما تسميش الدالة authentication؛ هي validation لصيغة input فقط. في تطبيق حقيقي، استخدم URI APIs في المنصة، تحقق من ownership على server، واختبر routing على جهاز.</p>

**Complexity:** Parsing and validation are O(n) in URL length with bounded accepted fields; memory is O(n) for parser/query strings. **Verification:** run `./gradlew clean test check run --no-daemon` and inspect [BUILD-VERIFICATION](../BUILD-VERIFICATION.md).
