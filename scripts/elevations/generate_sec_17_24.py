#!/usr/bin/env python3
"""Generator for SEC-17 through SEC-24 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sec.json"

SEC_17_24 = [
    {
        "id": "SEC-17",
        "arabic_explanation": (
            "كيف تحمي الـ Buffers الحساسة في الذاكرة وتقلل زمن بقائها (Memory Residence Time) لتجنب هجمات الذاكرة؟\n\n"
            "1. مخاطر بقاء البيانات الحساسة في الذاكرة (Memory Exposure Window):\n"
            "   - عند معالجة مفاتيح التشفير، كلمات المرور، أو رموز PIN في مصفوفات عادية، قد تظل تلك البيانات في مساحة الـ Heap لساعات طويلة حتى يقوم مجمع المهملات (GC) بحذفها.\n   - خلال هذه الفترة، يكون التطبيق عرضة لـ:\n     * هجمات استخراج الذاكرة (Memory Dumps عبر `am dumpheap` على الأجهزة المعدلة أو بوجود أدوات تصحيح).\n     * قراءة الذاكرة من خلال ملف `/proc/<pid>/mem`.\n     * حفظ صفحات الذاكرة المؤقتة على وسائط التخزين عند حدوث Low Memory Swapping.\n\n"
            "2. أفضل الممارسات البرمجية لتقليل زمن البقاء:\n   - **التصفير الفوري (Immediate Zeroization)**: استخدام `ByteArray` وتصفيرها فوراً بعد الاستخدام عبر `Arrays.fill(bytes, 0.toByte())` داخل بلوك `finally`.\n   - **تجنب النسخ غير الضرورية (Zero-Copy Processing)**: كل تحويل بين `String` و `ByteArray` ينشئ نسخة جديدة غير قابلة للمسح في الـ Heap. يجب معالجة البيانات كمصفوفة بايتات مباشرة من الإدخال حتى الاستهلاك.\n   - **استخدام الذاكرة المباشرة (Direct ByteBuffers)**: حجز ذاكرة خارج الـ Managed Heap عبر `ByteBuffer.allocateDirect()` يتيح التحكم الدقيق في مسح البيانات دون تدخل الـ Garbage Collector.\n   - **العزل في عملية مستقلة (Isolated Process)**: تشغيل العمليات التشفيرية الفائقة الحساسية في Process منفصلة وتدميرها (`android:process=\":crypto_worker\"`) فور الانتهاء، مما يجبر نواة Linux على تحرير مساحة الذاكرة بالكامل فوراً."
        ),
        "practical_walkthrough": (
            "تنفيذ إدارة الذاكرة الصارمة للـ Buffers الحساسة مع التصفير الحتمي وتجنب النسخ الزائد:\n"
            "```kotlin\n"
            "// ❌ تعامل خاطئ مع الذاكرة: إنشاء نسخ متعددة وغير قابلة للمسح في الـ Heap:\n"
            "fun processUserPinInsecurely(pinInput: String) {\n"
            "    val bytes = pinInput.toByteArray(Charsets.UTF_8) // نسخة 1 في الـ Heap\n"
            "    val hashed = MessageDigest.getInstance(\"SHA-256\").digest(bytes) // نسخة 2\n"
            "    val hexString = hashed.joinToString(\"\") { \"%02x\".format(it) } // نسخة 3 مستمرة في الـ String Pool\n"
            "    sendHashToBackend(hexString)\n"
            "    // تظل النصوص الصريحة مبعثرة في الذاكرة حتى إشعار آخر!\n"
            "}\n"
            "\n"
            "// ✅ أسلوب متقدم: استخدام ByteArray قابلة للتصفير ومسحها فوراً في بلوك finally:\n"
            "class SensitiveBufferHandler {\n"
            "    fun processPinSecurely(pinBytes: ByteArray, onProcessed: (ByteArray) -> Unit) {\n"
            "        var derivedKey: ByteArray? = null\n"
            "        try {\n"
            "            // 1. معالجة البيانات الحساسة مباشرة بدون تحويلها إلى Strings\n"
            "            val digest = MessageDigest.getInstance(\"SHA-256\")\n"
            "            digest.update(pinBytes)\n"
            "            derivedKey = digest.digest()\n"
            "            \n"
            "            onProcessed(derivedKey)\n"
            "        } finally {\n"
            "            // 2. تصفير الـ Buffers فوراً وبشكل حتمي لحماية الذاكرة\n"
            "            pinBytes.fill(0)\n"
            "            derivedKey?.fill(0)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Protect sensitive buffers by minimizing allocations, processing data strictly as primitive ByteArrays or Direct ByteBuffers rather than Strings, and deterministically overwriting the memory with zeroes in a finally block immediately after use. For extreme isolation, execute sensitive operations in an isolated process that exits immediately.",
        "best_answer": (
            "Minimizing sensitive memory residence time requires controlling the allocation and lifecycle of byte buffers:\n\n"
            "1. **Eliminate Intermediate String Copies**: Strings cannot be mutated or wiped programmatically. Avoid transforming credentials into `String` representations. Handle inputs as `ByteArray` or `CharArray` from entry point to crypto consumer.\n\n"
            "2. **Deterministic Memory Zeroization**: In Java/Kotlin, always execute cleanup inside a `finally` block using `Arrays.fill(bytes, 0.toByte())`. This ensures that even if an exception occurs during processing, the sensitive buffer is overwritten with zeroes before execution leaves the scope.\n\n"
            "3. **Direct Byte Buffers**: `ByteBuffer.allocateDirect()` allocates memory outside the standard JVM managed heap. This bypasses ART moving garbage collectors, preventing unzeroed duplicate copies from lingering in fragmented memory blocks.\n\n"
            "4. **Isolated Process Lifecycle**: For extreme risk profiles (e.g., signing hardware transactions or decrypting seed phrases), launch a transient private Android Service marked with `android:isolatedProcess=\"true\"`. Once the computation concludes, kill the process with `Process.killProcess(Process.myPid())`, forcing the Linux kernel to reclaim and unmap the entire address space."
        ),
        "deep_answer": (
            "From an OS internals perspective, managing memory exposure in managed runtimes faces architectural challenges:\n\n"
            "1. **Compiler Optimization Hazards (Dead Store Elimination)**: In native C/C++ code, standard compilers often optimize away calls like `memset()` if the variable is not referenced subsequently. Production native libraries must use `explicit_bzero()` or volatile pointer loops to guarantee that the wiping operation is physically executed in hardware cache.\n\n"
            "2. **Swap and Linux OOM Killer**: Android devices utilize `zRAM` (compressed RAM swap) to manage memory pressure. If sensitive unencrypted memory pages are compressed and swapped to zRAM before zeroization, copies persist in compressed system swap partitions. Allocating small buffers and wiping them in millisecond timeframes reduces the probability of a page being selected for compaction.\n\n"
            "3. **Hardware Keystore Offloading**: The ultimate mitigation is ensuring the secret never enters application memory at all. By delegating key generation, signing, and decryption entirely to Android Keystore and the hardware Secure Element (StrongBox), zero private key bytes ever touch user-space RAM."
        ),
        "follow_ups": [
            {
                "question": "Why does calling System.gc() not solve sensitive data cleanup?",
                "answer": "System.gc() is only a hint to the runtime, does not guarantee immediate collection, does not overwrite the old object's memory with zeroes, and causes severe UI frame drops."
            },
            {
                "question": "Can root users dump RAM even if memory is zeroed after use?",
                "answer": "Root users can only capture what is currently in memory at the exact instant the snapshot is taken; wiping immediately closes the window of opportunity."
            }
        ]
    },
    {
        "id": "SEC-18",
        "arabic_explanation": (
            "كيف تتحقق من أمان المكونات المصدرة (Exported Components)، الروابط العميقة (Deep Links)، والـ PendingIntents؟\n\n"
            "1. تأمين المكونات المصدرة (Exported Components):\n"
            "   - بدءاً من Android 12 (API 31)، أصبح تحديد `android:exported=\"true|false\"` إلزامياً لكل Activity و Service و Receiver يحتوي على Intent Filter.\n   - **القاعدة الأساسية**: اجعل كل المكونات `exported=\"false\"` ما لم تكن مخصصة صراحة للاستدعاء من تطبيقات خارجية أو النظام.\n   - إذا كان المكون مصدراً لتبادل البيانات مع تطبيقاتك الأخرى التابعة لنفس الشركة، احمه بـ **Signature Permission** (`android:protectionLevel=\"signature\"`)، بحيث يرفض النظام استدعاء المكون إلا إذا كان التطبيق المتصل موقعاً بنفس مفتاح الشهادة الخاص بك.\n\n"
            "2. حماية الـ Deep Links ومنع الـ Intent Redirection:\n"
            "   - الروابط العميقة التقليدية (`scheme://host/path`) يمكن لأي تطبيق خبيث على الهاتف تسجيل نفس الـ Scheme واعتراضها.\n   - **الحل**: استخدام **Android App Links** المدعومة بنظام Digital Asset Links (`.well-known/assetlinks.json`) للتحقق المشفر من ملكية الدومين.\n   - فحص وتطهير (Sanitize) جميع المعاملات (Query Parameters) بدقة، وتجنب استخدامها مباشرة في فتح شاشات داخلية أو WebViews لمنع ثغرات Open Redirect.\n\n"
            "3. تأمين الـ PendingIntents (Mutability Risks):\n"
            "   - الـ PendingIntent يمنح التطبيق المستلم صلاحية تنفيذ الـ Intent المرفق بصلاحيات وهوية تطبيقك الأصلي!\n   - إذا تم إنشاء PendingIntent كـ `FLAG_MUTABLE`، يمكن لتطبيق وسيط تعديل الـ Action أو الـ Extras واستغلاله في اختراق التطبيق أو تسريب بيانات.\n   - **الحل الإلزامي**: استخدام `PendingIntent.FLAG_IMMUTABLE` دائماً، ولا تستخدم `FLAG_MUTABLE` إلا إذا كان الـ Intent يتطلب ملء بيانات من النظام (مثل أزرار الرد السريع في الإشعارات Direct Reply)."
        ),
        "practical_walkthrough": (
            "تأمين المكونات، الروابط العميقة، والـ PendingIntents ضد هجمات الـ Hijacking والـ Intent Injection:\n"
            "```kotlin\n"
            "// 1. إنشاء PendingIntent غير قابل للتعديل (Immutable) لتأمين الإشعارات:\n"
            "fun createSecureNotificationPendingIntent(context: Context, orderId: String): PendingIntent {\n"
            "    val intent = Intent(context, OrderDetailsActivity::class.java).apply {\n"
            "        // تحديد المكون الصريح لمنع اعتراض الـ Intent\n"
            "        putExtra(\"extra_order_id\", orderId)\n"
            "    }\n"
            "    \n"
            "    // استخدام FLAG_IMMUTABLE يمنع أي تطبيق خارجي من التلاعب بالـ Extras أو الـ Action\n"
            "    return PendingIntent.getActivity(\n"
            "        context,\n"
            "        orderId.hashCode(),\n"
            "        intent,\n"
            "        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE\n"
            "    )\n"
            "}\n"
            "\n"
            "// 2. التحقق الصارم من مدخلات الـ Deep Link ومنع الـ Open Redirect:\n"
            "class DeepLinkHandlerActivity : ComponentActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        val uri = intent.data ?: run { finish(); return }\n"
            "        \n"
            "        // التحقق من الدومين والمسار لمنع الـ Path Traversal أو الـ Injections\n"
            "        if (uri.scheme == \"https\" && uri.host == \"pay.example.com\") {\n"
            "            val safeTarget = when (uri.path) {\n"
            "                \"/checkout\" -> {\n"
            "                    val rawToken = uri.getQueryParameter(\"token\")\n"
            "                    if (isValidTokenFormat(rawToken)) Screen.Checkout(rawToken) else Screen.Error\n"
            "                }\n"
            "                else -> Screen.Home\n"
            "            }\n"
            "            navigateTo(safeTarget)\n"
            "        } else {\n"
            "            finish() // رفض أي روابط غير معروفة فوراً\n"
            "        }\n"
            "    }\n"
            "    private fun isValidTokenFormat(token: String?): Boolean = token?.matches(Regex(\"^[a-zA-Z0-9_-]{16,64}$\")) == true\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Set android:exported=\"false\" unless public access is required, and protect inter-app components with signature permissions. For PendingIntents, strictly use FLAG_IMMUTABLE to prevent malicious payload mutation. For deep links, enforce verified Android App Links and strictly validate query parameters to prevent intent redirection and path traversal.",
        "best_answer": (
            "Securing IPC boundaries requires rigorous controls across components, deep links, and intents:\n\n"
            "1. **Exported Components**: Unintentionally exported components create unauthorized entry points into private business logic. Mark all Activities, Services, and Receivers `android:exported=\"false\"` unless explicitly required. For multi-app suites sharing components, enforce custom permissions with `android:protectionLevel=\"signature\"`.\n\n"
            "2. **PendingIntent Immutability**: A `PendingIntent` executes with the permissions and identity of the creating application. If flagged `FLAG_MUTABLE`, receiving applications can mutate the wrapped intent's action, data, or flags—enabling Intent Redirection attacks. Always apply `PendingIntent.FLAG_IMMUTABLE` unless interaction requires runtime system completion (such as Inline Reply in notifications).\n\n"
            "3. **Deep Link Validation & App Links**: Custom URI schemes (`scheme://`) lack ownership verification and can be claimed by malicious apps. Use **Android App Links** with SHA-256 assetlinks verification on the server. Never pass deep link URLs directly to internal WebViews or invoke component launch intents dynamically based on untrusted intent extras."
        ),
        "deep_answer": (
            "From a threat modeling perspective, Intent-based attacks represent a significant vulnerability surface in Android applications:\n\n"
            "1. **Intent Redirection / Proxying Vulnerability**: A common flaw occurs when an exported Activity extracts an untrusted `Intent` from its extras (e.g., `intent.getParcelableExtra(\"target_intent\")`) and invokes `startActivity(targetIntent)`. An attacker can construct an intent pointing to an unexported internal activity, effectively bypassing `exported=\"false\"` using the victim app as an unintentional proxy.\n\n"
            "2. **PendingIntent Hijacking in Foreground Services**: When creating `PendingIntent` instances for notifications or alarms, ensure the wrapped Intent explicitly targets a concrete component class name (`setClass()` or `setComponent()`). Implicit intents wrapped in PendingIntents can be intercepted by rival apps registered for the matching intent filter.\n\n"
            "3. **Automated Manifest Auditing**: Run automated CI static analysis (e.g., Android Lint `ExportedService`, `UnspecifiedImmutableFlag`) to block builds containing unreviewed exported declarations or mutable pending intents."
        ),
        "follow_ups": [
            {
                "question": "When is PendingIntent.FLAG_MUTABLE legitimately required?",
                "answer": "When the receiving process must fill in intent extras, such as Android Notification Inline Reply actions or Geofence transition data."
            },
            {
                "question": "What is the difference between Android Deep Links and Android App Links?",
                "answer": "Deep Links use custom schemes without verification and trigger an app picker disambiguation dialog; App Links use HTTPS and verify domain ownership via Digital Asset Links to open directly without prompts."
            }
        ]
    },
    {
        "id": "SEC-19",
        "arabic_explanation": (
            "كيف تقوم بتأمين الـ WebView، جسور الـ JavaScript، والوصول إلى ملفات النظام و الـ Content URIs؟\n\n"
            "1. مخاطر الـ WebView في أندرويد:\n"
            "   - الـ WebView هو متصفح كامل مدمج داخل تطبيقك. إذا سمحت له بتحميل محتوى غير موثوق، فإن أي ثغرة Cross-Site Scripting (XSS) في صفحة الويب تتحول مباشرة إلى ثغرة اختراق لتطبيق أندرويد نفسه!\n\n"
            "2. تأمين جسر الـ JavaScript (@JavascriptInterface):\n"
            "   - ربط كود Kotlin بـ JavaScript عبر `addJavascriptInterface` يسمح لكود الويب باستدعاء دوال native.\n   - **قاعدة صارمة**: لا تقم بحقن الـ JS Interface أبداً في صفحات غير موثوقة. يجب التحقق من الدومين ومسار الصفحة (`origin`) في كود الـ WebView قبل تفعيل أو تنفيذ أي دالة في الجسر.\n\n"
            "3. إغلاق منافذ الوصول للملفات المحلية (Local File Access):\n"
            "   - بشكل افتراضي في الإصدارات الحديثة، ولكن يجب تأكيده برمجياً:\n     * `settings.allowFileAccess = false`: يمنع تحميل ملفات التطبيق المحلية عبر `file://`.\n     * `settings.allowContentAccess = false`: يمنع الوصول إلى الـ Content Providers.\n     * يمنع هجمات سرقة ملفات الـ SharedPreferences وقواعد البيانات عبر كود HTML خبيث.\n\n"
            "4. التحميل الآمن للأصول المحلية عبر `WebViewAssetLoader`:\n"
            "   - بدلاً من تحميل الملفات عبر بروتوكول `file:///android_asset/` غير الآمن، استخدم مكتبة AndroidX `WebViewAssetLoader` التي تقوم بتحميل الأصول المحلية تحت بروتوكول افتراضي آمن (`https://appassets.androidplatform.net/`)، مما يحافظ على تطبيق سياسة Same-Origin Policy ويمنع تسريب البيانات.\n\n"
            "5. التعامل الصارم مع أخطاء شهادات الـ SSL:\n"
            "   - **ممنوع نهائياً**: استدعاء `handler.proceed()` داخل دالة `onReceivedSslError`. هذا يسمح بهجمات Man-in-the-Middle (MITM). يجب دائماً استدعاء `handler.cancel()`."
        ),
        "practical_walkthrough": (
            "تكوين WebView آمن للإنتاج مع إغلاق منافذ الملفات واستخدام WebViewAssetLoader والتحقق من الـ SSL:\n"
            "```kotlin\n"
            "class SecureWebActivity : ComponentActivity() {\n"
            "    private lateinit var webView: WebView\n"
            "\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        webView = WebView(this)\n"
            "        setContentView(webView)\n"
            "        configureSecureSettings(webView)\n"
            "    }\n"
            "\n"
            "    private fun configureSecureSettings(view: WebView) {\n"
            "        view.settings.apply {\n"
            "            // 1. تقييد الوصول للملفات والـ Content URIs:\n"
            "            allowFileAccess = false\n"
            "            allowContentAccess = false\n"
            "            javaScriptEnabled = true // تفعيل فقط عند الحاجة القصوى\n"
            "            \n"
            "            // تعطيل مشاركة الموقع والتخزين غير الضروري\n"
            "            setGeolocationEnabled(false)\n"
            "            databaseEnabled = false\n"
            "        }\n"
            "\n"
            "        // 2. استخدام AssetLoader الآمن لتحميل الملفات المحلية كـ HTTPS مجازي:\n"
            "        val assetLoader = WebViewAssetLoader.Builder()\n"
            "            .addPathHandler(\"/assets/\", WebViewAssetLoader.AssetsPathHandler(this))\n"
            "            .build()\n"
            "\n"
            "        view.webViewClient = object : WebViewClient() {\n"
            "            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {\n"
            "                return assetLoader.shouldInterceptRequest(request.url)\n"
            "            }\n"
            "\n"
            "            override fun onReceivedSslError(view: WebView, handler: SslErrorHandler, error: SslError) {\n"
            "                // ❌ لا تقم أبداً باستدعاء handler.proceed()!\n"
            "                // ✅ إلغاء الطلب فوراً لحماية المستخدم من هجمات MITM:\n"
            "                handler.cancel()\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Secure WebViews by disabling allowFileAccess and allowContentAccess, loading local bundled content safely via AndroidX WebViewAssetLoader under a virtual HTTPS origin, canceling onReceivedSslError unconditionally, and strictly restricting addJavascriptInterface to audited, whitelisted internal origins.",
        "best_answer": (
            "Hardening Android WebView requires mitigating data exfiltration, local file access, and bridge exploitation:\n\n"
            "1. **Disable File & Content Scheme Access**: \n"
            "   - Explicitly disable `settings.allowFileAccess = false` and `settings.allowContentAccess = false`. This blocks attackers from using malicious scripts or iframe tags to read private app files (`file:///data/data/<package>/...`) or query internal ContentProviders.\n\n"
            "2. **Use AndroidX WebViewAssetLoader**:\n"
            "   - Traditional `file:///android_asset/` URLs violate modern web security models and cross-origin boundaries. `WebViewAssetLoader` intercepts requests and serves local assets via a virtual domain (`https://appassets.androidplatform.net/assets/`), enforcing the standard Same-Origin Policy and secure HTTPS context.\n\n"
            "3. **Lock Down JavaScript Interfaces**:\n"
            "   - Only expose `@JavascriptInterface` methods to pages loaded from strictly whitelisted, first-party HTTPS origins verified inside `shouldOverrideUrlLoading` or `onPageStarted`.\n\n"
            "4. **Unconditional SSL Error Rejection**:\n"
            "   - In `WebViewClient.onReceivedSslError()`, always call `handler.cancel()`. Never call `handler.proceed()`, as doing so completely bypasses TLS validation and exposes users to Man-in-the-Middle attacks."
        ),
        "deep_answer": (
            "From an advanced security engineering perspective, WebViews represent a hybrid execution environment requiring strict boundaries:\n\n"
            "1. **Safe Browsing Integration**: In Android 8.0+ (API 27), verify that Google Safe Browsing is enabled in WebView (`settings.safeBrowsingEnabled = true`). Implement `onSafeBrowsingHit()` to handle malicious phishing URLs identified by Google before page rendering begins.\n\n"
            "2. **Mitigating Universal Cross-Site Scripting (UXSS)**: For sensitive hybrid applications, enable multi-process WebView mode (default on Android 8+) and restrict JavaScript execution permissions dynamically. Avoid exposing native payment or authentication tokens through JavaScript bridge callback return values; instead, bridge only transient action triggers while executing actual cryptographic token transfers over native secure channels.\n\n"
            "3. **Content Security Policy (CSP)**: Ensure server responses loaded into WebViews include strict HTTP Content Security Policy headers (`default-src 'self'`), mitigating inline script injections and preventing unauthorized external script loading."
        ),
        "follow_ups": [
            {
                "question": "Why is addJavascriptInterface dangerous on Android versions prior to API 17?",
                "answer": "On Android < 4.2, reflection could be used by injected JavaScript to access getClass().forName() on Java objects and execute arbitrary Linux shell commands."
            },
            {
                "question": "What is the security risk of enabling setAllowUniversalAccessFromFileURLs(true)?",
                "answer": "It permits scripts running in a local file context to make cross-origin requests to arbitrary web origins, completely dismantling Same-Origin Policy."
            }
        ]
    },
    {
        "id": "SEC-20",
        "arabic_explanation": (
            "كيف تنفذ تثبيت الشهادات (Certificate Pinning) وما هي استراتيجية التدوير والإنعاش لتجنب تعطيل التطبيق (Bricking)؟\n\n"
            "1. ما هو تثبيت الشهادات (Certificate Pinning) ولماذا نستخدمه؟\n"
            "   - الوضع الافتراضي في HTTPS يعتمد على سلسلة الثقة (Chain of Trust) من الـ Certificate Authorities (CAs). إذا تم اختراق أي CA حول العالم أو تثبيت شهادة مزيفة في الهاتف، يمكن للمهاجم فك تشفير اتصالات التطبيق.\n   - الـ Pinning يحدد بصمة تشفيرية صريحة (SHA-256 Hash لـ Subject Public Key Info - SPKI) يقبلها التطبيق فقط للخادم المطلوب، ويرفض أي شهادة أخرى حتى لو كانت موقعة من CA معتمد.\n\n"
            "2. كارثة التثبيت العشوائي (The Bricking Hazard):\n"
            "   - إذا انتهت صلاحية شهادة الخادم أو تم اختراق السيرفر واضطر فريق البنية التحتية لتغيير الشهادة بسرعة، فإن جميع إصدارات التطبيق المثبتة لدى المستخدمين ستفشل في الاتصال فوراً برمي `SSLPeerUnverifiedException`!\n   - التطبيق يصبح \"معطلاً كلياً (Bricked)\" ولن يستطيع حتى الاتصال بالسيرفر لمعرفة التحديث الجديد إلا إذا قام المستخدم بتحديث التطبيق يدوياً من Google Play!\n\n"
            "3. استراتيجية التدوير والإنعاش الآمنة (Rotation & Recovery Strategy):\n"
            "   - **تثبيت الـ Public Key وليس الشهادة بالكامل**: تثبيت الـ SPKI يسمح بتجديد الشهادة طالما تم الحفاظ على نفس الـ Key Pair.\n   - **تضمين مفاتيح احتياطية (Backup Pins)**: تثبيت بصمة المفتاح الأساسي + بصمة مفتاح احتياطي أو اثنين يتم الاحتفاظ بهما في خزنة أمنية مشفرة (Hardware Security Module).\n   - **تاريخ انتهاء الصلاحية في Network Security Config**: تحديد خاصية `<pin-set expiration=\"YYYY-MM-DD\">` في أندرويد. إذا انتهى هذا التاريخ، يعود النظام تلقائياً للتحقق الطبيعي عبر الـ CAs بدلاً من إيقاف التطبيق نهائياً."
        ),
        "practical_walkthrough": (
            "تنفيذ Certificate Pinning متقدم مع مفاتيح احتياطية عبر OkHttp وملف Network Security Config:\n"
            "```xml\n"
            "<!-- 1. التثبيت عبر res/xml/network_security_config.xml مع تاريخ انتهاء لمنع تعطيل التطبيق -->\n"
            "<network-security-config>\n"
            "    <domain-config>\n"
            "        <domain includeSubdomains=\"true\">api.example.com</domain>\n"
            "        <!-- تحديد تاريخ انتهاء؛ بعد هذا التاريخ يعود النظام لفحص الـ CAs الطبيعي ولا يعطل التطبيق -->\n"
            "        <pin-set expiration=\"2026-12-31\">\n"
            "            <!-- المفتاح الأساسي الفعال حالياً في الإنتاج -->\n"
            "            <pin digest=\"SHA-256\">k2oTX1jqhUxMwVTmrttBm2LocGaHGebWZmc85yfYXO8=</pin>\n"
            "            <!-- المفتاح الاحتياطي للطوارئ المخزن في الـ HSM -->\n"
            "            <pin digest=\"SHA-256\">YW63uKGCRvrVAqhJ6usDxn7NUOwG+KpgMUizDG4Nk2U=</pin>\n"
            "        </pin-set>\n"
            "    </domain-config>\n"
            "</network-security-config>\n"
            "```\n\n"
            "```kotlin\n"
            "// 2. تطبيق التثبيت عبر OkHttp CertificatePinner في كود Kotlin كطبقة حماية إضافية:\n"
            "fun createPinnedOkHttpClient(): OkHttpClient {\n"
            "    val certificatePinner = CertificatePinner.Builder()\n"
            "        .add(\n"
            "            \"api.example.com\",\n"
            "            \"sha256/k2oTX1jqhUxMwVTmrttBm2LocGaHGebWZmc85yfYXO8=\", // Primary Pin\n"
            "            \"sha256/YW63uKGCRvrVAqhJ6usDxn7NUOwG+KpgMUizDG4Nk2U=\"  // Disaster Recovery Pin\n"
            "        )\n"
            "        .build()\n"
            "\n"
            "    return OkHttpClient.Builder()\n"
            "        .certificatePinner(certificatePinner)\n"
            "        .connectTimeout(15, TimeUnit.SECONDS)\n"
            "        .build()\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Pin the Subject Public Key Info (SPKI) SHA-256 hash rather than the leaf certificate, and always include at least one secure offline backup pin. Configure an expiration date in Android's network_security_config.xml so that expired pins degrade safely to standard CA validation rather than permanently bricking user connectivity.",
        "best_answer": (
            "Certificate pinning secures network channels against fraudulent Certificate Authorities, but poor rotation strategies risk catastrophic app bricking:\n\n"
            "1. **Pin the Public Key (SPKI), Not the Certificate**: Pin the SHA-256 hash of the Subject Public Key Info. This decouples pinning from certificate expiration dates, allowing site certificates to be re-issued using the existing private key without breaking client pins.\n\n"
            "2. **Mandatory Backup Pins**: Never release an app with only a single pin. Always configure at least one active pin and one or two cold-storage backup pins (generated and stored securely in an enterprise HSM). If the primary certificate is compromised, ops can deploy the backup key on servers without releasing an app update.\n\n"
            "3. **Expiration Safeguard**: In Android's `network_security_config.xml`, specify `<pin-set expiration=\"YYYY-MM-DD\">`. Once the timestamp elapses, the Android framework automatically ceases pin enforcement and falls back to standard system CA validation, ensuring older app versions remain functional even if scheduled rotations miss target release windows."
        ),
        "deep_answer": (
            "From an operational reliability perspective, senior architects design dynamic recovery mechanisms for pinned endpoints:\n\n"
            "1. **Intermediate vs. Leaf Pinning**: Pinning the leaf certificate's public key provides maximum security but highest rotation risk. Pinning the Intermediate CA certificate of a dedicated enterprise PKI provides easier server-side rotation at the cost of trusting all certificates issued under that intermediate.\n\n"
            "2. **Dynamic Remote Pin Fallbacks**: High-assurance financial apps often maintain a dedicated unpinned or multi-CDN fallback domain (`fallback-config.example.com`). If all pinned API calls fail with `SSLPeerUnverifiedException`, the app queries this hardened secondary endpoint to retrieve an authenticated, cryptographically signed pin configuration update.\n\n"
            "3. **Telemetry & Audit Logging**: Implement OkHttp's `EventListener` to log pinning failures with exact peer certificate chain hashes. This provides real-time alerting on potential MITM attacks or configuration drift before certificates expire."
        ),
        "follow_ups": [
            {
                "question": "Can certificate pinning prevent attackers using Frida on rooted devices from sniffing traffic?",
                "answer": "No; dynamic instrumentation tools hook TrustManager.checkServerTrusted() or OpenSSL verification functions directly in memory, bypassing pins effortlessly."
            },
            {
                "question": "Why should you avoid pinning the Root CA?",
                "answer": "Pinning the Root CA offers little security advantage over standard PKI validation because root CAs sign millions of certificates, negating specific domain identity verification."
            }
        ]
    },
    {
        "id": "SEC-21",
        "arabic_explanation": (
            "ما هي Play Integrity API؟ وما هي القرارات الأمنية التي يجب أن تُتخذ حصرياً على السيرفر (Server-Side Decisions)؟\n\n"
            "1. ما هي Play Integrity API وماذا تفحص؟\n"
            "   - هي البديل الرسمي والحديث لـ SafetyNet Attestation من Google.\n   - تقوم بفحص حالة البيئة التي يعمل فيها التطبيق وإصدار شهادة موقعة مشفرة (Cryptographically Signed Token) تحتوي على ثلاثة مؤشرات رئيسية:\n     * **App Licensing Verdict**: هل التطبيق مرخص ومثبت من متجر Google Play الرسمي؟\n     * **App Recognition Verdict**: هل توقيع الـ APK والـ Package Name مطابقان للإصدار الأصلي المسجل في Play Console؟\n     * **Device Recognition Verdict**: مستوى سلامة الجهاز والعتاد (MEETS_BASIC_INTEGRITY, MEETS_DEVICE_INTEGRITY, MEETS_STRONG_INTEGRITY).\n\n"
            "2. القاعدة الذهبية: العميل لا يفك التشفير ولا يتخذ القرار!\n   - **خطأ ساذج**: فك تشفير الـ Token على الهاتف وفحص النتيجة في كود Kotlin (`if (verdict == MEETS_DEVICE_INTEGRITY)`). هذا الفحص يمكن تجاوزه بسهولة عبر Frida أو تعديل الـ Smali!\n   - **المعمارية الصحيحة**: يقوم السيرفر بإنشاء رقم عشوائي (Cryptographic Nonce) مشفر مرتبط بطلب المستخدم. يطلب التطبيق الـ Token من Google Play مدمجاً بهذا الـ Nonce، ثم يرسل الـ Token الخام إلى السيرفر. السيرفر هو الطرف الوحيد الذي يفك تشفير الـ Token ويفحص التوقيع وصحة الـ Nonce ويتخذ قرار السماح أو الرفض."
        ),
        "practical_walkthrough": (
            "المعمارية الصحيحة لطلب Play Integrity Token وإرساله للسيرفر للتحقق منه:\n"
            "```kotlin\n"
            "class PlayIntegrityRepository(\n"
            "    private val context: Context,\n"
            "    private val backendApi: BackendSecurityApi\n"
            ") {\n"
            "    private val integrityManager = IntegrityManagerFactory.create(context)\n"
            "\n"
            "    // 1. طلب الـ Token باستخدام Nonce وارد من السيرفر لمنع هجمات Replay Attacks:\n"
            "    suspend fun verifyTransaction(serverNonce: String, transactionId: String): TransactionResult {\n"
            "        val request = IntegrityTokenRequest.builder()\n"
            "            .setCloudProjectNumber(123456789012L) // Cloud Project Number الخاص بالتطبيق\n"
            "            .setRequestHash(serverNonce) // ربط الـ Token بالـ Nonce السيرفري\n"
            "            .build()\n"
            "\n"
            "        val tokenResponse = integrityManager.requestIntegrityToken(request).await()\n"
            "        val integrityToken = tokenResponse.token()\n"
            "\n"
            "        // 2. إرسال الـ Token الخام للسيرفر دون فحص محلي:\n"
            "        // السيرفر يستخدم Google Play Developer API لفك التشفير والتأكد من سلامة التوقيع والجهاز\n"
            "        return backendApi.authorizeSensitiveTransaction(\n"
            "            transactionId = transactionId,\n"
            "            integrityToken = integrityToken\n"
            "        )\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Play Integrity API evaluates app binary authenticity, licensing, and device integrity verdicts. The client must never decrypt or act on the token locally; instead, it requests a token bound to a server-generated nonce and sends it to the backend, which decodes Google's cryptographic verdict to enforce policy.",
        "best_answer": (
            "Play Integrity API provides attestation of app authenticity and device trustworthiness:\n\n"
            "1. **Evaluation Signals**:\n"
            "   - **App Recognition**: Validates whether the running APK matches the package name and signing certificate registered in Google Play.\n   - **App Licensing**: Verifies whether the user acquired the app legitimately through Google Play.\n   - **Device Recognition**: Returns graduated verdicts (`MEETS_BASIC_INTEGRITY` for emulators/rooted devices without active tampering, `MEETS_DEVICE_INTEGRITY` for certified CTS-compliant Android devices, `MEETS_STRONG_INTEGRITY` for hardware-backed keystore and bootloader locking).\n\n"
            "2. **Mandatory Server-Side Verification**:\n"
            "   - Decrypting or validating verdicts on the Android client is an anti-pattern because client memory and conditional branches can be hooked.\n   - The server initiates an action by generating a cryptographically random, short-lived `nonce`. The mobile client requests an integrity token embedding this nonce, and forwards the token to the backend.\n   - The backend validates the verdict payload directly via Google APIs or Google's public keys, verifying the nonce, timestamp, package name, and integrity level."
        ),
        "deep_answer": (
            "Senior architects implement Play Integrity using risk-based decision ladders rather than binary kill-switches:\n\n"
            "1. **Tiered Risk Responses**: Failing `MEETS_STRONG_INTEGRITY` should not immediately block app usage. Budget devices, custom vendor builds, or uncertified devices can pass `MEETS_BASIC_INTEGRITY`. High-risk financial operations (wire transfers, password resets) can mandate `MEETS_DEVICE_INTEGRITY`, while read-only browsing can proceed under basic integrity with stepped-up MFA requirements.\n\n"
            "2. **Play Integrity Standard vs. Classic Requests**: The standard API offers cached attestation tokens for low latency, while classic requests communicate directly with Google Play servers. For sensitive payments, classic requests bound to dynamic nonces guarantee fresh, un-cached hardware validation.\n\n"
            "3. **Fallback & Graceful Degradation**: Google Play Services may be temporarily unavailable or throttled. Backend architectures must establish fallback policies (e.g., rate-limiting requests or requiring SMS OTP) rather than completely blocking legitimate users during Google outages."
        ),
        "follow_ups": [
            {
                "question": "What happens on devices without Google Play Services (e.g., Huawei or custom AOSP)?",
                "answer": "Play Integrity API fails immediately with an integrity service unavailable error; alternative attestations or server-side risk scoring must be used."
            },
            {
                "question": "Why is the nonce parameter critical for Play Integrity requests?",
                "answer": "The nonce binds the integrity verdict to a specific transaction and timestamp, preventing attackers from capturing a valid token and replaying it against future requests."
            }
        ]
    },
    {
        "id": "SEC-22",
        "arabic_explanation": (
            "كيف تصمم وصولاً مشروطاً بالبصمة (Biometric-Gated Access) لعمليات Android Keystore بشكل عتادي لا يمكن تجاوزه برمجياً؟\n\n"
            "1. الفرق الجوهري بين الفحص الشكلي والتأمين العتادي:\n"
            "   - **الفحص الشكلي (Boolean Authentication - ❌)**: مجرد إظهار `BiometricPrompt` واستدعاء العملية في `onAuthenticationSucceeded()`. هذا الفحص يمكن لمهاجم تجاوزه بسطر واحد في Frida عبر استدعاء الـ Callback مباشرة دون لمس مستشعر البصمة!\n   - **التأمين العتادي التشفيري (Crypto-Gated Authentication - ✅)**: ربط مفتاح الـ Keystore بمتطلب التحقق البيومتري (`setUserAuthenticationRequired(true)`). في هذا النمط، يظل المفتاح مقفلاً داخل عتاد الهاتف (TEE / Secure Element) وترفض الشريحة إجراء أي عملية تشفير أو فك تشفير حتى يقدم مستشعر البصمة العتادي تصريحاً مشفراً للـ Keystore!\n\n"
            "2. دور كائن `BiometricPrompt.CryptoObject`:\n   - نقوم بإنشاء `Cipher` غير مهيأ بالكامل، ونمرره مغلفاً داخل `CryptoObject` إلى `BiometricPrompt.authenticate()`.\n   - عند نجاح البصمة الحقيقية عتادياً، يفتح الـ Keymaster تصريح الـ Cipher مؤقتاً.\n   - نقوم باسترجاع الـ Cipher المشفر من الـ Callback واستخدامه في تنفيذ `cipher.doFinal()`. لو حاول المهاجم استدعاء الـ Callback عبر Frida دون بصمة حقيقية، سيفشل `cipher.doFinal()` برمي `UserNotAuthenticatedException` لأن العتاد لم يفتح المفتاح!"
        ),
        "practical_walkthrough": (
            "تنفيذ Biometric-Gated Crypto حقيقي مدعوم عتادياً ومحصن ضد هجمات الـ Hooking:\n"
            "```kotlin\n"
            "class BiometricCryptoManager(private val activity: FragmentActivity) {\n"
            "    private val KEY_ALIAS = \"biometric_user_vault_key\"\n"
            "\n"
            "    // 1. توليد مفتاح مقفل عتادياً يتطلب بصمة المستخدم لكل عملية:\n"
            "    fun generateBiometricProtectedKey() {\n"
            "        val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, \"AndroidKeyStore\")\n"
            "        val spec = KeyGenParameterSpec.Builder(\n"
            "            KEY_ALIAS,\n"
            "            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT\n"
            "        )\n"
            "            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)\n"
            "            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)\n"
            "            .setUserAuthenticationRequired(true) // يتطلب بصمة لكل عملية تشفير/فك تشفير\n"
            "            .setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG) // مدة الصلاحية 0 = لكل عملية على حدة\n"
            "            .setInvalidatedByBiometricEnrollment(true) // إبطال المفتاح فوراً إذا أضيفت بصمة جديدة للهاتف\n"
            "            .build()\n"
            "        keyGen.init(spec)\n"
            "        keyGen.generateKey()\n"
            "    }\n"
            "\n"
            "    // 2. فك تشفير البيانات عبر ربط الـ Cipher بـ BiometricPrompt.CryptoObject:\n"
            "    fun authenticateAndDecrypt(iv: ByteArray, ciphertext: ByteArray, onSuccess: (ByteArray) -> Unit) {\n"
            "        val keyStore = KeyStore.getInstance(\"AndroidKeyStore\").apply { load(null) }\n"
            "        val secretKey = keyStore.getKey(KEY_ALIAS, null) as SecretKey\n"
            "        val cipher = Cipher.getInstance(\"AES/GCM/NoPadding\").apply {\n"
            "            init(Cipher.DECRYPT_MODE, secretKey, GCMParameterSpec(128, iv))\n"
            "        }\n"
            "\n"
            "        val promptInfo = BiometricPrompt.PromptInfo.Builder()\n"
            "            .setTitle(\"Confirm payment\")\n"
            "            .setNegativeButtonText(\"Cancel\")\n"
            "            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)\n"
            "            .build()\n"
            "\n"
            "        val biometricPrompt = BiometricPrompt(\n"
            "            activity,\n"
            "            ContextCompat.getMainExecutor(activity),\n"
            "            object : BiometricPrompt.AuthenticationCallback() {\n"
            "                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {\n"
            "                    // الـ Cipher الآن فقط أصبح مفكوك القفل عتادياً!\n"
            "                    val authenticatedCipher = result.cryptoObject?.cipher!!\n"
            "                    val decryptedPayload = authenticatedCipher.doFinal(ciphertext)\n"
            "                    onSuccess(decryptedPayload)\n"
            "                }\n"
            "            }\n"
            "        )\n"
            "\n"
            "        // تمرير الـ CryptoObject إلزامي لجعل القفل عتادياً\n"
            "        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Gate Keystore operations with biometrics by setting setUserAuthenticationRequired(true) on the key and passing a Cipher wrapped in a BiometricPrompt.CryptoObject to authenticate(). Decrypt only using the authenticated Cipher in onAuthenticationSucceeded; hardware enforces key release, preventing bypass via software hooks.",
        "best_answer": (
            "Biometric-gated security must be backed cryptographically rather than relying on boolean UI callback results:\n\n"
            "1. **The Vulnerability of Boolean Prompts**: Invoking `BiometricPrompt.authenticate(promptInfo)` without a `CryptoObject` treats the result as a simple boolean status. An attacker running Frida hooks `onAuthenticationSucceeded()` to invoke the success callback directly without touching the sensor.\n\n"
            "2. **Hardware Cryptographic Binding (CryptoObject)**:\n"
            "   - When generating the AES key in `AndroidKeyStore`, configure `.setUserAuthenticationRequired(true)` with `.setUserAuthenticationParameters(0, AUTH_BIOMETRIC_STRONG)` and `.setInvalidatedByBiometricEnrollment(true)`.\n   - Initialize a `Cipher` with the key and wrap it inside `BiometricPrompt.CryptoObject(cipher)`.\n   - Pass the `CryptoObject` into `biometricPrompt.authenticate()`.\n\n"
            "3. **Hardware Enforcement**: The Android Keymaster / TEE hardware keeps the key material locked. Only upon receiving authenticated biometric proof from the hardware fingerprint sensor does the secure enclave release the cryptographic key for that specific `Cipher` instance. Attempting to call `cipher.doFinal()` without biometric hardware unlocking throws `UserNotAuthenticatedException`."
        ),
        "deep_answer": (
            "From an architectural standpoint, designing biometric crypto requires handling edge cases in the user security lifecycle:\n\n"
            "1. **Biometric Enrollment Changes**: When a user registers a new finger on the device, `setInvalidatedByBiometricEnrollment(true)` immediately renders the key permanently unusable. Any subsequent `cipher.init()` throws `KeyPermanentlyInvalidatedException`. The application must handle this by safely deleting the invalid key, purging local biometric-gated caches, and prompting the user for full password authentication.\n\n"
            "2. **Per-Use vs. Time-Window Authentication**: Specifying a duration of `0` in `setUserAuthenticationParameters` requires biometric verification for every individual cryptographic transaction. Setting a duration greater than zero allows the hardware key to remain unlocked for that duration (e.g., 30 seconds), which is useful for bulk operations but presents a larger attack window.\n\n"
            "3. **Strong vs. Weak Biometrics**: Financial applications must strictly configure `BiometricManager.Authenticators.BIOMETRIC_STRONG` (Class 3 hardware with < 0.002% False Acceptance Rate and liveness detection). Weak biometrics (Class 2 / 2D camera face unlock) are prohibited from unlocking Keystore keys marked with `AUTH_BIOMETRIC_STRONG`."
        ),
        "follow_ups": [
            {
                "question": "Can Face Unlock on budget Android devices unlock AUTH_BIOMETRIC_STRONG keys?",
                "answer": "No; standard 2D camera face recognition is classified as Class 1 or Class 2 (Weak) and Android Keystore blocks it from unlocking Strong-tier cryptographic keys."
            },
            {
                "question": "What happens if the device has no screen lock set when generating a biometric key?",
                "answer": "KeyGenParameterSpec initialization fails immediately with an InvalidAlgorithmParameterException because secure lock screen credentials are a prerequisite."
            }
        ]
    },
    {
        "id": "SEC-23",
        "arabic_explanation": (
            "ما هي التهديدات الأمنية المترتبة على النسخ الاحتياطي غير الآمن (Insecure Backup) وملفات قواعد البيانات المحلية غير المشفرة؟\n\n"
            "1. تهديد النسخ الاحتياطي المحلي و السحابي (Insecure Backups):\n"
            "   - **ADB Backup Extraction**: في التطبيقات التي تترك `android:allowBackup=\"true\"` في الـ Manifest، يمكن لأي شخص يملك وصولاً فيزيائياً للهاتف عبر كابل USB تفعيل USB Debugging وتنفيذ أمر:\n     `adb backup -f backup.ab com.example.app`.\n   - هذا الأمر يستخرج ملفات التطبيق الخاصة بالكامل (SharedPreferences, Databases, Caches) إلى جهاز الكمبيوتر بدون الحاجة لصلاحيات Root!\n   - **Android Cloud Backup**: رفع ملفات التطبيق إلى حساب Google Drive الخاص بالمستخدم. إذا تم اختراق حساب Google أو استرجاع النسخة على جهاز آخر، قد تتسرب البيانات أو تتعطل التشفيرات.\n\n"
            "2. تهديد قواعد البيانات المحلية غير المشفرة (Plaintext SQLite / Room):\n   - ملفات قواعد البيانات (`/data/data/<package>/databases/app.db`) تخزن الجداول والنصوص كـ Plaintext.\n   - أي تطبيق خبيث يستغل ثغرة في النظام أو جهاز معمول له Root يستطيع نسخ الملف وفتحه باستخدام أي أداة SQLite Viewer وقراءة كل سجلات المعاملات، الحسابات، والبيانات الشخصية (PII).\n\n"
            "3. الحلول الهندسية الموصى بها:\n   - تعطيل النسخ الاحتياطي في الـ Manifest (`android:allowBackup=\"false\"`) أو تخصيص قواعد استثناء صارمة عبر `backup_rules.xml`.\n   - تشفير قاعدة البيانات بالكامل باستخدام **SQLCipher** المدمج مع Android Room Database.\n   - حفظ مفتاح تشفير قاعدة البيانات داخل Android Keystore بدلاً من كتابته كنص صريح في الكود."
        ),
        "practical_walkthrough": (
            "تأمين قواعد بيانات Room باستخدام SQLCipher وتعطيل النسخ الاحتياطي الحساس:\n"
            "```kotlin\n"
            "// 1. بناء قاعدة بيانات Room مشفرة بالكامل عبر SQLCipher بمفتاح من Keystore:\n"
            "class EncryptedDatabaseProvider(\n"
            "    private val context: Context,\n"
            "    private val keyStoreManager: KeystoreSecretStorage\n"
            ") {\n"
            "    fun buildEncryptedRoomDatabase(): AppDatabase {\n"
            "        // استرجاع مصفوفة بايتات مفتاح التشفير من الـ Keystore المشفر\n"
            "        val dbPassphrase = keyStoreManager.getOrCreateDatabasePassphrase()\n"
            "        \n"
            "        // إنشاء SupportFactory الخاص بمكتبة SQLCipher:\n"
            "        val supportFactory = SupportFactory(dbPassphrase)\n"
            "\n"
            "        return Room.databaseBuilder(context, AppDatabase::class.java, \"secure_app_vault.db\")\n"
            "            .openHelperFactory(supportFactory) // تفعيل تشفير SQLCipher AES-256 بالكامل لملف الداتابيز\n"
            "            .build()\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "```xml\n"
            "<!-- 2. حماية الـ Manifest واستثناء البيانات الحساسة من النسخ الاحتياطي -->\n"
            "<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\">\n"
            "    <application\n"
            "        android:allowBackup=\"false\"\n"
            "        android:fullBackupContent=\"false\"\n"
            "        android:dataExtractionRules=\"@xml/secure_backup_rules\">\n"
            "    </application>\n"
            "</manifest>\n"
            "```"
        ),
        "quick_answer": "Insecure backups allow full sandbox extraction via adb backup or Google Drive sync if allowBackup is enabled. Unencrypted SQLite databases leave records readable in plaintext. Remediate by disabling allowBackup or setting strict extraction rules, and encrypting databases at rest using SQLCipher with Keystore-derived passphrases.",
        "best_answer": (
            "Local storage vulnerabilities stem from assumptions about sandbox persistence and physical isolation:\n\n"
            "1. **Insecure Backup Vulnerabilities**:\n"
            "   - If `android:allowBackup=\"true\"` is present in `AndroidManifest.xml`, an attacker with physical access and USB debugging enabled can run `adb backup` to extract the entire application sandbox—including shared preferences, cached HTTP responses, and SQLite databases—into a plaintext tar archive on a desktop machine.\n   - In cloud backups, sensitive data syncs to the user's Google Drive, where it may be exposed to secondary account compromise.\n\n"
            "2. **Unencrypted Database Risks**:\n"
            "   - Standard Room / SQLite databases store records in plaintext binary pages. Anyone with root access, physical flash extraction tools, or system debugging privileges can run `sqlite3` on `/data/data/<package>/databases/` to inspect transaction histories and PII.\n\n"
            "3. **Defensive Architecture**:\n"
            "   - Set `android:allowBackup=\"false\"` for security-critical apps, or define granular `dataExtractionRules` excluding all databases and datastores.\n   - Encrypt databases using **SQLCipher for Android**, passing a 256-bit passphrase derived from Android Keystore directly into Room's `SupportFactory`."
        ),
        "deep_answer": (
            "From a compliance and forensics perspective, securing data-at-rest requires comprehensive storage hygiene:\n\n"
            "1. **SQLCipher Key Management**: The security of SQLCipher is entirely dependent on its encryption key. Hardcoding a passphrase in Kotlin or using a static salt renders SQLCipher completely ineffective against reverse engineering. The passphrase must be generated randomly on first launch, encrypted using an `AndroidKeyStore` AES-GCM master key, and loaded into memory only during database initialization.\n\n"
            "2. **Database Wal & Journal Leaks**: SQLite uses Write-Ahead Logging (WAL) and rollback journals (`.db-wal` and `.db-shm`). When SQLCipher is used, WAL files are also encrypted under the same cipher. However, if unencrypted SQLite is used, deleting rows does not immediately wipe data from disk pages until a `VACUUM` command is issued, leaving deleted records recoverable in forensic memory scraps.\n\n"
            "3. **Scoped Storage Realities**: Never store databases or sensitive temporary export files in shared public storage (`/sdcard/` or `MediaStore`). Maintain all sensitive relational and file stores strictly within internal application directory spaces (`context.filesDir`, `context.noBackupFilesDir`)."
        ),
        "follow_ups": [
            {
                "question": "What is the purpose of context.noBackupFilesDir?",
                "answer": "It provides a private filesystem directory whose contents are guaranteed to never be backed up to the cloud, regardless of manifest backup settings."
            },
            {
                "question": "Does SQLCipher introduce performance overhead in Room?",
                "answer": "Yes, page-level AES encryption/decryption introduces approximately 5-15% overhead on heavy read/write database transactions."
            }
        ]
    },
    {
        "id": "SEC-24",
        "arabic_explanation": (
            "كيف يمكن تحليل الكود المكتوب بلغة C/C++ و JNI وهندسته عكسياً، وما هي حدود الاعتماد عليه كدرع أمني؟\n\n"
            "1. الوهم الشائع حول الـ Native Code (C/C++ via NDK):\n"
            "   - يعتقد الكثير من المطورين أن كتابة منطق التشفير أو إخفاء الـ API Keys داخل مكتبة `.so` عبر JNI يجعل الكود مستحيل الكسر لأنها ملفات Binary مترجمة وليس Dalvik Bytecode.\n   - **الحقيقة الصادمة**: مكتبات الـ `.so` يتم تحليلها وفك تجميعها بسهولة فائقة باستخدام أدوات التحليل الثنائي المتقدمة مثل **Ghidra**, **IDA Pro**, و **Binary Ninja**!\n\n"
            "2. كيف يتم تحليل كود JNI عكسياً؟\n   - **Static Disassembly**: فتح ملف `libnative.so` في Ghidra. تظهر دوال JNI المصدرة بالاسم الصريح فوراً (مثل `Java_com_example_Security_getApiKey`)، ويقوم الـ Decompiler بإعادة بناء كود C شبه أصلي بدقة متناهية!\n   - **استخراج النصوص عبر Strings**: أي API Key مكتوب كنص في كود C++ يُخزن في الـ `.rodata` section ويمكن استخراجه بأمر سطر واحد: `strings libnative.so`.\n   - **Dynamic Hooking عبر Frida**: يمكن لـ Frida اعتراض دوال الـ Native بسهولة عبر `Interceptor.attach(Module.findExportByName('libnative.so', 'decryptPayload'), ...)` وقراءة المدخلات والمخرجات في الـ Registers.\n\n"
            "3. أساليب تصعيب التحليل وحدودها:\n   - **Strip Symbols**: حذف أسماء الدوال ومعلومات الـ Debug عبر `strip --strip-all`.\n   - **JNI Dynamic Registration**: تسجيل الدوال ديناميكياً عبر `JNI_OnLoad` و `env->RegisterNatives` بدلاً من التصدير التقليدي لإخفاء أسماء الدوال.\n   - **LLVM Obfuscation (OLLVM)**: تشويش مسارات التنفيذ (Control Flow Flattening).\n   - **الخلاصة**: الـ Native Code يرفع تكلفة التحليل العكسي مقارنة بالـ Bytecode، ولكنه **لا يحمي الأسرار** ولا يعوض غياب الأمان السيرفري."
        ),
        "practical_walkthrough": (
            "تسجيل دوال JNI ديناميكياً عبر JNI_OnLoad وتجنب كتابة الأسرار كنصوص صريحة:\n"
            "```cpp\n"
            "// ❌ أسلوب بدائي مكشوف: تصدير الدالة بالاسم الصريح وحفظ السر كنص ثابت:\n"
            "// يمكن قراءة النص بـ strings أو العثور على الدالة فوراً في Ghidra:\n"
            "JNIEXPORT jstring JNICALL\n"
            "Java_com_example_Legacy_getSecretApiKey(JNIEnv *env, jobject thiz) {\n"
            "    return env->NewStringUTF(\"AIzaSyD-SecretApiKey1234567890\"); // مكشوف في .rodata section!\n"
            "}\n"
            "\n"
            "// ✅ أسلوب متقدم: التسجيل الديناميكي وإخفاء الأسماء مع حذف الـ Symbols:\n"
            "static jbyteArray calculateChecksumNative(JNIEnv *env, jobject thiz, jbyteArray input) {\n"
            "    // تنفيذ خوارزمية فحص سلامة بدون تخزين أسرار ثابتة\n"
            "    return input; \n"
            "}\n"
            "\n"
            "static const JNINativeMethod methods[] = {\n"
            "    {\"calculateChecksum\", \"([B)[B\", (void*)calculateChecksumNative}\n"
            "};\n"
            "\n"
            "JNIEXPORT jint JNI_OnLoad(JavaVM *vm, void *reserved) {\n"
            "    JNIEnv *env = nullptr;\n"
            "    if (vm->GetEnv((void**)&env, JNI_VERSION_1_6) != JNI_OK) return JNI_ERR;\n"
            "    \n"
            "    jclass clazz = env->FindClass(\"com/example/SecureNativeBridge\");\n"
            "    if (clazz == nullptr) return JNI_ERR;\n"
            "    \n"
            "    // تسجيل الدوال ديناميكياً لإخفاء الـ Function Export Names من جدول الـ Exports\n"
            "    if (env->RegisterNatives(clazz, methods, sizeof(methods)/sizeof(methods[0])) < 0) {\n"
            "        return JNI_ERR;\n"
            "    }\n"
            "    return JNI_VERSION_1_6;\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Native code in .so files is disassembled into readable C pseudocode using Ghidra or IDA Pro, strings in .rodata are extractable via strings CLI, and runtime calls are hooked using Frida's Interceptor. Dynamic JNI registration and symbol stripping raise reverse engineering costs, but native code cannot guarantee secret confidentiality.",
        "best_answer": (
            "Compiling security logic into C/C++ `.so` files using the Android NDK raises reverse engineering difficulty compared to DEX bytecode, but does not provide confidentiality:\n\n"
            "1. **Static Analysis of ELF Binaries**: Reverse engineers analyze shared libraries using disassemblers like Ghidra, IDA Pro, and Binary Ninja. String constants reside in the `.rodata` segment, readable instantly via the `strings` utility. Standard exported JNI functions (`Java_com_example_...`) are mapped directly in the ELF export table, providing clear starting points for decompilation.\n\n"
            "2. **Dynamic Instrumentation with Frida**: Frida attaches directly to native memory address spaces via `Interceptor.attach()`. Attackers hook exported functions or specific instruction offsets in memory, inspect CPU registers (`x0`, `x1` on ARM64), read decrypted payloads, and alter return values.\n\n"
            "3. **Hardening Techniques**:\n"
            "   - **Dynamic Registration**: Register native methods dynamically in `JNI_OnLoad` via `RegisterNatives()`. This prevents exposing explicit package-mangled function names in the dynamic symbol table.\n   - **Symbol Stripping**: Ensure `strip --strip-all` is configured in CMake/NDK build scripts to remove debugging symbols."
        ),
        "deep_answer": (
            "From an offensive security perspective, relying on native code for client security is classic security-through-obscurity:\n\n"
            "1. **Automated Decompilation Fidelity**: Modern decompilers reconstruct control flow graphs, loop structures, and type inferences for ARM64 ELF binaries with remarkable accuracy. While decompiled C is harder to read than decompiled Kotlin, an experienced analyst can locate cryptographic transformations and key derivations within hours.\n\n"
            "2. **Anti-Debugging & Ptrace Limitations**: Native libraries often attempt anti-debugging by invoking `ptrace(PTRACE_TRACEME, 0, 1, 0)` or monitoring `/proc/self/status` for `TracerPid`. However, dynamic instrumentation engines (e.g. Frida / Gum) do not rely on standard gdb `ptrace` mechanisms, bypassing these checks unless specialized kernel-level hooks are implemented.\n\n"
            "3. **Architectural Rule**: Use native C/C++ libraries for performance, cross-platform audio/graphics engines, or low-level cryptographic algorithm execution. Never use native code as an alleged secure vault for private API keys or unverified business decisions."
        ),
        "follow_ups": [
            {
                "question": "What is Control Flow Flattening in native code obfuscation?",
                "answer": "It breaks basic code blocks into cases within a massive switch statement controlled by a state variable, obscuring natural loop and conditional logic."
            },
            {
                "question": "Can Frida hook non-exported static C++ functions?",
                "answer": "Yes; by calculating the base address of the loaded module in memory and adding the static function's offset determined via Ghidra."
            }
        ]
    }
]


def update_sec_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in SEC_17_24:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions SEC-17 to SEC-24. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_sec_data()
