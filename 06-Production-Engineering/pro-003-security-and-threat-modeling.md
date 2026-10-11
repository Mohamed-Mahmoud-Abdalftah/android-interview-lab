---
id: PRO-003
title: Security and threat modeling
module: 06-Production-Engineering
tier: Core
estimated_minutes: 60
prerequisite_ids: [AND-003]
learning_outcomes:
  - Build a small threat model from assets, actors, entry points and trust boundaries
  - Explain why manifest routing and intent filters are not authorization checks
  - Validate a payment return URL with an allowlist and typed result
  - Separate JVM parser evidence from Android App Links, server and device evidence
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://developer.android.com/privacy-and-security/security-tips
  - https://developer.android.com/privacy-and-security/risks/unsafe-use-of-deeplinks
  - https://developer.android.com/privacy-and-security/risks/implicit-intent-hijacking
  - https://developer.android.com/training/app-links/about
  - https://developer.android.com/training/app-links/verify-applinks
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/TrustedReturnLink.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/TrustedReturnLinkTest.kt
question_ids: [PRO-Q001, PRO-Q002, PRO-Q003, PRO-Q004, PRO-Q005]
---

# PRO-003 — Security and threat modeling

**مسار الساعتين:** 60 دقيقة شرح وتتبع، 20 دقيقة [أسئلة وإجابات كاملة](../Interview-Question-Bank/BY-TOPIC.md)، 25 دقيقة [LAB-011](../Coding-Challenges/LAB-011-trusted-payment-return-link.md)، 10 دقائق [مراجعة](../Flashcards-Revision/PRO-003.md)، و5 دقائق شرح بصوتك من [Day 33](../Speaking-Shadowing/DAY-33.md). المتطلب في المنهج هو AND-003؛ بما إن محتواه لسه ناقص، راجع أساسيات exported components وintents من المصادر الرسمية قبل الاعتماد على الدرس كمراجعة نهائية.

## Mental model — نموذج التهديد قبل الكود

<p dir="rtl" lang="ar">الأمان مش checklist بتحط عليها HTTPS وخلاص. ابدأ بأربع أسئلة: إيه الـ assets اللي بتحميها؟ مين يقدر يبعت input؟ فين الـ entry points؟ وفين البيانات بتعدي trust boundary؟ في تطبيق دفع مثلًا الـ assets تشمل session، order ID، قرار إن الدفع نجح، وبيانات العميل. الـ entry points تشمل deep link، exported Activity، notification action، clipboard، network response، وملف مستورد. أي input جاي من برا process التطبيق اعتبره غير موثوق لحد ما تتحقق منه.</p>

<p dir="rtl" lang="ar">ارسم flow صغير: Browser أو تطبيق خارجي يرسل URL، Android يحاول يوجّهها، Activity تستقبل Intent، parser تحول النص إلى command typed، وبعدها repository أو server تتحقق من حالة الطلب. كل سهم يعبر boundary له سؤال: هل المرسل معروف؟ هل المحتوى اتعدل؟ هل العملية مسموحة للمستخدم الحالي؟ هل التكرار آمن؟ الفكرة دي أهم من حفظ أسماء هجمات، لأنها تخليك تكتشف إن URL صحيحة شكليًا لا تثبت إن الدفع نجح.</p>

<table dir="rtl" lang="ar"><thead><tr><th>الجزء</th><th>سؤال لازم يتجاوب</th><th>مثال حماية</th></tr></thead><tbody>
<tr><td>Routing</td><td>مين يقدر يفتح الشاشة أو يستقبل الرابط؟</td><td>Verified App Links و<code dir="ltr">android:exported</code> مقصودة.</td></tr>
<tr><td>Parsing</td><td>هل scheme/host/path/query مطابقة لعقد ضيق؟</td><td>Allowlist وقيم typed ورفض duplicate fields.</td></tr>
<tr><td>Authorization</td><td>هل المستخدم الحالي يملك الـ order؟</td><td>تحقق server-side مربوط بالsession.</td></tr>
<tr><td>Integrity</td><td>هل النتيجة مصدرها موثوق ولا parameter عدّلها المهاجم؟</td><td>اقرأ النتيجة من backend؛ لا تثق في <code dir="ltr">status=success</code>.</td></tr>
<tr><td>Replay</td><td>هل إعادة نفس الطلب تعمل أثر مرتين؟</td><td>Idempotency key وحالة order/version.</td></tr>
</tbody></table>

## Mechanism and execution trace

<p dir="rtl" lang="ar">المعمل يختبر boundary واحدة فقط: تحويل payment return URL إلى <code dir="ltr">PaymentReturn</code>. الدالة تقبل <code dir="ltr">https</code>، host محدد، port افتراضي، path واحدة، من غير user-info أو fragment. الـ query لازم تحتوي <code dir="ltr">orderId</code> و<code dir="ltr">status</code> مرة واحدة فقط؛ أي field زيادة أو encoding خارج العقد يترفض. القيم المقبولة تتحول إلى enum بدل strings تنتشر في التطبيق. اقرأ <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/TrustedReturnLink.kt">التنفيذ</a> و<a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/TrustedReturnLinkTest.kt">الاختبارات</a>.</p>

```kotlin
fun parseTrustedPaymentReturn(raw: String): PaymentReturn? {
    val uri = runCatching { URI(raw) }.getOrNull() ?: return null
    if (uri.scheme != "https" || uri.host != "pay.example.com") return null
    if (uri.path != "/payment/return") return null
    // Reject user-info, custom ports, fragments, duplicates and unknown fields.
    // Convert the two accepted fields into constrained types.
    return validatedReturnOrNull(uri)
}
```

<p dir="rtl" lang="ar">تتبع الرابط الصحيح: parser تقرأ URI، تقارن origin، تفحص path، تفك fields حسب contract، تتحقق من طول وشكل order ID، وتحول status إلى enum. النتيجة معناها “الرابط مطابق لصيغة نسمح بها”، مش “الدفع مؤكد”. الخطوة التالية في التطبيق الحقيقي هي سؤال backend عن order تخص المستخدم الحالي وإظهار state من المصدر ده. رابط host شبيه زي <code dir="ltr">pay.example.com.attacker.test</code> يترفض لأن المقارنة على host كاملة، مش <code dir="ltr">contains</code>.</p>

<p dir="rtl" lang="ar">Android App Links تضيف association بين موقع تملكه والتطبيق من خلال <code dir="ltr">assetlinks.json</code> وبصمة شهادة التوقيع. ده يقلل hijacking ويوجه الرابط للتطبيق، لكنه لا يحول query parameters إلى بيانات موثوقة. لازم تختبر domain verification على جهاز بأوامر <code dir="ltr">adb shell pm get-app-links</code> وتختبر كل path. راجع <a dir="ltr" href="https://developer.android.com/training/app-links/about">About App Links</a> و<a dir="ltr" href="https://developer.android.com/training/app-links/verify-applinks">verification guide</a>، اتراجعوا 2026-10-10.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>غلط:</strong> تفحص إن النص يحتوي اسم الدومين، تقرأ status مباشرة، وبعدها تحدث الطلب محليًا. المهاجم يقدر يبني host شبيه، يكرر field، أو يفتح exported component explicit حتى لو intent filter ما كانتش هتطابقه. توجيه Android واضح إن intent filters ليست security boundary؛ لازم component نفسها تتحقق من caller/input/authorization حسب الحالة.</p>

```kotlin
fun onReturn(raw: String) {
    if (raw.contains("pay.example.com") && raw.contains("status=success")) {
        markOrderPaid() // False authority: URL text is not payment evidence.
    }
}
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> استخدم verified HTTPS association للتوجيه، parser ضيقة للـ shape، وما تعتبرش status في الرابط authority. ابعت order ID للـ backend مع session الحالية، والbackend يتحقق من الملكية وحالة provider ويعيد النتيجة. خلي operation idempotent عشان إعادة الرابط أو retry ما تعملش capture مرتين. لو بتبعت sensitive data لتطبيق محدد استخدم explicit intent؛ ولو اختيار التطبيق جزء من التجربة استخدم chooser وما تحطش secret في implicit intent. <a dir="ltr" href="https://developer.android.com/privacy-and-security/risks/implicit-intent-hijacking">Implicit intent hijacking guidance</a>.</p>

## Practical threat-model workflow

<ol dir="rtl" lang="ar">
<li><strong>حدد scope:</strong> feature واحدة وdata flow واحد؛ مثل payment return من browser لعرض receipt.</li>
<li><strong>اكتب assets:</strong> session، order ownership، payment state، PII، signing identity.</li>
<li><strong>حدد actors:</strong> مستخدم شرعي، تطبيق خبيث على الجهاز، رابط من رسالة، attacker على account، وخدمة backend.</li>
<li><strong>علّم boundaries:</strong> OS routing، Intent extras، process boundary، network، database، وthird-party SDK.</li>
<li><strong>اكتب abuse cases:</strong> host شبيه، duplicate parameter، replay، order لمستخدم آخر، exported Activity مباشرة، logging للtoken.</li>
<li><strong>اربط control واختبار:</strong> allowlist لها unit tests، authorization لها API integration test، App Link لها device verification، وreplay لها idempotency test.</li>
</ol>

<p dir="rtl" lang="ar">ما تسجلش URL كاملة لو ممكن تحتوي identifiers أو tokens. خزن telemetry أقل ما يمكن: نوع الرفض، نسخة contract، وrequest correlation غير حساس. الأسرار ما تتحطش في APK أو repository؛ أي قيمة داخل client يقدر المهاجم يستخرجها. استخدم Android Keystore للمفاتيح التي لازم تكون على الجهاز، لكن افهم إن ده لا يحمي من جهاز compromised ولا يصلح server authorization. اطلب permissions وقت الحاجة وبأقل scope، واقفل components غير المطلوبة بـ <code dir="ltr">android:exported="false"</code>.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">ستة اختبارات JUnit بدأت بفشل compile قبل التنفيذ، وبعدها غطت happy path، اختلاف ترتيب query، scheme/host شبيه، user-info/port/path/fragment، duplicate/unknown/encoded fields، وmissing/invalid/oversized values. دي اختبارات parser حقيقية على JVM. لا تثبت manifest، domain verification، caller identity، Activity lifecycle، TLS pinning، backend authorization، payment provider، أو مقاومة tampering على جهاز. لازم كل claim يتربط بمستوى الاختبار الصحيح.</p>

<p dir="rtl" lang="ar">اختبارات Android المطلوبة لاحقًا: افتح links مسموحة ومرفوضة عبر adb، افحص حالة verification، جرّب explicit Intent للـ exported component، واختبر إن الشاشة لا تنفذ عملية privileged قبل backend authorization. اختبارات server: order من حساب آخر تترفض، request مكررة idempotent، وprovider callback signature/lookup تتراجع حسب عقد المزود. راجع <a dir="ltr" href="https://developer.android.com/privacy-and-security/security-tips">Android security checklist</a> و<a dir="ltr" href="https://developer.android.com/privacy-and-security/risks/unsafe-use-of-deeplinks">unsafe deep links</a>.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> ببدأ threat model من الـ assets والentry points والtrust boundaries. في payment return، App Link verified تساعد في التوجيه، وبعدها parser allowlist ترفض أي origin أو shape خارج العقد. ومع ذلك ما بثقش في success parameter؛ backend هي authority وتتحقق من session وorder وتتعامل مع replay بشكل idempotent. اختبارات JVM تثبت parser فقط، واختبارات Android/server تثبت باقي السلسلة.</p>

**English, 20 seconds:** “I treat every external intent as untrusted input. Verified App Links protect routing, a strict parser protects the input shape, and server-side authorization remains the authority for payment state.”

**English, 60–90 seconds:** “I start with assets, entry points, actors, and trust boundaries. For a payment return link, I verify the owned web domain at the Android layer and parse only an exact HTTPS origin, path, and small query contract. I reject duplicates and unknown fields and convert accepted values into typed data. That still does not prove payment success, so the client queries the backend under the current session. The backend checks order ownership and provider state and handles replay idempotently. JVM tests cover the parser; device tests cover App Link routing and exported components; API tests cover authorization and persistence.”

## Senior follow-ups

<ol dir="rtl" lang="ar"><li><strong>هل certificate pinning لازم لكل تطبيق؟</strong> لأ. له operational cost وتدوير certificates، وAndroid network security defaults وTLS الصحيح أساس. استخدمه بعد threat model وخطة rotation/recovery.</li><li><strong>هل إخفاء API key بـ obfuscation يحميها؟</strong> لأ؛ أي secret موزعة على client قابلة للاستخراج. انقل authority للserver وقيّد المفتاح إن كان public client identifier.</li><li><strong>هل non-exported component آمنة من كل input؟</strong> تقلل callers من خارج التطبيق، لكن input داخلي أو compromised flow يظل يحتاج validation حسب الأثر.</li><li><strong>كيف تراجع third-party SDK؟</strong> inventory، permissions/components/network/data collected، update policy، SBOM/dependency scan، وعزل أقل صلاحية ممكنة.</li></ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar"><li>“HTTPS يعني payload موثوقة.” غلط؛ يحمي النقل للendpoint، لا يثبت authorization أو صحة query من المستخدم.</li><li>“Intent filter تمنع explicit invocation.” غلط؛ لا تستخدمها كauthorization.</li><li>“Deep link valid تعني العملية نجحت.” غلط؛ ارجع لمصدر الحقيقة.</li><li>“Client secret يمكن إخفاؤها.” غلط؛ صمّم على إنها قابلة للاستخراج.</li><li>“Unit tests الأمنية تكفي.” غلط؛ اختبر routing والجهاز والAPI والعمليات.</li></ul>

**Evidence limit:** The strict parser and six JVM cases are executed. Android SDK, manifest, App Links domain verification, backend authorization, storage, hardware, and payment provider behavior were not executed in this workspace.
