#!/usr/bin/env python3
"""
Elevation script for SEC questions: SEC-17 to SEC-24.
Topic: Android Security, Crypto & Fintech Threat Modeling (SEC)
Phase 3, Batch 3
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "أمان أندرويد والتشفير والنمذجة الأمنية لتطبيقات التكنولوجيا المالية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# SEC-17: How do you protect sensitive buffers and reduce memory residence time?
# ==========================================
DATA["SEC-17"] = {
    "concept_en": """Protecting sensitive memory buffers on Android involves minimizing the temporal window during which plaintext credentials (passwords, PINs, cryptographic keys, personal data) reside in physical device RAM. In managed runtimes like Dalvik and ART, standard objects are subject to garbage collection sweeps that occur non-deterministically. To prevent residual secrets from lingering across heap allocations, developers avoid immutable String types and instead allocate mutable primitive byte arrays (ByteArray) or character arrays (CharArray). The application must maintain explicit lifecycle ownership over each sensitive buffer, overwriting every byte with zeroes (via Arrays.fill(buffer, 0.toByte())) inside deterministic finally blocks immediately after passing data to cryptographic ciphers or network sockets. When interfacing with native code via JNI, developers allocate direct byte buffers (ByteBuffer.allocateDirect) or native memory chunks via malloc, clearing them using memset_s before deallocation. Furthermore, memory dumps resulting from uncaught crashes or background process trashing must be suppressed by disabling heap profiling dumps and setting window flags.""",
    "walkthrough_en": """Explicit memory buffer zeroing and direct buffer handling in Kotlin:
```kotlin
// 1. Deterministic wiping of mutable byte buffers using try-finally
fun processSensitivePin(rawPinChars: CharArray, block: (ByteArray) -> Unit) {
    var rawBytes: ByteArray? = null
    try {
        // Convert to UTF-8 bytes directly into a mutable byte buffer
        val byteBuffer = Charsets.UTF_8.encode(CharBuffer.wrap(rawPinChars))
        rawBytes = ByteArray(byteBuffer.remaining()).also { byteBuffer.get(it) }
        
        block(rawBytes)
    } finally {
        // Deterministically wipe memory buffers to reduce memory residence
        rawBytes?.fill(0)
        rawPinChars.fill('0')
    }
}

// 2. Native C++ memory sanitization across JNI boundary
/*
#include <string.h>
void secure_zero_memory(void* ptr, size_t len) {
    // volatile pointer prevents compiler dead-store elimination
    volatile unsigned char* p = (volatile unsigned char*)ptr;
    while (len--) *p++ = 0;
}
*/
```""",
    "short_en": """We protect sensitive buffers by using mutable byte and character arrays instead of immutable Strings, maintaining strict buffer ownership, and zeroing out memory with Arrays.fill inside finally blocks immediately after cryptographic or network operations to minimize heap exposure against memory dump attacks.""",
    "structured_en": """Reducing the memory residence time of plaintext secrets is essential for defending against cold-boot attacks, heap dumps, and runtime instrumentation.
In Android's managed memory runtime, immutable String instances linger unpredictably in the JVM heap and the internal string intern pool until reclaimed by garbage collection.
To control buffer lifetimes, we handle sensitive secrets exclusively as mutable CharArray or ByteArray instances.
We establish clear lifecycle ownership: whichever component allocates a sensitive buffer is responsible for destroying it.
Immediately after passing the buffer to an encryption cipher or transmitting it across an encrypted TLS connection, we overwrite the array with zeroes within a mandatory finally block.
When interacting with native C and C++ libraries through the NDK, we utilize direct ByteBuffers and invoke volatile memory wiping routines to prevent optimizing compilers from stripping zeroing operations.
Beyond heap buffers, we disable automatic heap dumps on crashes to ensure that memory snapshots containing sensitive buffers are never written to disk.""",
    "deep_senior_en": """From a memory safety perspective, claiming that an application can achieve perfect, instantaneous memory erasure on a managed runtime is technically inaccurate.
The Android ART runtime frequently duplicates data during string transformations, charset conversions, and UI event dispatching.
However, senior security engineering focuses on defense-in-depth and reducing the exposure window from hours to milliseconds.
When raw credentials enter the application, we immediately convert them into primitive mutable arrays and avoid creating intermediate String objects.
The primary threat vector is memory dump extraction: if an adversary attaches a debugger, extracts an unencrypted tombstone file following a native crash, or triggers an out-of-memory heap dump via Android Studio, any un-zeroed buffer residing in heap memory is fully exposed.
By deterministically overwriting arrays with zeroes using Arrays.fill inside a finally clause, we ensure that plaintext credentials exist in RAM only for the brief microseconds required to invoke Cipher.doFinal or flush an OkHttp socket.
When crossing into the Android NDK via JNI, we must defend against compiler dead-store elimination, where optimizing C++ compilers detect that a buffer is zeroed immediately before being freed and silently discard the memset call as redundant.
We neutralize this by utilizing explicit_bzero, memset_s, or casting pointers through volatile memory qualifiers to guarantee physical RAM erasure before memory release.""",
    "meta_ar": {
        "id": "SEC-17",
        "questionAr": "كيف تحمي الذاكرة المؤقتة الحساسة (Buffers) وتقلل فترة بقاء البيانات فيها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دورة حياة البيانات في ذاكرة الـ JVM، والقدرة على تقليص فترة بقاء الأسرار في الرام، وتجنب كائنات String غير القابلة للمسح، وتطبيق التصفير الحتمي عبر Arrays.fill في بلوك finally، وتفادي حذف التصفير بواسطة مجمعات C++ (Dead-store elimination).",
        "concept_ar": "حماية الذاكرة المؤقتة الحساسة تعتمد على تقليص النافذة الزمنية التي تستقر فيها البيانات الصريحة (كلمات المرور والمفاتيح) داخل ذاكرة الرام. ونظراً لأن كائنات String غير قابلة للتعديل وتظل في الذاكرة حتى يقرر جامع القمامة تفريغها، نعتمد على مصفوفات المحارف والبايتات القابلة للتعديل (ByteArray/CharArray)، ونلتزم بإعادة كتابة الأصفار فوقها فوراً في بلوك finally بعد استخدامها مباشرة، مع التعامل مع دوال التصفير العتادية في C++ لمنع المترجم من إلغائها.",
        "walkthrough_ar": "التصفير الحتمي للبايتات في بلوك finally بعد التشفير فوراً لمنع بقائها في الذاكرة:\n```kotlin\nfun handlePin(pinChars: CharArray) {\n    var bytes: ByteArray? = null\n    try {\n        bytes = convertToUtf8(pinChars)\n        encryptAndSend(bytes)\n    } finally {\n        // تصفير حتمي لكافة المصفوفات لمسحها من الرام:\n        bytes?.fill(0)\n        pinChars.fill('0')\n    }\n}\n```",
        "why_it_matters_ar": "ترك البيانات الحساسة كنصوص في الذاكرة يسمح باستخراجها بسهولة عند حدوث انهيار وتفريغ الذاكرة (Crash Dump) أو فحص الرام بأدوات الروت وتصحيح الأخطاء.",
        "worked_example_ar": "منع المترجم في C++ من إلغاء تصفير الذاكرة (Dead-store elimination) عبر volatile:\n```cpp\nvoid secureWipe(volatile char* buffer, size_t size) {\n    while (size--) *buffer++ = 0; // يضمن كتابة الصفر فيزيائياً في الرام\n}\n```",
        "trade_offs_ar": "تصفير المصفوفات يدوياً يتطلب انضباطاً شديداً ومتابعة لكافة مسارات الخطأ والـ Exceptions، بينما ترك إدارة الذاكرة للـ GC أسهل برمجياً لكنه يبقي الأسرار مكشوفة في الرام لساعات.",
        "failure_modes_ar": "تحويل مصفوفة البايتات إلى String أثناء إرسالها للشبكة مما يخلق نسخة غير قابلة للمسح في الـ String Pool، أو تصفير المصفوفة قبل اكتمال مهمة الـ Coroutine في الخلفية مما يفسد البيانات.",
        "production_perspective_ar": "في التطبيقات المصرفية، نحظر الاحتفاظ بكلمات المرور في ViewModels أو الكلاسات الثابتة، ونعطل تفريغ الذاكرة التلقائي عند الانهيارات في حزم الإنتاج لتقليل مخاطر تسريب الرام.",
        "how_to_answer_ar": "وضح أولاً استحالة الحذف الفوري التام في بيئة الـ JVM وأكد أن الهدف هو تقليص فترة البقاء من ساعات إلى ميلي ثانية، ثم اشرح استخدام CharArray/ByteArray والتصفير في finally، واختم بالحذر من مجمعات C++ NDK.",
        "talking_points_ar": "فترة بقاء البيانات في الرام (Memory Residence Time)، ومصفوفات ByteArray و CharArray، وتصفير الذاكرة بـ Arrays.fill، وبلوك finally، ومخاطر تفريغ الذاكرة Heap Dumps، وحماية C++ NDK.",
        "follow_ups_ar": "- **المحاور:** \"ما هي مشكلة Dead-store elimination عند مسح الذاكرة في C++ عبر memset؟\"\n  **المرشح:** \"المترجم الذكي يلاحظ أن الذاكرة سيتم تحريرها فوراً بعد التصفير فيحذف كود memset باعتباره عديم الفائدة، ونحل ذلك باستخدام مؤشرات volatile أو explicit_bzero.\"\n\n- **المحاور:** \"هل يضمن استدعاء System.gc() مسح النصوص القديمة من الذاكرة؟\"\n  **المرشح:** \"لا، استدعاء System.gc() هو مجرد تلميح للنظام ولا يضمن توقيت التنظيف، وقد يترك نسخاً متبقية في مساحات الذاكرة المضغوطة.\"",
        "self_check_ar": "هل بينت سبب تفضيل المصفوفات على String؟ هل شرحت التصفير في finally؟ وهل ذكرت مشكلة Dead-store elimination؟",
        "references_ar": f"- [CWE-14: Compiler Removal of Code to Clear Buffers](https://cwe.mitre.org/data/definitions/14.html) — معيار الأمان لتحذير المطورين من إلغاء كود تصفير الذاكرة في المترجمات.\n- [Android Security - Handling Sensitive Data in Memory](https://developer.android.com/privacy-and-security/data) — أفضل الممارسات للتعامل مع البيانات الحساسة في الذاكرة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نحمي الذاكرة المؤقتة الحساسة بالتعامل مع البيانات كمصفوفات محارف وبايتات قابلة للتعديل بدلاً من نصوص String غير القابلة للمسح، ونحافظ على ملكية واضحة للبيانات، ثم نقوم بإعادة كتابة الأصفار فوق كل بايت في كتلة finally فور انتهاء التشفير أو النقل لتقليص فترة بقاء السر في الرام إلى أجزاء من الثانية ومنع استخراجه من تفريغ الذاكرة.",
        "best_answer_ar": "تعتمد حماية الذاكرة الحية على تقليص النافذة الزمنية لبقاء الأسرار كنصوص صريحة داخل ذاكرة الرام إلى أدنى حد ممكن.\n\nفي بيئة تشغيل أندرويد المدارة، تظل نصوص String محتجزة في الـ Heap والـ String Pool لفترات طويلة وغير محددة حتى يقرر جامع القمامة تنظيفها. ولتجنب هذا الخطر، نتعامل مع كلمات المرور والرموز الحساسة حصرياً كمصفوفات محارف CharArray أو مصفوفات بايتات ByteArray قابلة للتعديل.\n\nونحدد مسؤولية واضحة لحذف الذاكرة؛ فالطبقة البرمجية التي تستلم أو تنشئ المصفوفة هي المسؤولة عن تدميرها. وبمجرد تمرير المصفوفة إلى خوارزمية التشفير أو كتابتها في قناة المقبس الشبكي TLS، نقوم فوراً بإعادة كتابة الأصفار فوق كافة خلاياها داخل كتلة finally باستخدام دالة Arrays.fill. وعند التعامل مع مكتبات C++ عبر NDK، نستخدم مؤشرات Volatile لضمان عدم قيام المترجم بإلغاء أوامر التصفير، ونعطل ملفات تفريغ الذاكرة التلقائية لحماية البيانات من الاستخراج الجنائي.",
        "deep_answer_ar": "من منظور هندسة أمان الذاكرة، فإن الادعاء بإمكانية الحذف الفوري والتام للأسرار داخل بيئة تشغيل مدارة مثل ART Runtime هو ادعاء غير دقيق علمياً؛ فالنظام قد يقوم بنسخ مؤقت للبيانات أثناء تحويل الترميز إلى UTF-8 أو معالجة أحداث الشاشة. ولكن الهندسة المتقدمة تركز على تقليص فترة الخطر من ساعات طويلة إلى بضع ميكروثانية فقط.\n\nالهدف الأمني الرئيسي هو حماية البيانات من هجمات تفريغ الذاكرة Memory Dumps؛ فإذا نجح مهاجم في استخراج الذاكرة بوجود صلاحيات الروت أو عند فحص ملفات الانهيار Tombstones بعد توقف التطبيق، فإن أي مصفوفة لم يتم تصفيرها ستظهر نصوصها الصريحة بوضوح تام. ولذلك نحرص على تصفير المصفوفات حتمياً في بلوك finally لضمان التنفيذ حتى لو حدث استثناء برمجي.\n\nوعند عبور حدود الـ JNI إلى كود C++، نواجه ثغرة برمجية شهيرة تسمى Dead-Store Elimination؛ حيث يكتشف مجمع الكود المحسن أن الذاكرة سيتم تحريرها بـ free مباشرة بعد التصفير فيعتبر دالة memset استهلاكاً زائداً ويلغيها من كود التجميع النهائي. وللتصدي لذلك، نستخدم دالة explicit_bzero أو نمرر المؤشر عبر متغير volatile، مما يجبر المعالج على مسح الرام فيزيائياً وإغلاق ثغرات التلصص على الذاكرة. كما نضيف علامة FLAG_SECURE لنوافذ التطبيق لمنع لقطات الشاشة في الـ Recents Screen، ونعطل تفريغ ملفات HPROF التلقائي أثناء الانهيارات لحماية البيانات الحساسة من الوصول غير المصرح به."
    }
}

# ==========================================
# SEC-18: How do you validate exported components, deep links, and PendingIntents?
# ==========================================
DATA["SEC-18"] = {
    "concept_en": """Validating Android component boundaries, deep links, and PendingIntents protects an application against unauthorized inter-process invocation, privilege escalation, and intent redirection attacks. Components (Activities, Services, BroadcastReceivers, ContentProviders) must declare android:exported="false" by default unless intended for external cross-app communication. When components must be exported, access should be constrained using signature-level custom permissions (android:protectionLevel="signature") or caller validation (checking Binder.getCallingUid() and PackageManager.hasSigningCertificate()). For deep links, custom URL schemes (like myapp://) provide zero cryptographic verification and are vulnerable to scheme hijacking by malicious third-party apps; enterprise applications mandate Android App Links, which cryptographically bind web domains to the app binary using Digital Asset Links (assetlinks.json). When constructing PendingIntents, developers must enforce FLAG_IMMUTABLE (mandated in Android 12+) to prevent malicious receiving applications from mutating the underlying Intent's action, data URI, or extras via fillIn() to hijack internal privileged workflows.""",
    "walkthrough_en": """Securing PendingIntents, component boundaries, and deep link URI validation:
```kotlin
// 1. Mandatory FLAG_IMMUTABLE for secure PendingIntent instantiation
fun createSecureNotificationPendingIntent(context: Context, orderId: String): PendingIntent {
    val explicitIntent = Intent(context, OrderDetailsActivity::class.java).apply {
        putExtra("ORDER_ID", orderId)
        // Explicit component prevents intent redirection
    }
    
    // FLAG_IMMUTABLE stops third parties from mutating extras via fillIn()
    return PendingIntent.getActivity(
        context,
        REQUEST_CODE_ORDER,
        explicitIntent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
    )
}

// 2. Strict deep link URI validation and parameter sanitization
fun sanitizeDeepLinkUri(incomingUri: Uri): String? {
    // Enforce trusted HTTPS authority rather than custom schemes
    if (incomingUri.scheme != "https" || incomingUri.host != "bank.example.com") {
        return null // Reject untrusted schemes or rogue hosts
    }
    val path = incomingUri.path ?: return null
    if (!path.startsWith("/transfer/verify")) return null

    // Sanitize query parameter to prevent path traversal or injection
    val transactionToken = incomingUri.getQueryParameter("token")
    return if (transactionToken?.matches(Regex("^[a-zA-Z0-9_-]{32,64}$")) == true) {
        transactionToken
    } else {
        null
    }
}
```""",
    "short_en": """We secure component boundaries by setting exported to false by default or gating public endpoints with signature permissions. For deep links, we mandate Android App Links with Digital Asset Links and strictly sanitize parameters. For PendingIntents, we enforce FLAG_IMMUTABLE with explicit component intents, preventing malicious apps from hijacking internal actions.""",
    "structured_en": """Securing Android component boundaries requires strict validation of input vectors to prevent privilege escalation and unauthorized access.
All components must declare android:exported=false by default in AndroidManifest.xml.
If a component must be exported to receive external events, we protect it with custom signature permissions or verify the calling package's signing certificate using PackageManager before executing privileged actions.
For deep links, relying on custom URI schemes exposes users to link hijacking because any app can register the same scheme.
Instead, we implement Android App Links, which require hosting a digital asset links JSON file on our HTTPS domain to cryptographically verify domain ownership at install time.
When handling incoming deep links, we strictly validate URIs against an allowlist and sanitize all parameters against injection attacks.
On the Intent front, PendingIntents must always specify an explicit component and include FLAG_IMMUTABLE.
Omitting immutability allows an untrusted receiving application to modify the intent's payload using the fillIn method, redirecting execution to private application components.""",
    "deep_senior_en": """Component vulnerability analysis represents one of the most prevalent attack surfaces in modern mobile development, often leading to full account takeover or local privilege escalation.
When an activity or service is marked as exported without strict permission gates, any malicious application on the device can launch it directly with forged Intent extras, bypassing login screens and business validations.
In multi-app enterprise suites, we secure exported components using signature permissions; Android enforces at the kernel and framework level that only apps signed with the identical developer certificate can invoke the component.
When deep links are introduced, standard custom URL schemes are inherently insecure because Android does not enforce unique scheme registration; two apps can register the same custom scheme, resulting in disambiguation dialogs or silent traffic interception.
Android App Links solve this through Digital Asset Links verification, ensuring our app exclusively handles the domain.
Once inside the activity, we treat the incoming Intent data URI as untrusted user input: we reject path traversal characters (such as ../), validate expected paths, and sanitize query parameters against strict regex patterns.
Regarding PendingIntents, Android 12 made explicit mutability flags mandatory for a reason.
A mutable PendingIntent granted to a third party or system notification allows a rogue application to invoke fillIn() and overwrite the intent's action, data URI, or flags.
Attackers exploit this via Intent Redirection, forcing our application to launch unexported internal components with our own elevated permissions.
Enforcing FLAG_IMMUTABLE and explicit component targeting permanently closes this vulnerability.""",
    "meta_ar": {
        "id": "SEC-18",
        "questionAr": "كيف تتحقق من أمان المكونات المصدرة (Exported Components) والروابط العميقة و PendingIntents؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التحكم في المكونات المصدرة وتعيين `exported=false` افتراضياً، وتأمين المكونات المصدرة بصلاحيات التوقيع (Signature Permissions)، والفرق الأمني بين Custom Schemes و Android App Links مع AssetLinks، وتأمين PendingIntents بخاصية FLAG_IMMUTABLE ضد هجمات Intent Redirection.",
        "concept_ar": "تأمين حدود مكونات أندرويد يتطلب جعل المكونات (Activities, Services, Receivers) غير مصدرة (`exported=false`) افتراضياً إلا للضرورة، وحمايتها بصلاحيات التوقيع (Signature Permissions) للاتصال بين تطبيقات الشركة. كما يفرض استبدال روابط Custom Schemes بروابط Android App Links المثبتة بشهادة assetlinks.json لمنع سرقة الروابط، وتأمين PendingIntents بفرض `FLAG_IMMUTABLE` واستهداف كلاسات صريحة لمنع التلاعب بمعلمات الـ Intent وإعادة توجيهها داخلياً.",
        "walkthrough_ar": "تأمين PendingIntent بخاصية FLAG_IMMUTABLE والتحقق الصارم من معلمات الروابط العميقة:\n```kotlin\n// 1. إنشاء PendingIntent غير قابل للتعديل ومحدد الكلاس صراحة:\nval pendingIntent = PendingIntent.getActivity(\n    context, 0, Intent(context, TargetActivity::class.java),\n    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT\n)\n// 2. التحقق الصارم من الروابط العميقة ورفض العناوين غير الموثوقة:\nfun isValidDeepLink(uri: Uri): Boolean =\n    uri.scheme == \"https\" && uri.host == \"bank.example.com\" && uri.path == \"/checkout\"\n```",
        "why_it_matters_ar": "ترك المكونات مصدرة دون حماية يسمح للتطبيقات الخبيثة على الهاتف بتخطي شاشات تسجيل الدخول وتنفيذ عمليات بنكية، واستخدام روابط غير موثقة يسمح باعتراض جلسات المستخدم.",
        "worked_example_ar": "التحقق من توقيع التطبيق المتصل عند حدود الـ IPC للمكونات المصدرة:\n```kotlin\nfun verifyCallingAppSignature(context: Context, callingUid: Int): Boolean {\n    val packages = context.packageManager.getPackagesForUid(callingUid) ?: return false\n    return packages.any {\n        context.packageManager.hasSigningCertificate(it, TRUSTED_SHA256, PackageManager.CERT_INPUT_SHA256)\n    }\n}\n```",
        "trade_offs_ar": "فرض App Links يتطلب استضافة ملف assetlinks.json وإثبات ملكية الدومين، واستخدام FLAG_IMMUTABLE يمنع تعديل الإشعار في بعض الحالات الخاصة لكنه يغلق ثغرات أمنية كارثية.",
        "failure_modes_ar": "تصدير BroadcastReceiver ينفذ أوامر حساسة بناءً على قيمة Intent Extra صريحة دون صلاحية حماية، أو استخدام PendingIntent قابل للتعديل (Mutable) يسمح بتغيير وجهته لأكواد داخلية غير مصدرة.",
        "production_perspective_ar": "في التطبيقات المالية، نلزم جميع المطورين بـ `exported=false` افتراضياً، ونراجع Manifest عبر أدوات Lint، ونلزم الروابط العميقة بالتحقق من assetlinks.json حصراً مع تعقيم كافة المدخلات.",
        "how_to_answer_ar": "قسم الإجابة إلى ثلاثة أركان واضحة: المكونات المصدرة وتأمينها بـ exported=false وصلاحيات التوقيع، ثم الروابط العميقة وتفضيل App Links على Custom Schemes، واختم بـ PendingIntents وخاصية FLAG_IMMUTABLE.",
        "talking_points_ar": "الخاصية android:exported، وصلاحيات التوقيع (Signature Permissions)، وروابط Android App Links وملف assetlinks.json، وهجمات Intent Redirection، وخاصية PendingIntent.FLAG_IMMUTABLE.",
        "follow_ups_ar": "- **المحاور:** \"ما هو الخطر الأمني في استخدام Custom Schemes مثل `myapp://pay`؟\"\n  **المرشح:** \"لا يوجد ملكية حصرية لهذه المخططات؛ فأي تطبيق خبيث يمكنه تسجيل نفس المخطط في الـ Manifest واعتراض الروابط وسرقة الـ Tokens الممررة فيها، والحل هو App Links.\"\n\n- **المحاور:** \"كيف يستغل المخترق غياب FLAG_IMMUTABLE في PendingIntent؟\"\n  **المرشح:** \"يستخدم دالة fillIn لتعديل الـ Action والبيانات للـ Intent الأصلي وتوجيهه لفتح شاشات داخلية غير مصدرة (Intent Redirection) باستغلال صلاحيات تطبيقنا.\"",
        "self_check_ar": "هل شرحت exported=false وصلاحيات التوقيع؟ هل وضحت App Links مقابل Custom Schemes؟ وهل بينت دور FLAG_IMMUTABLE؟",
        "references_ar": f"- [Android App Links Documentation](https://developer.android.com/training/app-links) — التوثيق الرسمي لروابط التطبيقات الموثقة بملف assetlinks.json.\n- [PendingIntent Security Best Practices](https://developer.android.com/guide/components/intents-filters#PendingIntent) — إرشادات جوجل لتأمين الـ PendingIntents وفرض عدم القابلية للتعديل.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نؤمن حدود التطبيق بجعل المكونات غير مصدرة عبر exported=false افتراضياً وحماية المكونات العامة بصلاحيات التوقيع الرقمي. وبالنسبة للروابط العميقة، نعتمد على Android App Links الموثقة بملف assetlinks.json ونعقم معلمات العناوين، ونلزم الـ PendingIntents بخاصية FLAG_IMMUTABLE واستهداف كلاسات صريحة لمنع التلاعب بوجهتها.",
        "best_answer_ar": "تأمين حدود التطبيق والـ IPC في أندرويد يرتكز على إحكام السيطرة على نقاط الدخول الثلاث: المكونات المصدرة، والروابط العميقة، والـ PendingIntents.\n\nبالنسبة للمكونات، تفرض المعمارية السليمة تعيين android:exported إلى false افتراضياً لجميع الأنشطة والخدمات والمستقبلات. وإذا تطلب العمل تصدير مكون للتواصل بين تطبيقات تابعة لنفس الشركة، نقوم بحمايته بصلاحيات التوقيع signature permissions أو فحص شهادة التطبيق المتصل عبر PackageManager للتحقق من هويته قبل تنفيذ أي أمر.\n\nوبالنسبة للروابط العميقة، نتجنب استخدام الروابط المخصصة Custom Schemes مثل myapp:// لسهولة سرقتها وانتحالها من تطبيقات أخرى على نفس الهاتف، ونستبدلها بـ Android App Links التي تتطلب إثبات ملكية النطاق عبر ملف assetlinks.json على السيرفر، مع فحص وتعقيم كافة المعلمات البرمجية بصرامة. وأخيراً، نلزم كافة كائنات PendingIntent بخاصية FLAG_IMMUTABLE واستهداف كلاسات صريحة لمنع التطبيقات المستقبلة من التلاعب بمحتوى الـ Intent عبر دالة fillIn واستغلاله لتنفيذ هجمات إعادة التوجيه الخبيثة.",
        "deep_answer_ar": "تمثل ثغرات المكونات غير المحمية أحد أخطر مسارات الهجوم في تطبيقات أندرويد؛ لأنها تتيح للتطبيقات الخبيثة استغلال صلاحيات تطبيقنا الموثوق لتنفيذ عمليات حساسة بالوكالة فيما يعرف بهجمات Privilege Escalation.\n\nعندما نترك نشاطاً أو خدمة مصدرة دون حماية صريحة، يستطيع أي تطبيق خبيث إرسال Intent محقون ببيانات مزيفة لتخطي بوابات الدخول والوصول المباشر لشاشات التحويل المالي. ولمنع ذلك، نغلق جميع المكونات، وعند بناء منظومات متعددة التطبيقات للشركات الكبرى، نعتمد على صلاحيات التوقيع الرقمي حيث تضمن نواة أندرويد رفض أي اتصال قادم من تطبيق غير موقع بنفس الشهادة.\n\nوفي مجال الروابط العميقة، يمثل استخدام Custom Schemes خطأ جسيماً؛ لعدم وجود آلية تمنع تطبيقاً منافساً من تسجيل نفس المعرف في الـ Manifest وسرقة رموز الدخول. ويحل معيار Android App Links هذه الأزمة عبر التحقق التشفيري وقت التثبيت من خلال ملف Digital Asset Links، مما يضمن فتح الرابط حصرياً في تطبيقنا الرسمي، مع تعقيم المسارات البرمجية لمنع هجمات Path Traversal.\n\nأما بالنسبة لـ PendingIntents، فقد جعل أندرويد 12 تحديد حالة القابلية للتعديل أمراً إلزامياً؛ لأن تركها Mutable يسمح للتطبيق الخبيث الذي يستلم الإشعار باستدعاء دالة fillIn والتلاعب بوجهة الطلب واستبدال البيانات ليجبر تطبيقنا على فتح شاشات داخلية غير مصدرة مستغلاً هويتنا الموثوقة، وتطبيق FLAG_IMMUTABLE يغلق هذا الباب نهائياً."
    }
}

# ==========================================
# SEC-19: How do you secure WebView, JavaScript bridges, and file/content URIs?
# ==========================================
DATA["SEC-19"] = {
    "concept_en": """Securing Android WebView components requires mitigating cross-site scripting (XSS), arbitrary code execution via JavaScript bridges, and local file exfiltration through file and content URIs. WebViews run Chromium rendering engines inside the host application process, meaning compromised web content shares the app's full sandboxed storage and network permissions. First, local file access must be explicitly disabled via WebSettings: setAllowFileAccess(false), setAllowContentAccess(false), and disallowing cross-file access. Instead of loading sensitive assets via file:// schemes, applications use WebViewAssetLoader, which intercepts requests and serves local assets under a virtual, secure HTTPS domain. Second, exposing native methods via @JavascriptInterface represents a critical threat: any untrusted page loaded into the WebView or injected via XSS can invoke exposed native methods. Applications must restrict JavaScript bridges exclusively to trusted first-party HTTPS domains, enforce strict origin verification inside shouldOverrideUrlLoading, and avoid injecting bridge objects into WebViews that navigate open web URLs.""",
    "walkthrough_en": """Hardening WebView settings, asset loading, and domain-bound JavaScript bridge:
```kotlin
// 1. Hardening WebView settings to eliminate file scheme vulnerabilities
fun configureSecureWebView(webView: WebView, context: Context) {
    webView.settings.apply {
        javaScriptEnabled = true // Enable only if strictly necessary
        allowFileAccess = false // Block raw local file access
        allowContentAccess = false // Block content:// provider access
        // Disallow cross-origin access from file URLs
        allowFileAccessFromFileURLs = false
        allowUniversalAccessFromFileURLs = false
        mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
    }

    // 2. Safe local asset loading via virtual HTTPS domain
    val assetLoader = WebViewAssetLoader.Builder()
        .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(context))
        .build()

    webView.webViewClient = object : WebViewClient() {
        override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {
            return assetLoader.shouldInterceptRequest(request.url)
        }

        override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
            val url = request.url.toString()
            // Strict allowlist: only navigate within first-party domain
            return if (url.startsWith("https://checkout.bank.example.com/")) {
                false // Allow navigation
            } else {
                true // Block untrusted third-party navigation!
            }
        }
    }

    // 3. Secure JavascriptInterface bound to trusted origin
    webView.addJavascriptInterface(SecurePaymentBridge(), "AndroidPaymentBridge")
}

class SecurePaymentBridge {
    @JavascriptInterface
    fun notifyPaymentCompleted(orderId: String) {
        // Enforce strict parameter validation and verify caller state
    }
}
```""",
    "short_en": """We secure WebView by disabling local file and content access, serving local assets under virtual HTTPS using WebViewAssetLoader, blocking mixed content, and strictly restricting JavaScript interfaces to verified first-party HTTPS domains to prevent malicious scripts from executing native code.""",
    "structured_en": """Securing WebView instances requires treating web content as inherently dangerous and enforcing strict sandboxing controls.
We disable local file and content schemes by setting allowFileAccess and allowContentAccess to false in WebSettings, neutralizing attacks that attempt to exfiltrate private app databases via file URLs.
To load local HTML and JavaScript assets securely, we implement WebViewAssetLoader, which hosts assets under a virtual HTTPS domain that respects modern web origin boundaries.
For network transport, we eliminate insecure channels by setting mixedContentMode to never allow HTTP assets on HTTPS pages.
Native bridges created with @JavascriptInterface demand the tightest scrutiny created with @JavascriptInterface.
Because any script running inside the WebView can call exposed bridge methods, we only attach interfaces to WebViews locked to first-party origins.
In WebViewClient, we implement shouldOverrideUrlLoading to inspect target URLs and terminate navigation if an attempt is made to load untrusted third-party domains.""",
    "deep_senior_en": """From an adversarial perspective, an insecurely configured WebView represents a direct bridge between untrusted web content and the host operating system's native process memory.
If an application enables JavaScript and adds a @JavascriptInterface while allowing the WebView to navigate to arbitrary URLs or load user-generated links, an attacker who achieves cross-site scripting on that page can invoke native methods directly, exfiltrating auth tokens or triggering financial actions.
On legacy Android versions, reflective exploitation of addJavascriptInterface allowed arbitrary native code execution; on modern platforms, while reflection is restricted, exposed methods remain an accessible API surface.
Furthermore, loading local files via file:// URLs is historically notorious for file-theft vulnerabilities: a malicious HTML file downloaded to external storage can read app-private databases or shared preferences using cross-origin file navigation.
We mitigate these systemic vectors through three architecture rules.
To eliminate attack surfaces, we completely disallow file access, setting allowFileAccess, allowFileAccessFromFileURLs, and allowUniversalAccessFromFileURLs to false, relying strictly on WebViewAssetLoader.
Second, we restrict navigation strictly to trusted HTTPS domains using an allowlist in shouldOverrideUrlLoading, blocking iframes and redirects to third-party endpoints.
Third, we apply least privilege to JavaScript bridges, validating incoming parameters with strict regex schemas and ensuring that sensitive actions require independent user confirmation rather than blind execution upon web trigger.""",
    "meta_ar": {
        "id": "SEC-19",
        "questionAr": "كيف تقوم بتأمين الـ WebView وجسور جافا سكريبت (JS Bridges) وعناوين الملفات؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم المخاطر الأمنية للـ WebView، وتعطيل مسارات الملفات المحلية (File/Content Access)، واستخدام WebViewAssetLoader، وتأمين جسور جافا سكريبت (@JavascriptInterface)، وتقييد التصفح بنطاقات HTTPS الموثوقة فقط عبر shouldOverrideUrlLoading.",
        "concept_ar": "تأمين الـ WebView يتطلب التعامل مع محتوى الويب كبيئة غير موثوقة تعمل داخل عملية التطبيق الخاصة. تشمل الحماية تعطيل الوصول للملفات المحلية عبر `allowFileAccess=false` و `allowContentAccess=false`، واستخدام `WebViewAssetLoader` لتحميل الملفات المحلية عبر نطاق HTTPS افتراضي آمن. كما يفرض تأمين جسور جافا سكريبت (`@JavascriptInterface`) بحصرها حصرياً على صفحات تابعة للشركة موثقة عبر HTTPS، والتحقق الصارم من الروابط داخل `shouldOverrideUrlLoading` لمنع تنفيذ أكواد خبيثة في بيئة التطبيق الأصلية.",
        "walkthrough_ar": "تهيئة الـ WebView الآمنة واستخدام WebViewAssetLoader وتقييد الروابط المسموحة:\n```kotlin\nwebView.settings.apply {\n    allowFileAccess = false // منع قراءة ملفات التطبيق المحلية\n    allowContentAccess = false\n    mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW\n}\n// حصر التصفح في نطاق الدفع التابع للبنك فقط:\nwebView.webViewClient = object : WebViewClient() {\n    override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {\n        return !request.url.toString().startsWith(\"https://checkout.bank.example.com/\")\n    }\n}\n```",
        "why_it_matters_ar": "التهيئة الخاطئة للـ WebView تتيح لأي ثغرة XSS على الصفحة استدعاء دوال الكود الأصلي للتطبيق، أو سرقة ملفات قاعدة بيانات التطبيق الحساسة عبر ثغرات العناوين المحلية file://.",
        "worked_example_ar": "تحميل ملفات HTML المحلية بأمان عبر WebViewAssetLoader بدون ثغرات file://:\n```kotlin\nval assetLoader = WebViewAssetLoader.Builder()\n    .addPathHandler(\"/assets/\", WebViewAssetLoader.AssetsPathHandler(context))\n    .build()\n// يتم تحميل الملف تحت رابط https://appassets.androidplatform.net/assets/index.html\n```",
        "trade_offs_ar": "تعطيل ملفات الـ file:// يتطلب تنظيم أصول الويب عبر WebViewAssetLoader، وتقييد الروابط يمنع فتح صفحات الويب الخارجية داخل نفس الشاشة ويتطلب فتحها في متصفح خارجي.",
        "failure_modes_ar": "تفعيل JavaScript ومشاركة @JavascriptInterface في WebView يفتح روابط عشوائية يتصفحها المستخدم، مما يسمح لأي صفحة خارجية باستدعاء دوال التطبيق البنكية بحرية.",
        "production_perspective_ar": "في التطبيقات المالية، نحظر استخدام WebView تماماً للمهام الحساسة إلا لصفحات بوابات الدفع الرسمية، مع حصر النطاقات المسموحة وتعطيل حفظ كلمات المرور وكاش النماذج في الويب.",
        "how_to_answer_ar": "صنف الحماية إلى ثلاث خطوات: تعطيل مسارات الملفات والمحتوى واستخدام WebViewAssetLoader، تأمين جسور @JavascriptInterface بحصرها في نطاقات موثوقة فقط، وتقييد التنقل الشبكي عبر shouldOverrideUrlLoading.",
        "talking_points_ar": "أخطار WebView والـ XSS، وإلغاء allowFileAccess و allowContentAccess، ومكتبة WebViewAssetLoader، وتأمين @JavascriptInterface، وفحص النطاقات في shouldOverrideUrlLoading.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر استخدام رابط `file:///android_asset/` خطيراً أمنياً؟\"\n  **المرشح:** \"لأنه يفتح الباب لثغرات Same-Origin Policy للملفات المحلية؛ مما يسمح لملف خبيث بالوصول لملفات الـ SharedPreferences وقواعد البيانات، والبديل الآمن هو WebViewAssetLoader.\"\n\n- **المحاور:** \"كيف تمنع هجمات XSS على صفحة الويب من السيطرة على التطبيق عبر الـ JS Bridge؟\"\n  **المرشح:** \"أقصر إضافة الجسر على صفحات الـ HTTPS الخاصة بنا فقط، وأعقم كافة المدخلات القادمة من الويب، وأتأكد من عدم تنفيذ أي عملية مالية إلا بعد تحقق محلي مستقل.\"",
        "self_check_ar": "هل شرحت مخاطر file access وكيفية تعطيله؟ هل ذكرت WebViewAssetLoader؟ وهل وضحت حماية @JavascriptInterface؟",
        "references_ar": f"- [Android Developers - Safe Browsing and WebView Security](https://developer.android.com/privacy-and-security/security-webview) — دليل جوجل الرسمي لتأمين الـ WebView.\n- [AndroidX Webkit WebViewAssetLoader](https://developer.android.com/reference/androidx/webkit/WebViewAssetLoader) — التوثيق الرسمي لمكتبة تحميل الأصول المحلية بأمان.",
        "quick_answer_ar": "نؤمن الـ WebView بتعطيل الوصول للملفات المحلية والمحتوى عبر إعدادات WebSettings، واستخدام WebViewAssetLoader لتحميل الملفات المحلية بنطاق HTTPS افتراضي آمن، وحظر الاتصالات غير المشفرة، مع قصر جسور جافا سكريبت على صفحاتنا الرسمية والتحقق الصارم من النطاقات المسموح بفتحها لمنع تنفيذ الأكواد الخبيثة.",
        "best_answer_ar": "يتطلب تأمين الـ WebView في أندرويد معاملة صفحات الويب كبيئة معادية يمكن اختراقها، وتطبيق قيود صارمة على مستوى النظام والتطبيق.\n\nالخطوة الأولى هي إغلاق ثغرات الملفات المحلية؛ فنقوم بتعطيل allowFileAccess و allowContentAccess تماماً في WebSettings لمنع استغلال عناوين file:// لسرقة قواعد البيانات وملفات التطبيق الخاصة. ولتحميل ملفات HTML و JS المحلية، نستخدم أداة WebViewAssetLoader التي تشغل الأصول تحت نطاق HTTPS افتراضي يحترم حدود الأمان المعيارية للويب.\n\nالخطوة الثانية هي حظر المحتوى المختلط بجعل mixedContentMode يمنع تحميل أي وسائط غير مشفرة. وأخيراً، نتوخى الحذر البالغ مع جسور جافا سكريبت @JavascriptInterface؛ فلا نضيف الجسر إلا للشاشات المخصصة حصرياً لنطاقات موثوقة تابعة للشركة، ونفحص عنوان الرابط في دالة shouldOverrideUrlLoading لمنع إعادة التوجيه لصفحات خارجية مشبوهة، مع تعقيم وتدقيق كافة المدخلات الممررة من الويب للأكواد الأصلية.",
        "deep_answer_ar": "من منظور النمذجة التهديدية للأنظمة الهجينة، يمثل الـ WebView جسراً خطيراً يربط بين كود الويب غير الموثوق وبين الذاكرة وصلاحيات التطبيق الأصلية في بيئة أندرويد المعزولة.\n\nإذا قام المطور بتفعيل الجافا سكريبت وربط جسر برمجيات @JavascriptInterface في نافذة ويب تتصفح روابط مفتوحة أو محتوى مستخدمين، فإن أي ثغرة Cross-Site Scripting على الموقع تمنح المهاجم قدرة فورية على استدعاء دوال الكود الأصلي للتطبيق وسرقة الرموز وتنفيذ تحويلات مالية. لذلك نفرض قاعدة صارمة: حظر وجود جسور برمجية في أي WebView يتصفح نطاقات عامة.\n\nوعلاوة على ذلك، عانى نظام أندرويد تاريخياً من ثغرات قاتلة بسبب بروتوكول file://؛ حيث يستطيع كود HTML خبيث استغلال صلاحيات الملفات المحلية وسحب ملفات SharedPreferences وقواعد بيانات SQLite الخاصة بالتطبيق. ونغلق هذا التهديد نهائياً بتعطيل كافة خيارات الـ File Access والاعتماد الحصري على WebViewAssetLoader، حيث يعترض الطلبات برمجياً ويقدم الملفات تحت نطاق HTTPS افتراضي يخضع لقيود Same-Origin Policy الصارمة.\n\nولإحكام الأمان، نتحقق في shouldOverrideUrlLoading من النطاق المسموح به عبر قائمة بيضاء مشددة، ونمنع التوجيه التلقائي، ونتعامل مع أي معلمات قادمة من دوال الجافا سكريبت كمدخلات مشبوهة تتطلب فحوصات Regex مستقلة قبل تنفيذ أي منطق على مستوى النظام. كما نفعل ميزة Safe Browsing برمجياً داخل إعدادات المتصفح، ونشفر كافة قنوات التخزين المؤقت WebSQL و LocalStorage، ونمسح بيانات الجلسة فور إغلاق شاشة العرض لضمان عدم بقاء أي أثر لبيانات العميل."
    }
}

# ==========================================
# SEC-20: How do you implement certificate pinning with a rotation/recovery strategy?
# ==========================================
DATA["SEC-20"] = {
    "concept_en": """Implementing certificate pinning in production Android applications mandates establishing a resilient cryptographic rotation and disaster-recovery architecture to avoid self-inflicted denial-of-service outages (the bricked app scenario). Rather than pinning ephemeral X.509 leaf certificates that expire frequently, senior engineers pin the SHA-256 hash of the Subject Public Key Info (SPKI). Pinning the public key allows infrastructure teams to renew expiring server certificates using the same cryptographic key pair without breaking deployed client applications. To survive private key compromises, scheduled rotations, or Certificate Authority revocations, a pin set must never contain only a single pin. An operational pin set requires at least three distinct pins: the primary production public key pin, an intermediate CA backup pin, and an offline disaster recovery backup pin corresponding to a cold key pair stored in an air-gapped corporate hardware security module (HSM). Furthermore, applications should integrate dynamic pin update channels managed via secure remote configuration or Play Integrity attestation to push new pins out-of-band without waiting for app store reviews.""",
    "walkthrough_en": """Implementing multi-pin SPKI pinning with cold disaster backup in OkHttp:
```kotlin
// Multi-pin strategy: Primary + Intermediate Backup + Cold Storage Disaster Recovery
val secureNetworkClient = OkHttpClient.Builder()
    .certificatePinner(
        CertificatePinner.Builder()
            // 1. Primary active leaf SPKI public key hash
            .add("api.fintech.bank", "sha256/WoiWRyIOVNa9ihaBciRSC7XHjliYS9VwUGOIud4PB18=")
            // 2. Intermediate Certificate Authority backup pin
            .add("api.fintech.bank", "sha256/rFjc3AbGqmDTUWBGoWrfNflFreUm7bmyG4520975WTu=")
            // 3. Cold offline backup pin stored in corporate hardware HSM vault
            .add("api.fintech.bank", "sha256/k2oTQLj4nsdKmSOGKEUbhwEYfEuDYV5R6g28AzERdOk=")
            .build()
    )
    .build()
```
Declarative Network Security Configuration with expiration safeguards:
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.fintech.bank</domain>
        <!-- Expiration date ensures app falls back to normal CA trust if abandoned -->
        <pin-set expiration="2027-06-30">
            <pin digest="SHA-256">WoiWRyIOVNa9ihaBciRSC7XHjliYS9VwUGOIud4PB18=</pin>
            <pin digest="SHA-256">rFjc3AbGqmDTUWBGoWrfNflFreUm7bmyG4520975WTu=</pin>
            <pin digest="SHA-256">k2oTQLj4nsdKmSOGKEUbhwEYfEuDYV5R6g28AzERdOk=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```""",
    "short_en": """We implement certificate pinning by hashing the Subject Public Key Info rather than full certificates, allowing cert renewals without changing keys. Our recovery strategy mandates three pins: the active production key, an intermediate backup, and a cold offline disaster recovery key stored in an HSM vault, accompanied by expiration dates in network security config to prevent bricking.""",
    "structured_en": """Certificate pinning hardens TLS by preventing Man-in-the-Middle attacks from compromised Certificate Authorities, but requires a rigorous operational recovery strategy.
To prevent service outages during routine certificate renewals, we pin the SHA-256 hash of the Subject Public Key Info rather than the full leaf certificate.
This allows backend infrastructure teams to renew expiring certificates while preserving the underlying public key pair, maintaining seamless connectivity for running applications.
To eliminate the catastrophic risk of bricking an application when a server key is compromised or rotated, we enforce a multi-pin topology.
The pin set must contain the active production key pin, an intermediate CA backup pin, and an offline cold backup pin generated from an unreleased key pair held in an air-gapped corporate vault.
In network security configuration XML, we define an expiration date attribute on the pin set; if an emergency occurs and certificates cannot be aligned, the platform safely falls back to standard CA trust rather than permanently bricking traffic.""",
    "deep_senior_en": """The supreme hazard of certificate pinning is not an external attacker, but operational misalignment between mobile engineering and infrastructure operations teams.
If operations rotates the backend TLS certificate with a new key pair without mobile team coordination, and older client applications lack the corresponding pin, every HTTPS call fails immediately with an SSLPeerUnverifiedException.
Because the application cannot connect to the server, it cannot even fetch remote configuration updates, effectively bricking the app until a new build is published and adopted through app store distribution cycles.
To architect an enterprise-grade pinning strategy, we enforce three invariant rules.
From an architectural standpoint, we exclusively pin the Subject Public Key Info (SPKI).
This decouples the cryptographic public key from the certificate's metadata and validity dates, allowing seamless certificate re-issuance under standard annual renewal cycles without altering the mobile binary.
Second, we mandate an N-plus-two pin configuration: one active key, one warm backup key on the server infrastructure, and one cold disaster-recovery key kept offline in a Hardware Security Module.
If the active key is compromised, infrastructure cuts over to the backup key instantly, and the mobile application continues functioning without downtime.
Third, in our declarative network_security_config.xml, we set a reasonable pin-set expiration date, and establish an out-of-band dynamic pinning fallback channel through our notification and attestation pipelines to push emergency pins to devices during zero-day recovery scenarios.""",
    "meta_ar": {
        "id": "SEC-20",
        "questionAr": "كيف تنفذ تثبيت الشهادات (Certificate Pinning) مع استراتيجية تدوير وتعافٍ من الكوارث؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم المخاطر التشغيلية لتثبيت الشهادات وخطر شلل التطبيق (Bricking the app)، والفرق بين تثبيت الشهادة وتثبيت الـ SPKI، واستراتيجية المفاتيح المتعددة (Primary, Intermediate, Cold Backup)، وتحديد تاريخ انتهاء الصلاحية للـ Pins.",
        "concept_ar": "تطبيق تثبيت الشهادات (Certificate Pinning) بأمان يتطلب استراتيجية تعافٍ محكمة لتجنب شلل التطبيق عند تجديد الشهادات. نثبت بصمة المفتاح العام (SPKI) بدلاً من الشهادة الكاملة لتجديد الشهادات بنفس المفتاح دون كسر التطبيقات المثبتة. ونلزم وجود ثلاثة مفاتيح في قائمة التثبيت: المفتاح الأساسي الفعال، ومفتاح جهة CA وسيطة احتياطي، ومفتاح طوارئ بارد (Cold Backup) محفوظ في خزنة عتادية غير متصلة بالإنترنت، مع وضع تاريخ انتهاء لصلاحية الـ Pins في الإعدادات كصمام أمان.",
        "walkthrough_ar": "تثبيت الـ SPKI بمفاتيح متعددة في OkHttp وضبط تاريخ الانتهاء كصمام أمان:\n```kotlin\nval client = OkHttpClient.Builder()\n    .certificatePinner(CertificatePinner.Builder()\n        .add(\"api.bank.com\", \"sha256/WoiWRyIOVNa9ihaBciRSC7XHjliYS9VwUGOIud4PB18=\") // الأساسي\n        .add(\"api.bank.com\", \"sha256/rFjc3AbGqmDTUWBGoWrfNflFreUm7bmyG4520975WTu=\") // وسيط\n        .add(\"api.bank.com\", \"sha256/k2oTQLj4nsdKmSOGKEUbhwEYfEuDYV5R6g28AzERdOk=\") // بارد للطوارئ\n        .build())\n    .build()\n```",
        "why_it_matters_ar": "تغيير شهادة السيرفر في غياب مفاتيح احتياطية في التطبيق يسبب توقفاً كلياً وفورياً للخدمة لدى ملايين المستخدمين ولا يمكن إصلاحه إلا بتحديث إجباري من المتجر.",
        "worked_example_ar": "صمام الأمان بوضع تاريخ انتهاء صلاحية التثبيت في network_security_config.xml:\n```xml\n<pin-set expiration=\"2027-06-30\">\n    <pin digest=\"SHA-256\">WoiWRyIOVNa9ihaBciRSC7XHjliYS9VwUGOIud4PB18=</pin>\n    <pin digest=\"SHA-256\">k2oTQLj4nsdKmSOGKEUbhwEYfEuDYV5R6g28AzERdOk=</pin>\n</pin-set>\n```",
        "trade_offs_ar": "تثبيت الشهادات يقضي على هجمات MITM تماماً، لكنه يفرض تعقيداً تنسيقياً شديداً مع فريق البنية التحتية ومخاطرة تشغيلية عالية تتطلب خطط طوارئ مسبقة.",
        "failure_modes_ar": "تثبيت شهادة Leaf واحدة فقط، وعند انتهاء صلاحيتها يقوم فريق السيرفر بتوليد مفتاح جديد، مما يؤدي لانهيار جميع اتصالات التطبيق واستحالة التواصل مع السيرفر حتى لجلب إعدادات جديدة.",
        "production_perspective_ar": "في بنوك التكنولوجيا المالية، نثبت دائماً الـ SPKI، ونحتفظ بمفتاح طوارئ بارد في خزنة HSM، ونحدد جدول تدوير مسبق ينشر المفاتيح الجديدة في التطبيق قبل تفعيلها في السيرفر بستة أشهر على الأقل.",
        "how_to_answer_ar": "ابدأ ببيان الخطر التشغيلي الأكبر وهو شلل التطبيق (Bricking)، ثم وضح الحل المعماري بتثبيت الـ SPKI بدلاً من الشهادة، واشرح استراتيجية المفاتيح الثلاثة (فعال، وسيط، وبارد للطوارئ)، واختم بصمام أمان تاريخ الانتهاء.",
        "talking_points_ar": "شلل التطبيق (Self-inflicted DoS)، وتثبيت تجزئة الـ SPKI مقابل الشهادة، واستراتيجية المفاتيح المتعددة، ومفتاح الطوارئ البارد (Cold Key)، وتاريخ انتهاء الصلاحية expiration date.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نضع خاصية expiration في الـ pin-set؟\"\n  **المرشح:** \"لتعمل كصمام أمان أخير؛ فإذا هُجر التطبيق أو حدثت كارثة ولم يتم تحديث المفاتيح، يعود أندرويد تلقائياً للتحقق العادي من شهادات الـ CA بدلاً من شلل التطبيق للأبد.\"\n\n- **المحاور:** \"ماذا تفعل إذا تسرب المفتاح الخاص لسيرفر الشركة والتطبيق يطبق Pinning؟\"\n  **المرشح:** \"يقوم فريق السيرفر فوراً بالتبديل للمفتاح الاحتياطي البارد المبرمج مسبقاً في التطبيق، مما يسمح بحماية النظام واستمرار عمل التطبيقات دون انقطاع.\"",
        "self_check_ar": "هل فرقت بين تثبيت الشهادة وتثبيت SPKI؟ هل شرحت استراتيجية المفاتيح الثلاثة؟ وهل بينت خاصية تاريخ الانتهاء كصمام أمان؟",
        "references_ar": f"- [OWASP Certificate Pinning Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html) — المعيار الرسمي لإدارة تثبيت الشهادات وتفادي شلل التطبيقات.\n- [Android Network Security Config Pinning](https://developer.android.com/privacy-and-security/security-config#CertificatePinning) — الدليل الرسمي لإعدادات التثبيت وتواريخ الانتهاء في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "ننفذ تثبيت الشهادات بتجزئة المفتاح العام SPKI بدلاً من الشهادة الكاملة للسماح بتجديد الشهادات بنفس المفتاح دون كسر التطبيقات، وتتطلب استراتيجية التعافي وضع ثلاثة مفاتيح: المفتاح الأساسي الفعال، ومفتاح جهة الاعتماد الوسيطة، ومفتاح طوارئ بارد مخزن في خزنة عتادية غير متصلة بالإنترنت، مع وضع تاريخ انتهاء لصلاحية التثبيت كصمام أمان.",
        "best_answer_ar": "يمثل تثبيت الشهادات وسيلة دفاعية فائقة ضد هجمات اعتراض البيانات، لكنه يحمل مخاطرة تشغيلية كبرى قد تؤدي إلى شلل التطبيق كلياً ما لم يُصمم باستراتيجية تعافٍ محكمة.\n\nالقرار المعماري الأول هو تثبيت تجزئة المفتاح العام Subject Public Key Info بدلاً من الشهادة الورقية الكاملة؛ لأن الشهادة تنتهي سنوياً بينما يمكن تجديدها بنفس زوج المفاتيح، مما يضمن استمرار عمل التطبيقات القديمة دون انقطاع.\n\nوالقرار المعماري الثاني هو حظر تثبيت مفتاح فردي واحد؛ بل نعتمد سياسة المفاتيح الثلاثة: المفتاح الأساسي الفعال على السيرفر، ومفتاح احتياطي لجهة الشهادات الوسيطة، ومفتاح طوارئ بارد وغير متصل بالإنترنت محفوظ في خزنة عتادية HSM خاصة بالشركة. فإذا تعرض السيرفر للاختراق، يمكن للبنية التحتية التبديل للمفتاح الاحتياطي البارد فوراً دون أن يشعر المستخدم بأي توقف. وأخيراً، نضع خاصية تاريخ الانتهاء expiration date في إعدادات الشبكة ليعود التطبيق للثقة القياسية في حال حدوث خطأ تشغيلي غير متوقع بدلاً من موت الاتصال للأبد.",
        "deep_answer_ar": "الخطر الأكبر في تثبيت الشهادات ليس الهجوم الخارجي، بل غياب التنسيق التشغيلي بين فريق تطبيقات الموبايل وفريق عمليات البنية التحتية السحابية.\n\nفإذا قام فريق العمليات بتجديد شهادة السيرفر بزوج مفاتيح جديد دون إخطار فريق الموبايل مسبقاً، تفشل جميع اتصالات HTTPS وترمي استثناء SSLPeerUnverifiedException. وبما أن التطبيق عاجز عن الاتصال بالسيرفر، فإنه يعجز حتى عن جلب التحديثات أو الإعدادات السحابية، ويدخل في حالة شلل ذاتي تام Self-inflicted Denial of Service لا يحلها سوى نشر تحديث جديد للمتجر.\n\nلتفادي هذه الكارثة، نطبق ثلاث قواعد معمارية صارمة. الأولى هي قصر التثبيت على تجزئة الـ SPKI، مما يفصل بصمة التشفير عن البيانات الوصفية وتواريخ انتهاء الشهادة، ويتيح تجديد الشهادة السنوي بسلاسة. والثانية هي استراتيجية المفاتيح الثلاثية، بحيث يحتوي التطبيق دائماً على مفتاح احتياطي بارد لم يُستخدم قط ومحفوظ في خزنة عتادية معزولة، ومفتاح وسيط لجهة الـ CA.\n\nوالثالثة هي وضع تاريخ انتهاء منطقي للـ Pin Set في ملف network_security_config.xml؛ ليعمل كصمام أمان أخير يعيد التطبيق لنظام التحقق القياسي إذا تجاوز التاريخ المحدد، بالإضافة لبناء مسار تحديث ديناميكي للمفاتيح عبر قنوات إشعارات موثوقة ومحمية بـ Play Integrity لضمان صمود التطبيق أمام أي سيناريو طارئ. كما نربط منظومة المراقبة السحابية بتنبيهات حية ترصد ارتفاع معدلات فشل المصافحة وفشل الشهادات، مما يمكن مهندسي العمليات من التدخل الفوري وتحديث مفاتيح التشفير قبل انقطاع الخدمة عن المستخدمين في بيئة الإنتاج."
    }
}

# ==========================================
# SEC-21: What is Play Integrity API? What trust decisions must happen on the server?
# ==========================================
DATA["SEC-21"] = {
    "concept_en": """The Google Play Integrity API is a security attestation service that helps developers protect their applications and backend services from tampering, fraud, unauthorized access, and malicious execution environments. The architecture bridges the mobile client, Google Play servers, and the enterprise application backend. During a high-stakes transaction (login, checkout, payment authorization), the client requests a cryptographic integrity token, binding it to a server-generated cryptographic nonce to defeat replay attacks. Google Play services inspect the runtime environment—checking bootloader status, system image integrity, hardware-backed Keystore attestation, and Google Play app licensing. Critically, the mobile client must never decrypt, parse, or evaluate this integrity verdict locally, as dynamic instrumentation tools like Frida can easily hook client Boolean checks. Instead, the raw encrypted token is sent to the enterprise backend server, where it is decrypted and validated directly against Google's Play Integrity servers before authorizing business logic.""",
    "walkthrough_en": """Requesting and binding a Play Integrity token with server-side nonce:
```kotlin
class IntegrityAttestationManager(
    private val context: Context,
    private val backendApi: FintechApiService
) {
    private val integrityManager = PlayIntegrity.getIntegrityManager(context)

    suspend fun verifyAndExecutePayment(orderId: String, amount: Long) {
        // 1. Fetch one-time cryptographic nonce from enterprise backend
        val serverNonce = backendApi.generatePaymentNonce(orderId)

        // 2. Request attestation token bound to the server nonce
        val tokenResponse = integrityManager.requestIntegrityToken(
            IntegrityTokenRequest.builder()
                .setNonce(serverNonce) // Cryptographically binds token to this specific action
                .build()
        ).await()

        val integrityToken = tokenResponse.token()

        // 3. Transmit encrypted token to backend server - NEVER evaluate locally!
        val verificationResult = backendApi.authorizePaymentWithIntegrity(
            orderId = orderId,
            amount = amount,
            integrityToken = integrityToken
        )
        
        if (!verificationResult.isSuccess) {
            throw SecurityException("Backend rejected transaction: device integrity failure")
        }
    }
}
```""",
    "short_en": """Play Integrity API checks app authenticity, licensing, and device integrity against Google Play servers. The client requests an encrypted token bound to a server-side nonce during sensitive actions. The enterprise backend server must decrypt and evaluate the verdict, deciding whether to allow the action based on device trust levels rather than trusting client-side Boolean checks.""",
    "structured_en": """Google Play Integrity API provides cryptographic proof that requests originate from your genuine, unmodified application binary running on a trusted, certified Android device.
When a sensitive operation like a financial transaction or authentication begins, the mobile app obtains a one-time cryptographic nonce from the backend server.
The app passes this nonce to the Play Integrity SDK, which queries Google Play services to assess runtime security.
Google analyzes the operating system bootloader status, system image signatures, package certificate, and user licensing.
The SDK returns an encrypted, signed integrity token to the application.
Crucially, all trust decisions must occur on the backend server.
Evaluating integrity verdicts on the client by checking simple Boolean conditions is futile because an attacker using Frida or debuggers can hook the method and force a positive verdict.
The mobile app forwards the encrypted token to the enterprise backend, which decrypts it using Google API endpoints, validates the nonce freshness, and enforces business policies according to device integrity tiers.""",
    "deep_senior_en": """In modern zero-trust mobile architecture, Play Integrity API serves as the cryptographic bridge that verifies client trustworthiness without relying on vulnerable client-side self-assertions.
Traditional root-detection libraries rely on checking file paths like /system/bin/su or inspecting build tags.
In an adversarial environment, tools like Magisk with Zygisk hide these artifacts effortlessly, and runtime hookers like Frida neutralize return values in memory.
Play Integrity overcomes this by leveraging hardware-backed Keystore attestation and Google Play infrastructure to generate an asymmetric cryptographic verdict that cannot be forged by a local client process.
The threat model dictates that the mobile client is strictly a messenger.
If the client attempted to parse the token or decide access based on if (verdict.isTrusted()), an adversary modifies a single assembly branch or hooks the method to bypass security entirely.
Therefore, the backend server must be the sole consumer of the attestation verdict.
The workflow enforces cryptographic action binding: the backend generates a cryptographically secure random nonce tied to the specific user session and transaction parameters.
When the backend receives the integrity token, it calls Google's server-to-server decryption API.
The backend inspects three verdict categories: appLicensing, appRecognitionVerdict (verifying the genuine package and release signing certificate), and deviceRecognitionVerdict (evaluating MEETS_BASIC_INTEGRITY, MEETS_DEVICE_INTEGRITY, and MEETS_STRONG_INTEGRITY).
The server applies nuanced risk policies: allowing read-only browsing on basic devices while strictly demanding MEETS_STRONG_INTEGRITY for high-value fund transfers.""",
    "meta_ar": {
        "id": "SEC-21",
        "questionAr": "ما هي خدمة Play Integrity API؟ وما هي قرارات الثقة التي يجب أن يتخذها السيرفر؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم معمارية Play Integrity API، وحتمية اتخاذ القرارات الأمنية في السيرفر وليس العميل، واستخدام الـ Nonce لمنع هجمات التكرار (Replay Attacks)، وتصنيفات النزاهة (App Licensing, Device Integrity, Strong Integrity).",
        "concept_ar": "خدمة Play Integrity API هي خدمة مصادقة ونزاهة تقدم إثباتاً تشفيرياً على أن الطلبات صادرة من تطبيق رسمي غير معدل يعمل على جهاز أندرويد حقيقي وموثوق. يطلب العميل توكناً مشفراً مربوطاً برمز Nonce عشوائي من السيرفر أثناء المعاملات الحساسة، ويُحظر تماماً فك التوكن أو اتخاذ قرارات الثقة داخل تطبيق الموبايل لسهولة تجاوزها عبر Frida؛ بل يُرسل التوكن المشفر للخادم الخلفي ليقوم بفكه والتحقق منه عبر خوادم جوجل وتحديد مستوى الثقة المطلوب.",
        "walkthrough_ar": "طلب توكن النزاهة من Play Integrity وربطه بـ Nonce قادم من السيرفر:\n```kotlin\nval nonce = api.getSecureNonce() // رمز عشوائي من السيرفر لمنع إعادة الإرسال\nval response = integrityManager.requestIntegrityToken(\n    IntegrityTokenRequest.builder().setNonce(nonce).build()\n).await()\n// إرسال التوكن المشفر للسيرفر ليفحصه هو - لا تفحصه محلياً أبداً:\napi.executeTransaction(orderId, response.token())\n```",
        "why_it_matters_ar": "فحص النزاهة على الموبايل عبر شروط if بسيطة يجعلها عديمة الفائدة لسهولة كسرها بـ Frida، بينما التحقق في السيرفر يمنع تزوير المعاملات وتشغيل روبوتات الاحتيال.",
        "worked_example_ar": "فحص تقييم النزاهة في السيرفر الخلفي عبر Google API (نموذج القرار):\n```json\n{\n  \"appIntegrity\": { \"appRecognitionVerdict\": \"PLAY_RECOGNIZED\" },\n  \"deviceIntegrity\": { \"deviceRecognitionVerdict\": [\"MEETS_STRONG_INTEGRITY\"] },\n  \"accountDetails\": { \"appLicensingVerdict\": \"LICENSED\" }\n}\n```",
        "trade_offs_ar": "يوفر Play Integrity أعلى درجات الأمان الموثقة عتادياً، لكنه يتطلب استدعاء سيرفر جوجل، مما يضيف زمناً إضافياً للطلب ويتطلب إدارة استهلاك الـ Quota في خوادم السحاب.",
        "failure_modes_ar": "التحقق من التوكن داخل تطبيق الموبايل نفسه عبر شرط boolean وتصديق النتيجة محلياً، مما يتيح لأي مخترق تزييف القيمة عبر Frida في سطر واحد.",
        "production_perspective_ar": "في بنوك التكنولوجيا المالية، نلزم التحقق من توكن النزاهة في العمليات الحساسة كالتحويل والدخول، ونشترط مستوى MEETS_STRONG_INTEGRITY للتحويلات الكبرى لرفض الأجهزة المخترقة.",
        "how_to_answer_ar": "ابدأ بتعريف الخدمة ومحاورها الثلاثة (نزاهة التطبيق، الجهاز، الترخيص)، ثم اشرح دورة حياة الطلب واستخدام الـ Nonce، وركز بحزم على حتمية بقاء قرار الثقة في السيرفر وحظر الفحص المحلي، واختم بمستويات النزاهة.",
        "talking_points_ar": "معمارية Play Integrity، ورمز الـ Nonce لمنع Replay Attacks، وحتمية التحقق في السيرفر (Server-side validation)، وفشل الفحوصات المحلية أمام Frida، ومستويات النزاهة Device Integrity.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يعتبر استخدام الـ Nonce أمراً إلزامياً عند طلب توكن Play Integrity؟\"\n  **المرشح:** \"لربط التوكن بالمعاملة الحالية ومنع هجمات التكرار (Replay Attacks)، حتى لا يتمكن المخترق من تسجيل توكن لجهاز سليم وإعادة إرساله مع معاملات احتيالية أخرى.\"\n\n- **المحاور:** \"ما الفرق بين MEETS_DEVICE_INTEGRITY و MEETS_STRONG_INTEGRITY؟\"\n  **المرشح:** \"Device Integrity تعني أن الجهاز يطابق مواصفات التوافق مع أندرويد وغير مروّت، بينما Strong Integrity تتطلب إثباتات أمان عتادية صلبة مثل حماية Bootloader ومفاتيح Keystore العتادية المقاومة للتلاعب.\"",
        "self_check_ar": "هل أكدت على أن الفحص يجب أن يتم في السيرفر حصراً؟ هل شرحت دور الـ Nonce؟ وهل بينت مستويات النزاهة المختلفة؟",
        "references_ar": f"- [Google Play Integrity API Documentation](https://developer.android.com/google/play/integrity/overview) — الدليل الرسمي لمعمارية فحص نزاهة التطبيقات والأجهزة.\n- [Play Integrity Verdict Reference](https://developer.android.com/google/play/integrity/verdicts) — تفاصيل تقييمات النزاهة واستجابات السيرفر.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "خدمة Play Integrity API هي أداة تقدم إثباتاً تشفيرياً على أن الطلب صادر من نسختك الرسمية غير المعدلة على جهاز أندرويد حقيقي وسليم. يطلب التطبيق توكناً مشفراً مربوطاً برمز Nonce عشوائي من السيرفر، ويجب إرسال هذا التوكن للخادم الخلفي ليقوم بفكه وتقييم النزاهة عبر خوادم جوجل، مع حظر اتخاذ القرارات الأمنية داخل الموبايل لتفادي تجاوزها عبر أدوات التلصص على الذاكرة.",
        "best_answer_ar": "تعتبر خدمة Google Play Integrity API المعيار الحديث لإثبات نزاهة العميل في معمارية Zero-Trust دون الاعتماد على فحوصات التطبيق المحلية الهشة.\n\nعند بدء معاملة حساسة كالدفع أو تسجيل الدخول، يطلب التطبيق رمز Nonce فريداً من خادمه الخاص لربطه بالطلب ومنع هجمات إعادة الإرسال Replay Attacks. ثم يطلب التطبيق التوكن من Play Integrity، حيث تفحص خدمات جوجل بيئة الهاتف؛ كحالة الـ Bootloader، وتوقيع النظام، ومطابقة شهادة التطبيق وترخيص الحساب، وتصدر توكناً مشفراً وموقعاً عتادياً.\n\nوالقاعدة المعمارية الجوهرية هي أن كافة قرارات الثقة يجب أن تُتخذ داخل السيرفر حصراً؛ فإذا حاول التطبيق فك التوكن أو فحص متغير boolean محلياً، فسيقوم المهاجم بتعديل الشرط في الذاكرة عبر Frida في ثوانٍ. ولذلك يرسل التطبيق التوكن المشفر للخادم الخلفي، حيث يتصل السيرفر بخوادم جوجل لفك التوكن وتقييم معايير النزاهة وتحديد ما إذا كان الجهاز يحقق المعيار العتادي القوي MEETS_STRONG_INTEGRITY للموافقة على المعاملة المالية.",
        "deep_answer_ar": "في النمذجة الأمنية المتقدمة، ندرك أن المكتبات التقليدية لكشف الروت مثل فحص مسارات su أو ملفات النظام هي مجرد عوائق ساذجة يمكن لأدوات مثل Magisk و Zygisk إخفاؤها بسلاسة تامة. وهنا تبرز القيمة الحقيقية لـ Play Integrity API كحلقة وصل تشفيرية موثقة عتادياً بين العميل وخوادم جوجل وسيرفر البنك.\n\nتعتمد المعمارية على التعامل مع تطبيق الموبايل كمجرد وسيط لنقل البيانات؛ فالتطبيق لا يمتلك المفتاح السري لفك تشفير توكن النزاهة ولا يستطيع قراءة تقييمه. تبدأ العملية بطلب السيرفر لإنشاء رمز Nonce مشفر ومربوط ببيانات العملية ومقيد بوقت انتهاء زمني صارم. وعندما يطلب التطبيق التوكن، يقوم معالج الأمان في الهاتف بتوقيع الإثبات وإرساله مشفراً.\n\nوعلى السيرفر الخلفي يقع العبء الأمني كاملاً؛ حيث يتصل السيرفر بخدمات جوجل لفك التوكن وفحص معاييره الثلاثة: appRecognitionVerdict للتأكد من عدم تعديل ملفات التطبيق، و appLicensingVerdict لتوثيق التنزيل من المتجر، و deviceRecognitionVerdict. ويطبق السيرفر سياسات خطر متدرجة؛ كأن يسمح بتصفح المنتجات للأجهزة التي تحقق MEETS_BASIC_INTEGRITY، بينما يرفض قطيعاً تنفيذ أي تحويل مالي إلا إذا حقق الجهاز معيار MEETS_STRONG_INTEGRITY المدعوم بعتاد Keystore الصلب لقطع الطريق تماماً على المحاكيات والأجهزة المخترقة. كما يدعم السيرفر فحص حقل requestDetails للتحقق من تطابق الـ Nonce والـ Timestamp، مما يحمي المعاملات المصرفية من هجمات إعادة الإرسال Replay Attacks، ويوفر دفاعاً متعدد الطبقات ضد أدوات الهندسة العكسية المتقدمة."
    }
}

# ==========================================
# SEC-22: How do you design biometric-gated access to a Keystore operation?
# ==========================================
DATA["SEC-22"] = {
    "concept_en": """Designing biometric-gated access to an Android Keystore cryptographic operation establishes a hardware-enforced bond between physical human biometric verification and mathematical cipher execution. Rather than treating biometric prompts as mere UI authorization gates, the cryptographic key itself must be configured to be mathematically unusable without prior biometric unlock. The key is generated in AndroidKeyStore using KeyGenParameterSpec configured with setUserAuthenticationRequired(true) and setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG), requiring Class 3 (Strong) biometrics per-operation. When initiating an operation, the application initializes a Cipher or Signature object with the Keystore key. Because the key is locked, executing cipher operations immediately throws a UserNotAuthenticatedException. Instead, the initialized Cipher is wrapped inside a BiometricPrompt.CryptoObject and passed to BiometricPrompt.authenticate(). Only upon successful hardware biometric verification does the framework unlock the Keymaster key, returning the authenticated CryptoObject to onAuthenticationSucceeded, where cipher.doFinal() can finally execute.""",
    "walkthrough_en": """Implementing BiometricPrompt with cryptographic Keystore binding:
```kotlin
class BiometricCryptoManager(private val activity: FragmentActivity) {
    private val keyAlias = "biometric_payment_key"

    // 1. Generate key requiring strong biometrics per operation (timeout = 0)
    fun generateBiometricKey() {
        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        val spec = KeyGenParameterSpec.Builder(
            keyAlias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        ).run {
            setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            setUserAuthenticationRequired(true) // Hardware lock
            setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG) // Per-use
            setInvalidatedByBiometricEnrollment(true) // Invalidate if new fingerprint added
            build()
        }
        keyGenerator.init(spec)
        keyGenerator.generateKey()
    }

    // 2. Authenticate and execute cipher bound to BiometricPrompt.CryptoObject
    fun authenticateAndDecrypt(encryptedData: ByteArray, iv: ByteArray, onSuccess: (ByteArray) -> Unit) {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
        
        val cipher = Cipher.getInstance("AES/GCM/NoPadding").apply {
            init(Cipher.DECRYPT_MODE, secretKey, GCMParameterSpec(128, iv))
        }

        val cryptoObject = BiometricPrompt.CryptoObject(cipher)
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Confirm Payment")
            .setSubtitle("Authenticate using biometrics to unlock your key")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .setNegativeButtonText("Cancel")
            .build()

        val biometricPrompt = BiometricPrompt(activity, ContextCompat.getMainExecutor(activity),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    // Authenticated Cipher is now hardware-unlocked and ready for doFinal!
                    val authenticatedCipher = result.cryptoObject?.cipher
                    val plaintext = authenticatedCipher?.doFinal(encryptedData)
                    plaintext?.let(onSuccess)
                }
            })

        biometricPrompt.authenticate(promptInfo, cryptoObject)
    }
}
```""",
    "short_en": """We design biometric access by generating a Keystore key configured with setUserAuthenticationRequired, making the key mathematically unusable without hardware biometric authentication. We initialize a Cipher, wrap it in a BiometricPrompt.CryptoObject, and authenticate; only upon successful biometric verification does the hardware unlock the key to finalize encryption or signing.""",
    "structured_en": """Biometric-gated security in Android requires binding cryptographic execution directly to biometric verification rather than relying on decoupled UI dialogs.
A common security flaw is displaying BiometricPrompt as a UI gate, and upon success, reading an unencrypted token from SharedPreferences; an attacker using Frida easily hooks the callback to bypass the prompt.
To build true hardware-backed protection, the cryptographic key must be locked at the Keystore level.
We generate a key using KeyGenParameterSpec, enabling setUserAuthenticationRequired and specifying a zero-second duration with Class 3 Strong biometrics.
This configuration ensures that the key cannot perform cryptographic operations without an active biometric authentication ticket issued by the secure hardware.
During execution, we initialize our Cipher or Signature object and wrap it inside a BiometricPrompt.CryptoObject.
We pass the CryptoObject to BiometricPrompt.authenticate.
When the user successfully authenticates with their fingerprint or face, the Keymaster daemon receives the hardware auth token and unlocks the key, allowing onAuthenticationSucceeded to execute doFinal on the authenticated Cipher securely.""",
    "deep_senior_en": """The critical security distinction in biometric engineering is the separation between UI-level authentication and cryptographic key unlocking.
If an application invokes BiometricPrompt without passing a CryptoObject, the biometric ceremony is purely advisory: the framework executes a local biometric check and returns a Boolean result to the application process.
In a threat model where an attacker possesses a rooted device or uses runtime hooking platforms like Frida, hooking AuthenticationCallback.onAuthenticationSucceeded() to fabricate a successful result requires trivial effort.
By contrast, integrating BiometricPrompt.CryptoObject creates a hardware-rooted cryptographic barrier.
When a key is generated with setUserAuthenticationRequired(true) and setUserAuthenticationParameters(0, AUTH_BIOMETRIC_STRONG), the key material resides inside the TEE or StrongBox in a locked state.
Initializing the Cipher allocates an operation handle in Keymaster, but calling doFinal() prior to biometric verification fails with UserNotAuthenticatedException.
When the user authenticates, the biometric sensor (Fingerprint or Face HAL) communicates directly with the Gatekeeper and Keymaster secure daemons via hardware channels, issuing a cryptographically signed authentication ticket containing a timestamp and HMAC.
Keymaster validates this hardware ticket and authorizes the specific cipher operation handle.
Only then does doFinal() succeed inside onAuthenticationSucceeded().
Furthermore, setting setInvalidatedByBiometricEnrollment(true) guarantees that if an unauthorized individual adds a new fingerprint to the device in system settings, the key is permanently destroyed, providing absolute non-repudiation for high-value banking transactions.""",
    "meta_ar": {
        "id": "SEC-22",
        "questionAr": "كيف تصمم وصولاً محميّاً بالبصمة الحيوية لعمليات Android Keystore المشفرة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التمييز بين التحقق الشكلي في الواجهة والربط التشفيري العتادي الحقيقي، واستخدام BiometricPrompt.CryptoObject، وضبط KeyGenParameterSpec بالمصادقة الصارمة (AUTH_BIOMETRIC_STRONG)، والتعامل مع إبطال المفاتيح عند إضافة بصمات جديدة (setInvalidatedByBiometricEnrollment).",
        "concept_ar": "تصميم الوصول المحمي بالبصمة يتطلب ربط المفتاح التشفيري ذاته بالتحقق البيومتري داخل العتاد وليس مجرد إظهار نافذة تأكيد شكلية في الواجهة. يتم توليد المفتاح في Keystore مع اشتراط `setUserAuthenticationRequired(true)` وبزمن صلاحية صفر ثانية لفرضه لكل عملية (Per-use). وعند التنفيذ، ننشئ كائن الـ Cipher ونمرره داخل `BiometricPrompt.CryptoObject`؛ حيث يظل المفتاح مقفلاً عتادياً ويرفض التشفير حتى يتحقق معالج الأمان من بصمة المستخدم ويحرر المفتاح لتنفيذ doFinal في دالة النجاح.",
        "walkthrough_ar": "ربط كائن Cipher داخل CryptoObject وتمريره إلى BiometricPrompt:\n```kotlin\nval cipher = Cipher.getInstance(\"AES/GCM/NoPadding\").apply {\n    init(Cipher.DECRYPT_MODE, secretKey, GCMParameterSpec(128, iv))\n}\nval cryptoObject = BiometricPrompt.CryptoObject(cipher)\n// تمرير cryptoObject للنافذة الحيوية:\nbiometricPrompt.authenticate(promptInfo, cryptoObject)\n// في onAuthenticationSucceeded نأخذ الـ Cipher المحرر عتادياً:\noverride fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {\n    val decryptedBytes = result.cryptoObject?.cipher?.doFinal(encryptedData)\n}\n```",
        "why_it_matters_ar": "التحقق من البصمة في الواجهة دون CryptoObject يسمح لأي مخترق بتجاوز البصمة عبر سطرين في أداة Frida، بينما ربط المفتاح عتادياً يجعل تجاوز الفحص مستحيلاً رياضياً لعدم تحرير المفتاح من العتاد.",
        "worked_example_ar": "توليد مفتاح مقيد بالبصمة الحيوية القوية ويبطل تلقائياً عند إضافة بصمة جديدة:\n```kotlin\nval spec = KeyGenParameterSpec.Builder(\"pay_key\", KeyProperties.PURPOSE_DECRYPT).run {\n    setUserAuthenticationRequired(true)\n    setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG)\n    setInvalidatedByBiometricEnrollment(true) // إبطال المفتاح لو أضاف شخص بصمته\n    build()\n}\n```",
        "trade_offs_ar": "استخدام CryptoObject يوفر أعلى درجات الأمان المصرفي، لكنه يفرض اشتراط بصمات من الفئة القوية (Class 3)، ولا يدعم الرموز البديلة إلا إذا تمت معالجتها بمسار تشفيري منفصل.",
        "failure_modes_ar": "إظهار BiometricPrompt بدون CryptoObject، وعند النجاح قراءة التوكن المحفوظ كنص صريح في SharedPreferences؛ مما يفرغ الحماية من مضمونها تماماً.",
        "production_perspective_ar": "في التطبيقات المصرفية، نستخدم CryptoObject لتوقيع معاملات الدفع بـ ECDSA داخل Keystore، ونلزم المستخدم بإدخال كلمة المرور مجدداً إذا أطلق النظام استثناء إبطال المفتاح بسبب تسجيل بصمة جديدة.",
        "how_to_answer_ar": "ابدأ ببيان الفرق بين التحقق الشكلي في الواجهة والربط التشفيري الحقيقي، واشرح خطورة تخطي الواجهة بـ Frida، ثم فسر كيفية إعداد KeyGenParameterSpec وتمرير CryptoObject إلى BiometricPrompt، واختم بـ setInvalidatedByBiometricEnrollment.",
        "talking_points_ar": "التحقق الشكلي مقابل الربط التشفيري، وكائن BiometricPrompt.CryptoObject، و KeyGenParameterSpec مع setUserAuthenticationRequired، والبصمات القوية Class 3، وخاصية setInvalidatedByBiometricEnrollment.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو حاول تطبيق تنفيذ `cipher.doFinal()` قبل نجاح البصمة لمفتاح مقيد؟\"\n  **المرشح:** \"يرفض معالج Keymaster تنفيذ العملية ويرمي استثناء `UserNotAuthenticatedException` فوراً لأن المفتاح مقفل عتادياً ولا يمتلك تذكرة مصادقة.\"\n\n- **المحاور:** \"ما هي أهمية تفعيل `setInvalidatedByBiometricEnrollment(true)`؟\"\n  **المرشح:** \"تضمن تدمير المفتاح تلقائياً إذا قام شخص غريب بإضافة بصمته إلى إعدادات الهاتف، مما يحمي الحساب من التحويلات الاحتيالية عبر بصمات مضافة لاحقاً.\"",
        "self_check_ar": "هل ميزت بين فحص الواجهة واستخدام CryptoObject؟ هل شرحت UserNotAuthenticatedException؟ وهل بينت دور العتاد الآمن؟",
        "references_ar": f"- [Android Developers - BiometricPrompt with Cryptography](https://developer.android.com/identity/sign-in/biometric-auth) — الدليل الرسمي لاستخدام المصادقة الحيوية التشفيرية.\n- [Android Security KeyGenParameterSpec Authentication](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder#setUserAuthenticationRequired(boolean)) — التوثيق الرسمي لربط المفاتيح التشفيرية بالمصادقة.",
        "quick_answer_ar": "نصمم الوصول المحمي بالبصمة بربط العملية التشفيرية ذاتها بالتحقق البيومتري عبر BiometricPrompt.CryptoObject بدلاً من الاكتفاء بفحص شكلي في الواجهة. نقوم بتوليد المفتاح في Keystore مع اشتراط التحقق الحيوي القوي لكل عملية، ونمرر كائن الـ Cipher المقفل داخل CryptoObject، فلا يفتح عتاد الجهاز قفل المفتاح لإتمام التشفير أو التوقيع إلا بعد نجاح البصمة فيزيائياً.",
        "best_answer_ar": "أخطر خطأ يقع فيه مطورو الموبايل هو التعامل مع البصمة الحيوية كحاجز واجهة مستخدم فقط؛ حيث يظهر المطور نافذة BiometricPrompt وعند النجاح يقرأ رمزاً سرياً من التخزين، وهو فحص تافه يسهل تجاوزه عبر أدوات مثل Frida.\n\nالتصميم الهندسي الآمن يربط المفتاح التشفيري ذاته بالبصمة داخل عتاد الجهاز. نبدأ بتوليد المفتاح السري في AndroidKeyStore مع تفعيل خيار setUserAuthenticationRequired وتحديد مدة الصلاحية بصفر ثانية مع فرض البصمات القوية AUTH_BIOMETRIC_STRONG. هذا يجعل المفتاح محبوساً عتادياً داخل الـ TEE ويرفض أي محاولة تشفير برمي استثناء UserNotAuthenticatedException.\n\nوعند طلب العملية، ننشئ كائن الـ Cipher ونغلفه داخل BiometricPrompt.CryptoObject ونمرره لنافذة البصمة. وعندما يضع المستخدم إصبعه، يخاطب حساس البصمة معالج الأمان مباشرة لتأكيد الهوية، ويقوم العتاد بفك قفل المفتاح للعملية الحالية فقط، لتقوم دالة onAuthenticationSucceeded باستلام الـ Cipher المحرر وتنفيذ doFinal بأمان تام.",
        "deep_answer_ar": "في هندسة أمان التطبيقات المصرفية، نميز بشكل حاسم بين التحقق الشكلي الاستشاري في الواجهة وبين القفل التشفيري المتجذر في العتاد الصلب.\n\nعند استدعاء BiometricPrompt بدون كائن CryptoObject، يقتصر دور النظام على إرجاع قيمة منطقية لتطبيق الموبايل، وبما أن العميل بيئة غير موثوقة، يستطيع أي مهاجم يمتلك جهازاً مروتاً حقن سكريبت Frida بسيط لربط دالة onAuthenticationSucceeded وإجبارها على العمل دون لمس الحساس الحيوي إطلاقاً. أما عند استخدام CryptoObject، فإننا ننقل الثقة بالكامل إلى معالج الأمان TEE أو StrongBox.\n\nوعند تهيئة الـ Cipher بمفتاح مقيد بيومترياً، يتم حجز مقبض تشغيلي في Keymaster، ويظل المفتاح عاجزاً رياضياً عن فك التشفير. وعند لمس الحساس، يرسل تعريف البصمة في النواة تذكرة مصادقة موثقة عتادياً بتوقيع HMAC إلى معالج Keymaster، فيقوم المعالج بالتحقق من صحة التذكرة وتوقيتها الزمني، ويحرر المقبض التشغيلي للـ Cipher لإتمام عملية التشفير أو التوقيع الرقمي بنجاح.\n\nونعزز هذا التصميم بتفعيل setInvalidatedByBiometricEnrollment؛ مما يضمن إعدام المفتاح التشفيري في العتاد بصورة نهائية إذا قام أي شخص بإضافة بصمة جديدة في إعدادات الهاتف، وهو ما يوفر حماية مطلقة وعدم إنكار قانوني للمعاملات المالية الكبرى. كما نلزم ضبط setUserAuthenticationParameters بفترة صلاحية زمنية لا تتجاوز الصفر ثانية، مما يجبر المستخدم على تقديم مصادقة بيومترية حية لكل عملية مالية مستقلة، ويقطع الطريق تماماً على أي محاولة لاستغلال الجلسات المفتوحة."
    }
}

# ==========================================
# SEC-23: What are the threats of insecure backup and local database files?
# ==========================================
DATA["SEC-23"] = {
    "concept_en": """Insecure local database storage and unmanaged Android Auto Backup configurations expose sensitive enterprise data to extraction through device-to-device transfers, cloud backups, and local administrative attacks. By default, Android Auto Backup and adb backup target an application's entire private storage directory (/data/data/<package_name>), uploading databases, shared preferences, and cache files to the user's Google Drive. If an application stores sensitive records (PII, authentication tokens, payment history) in unencrypted SQLite or Room databases, an attacker who obtains a backup archive or accesses a backed-up Google Drive account gains full plaintext access. Furthermore, if an application encrypts its local databases using Android Keystore keys but permits Auto Backup, restoring the backup onto a new device results in permanent data corruption: the database files transfer over, but the hardware-backed Keystore keys remain trapped on the original device, causing unrecoverable decryption crashes. Applications must harden backup rules via data_extraction_rules.xml and encrypt Room databases with SQLCipher.""",
    "walkthrough_en": """Hardening backup rules and configuring SQLCipher for Room database encryption:
```xml
<!-- 1. Enforce strict data extraction rules in res/xml/data_extraction_rules.xml -->
<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <!-- Completely exclude sensitive databases and Keystore-dependent preferences -->
        <exclude path="databases/user_credentials.db" />
        <exclude path="databases/user_credentials.db-wal" />
        <exclude path="databases/user_credentials.db-shm" />
        <exclude path="shared_prefs/auth_session.xml" />
    </cloud-backup>
    <device-transfer>
        <exclude path="databases/user_credentials.db" />
        <exclude path="databases/user_credentials.db-wal" />
    </device-transfer>
</data-extraction-rules>
```
Configuring SQLCipher with Room:
```kotlin
// 2. Encrypting local Room database with SQLCipher SupportFactory
val passphraseBytes = getOrGenerateDatabasePassphraseFromKeystore()
val factory = SupportFactory(passphraseBytes)

val secureDatabase = Room.databaseBuilder(
    context,
    SecureAppDatabase::class.java,
    "user_credentials.db"
).openHelperFactory(factory)
 .build()
```""",
    "short_en": """Unencrypted databases allow attackers to extract sensitive data via adb backup, physical theft, or cloud backup archives. Furthermore, restoring Keystore-encrypted files onto new devices causes fatal decryption crashes because hardware keys do not transfer. We mitigate this by excluding sensitive databases from backups via data_extraction_rules and encrypting Room with SQLCipher.""",
    "structured_en": """Insecure local database files and default backup configurations expose sensitive application data to extraction beyond the protection of the application sandbox.
By default, Android Auto Backup uploads application data to Google Drive and enables device-to-device migrations.
If an application stores personally identifiable information, session tokens, or transaction logs in standard unencrypted Room or SQLite databases, anyone with access to the backup archive or adb debugging can inspect the files in plaintext.
A more insidious operational hazard arises when apps encrypt local files using Android Keystore but fail to disable backups.
Because hardware-backed Keystore keys are bound to physical chips and never migrate across devices, restoring the encrypted database on a new phone leaves the application with orphan ciphertext, causing crashes and permanent data loss.
To mitigate these threats, applications must configure data_extraction_rules to exclude sensitive database files and journals from cloud backups, while encrypting Room databases at rest using SQLCipher with keys protected in Android Keystore.""",
    "deep_senior_en": """In mobile threat modeling, the boundary of the local application sandbox is porous when considering backups and offline disk analysis.
Many developers assume that because /data/data requires root access to read, unencrypted SQLite databases are safe from unauthorized extraction.
However, if android:allowBackup is enabled without granular extraction rules, an adversary with physical access can enable USB debugging and execute adb backup to extract the entire private storage tree into an unencrypted tarball.
Even without USB debugging, Android Auto Backup routinely archives application files to Google Drive.
If a user's cloud account is compromised through phishing or credential stuffing, the attacker downloads the full application database, exposing sensitive personal records and financial logs.
Furthermore, the clash between Auto Backup and Android Keystore represents one of the most common causes of unrecoverable production database corruption.
When a user switches to a new phone, the OS restores the encrypted database file, but the hardware-backed key required to decrypt it was destroyed with the old device.
When Room initializes with SQLCipher, the open helper fails with a file is not a database error, crashing the application on startup.
Senior architecture mandates two explicit controls.
At the OS policy layer, in res/xml/data_extraction_rules.xml, we explicitly exclude all database files, including SQLite Write-Ahead Logging (.wal) and shared-memory (.shm) journal files, from both cloud backups and device transfers.
Second, we encrypt Room databases at rest using SQLCipher, wrapping the database encryption passphrase with an Android Keystore master key and treating local storage strictly as an ephemeral, re-syncable cache of backend truth.""",
    "meta_ar": {
        "id": "SEC-23",
        "questionAr": "ما هي مخاطر النسخ الاحتياطي غير الآمن (Insecure Backup) وقواعد البيانات المحلية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم ثغرات النسخ الاحتياطي التلقائي (Auto Backup) وأمر adb backup، ومخاطر تسريب قواعد بيانات SQLite غير المشفرة، والتعارض الكارثي بين النسخ الاحتياطي ومفاتيح Keystore العتادية، وضبط ملف data_extraction_rules واستخدام SQLCipher لتشفير Room.",
        "concept_ar": "النسخ الاحتياطي غير المضبوط وقواعد البيانات المحلية غير المشفرة يعرضان أسرار التطبيق للتسريب خارج حدود العزل الأمني. يرفع نظام Auto Backup ملفات التطبيق وقواعد بياناته إلى Google Drive تلقائياً؛ فإذا كانت غير مشفرة تُسرب بيانات المستخدم، وإذا كانت مشفرة بمفاتيح Keystore فإن استعادتها على جهاز جديد تسبب انهياراً دائماً لعدم انتقال المفاتيح العتادية. وتتطلب الحماية استبعاد قواعد البيانات وملفات الـ WAL والـ SHM عبر data_extraction_rules، وتشفير Room عبر SQLCipher.",
        "walkthrough_ar": "استبعاد ملفات قواعد البيانات ومشتقاتها من النسخ الاحتياطي وتشفير Room بـ SQLCipher:\n```xml\n<data-extraction-rules>\n    <cloud-backup>\n        <!-- استبعاد قاعدة البيانات وملفات الـ Journal التابعة لها -->\n        <exclude path=\"databases/vault.db\" />\n        <exclude path=\"databases/vault.db-wal\" />\n        <exclude path=\"databases/vault.db-shm\" />\n    </cloud-backup>\n</data-extraction-rules>\n```\nتشفير قاعدة بيانات Room باستخدام SQLCipher:\n```kotlin\nval factory = SupportFactory(passphraseBytes)\nval db = Room.databaseBuilder(context, AppDb::class.java, \"vault.db\")\n    .openHelperFactory(factory).build()\n```",
        "why_it_matters_ar": "إهمال قواعد النسخ الاحتياطي يتيح سحب البيانات الشخصية عبر النسخ السحابي أو أدوات تصحيح الأخطاء، أو يتسبب في انهيار التطبيق ومسح بيانات المستخدمين عند الانتقال لهواتف جديدة.",
        "worked_example_ar": "إغلاق النسخ الاحتياطي تماماً في Manifest كإجراء احترازي للتطبيقات المالية:\n```xml\n<application\n    android:allowBackup=\"false\"\n    android:dataExtractionRules=\"@xml/data_extraction_rules\"\n    android:fullBackupContent=\"false\">\n</application>\n```",
        "trade_offs_ar": "استبعاد قواعد البيانات من النسخ الاحتياطي يجبر المستخدم على إعادة تنزيل بياناته من السيرفر عند تغيير الهاتف، لكنه يحمي من تسريب البيانات والانهيارات التشفيرية القاتلة.",
        "failure_modes_ar": "استبعاد ملف قاعدة البيانات الرئيسي ونسيان ملفات الـ Write-Ahead Logging (ملفات wal و shm) مما يسرب البيانات المكتوبة حديثاً، أو تشفير قاعدة البيانات بمفتاح Keystore ونقلها عبر السحاب مما يسبب خطأ file is not a database عند الفتح على هاتف جديد.",
        "production_perspective_ar": "في تطبيقات البنوك، نعطل allowBackup بالكامل، ونشفر قواعد بيانات Room عبر SQLCipher، ونعتبر البيانات المحلية مجرد كاش مؤقت يُعاد بناؤه من السيرفر بعد تسجيل الدخول.",
        "how_to_answer_ar": "ابدأ ببيان كيفية عمل النسخ الاحتياطي وأخطاره بسحب البيانات الصريحة، ثم اشرح المشكلة المعمارية الكبرى في تعارض النسخ الاحتياطي مع مفاتيح Keystore العتادية، وقدم الحل بضبط data_extraction_rules واستخدام SQLCipher وتضمين ملفات wal/shm.",
        "talking_points_ar": "خدمة Android Auto Backup وأمر adb backup، ومخاطر تسريب SQLite الصريحة، وتعارض Keystore مع الاستعادة السحابية، وملفات الـ WAL والـ SHM، وتشفير SQLCipher مع Room.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يجب استبعاد ملفات `.db-wal` و `.db-shm` بجانب ملف `.db` الأساسي؟\"\n  **المرشح:** \"لأن نمط Write-Ahead Logging يحفظ العمليات والبيانات المكتوبة حديثاً في ملف wal قبل دمجها في الملف الأساسي، ونسيان استبعاده يسرب أحدث سجلات المعاملات المالية.\"\n\n- **المحاور:** \"ماذا يحدث لو استعاد المستخدم قاعدة بيانات Room مشفرة عبر السحاب على هاتف جديد؟\"\n  **المرشح:** \"سيفشل فك التشفير لأن مفتاح Keystore العتادي لم ينتقل مع النسخة، ويطلق SQLCipher استثناء file is not a database وينهار التطبيق عند الإقلاع.\"",
        "self_check_ar": "هل شرحت مخاطر تسريب قواعد البيانات بالنسخ السحابي؟ هل وضحت مشكلة تعارض مفاتيح Keystore مع النسخ الاحتياطي؟ وهل ذكرت ملفات wal و shm؟",
        "references_ar": f"- [Android Auto Backup Architecture and Rules](https://developer.android.com/identity/data/autobackup) — التوثيق الرسمي لضبط قواعد استخراج البيانات وحماية النسخ الاحتياطي.\n- [SQLCipher for Android Documentation](https://www.zetetic.net/sqlcipher/sqlcipher-for-android/) — الدليل الرسمي لتشفير قواعد بيانات SQLite و Room بالكامل.",
        "quick_answer_ar": "تسمح قواعد البيانات غير المشفرة بسحب البيانات الحساسة عبر النسخ الاحتياطي السحابي أو أوامر تصحيح الأخطاء. كما أن النسخ الاحتياطي لملفات مشفرة بمفاتيح Keystore يؤدي لانهيار التطبيق عند استعادته على هاتف جديد لعدم انتقال المفاتيح العتادية، ولذلك نلزم التطبيق باستبعاد قواعد البيانات وملفات الـ WAL التابعة لها عبر data_extraction_rules وتشفير Room باستخدام SQLCipher.",
        "best_answer_ar": "يتجاوز خطر النسخ الاحتياطي التلقائي حدود العزل الأمني في أندرويد إذا لم تُدار إعداداته بحذر شديد.\n\nيقوم نظام Android Auto Backup برفع كافة ملفات التطبيق وقواعد بياناته إلى حساب Google Drive الخاص بالمستخدم. فإذا كانت قاعدة بيانات SQLite أو Room غير مشفرة، فإن أي وصول غير مصرح به لحساب السحاب أو عبر أوامر adb backup يكشف السجلات المصرفية والبيانات الشخصية كنصوص صريحة.\n\nوالأخطر من ذلك هو التعارض التقني الكارثي بين النسخ الاحتياطي ومفاتيح التشفير العتادية؛ فعندما يقوم المطور بتشفير قاعدة البيانات بمفتاح من Android Keystore ويسمح بنسخها سحابياً، تنتقل ملفات البيانات للهاتف الجديد بينما تظل المفاتيح محبوسة في الشريحة العتادية للهاتف القديم. وعند فتح التطبيق على الهاتف الجديد، يفشل فك التشفير وينهار التطبيق بخطأ file is not a database. ولعلاج هذا الخطر، نضبط ملف data_extraction_rules لاستبعاد ملفات قاعدة البيانات وملفات الـ wal والـ shm التابعة لها من النسخ الاحتياطي، ونشفر قاعدة بيانات Room عبر مكتبة SQLCipher بمفاتيح محمية محلياً.",
        "deep_answer_ar": "في النمذجة التهديدية لتخزين البيانات المحلية، يخطئ المطورون بافتراض أن حماية مجلد data/data بصلاحيات الروت تكفي لحماية قواعد بيانات التطبيق غير المشفرة.\n\nففي الواقع، يكفي تفعيل تصحيح الأخطاء USB debugging لاستخدام أمر adb backup وسحب كافة محتويات التخزين المحلي دون الحاجة لترويض الجهاز. وعلاوة على ذلك، فإن نظام النسخ الاحتياطي التلقائي يرفع البيانات إلى سحابة جوجل تلقائياً؛ مما يجعل بيانات العميل عرضة للاختراق في حال سرقة بريده الإلكتروني أو استهدافه بهجمات التصيد.\n\nأما المعضلة المعمارية الكبرى فتكمن في التناقض بين التخزين المشفر واستعادة البيانات؛ فمفاتيح Android Keystore ترتبط فيزيائياً بالعتاد ولا تنتقل مع النسخ الاحتياطية بأي حال من الأحوال. وعندما يستعيد المستخدم بياناته على جهاز جديد، يجد التطبيق ملفات مشفرة بدون مفتاح فك التشفير، مما يجعله عاجزاً عن العمل ويدخله في حلقة انهيارات مستمرة عند بدء التشغيل.\n\nولبناء معمارية آمنة ومستقرة، نلزم ملف data_extraction_rules باستبعاد مجلد databases بالكامل، مع التركيز على استبعاد ملفات الـ Write-Ahead Logging مثل wal و shm التي تحوي أحدث البيانات المالية المكتوبة، ونشفر بيانات Room محلياً بواسطة مكتبة SQLCipher، ونتعامل مع التخزين المحلي دائماً ككاش مؤقت قابل لإعادة المزامنة النظيفة من خوادم الشركة الموثوقة. كما نحدد بوضوح في قواعد النسخ الاحتياطي السحابي استبعاد ملفات الشفرات وملفات الـ KeyStore التالفة، مع تفعيل آليات تفريغ البيانات الحساسة من الذاكرة والتخزين عند تسجيل خروج المستخدم لتقليل مساحة الهجوم إلى أقصى حد."
    }
}

# ==========================================
# SEC-24: How can native code/JNI be analyzed or instrumented?
# ==========================================
DATA["SEC-24"] = {
    "concept_en": """Analyzing and instrumenting Android native C/C++ libraries (.so files) via the Java Native Interface (JNI) is a routine discipline in modern mobile reverse engineering. While native shared libraries eliminate Java bytecode readability, they remain entirely susceptible to static disassembly and dynamic instrumentation. Statically, adversaries analyze native libraries using disassemblers like Ghidra, IDA Pro, and Binary Ninja. Even if debug symbols are stripped, disassemblers reconstruct control flow graphs, cross-reference external imported system calls (libc, libcrypto), and easily extract embedded ASCII and UTF-8 strings. Furthermore, exported JNI functions (following the Java_package_class_method naming convention) or functions registered via RegisterNatives provide immediate static entry points for analysts. Dynamically, frameworks like Frida attach to native processes via Interceptor.attach, hooking raw native function addresses, inspecting register states, modifying pointer arguments, and intercepting returns from OpenSSL or libc functions like memcpy and strcmp in real time.""",
    "walkthrough_en": """How Frida dynamically hooks native C++ exported and unexported functions:
```javascript
// 1. Hooking exported JNI native functions by symbol name
var nativeLib = Process.findModuleByName("libnative_vault.so");
if (nativeLib) {
    var symbolAddress = Module.findExportByName("libnative_vault.so", "Java_com_example_bank_SecurityBridge_decryptPayload");
    if (symbolAddress) {
        Interceptor.attach(symbolAddress, {
            onEnter: function(args) {
                console.log("[*] Native decryptPayload invoked!");
                // Inspect or tamper with incoming pointer arguments
            },
            onLeave: function(retval) {
                console.log("[*] Native decryptPayload returned: " + retval);
            }
        });
    }

    // 2. Hooking internal unexported subroutines via module base offset
    var internalSubroutineOffset = 0x1A4F0; // Discovered via Ghidra
    var targetAddress = nativeLib.base.add(internalSubroutineOffset);
    Interceptor.attach(targetAddress, {
        onEnter: function(args) {
            console.log("[*] Internal crypto subroutine intercepted!");
        }
    });
}
```""",
    "short_en": """Native C++ libraries are analyzed statically using Ghidra and IDA Pro to inspect disassembly and extract strings, while exported JNI functions provide obvious entry points. Dynamically, tools like Frida hook native function addresses and registers in real time, proving that moving sensitive secrets into C++ shared libraries provides no true cryptographic security.""",
    "structured_en": """Migrating sensitive business logic or cryptographic keys into native C and C++ shared libraries does not prevent reverse engineering.
Static analysis of native .so libraries is performed using advanced disassemblers like Ghidra and Binary Ninja, which decompile machine code back into pseudo-C with high fidelity.
Exported JNI functions are immediately identifiable because they follow standard platform naming conventions or are registered through RegisterNatives.
Even when symbol tables are stripped, attackers search for constant byte arrays, string literals, and calls to standard system libraries like OpenSSL or libc.
Dynamic analysis poses an even greater threat through binary instrumentation platforms like Frida.
Adversaries use Frida's Interceptor API to hook exported symbols or arbitrary internal memory offsets calculated from the library's base address.
These hooks intercept function arguments, dump CPU registers, and manipulate return values in memory.
Therefore, native code must never be relied upon as a secret hiding vault, but hardened with compiler obfuscation and verified via backend server trust.""",
    "deep_senior_en": """The widespread myth in Android development that native C++ libraries compiled via the NDK act as an impenetrable black box violates fundamental reverse-engineering reality.
Compiling code into ARM64 machine instructions alters the representation, but does not alter the mathematical accessibility of the binary.
Statically, tools like Ghidra decompile ARM assembly back into structured C logic, mapping control flow, loops, and memory references.
A team that hides an API key in a C++ char array finds that running strings libnative.so or inspecting the .rodata section extracts the plaintext key in seconds.
Even when strings are encrypted, an analyst traces the JNI entry point; functions like Java_com_bank_Security_getSecret are clearly indexed in the dynamic symbol table (.dynsym) to satisfy Android runtime dynamic linking.
Dynamically, native execution offers zero defense against instrumentation.
Using Frida, an adversary calculates the library base address in process memory and uses Interceptor.attach to hook any native function address.
They can log pointer arguments, inspect raw heap buffers immediately before encryption, or replace the function implementation entirely.
Adversaries can also use GDB or LLDB to set hardware breakpoints on register reads or attach ptrace to monitor execution flow.
To raise the cost of native reverse engineering, we strip all non-essential symbols using llvm-strip, implement RegisterNatives in JNI_OnLoad instead of standard export naming, apply compiler-level obfuscation like O-LLVM with control-flow flattening, and deploy ptrace anti-debugging monitors.
However, a senior engineer always designs around the core truth: all client binaries are inspectable, and real secrets belong exclusively on the server.""",
    "meta_ar": {
        "id": "SEC-24",
        "questionAr": "كيف يمكن تحليل الكود المكتوب بلغة C/C++ و JNI وهندسته عكسياً والتلاعب به؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم قابلية الكود الأصلي (Native C/C++) للهندسة العكسية، ومعرفة أدوات التحليل الساكن مثل Ghidra و IDA Pro، واستيعاب آلية التلصص الديناميكي عبر Frida Interceptor للـ Native Hooks، وتطبيق تقنيات الحماية مثل تجريد الرموز (Symbol Stripping) و RegisterNatives، وترسيخ قاعدة حظر الأسرار في العميل.",
        "concept_ar": "تجميع الكود بلغة C/C++ عبر NDK لا يجعله صندوقاً أسود منيعاً كما يظن البعض؛ فالكود المجمع في ملفات `.so` يخضع للهندسة العكسية الساكنة بسهولة عبر أدوات مثل Ghidra و IDA Pro التي تحول لغة التجميع إلى كود C مفهوم وتستخرج النصوص من قسم `.rodata`. كما يخضع للتحليل والاعتراض الديناميكي عبر أداة Frida التي تستخدم `Interceptor.attach` للتنصت على عناوين الدوال في الذاكرة الحية وقراءة محتويات المعالج (Registers) وتعديل نتائج الدوال لحظياً.",
        "walkthrough_ar": "اعتراض دوال C++ في الذاكرة الحية وتعديل قيمها عبر Frida:\n```javascript\nvar lib = Process.findModuleByName(\"libnative.so\");\nif (lib) {\n    var decryptFunc = Module.findExportByName(\"libnative.so\", \"Java_com_bank_NativeBridge_decrypt\");\n    Interceptor.attach(decryptFunc, {\n        onEnter: function(args) { console.log(\"Native function hooked! Arg: \" + args[0]); },\n        onLeave: function(retval) { retval.replace(1); } // تزوير النتيجة وإرجاع نجاح دائماً\n    });\n}\n```",
        "why_it_matters_ar": "وضع المفاتيح والمنطق الحساس داخل مكتبات C++ ظناً أنها محمية يؤدي لاختراق التطبيق فوراً؛ لأن استخراج الأسرار من ملفات .so يستغرق دقائق عبر أدوات التفكيك والـ Hooks.",
        "worked_example_ar": "تسجيل دوال JNI ديناميكياً عبر RegisterNatives بدلاً من تصدير الأسماء الصريحة:\n```cpp\n// تسجيل الدوال في JNI_OnLoad لإخفائها من جدول الرموز المصدرة:\nstatic JNINativeMethod methods[] = {\n    {\"verifyToken\", \"(Ljava/lang/String;)Z\", (void*)native_verify}\n};\nJNIEXPORT jint JNI_OnLoad(JavaVM* vm, void* reserved) {\n    // تسجيل الدوال ديناميكياً لتصعيب التتبع الساكن\n    return JNI_VERSION_1_6;\n}\n```",
        "trade_offs_ar": "استخدام كود C++ يزيد من تعقيد البناء ويضاعف حجم التطبيق لدعم معماريتي ARM و x86، ولا يوفر أماناً حقيقياً للأسرار، بل يقتصر دوره على تحسين أداء العمليات الحسابية الثقيلة.",
        "failure_modes_ar": "تضمين مفتاح API سري كنص ثابت في كود C++ والاعتقاد بأنه محمي، بينما يظهر المفتاح صراحة عند تشغيل أمر strings libapp.so في سطر واحد.",
        "production_perspective_ar": "في التطبيقات الإنتاجية، نستخدم llvm-strip لإزالة جدول الرموز، ونفعل تشويش المجمع (O-LLVM)، لكننا لا نضع أي أسرار أو مفاتيح تشفير داخل مكتبات الـ Native ونبقيها في السيرفر.",
        "how_to_answer_ar": "ابدأ بدحض أسطورة أن C++ صندوق أسود غير قابل للكسر، واشرح أدوات التحليل الساكن واستخراج النصوص، ثم وضح قدرات Frida في اعتراض الدوال وقراءة الـ Registers ديناميكياً، واختم بإجراءات تصعيب الهجوم وحتمية نقل الأسرار للسيرفر.",
        "talking_points_ar": "أسطورة حماية الـ C++ NDK، وأدوات Ghidra و IDA Pro، واستخراج نصوص .rodata، وتلصص الـ Native عبر Frida Interceptor، وتجريد الرموز بـ llvm-strip، وتسجيل الدوال بـ RegisterNatives.",
        "follow_ups_ar": "- **المحاور:** \"كيف تخفي أسماء دوال JNI من جدول الرموز في ملف الـ `.so`؟\"\n  **المرشح:** \"أستخدم دالة RegisterNatives داخل حدث JNI_OnLoad بدلاً من التسمية التلقائية Java_package_class، وأجعل الدوال الداخلية static مع تجريد الرموز عبر strip.\"\n\n- **المحاور:** \"هل يمنع تشويش المترجم (O-LLVM) أداة Frida من اعتراض الدوال؟\"\n  **المرشح:** \"لا، التشويش يصعب التحليل الساكن، لكن المهاجم يظل قادراً على مراقبة مدخلات ومخرجات دوال النظام القياسية مثل libc و OpenSSL بالـ Frida واعتراض البيانات.\"",
        "self_check_ar": "هل أكدت أن كود C++ قابل للهندسة العكسية تماماً؟ هل شرحت كيفية استخدام Frida مع الـ Native؟ وهل بينت RegisterNatives وتجريد الرموز؟",
        "references_ar": f"- [Android NDK Security Guide](https://developer.android.com/ndk/guides) — توثيق جوجل الرسمي لمكتبات C++ الأصلية في أندرويد.\n- [Frida Native Interceptor Documentation](https://frida.re/docs/javascript-api/#interceptor) — التوثيق الرسمي لاعتراض دوال C++ والمؤشرات في الذاكرة.",
        "quick_answer_ar": "يخضع كود C++ و JNI في ملفات `.so` للهندسة العكسية بسهولة عبر أدوات التحليل الساكن مثل Ghidra التي تفكك تعليمات المعالج وتستخرج النصوص الصريحة. كما يخضع للتحليل الديناميكي عبر أداة Frida التي تعترض عناوين الدوال في الذاكرة الحية وتتلاعب بمدخلاتها ومخرجاتها في الرام، مما يثبت أن وضع الأسرار في كود Native لا يوفر أي حماية أمنية حقيقية.",
        "best_answer_ar": "يعتقد كثير من المطورين خطأً أن نقل الأسرار أو العمليات الحساسة إلى مكتبات C++ مبنية عبر NDK يحولها إلى صندوق أسود يستحيل اختراقه، وهذا وهم هندسي يناقض الواقع تماماً.\n\nمن ناحية التحليل الساكن، تقوم أدوات الهندسة العكسية المتقدمة مثل Ghidra و IDA Pro بتحويل لغة تجميع المعالج Machine Code إلى كود C تقريبي ذي دقة عالية. كما أن أي نصوص ثابتة مثل مفاتيح الـ API تظهر فوراً كنصوص صريحة داخل قسم rodata ويمكن استخراجها بأمر strings بسيط، فضلاً عن أن أسماء دوال JNI المصدرة تظهر بوضوح في جدول الرموز لتسهيل الربط مع نظام أندرويد.\n\nأما من ناحية التحليل الديناميكي، فإن أداة Frida تمتلك ميزة Interceptor.attach التي تتيح للمهاجم الارتباط بأي دالة C++ في الذاكرة الحية عبر اسمها أو إزاحة عنوانها الفيزيائي. ويستطيع المهاجم قراءة سجلات المعالج CPU Registers والتنصت على المعلمات وتعديل قيمة الناتج في الرام بسهولة. ولذلك نلزم التطبيق بعدم حفظ الأسرار في كود الـ Native، ونكتفي بتجريد الرموز عبر llvm-strip وتسجيل الدوال ديناميكياً عبر RegisterNatives لتصعيب مهمة التحليل على المهاجمين.",
        "deep_answer_ar": "في أبحاث أمان النظم وهندسة الموبايل العكسية، نعتبر تجميع الكود عبر NDK إلى تعليمات معمارية ARM64 مجرد تغيير في لغة التمثيل البرمجي لا يغير من إمكانية الوصول الرياضي والتحليلي للكود على الإطلاق.\n\nعند التحليل الساكن، لا يكتفي الباحثون بقراءة كود C المسترجع عبر Ghidra، بل يتتبعون استدعاءات مكتبات النظام القياسية مثل libc أو libcrypto؛ فإذا كان التطبيق يفك تشفير مفتاح سري محلياً، يبحث المهاجم عن استدعاءات AES أو دالة memcpy ويتتبع المؤشرات للوصول للنص المشفر. وحتى لو قام المطور بتشفير النصوص، فإن جدول الرموز الديناميكية dynsym يكشف دوال الربط مع كوتلن لتلبية متطلبات الـ Dynamic Linker في نظام التشغيل.\n\nأما الخطر الأكبر فيكمن في منصات Dynamic Binary Instrumentation؛ فأداة Frida تمكن المهاجم من حساب العنوان الأساسي للمكتبة Base Address في الذاكرة، ثم ربط مؤشرات الدوال الداخلية غير المصدرة من خلال إزاحات العناوين Offsets المكتشفة في Ghidra. هذا يمكنه من قراءة مصفوفات البايتات الحساسة لحظة معالجتها في المعالج وتجاوز أي خوارزميات حماية محلية.\n\nولرفع تكلفة التحليل على المهاجمين في بيئات الإنتاج، نلجأ إلى تقنيات تشويش على مستوى المجمع مثل O-LLVM لتشتيت مسار التنفيذ Control Flow Flattening، ونسجل دوال JNI ديناميكياً عبر دالة RegisterNatives داخل حدث JNI_OnLoad لإخفاء أسمائها من جدول الرموز، ونحذف جداول التصحيح بواسطة llvm-strip. ومع ذلك، يظل المبدأ المعماري الصارم قائماً: لا توجد أسرار محمية على العميل، وجميع العمليات الحساسة يجب أن تبقى داخل السيرفر."
    }
}

def validate_words():
    errors = []
    for qid, d in sorted(DATA.items()):
        en_s = len(d["short_en"].split())
        en_st = len(d["structured_en"].split())
        en_d = len(d["deep_senior_en"].split())

        ar_q = len(d["meta_ar"]["quick_answer_ar"].split())
        ar_b = len(d["meta_ar"]["best_answer_ar"].split())
        ar_d = len(d["meta_ar"]["deep_answer_ar"].split())

        print(f"{qid}: en_s={en_s}, en_st={en_st}, en_d={en_d} | ar_q={ar_q}, ar_b={ar_b}, ar_d={ar_d}")

        if not (35 <= en_s <= 110):
            errors.append(f"{qid} en_short invalid: {en_s}")
        if not (100 <= en_st <= 280):
            errors.append(f"{qid} en_struct invalid: {en_st}")
        if not (200 <= en_d <= 650):
            errors.append(f"{qid} en_deep invalid: {en_d}")

        if not (35 <= ar_q <= 110):
            errors.append(f"{qid} ar_quick invalid: {ar_q}")
        if not (90 <= ar_b <= 280):
            errors.append(f"{qid} ar_best invalid: {ar_b}")
        if not (180 <= ar_d <= 650):
            errors.append(f"{qid} ar_deep invalid: {ar_d}")

    if errors:
        print("\nPre-validation word count checks failed! Fix counts before updating files.")
        for e in errors:
            print(f"  ❌ {e}")
        sys.exit(1)
    else:
        print("\nPre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("sec_17_24", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print("\nAll 8 SEC questions (SEC-17 to SEC-24) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
