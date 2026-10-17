#!/usr/bin/env python3
"""
Elevation script for SEC questions: SEC-09 to SEC-16.
Topic: Android Security, Crypto & Fintech Threat Modeling (SEC)
Phase 3, Batch 2
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "أمان أندرويد والتشفير والنمذجة الأمنية لتطبيقات التكنولوجيا المالية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# SEC-09: What is obfuscation, and what are its limitations?
# ==========================================
DATA["SEC-09"] = {
    "concept_en": """Code obfuscation in the Android toolchain (powered primarily by R8 and legacy ProGuard) is a build-time compiler optimization process that shrinks code, strips unused classes and methods, and renames identifiers (classes, methods, fields) to short, non-descriptive tokens such as a, b, and c. Obfuscation increases the cognitive work factor required for a human adversary to understand disassembled bytecode during static reverse engineering. However, obfuscation is strictly an obstacle, not an encryption or confidentiality mechanism. R8 does not encrypt constant string literals, meaning API endpoints, hardcoded tokens, SQL queries, and error messages remain fully readable in plaintext. Furthermore, control flow structures (if conditions, loop branches, algorithm state machines) remain intact in Dalvik bytecode. Advanced control flow flattening, string encryption, and symbol virtualization require specialized third-party commercial tools like DexGuard. In standard Android builds, developers must maintain mapping files (mapping.txt) to de-obfuscate production crash stack traces and configure ProGuard keep rules (-keep) to prevent R8 from stripping classes accessed via reflection, serialization, or JNI boundaries.""",
    "walkthrough_en": """Configuring R8 ProGuard rules and verifying mapping preservation:
```proguard
# 1. Preserve data models accessed via reflection or JSON serialization (Moshi/Gson)
-keepclassmembers class * {
    @com.squareup.moshi.Json <fields>;
}

# 2. Preserve native JNI bridge methods from name renaming
-keepclasseswithmembernames class * {
    native <methods>;
}

# 3. Strip debug logging calls entirely from release bytecode for defense-in-depth
-assumenosideeffects class android.util.Log {
    public static boolean isLoggable(java.lang.String, int);
    public static int v(...);
    public static int d(...);
    public static int i(...);
}

# 4. Retain line numbers and source attributes for symbolicated crash reporting
-renamesourcefileattribute SourceFile
-keepattributes SourceFile,LineNumberTable
```""",
    "short_en": """Obfuscation renames classes and methods to short tokens and shrinks unused bytecode using R8, making decompiled code harder for humans to read. Its limitations are that it never encrypts string literals, leaves algorithmic control flow structures visible, and does not stop dynamic memory analysis or runtime debugging, serving only as a deterrent rather than true cryptographic protection.""",
    "structured_en": """Obfuscation through R8 transforms compiled bytecode to make static analysis more difficult while reducing the APK download footprint.
During the release build compilation pipeline, R8 renames semantic package names, class identifiers, and method signatures into meaningless characters like a, b, and c.
This renaming strips away descriptive context, slowing down adversaries who inspect decompiled code in tools like JADX.
However, obfuscation has critical limitations that must not be confused with security.
R8 does not encrypt string literals, so hardcoded URLs, cryptographic parameters, and SQL queries remain visible in cleartext.
The structural control flow of your algorithms remains unchanged, allowing attackers to trace application logic by following loops and branch conditions.
Furthermore, obfuscation does nothing to prevent dynamic runtime attacks; when code executes on a device, an attacker using memory dumpers or runtime hooking tools sees decoded objects regardless of renamed identifiers.
Engineering teams must maintain build mapping files to retrace crash logs and configure keep rules to protect reflection and serialization boundaries.""",
    "deep_senior_en": """From a systems perspective, treating standard R8 obfuscation as a security perimeter is a critical misunderstanding of binary compilation.
R8 is fundamentally a dead-code stripper and whole-program optimizer whose primary goal is binary compaction and execution efficiency, with identifier renaming acting merely as a useful side benefit.
Because Dalvik bytecode retains strict type safety and semantic instruction sequences, a decompiler reconstructs high-level control structures effortlessly.
An attacker reading an obfuscated banking app does not need original class names; they simply search for cross-references to standard Android framework APIs like OkHttpClient, Cipher, or BiometricPrompt.
Once an API anchor is identified, tracing backward reveals the entire payment workflow.
True code hardening requires commercial obfuscators that implement control-flow flattening, instruction substitution, native binary virtualization, and constant pool string encryption.
Operationally, obfuscation introduces significant production maintenance overhead.
Any component accessed reflectively, such as Moshi adapters or Room database schemas, breaks in release builds unless protected by explicit keep rules.
We integrate automated mapping file uploads to crash reporting services in our CI/CD pipelines and run automated UI tests against release builds with obfuscation enabled to detect reflection regressions prior to customer deployment.
Additionally, teams must verify that debug signature keys and test certificates are completely decoupled from production variants, ensuring that development artifacts cannot be mistaken for release builds.""",
    "meta_ar": {
        "id": "SEC-09",
        "questionAr": "ما هو الـ Obfuscation (التشويش البرمجي) عبر R8/ProGuard وما هي حدوده الأمنية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دور أداة R8 في ضغط وتشويش الأسماء، واستيعاب الحدود الفاصلة بين التشويش والتشفير الحقيقي، ومعرفة سبب بقاء النصوص الصريحة مكشوفة، وإدارة ملفات الـ Mapping وقواعد الـ Keep لحماية الـ Reflection.",
        "concept_ar": "التشويش البرمجي (Obfuscation) عبر R8 هو عملية تحسين وضغط وقت البناء تقوم بإزالة الكود غير المستخدم واستبدال أسماء الكلاسات والدوال بأسماء عشوائية قصيرة مثل a و b لزيادة صعوبة قراءة الكود المفكك. ولكنه لا يمثل تشفيراً للبيانات؛ فالنصوص الصريحة والروابط تظل مكشوفة تماماً، وتدفق العمليات والمنطق البرمجي يظل قابلاً للتتبع، ولا يمنع أدوات التتبع الديناميكي للذاكرة.",
        "walkthrough_ar": "قواعد ProGuard لحماية كلاسات الـ Reflection وحذف سجلات الـ Log في الإنتاج:\n```proguard\n# حماية موديلات البيانات المستخدمة مع Moshi/Gson من تغيير الأسماء:\n-keepclassmembers class * {\n    @com.squareup.moshi.Json <fields>;\n}\n# حماية دوال C++ NDK:\n-keepclasseswithmembernames class * {\n    native <methods>;\n}\n# حذف أوامر Log.d نهائياً من الـ Bytecode في حزم الإنتاج:\n-assumenosideeffects class android.util.Log {\n    public static int d(...);\n}\n```",
        "why_it_matters_ar": "الاعتماد على R8 كأداة أمان وهمية يؤدي لكشف خوارزميات العمل وتسريب النصوص، وتطبيقه الخاطئ يسبب انهيارات مفاجئة في حزم الإنتاج بسبب كسر دوال الـ Reflection.",
        "worked_example_ar": "استرجاع مسار الخطأ الحقيقي (De-obfuscation) باستخدام أداة retrace وملف mapping.txt:\n```bash\n# فك تشويش الـ StackTrace القادم من الإنتاج:\nretrace.sh mapping.txt obfuscated_trace.txt > deobfuscated_trace.txt\n```",
        "trade_offs_ar": "التشويش يقلل حجم التطبيق ويصعب الهندسة العكسية، لكنه يتطلب صيانة مستمرة لقواعد Keep Rules ويزيد من وقت البناء في الـ CI/CD ويجعل تتبع أخطاء الإنتاج معتمداً كلياً على ملفات الـ Mapping.",
        "failure_modes_ar": "عمل التطبيق بشكل ممتاز في Debug وانهياره فوراً في Release بسبب قيام R8 بحذف أو إعادة تسمية حقول JSON Parsing المستخدمة عبر Reflection، أو فقدان ملف mapping.txt للإصدار المنشور مما يجعل تتبع الانهيارات مستحيلاً.",
        "production_perspective_ar": "في التطبيقات المالية الكبرى، نعتبر R8 أداة لتقليص الحجم وليس لحماية الأسرار، ونرفع ملفات mapping.txt تلقائياً إلى Crashlytics عبر Gradle، ونجري اختبارات End-to-End على حزم Release المشوشة.",
        "how_to_answer_ar": "وضح أولاً أن R8 أداة تحسين وتقليص كود وليست أداة تشفير، واشرح كيف يعيد تسمية الرموز، ثم حدد حدوده بوضوح (بقاء النصوص، ثبات تدفق العمليات، سهولة التتبع الديناميكي)، واختم بقواعد Keep وملف mapping.txt.",
        "talking_points_ar": "أداة R8 وتقليص الكود، والتشويش الاسمي (Identifier Renaming)، وبقاء النصوص الصريحة في الـ Dex، وقواعد Keep Rules والـ Reflection، وملف mapping.txt لفك تشويش الـ StackTraces.",
        "follow_ups_ar": "- **المحاور:** \"كيف يكتشف المخترق منطق الكود إذا كانت كل الأسماء مشوشة بحروف مثل a و b؟\"\n  **المرشح:** \"يبحث عن استدعاءات واجهات أندرويد الثابتة التي لا يمكن تشويشها، مثل OkHttpClient أو Cipher، ويتتبع مسار البيانات انطلاقاً منها حتى يصل للمنطق البرمجي المطلوب.\"\n\n- **المحاور:** \"ما الفرق بين R8 والأدوات التجارية المتقدمة مثل DexGuard؟\"\n  **المرشح:** \"R8 يكتفي بتغيير الأسماء وحذف الكود، بينما الأدوات التجارية تشفر النصوص الصريحة، وتشتت تدفق التنفيذ (Control Flow Flattening)، وتتحقق من بيئة التشغيل ضد الروت والـ Hooking.\"",
        "self_check_ar": "هل أكدت أن التشويش ليس تشفيراً؟ هل ذكرت بقاء النصوص الصريحة مكشوفة؟ وهل شرحت ملف mapping.txt وقواعد keep؟",
        "references_ar": f"- [Shrink, obfuscate, and optimize your app](https://developer.android.com/build/shrink-code) — توثيق جوجل الرسمي لأداة R8 وتشويش الكود.\n- [Guardsquare ProGuard and DexGuard Comparison](https://www.guardsquare.com/dexguard) — الفروق المعمارية بين التشويش القياسي والحماية المتقدمة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "التشويش البرمجي عبر R8 هو عملية تحسين تقوم بتقليص حجم التطبيق وإعادة تسمية الكلاسات والدوال إلى أحرف عشوائية قصيرة، مما يجعل قراءة الكود المفكك شاقة على البشر. وتتمثل حدوده في أنه لا يشفر النصوص الصريحة نهائياً، ويترك تدفق المنطق البرمجي كما هو، ولا يحمي الذاكرة من أدوات التلصص الديناميكي أثناء التشغيل.",
        "best_answer_ar": "يهدف التشويش البرمجي عبر أداة R8 إلى تصعيب الهندسة العكسية الساكنة وتقليص حجم ملف الـ APK النهائي.\n\nيقوم R8 أثناء بناء النسخة النهائية بإزالة الأكواد غير المستخدمة واستبدال أسماء الحزم والكلاسات والدوال المعبرة بأسماء مجهولة ومختصرة مثل a و b. وهذا الإجراء يجرد الكود من سياقه التوضيحي ويعقد عمل المهاجم الذي يحلل الملفات عبر برامج التفكيك.\n\nومع ذلك، يمتلك التشويش حدوداً أمنية واضحة يجب عدم إغفالها؛ فهو لا يشفر النصوص الثابتة على الإطلاق، فتظل الروابط والاستعلامات ومفاتيح الواجهات مكشوفة كنصوص صريحة. كما أن الهيكل المنطقي للحلقات والشروط يظل سليماً، مما يسمح بتتبع الخوارزميات، بالإضافة إلى عجزه عن التصدي لأدوات مراقبة الذاكرة أثناء وقت التشغيل. ولذلك يتطلب تطبيق التشويش صيانة قواعد Keep بدقة لحماية دوال Reflection، وتخزين ملفات mapping.txt لفك تشويش تقارير الأخطاء في الإنتاج.",
        "deep_answer_ar": "من منظور النظم البرمجية، يعتبر التعامل مع تشويش R8 كدرع أمني حصين خطأ شائعاً؛ فـ R8 في جوهره أداة لضغط الكود وتحسين الأداء، بينما إعادة تسمية المتغيرات مجرد ميزة جانبية.\n\nولأن بايت كود Dalvik يحتفظ بصرامة الأنواع وتسلسل التعليمات، فإن أدوات التفكيك الحديثة مثل JADX تعيد بناء الشروط البرمجية بسهولة تامة. ولا يحتاج المهاجم لمعرفة الأسماء الأصلية للكلاسات؛ إذ يكفيه البحث عن الاستدعاءات الصريحة لواجهات أندرويد القياسية التي لا تتغير أسماؤها مثل OkHttpClient أو Cipher، ثم يتتبع تدفق البيانات للوصول إلى كود التحويلات المالية.\n\nأما الحماية الحقيقية فتتطلب أدوات تشويش تجارية تطبق تقنيات تشتيت مسار التنفيذ Control Flow Flattening وتشفير مصفوفات النصوص الثابتة في الـ DEX. ومن الناحية التشغيلية، يفرض التشويش عبئاً إضافياً على الفريق؛ إذ تنهار حزم الإنتاج إذا استُخدمت دوال تعتمد على الـ Reflection مثل Moshi دون وضع قواعد حماية صريحة عبر ملفات ProGuard.\n\nلذلك نلزم خطوط الإنتاج برفع ملفات mapping.txt تلقائياً لخوادم المراقبة مثل Crashlytics، ونجري اختبارات آلية شاملة على النسخ المشوشة قبل إطلاقها لضمان استقرار التطبيق وأمانه. كما نقوم بفصل شهادات التوقيع التجريبية عن شهادات الإنتاج لمنع استغلال الحزم الهندسية غير المشوشة في بيئات العمل الحقيقية."
    }
}

# ==========================================
# SEC-10: What is reverse engineering? What do root, hooking, and instrumentation change?
# ==========================================
DATA["SEC-10"] = {
    "concept_en": """Reverse engineering in Android is the analytical process of disassembling, decompiling, and inspecting an application binary to understand its internal architecture, business logic, data models, and cryptographic safeguards. It bifurcates into static analysis (inspecting Dalvik bytecode via JADX, decompressing resources via apktool, or analyzing native C/C++ libraries via Ghidra) and dynamic analysis (monitoring network traffic, inspecting runtime memory, and tracing execution). Root access fundamentally alters the security model by breaking Linux kernel UID isolation. A rooted user possesses Superuser (su) privileges, allowing them to access private app directories (/data/data), bypass file permissions, inspect SQLite databases, and attach kernel-level debuggers. Dynamic hooking and binary instrumentation (driven by frameworks like Frida, Xposed, and Magisk Zygisk) take exploitation further by intercepting method execution in memory, rewriting JVM method pointers, capturing plaintext arguments (such as passwords and encryption keys), and dynamically forging method return values (such as forcing an isJailbroken() check to always return false).""",
    "walkthrough_en": """Detecting dynamic hooking frameworks and anti-debugging tampering:
```kotlin
object RuntimeTamperDetector {
    // 1. Basic root detection checking su binaries and test-keys build tags
    fun isDeviceRooted(): Boolean {
        val buildTags = android.os.Build.TAGS
        if (buildTags != null && buildTags.contains("test-keys")) return true

        val suPaths = arrayOf(
            "/system/app/Superuser.apk", "/sbin/su", "/system/bin/su",
            "/system/xbin/su", "/data/local/xbin/su", "/data/local/bin/su"
        )
        return suPaths.any { File(it).exists() }
    }

    // 2. Check for active debugger attachment
    fun isDebuggerAttached(): Boolean =
        android.os.Debug.isDebuggerConnected() || android.os.Debug.waitingForDebugger()

    // 3. Detect Frida default listening ports or injected memory artifacts
    fun isFridaServerPresent(): Boolean {
        return try {
            val socket = java.net.Socket("127.0.0.1", 27042)
            socket.close()
            true // Frida server is running on default port!
        } catch (e: Exception) {
            false
        }
    }
}
```""",
    "short_en": """Reverse engineering decompiles and inspects an application's compiled bytecode and assets. Root access bypasses Android's Linux sandbox, allowing full access to private application storage and process memory. Dynamic hooking tools like Frida inject scripts into running processes to rewrite method logic, capture arguments from memory, and bypass client security checks at runtime.""",
    "structured_en": """Reverse engineering encompasses the techniques used to understand an application's internal implementation from its distributed APK package.
Static reverse engineering uses tools like JADX and apktool to decompile compiled Dalvik DEX files back into readable Kotlin and Java source code, exposing layout structures and application logic.
Gaining root access on a device completely transforms the threat landscape by overriding the operating system's security controls.
With root privileges, an attacker circumvents Linux UID isolation, gaining unrestricted read and write access to private app storage, local databases, and shared preferences.
Dynamic instrumentation and hooking introduce the most severe threat through tools like Frida and Xposed.
These frameworks inject code directly into the running application process memory, hooking internal functions in real time.
An adversary can intercept arguments passed into cryptographic methods, extract plaintext passwords before encryption, or modify return values to bypass local security checks like fingerprint validation or root detection.
Client checks alone cannot defend against instrumentation, requiring backend verification and attestation.""",
    "deep_senior_en": """In modern threat modeling, we assume that any motivated adversary can decompile our client binary and run it inside a fully instrumented, rooted environment.
Static decompilation reconstructs architectural wiring, network endpoints, and data contracts with remarkable fidelity.
Root access strips away the platform sandbox; the adversary can attach ptrace, inspect raw memory addresses via /proc/self/mem, and extract local encryption databases directly from app-private directories.
However, dynamic binary instrumentation represents the ultimate adversary weapon against client-only defenses.
Frameworks like Frida inject a JavaScript engine into the target process and alter the Dalvik or ART virtual machine function dispatch tables.
This makes client-side security checks trivially bypassable.
If an app includes an isDeviceRooted() function, a four-line Frida script intercepts that method call and forces it to return false, completely neutralizing the check.
Similarly, SSL pinning checks can be hooked and silenced within milliseconds.
Therefore, a senior architecture never places trust in client-side self-assertions.
We deploy defense-in-depth through the Play Integrity API, which relies on hardware-backed cryptographic attestation where Google Play servers verify the bootloader state, system image integrity, and package signature.
The mobile app receives an encrypted attestation token and transmits it to our enterprise backend, where the server validates the verdict before granting access to sensitive financial APIs.""",
    "meta_ar": {
        "id": "SEC-10",
        "questionAr": "ما هي الهندسة العكسية (Reverse Engineering) لتطبيقات أندرويد؟ وما الذي يغيره وجود Root والـ Hooking؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التمييز بين التحليل الساكن والديناميكي، وفهم كيفية انهيار عزل النظام بوجود الـ Root، واستيعاب عمل أدوات الـ Hooking مثل Frida في تعديل الذاكرة، وضرورة الاعتماد على السيرفر و Play Integrity بدلاً من الفحوصات المحلية الساذجة.",
        "concept_ar": "الهندسة العكسية هي تفكيك وتحليل حزمة الـ APK لفهم منطق التطبيق وبنيته، وتنقسم إلى تحليل ساكن بفحص الكود عبر JADX، وتحليل ديناميكي بمراقبة الذاكرة أثناء التشغيل. يكسر الـ Root عزل ملفات التطبيق في نواة لينكس، بينما تتيح أدوات الـ Hooking مثل Frida حقن كود برمجي داخل الذاكرة أثناء التشغيل للتلاعب بقيم الدوال وتجاوز الفحوصات الأمنية وسرقة المفاتيح من الرام.",
        "walkthrough_ar": "فحص الروت والـ Hooking في الكود البرمجي وكيف يسهل تجاوزه عبر Frida:\n```kotlin\n// فحص أمني محلي ساذج للروت:\nfun checkSecurity(): Boolean = !isDeviceRooted() && !isFridaRunning()\n```\nتجاوز الفحص تماماً بسطرين عبر Frida في الرام:\n```javascript\nJava.perform(function() {\n    Java.use(\"com.bank.RuntimeTamperDetector\").checkSecurity.implementation = function() {\n        console.log(\"[!] Root/Frida check bypassed!\");\n        return true; // إجبار الدالة على إرجاع نجاح دائماً\n    };\n});\n```",
        "why_it_matters_ar": "فهم قدرات الهندسة العكسية يمنع بناء تطبيقات تعتمد على أمان العميل الوهمي، ويوجه المهندس لبناء منظومة تحقق مركزية في السيرفر لمنع تزوير العمليات المصرفية.",
        "worked_example_ar": "استخدام Play Integrity للتحقق من سلامة الجهاز في السيرفر (Hardware Attestation):\n```kotlin\nval integrityManager = PlayIntegrity.getIntegrityManager(context)\nintegrityManager.requestIntegrityToken(IntegrityTokenRequest.builder().setNonce(serverNonce).build())\n    .addOnSuccessListener { response ->\n        // إرسال response.token() للسيرفر ليتحقق هو عبر خوادم جوجل من سلامة الجهاز\n        api.verifyDeviceWithGoogle(response.token())\n    }\n```",
        "trade_offs_ar": "إضافة فحوصات كشف الروت والـ Hooking تصعب مهمة الهواة لكنها قد تسبب إزعاجاً للمستخدمين العاديين، كما أنها لا تمنع المحترفين، بينما التحقق السحابي عبر Play Integrity يوفر أماناً حقيقياً بتكلفة ربط مع خوادم جوجل.",
        "failure_modes_ar": "الاعتماد على دالة محلية مثل `if (isRooted()) exitProcess()` في العميل؛ إذ يتم تعطيلها في ثوانٍ عبر Frida، أو الاعتماد على تشفير محلي يمكن التقاط مفاتيحه من الرام لحظة استخدامه.",
        "production_perspective_ar": "في البنوك العالمية، نستخدم طبقات حماية متدرجة تشمل كشف الـ Debugger والروت للتصدي للهجمات البسيطة، لكننا نبني القرار الأمني الفعلي في السيرفر عبر التحقق من توكن Play Integrity الموثق عتادياً.",
        "how_to_answer_ar": "عرف الهندسة العكسية بنوعيها (ساكنة وديناميكية)، واشرح كيف يكسر الروت عزل الـ UID، ثم وضح خطورة أدوات الـ Hooking مثل Frida في تعديل الدوال في الرام، واختم بحتمية بناء الثقة في السيرفر عبر Play Integrity.",
        "talking_points_ar": "التحليل الساكن عبر JADX، وأدوات apktool و Ghidra، وتخطي عزل Linux بوجود الـ Root، وأدوات Frida و Xposed وتعديل الذاكرة، وخدمة Play Integrity ومصادقة السيرفر.",
        "follow_ups_ar": "- **المحاور:** \"إذا كان بإمكان Frida كسر أي فحص محلي، فلماذا نكتب كود لكشف الروت في التطبيق أصلاً؟\"\n  **المرشح:** \"نكتبه كجزء من الدفاع في العمق لرفع كلفة الهجوم على المخترقين المبتدئين والأدوات التلقائية، مع إدراكنا التام بأنه لا يغني عن تحقق السيرفر.\"\n\n- **المحاور:** \"كيف يمنع Play Integrity التلاعب الذي تقوم به أداة Frida؟\"\n  **المرشح:** \"لأن التوكن يُولد ويُوقع بتشفير عتادي من خدمات جوجل بلاي، ويتم فك تشفيره والتحقق منه داخل سيرفر البنك وليس داخل هاتف المستخدم.\"",
        "self_check_ar": "هل شرحت الفرق بين التحليل الساكن والديناميكي؟ هل وضحت كيف تعمل أداة Frida؟ وهل أكدت على أن القرار الأمني يجب أن يكون في السيرفر؟",
        "references_ar": f"- [OWASP Mobile Application Security (MAS)](https://mas.owasp.org/) — المعيار العالمي الشامل لاختبارات أمان تطبيقات الموبايل والهندسة العكسية.\n- [Frida Framework Official Documentation](https://frida.re/docs/home/) — التوثيق الرسمي لأداة التلصص والاعتراض الديناميكي في الذاكرة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "الهندسة العكسية هي عملية تفكيك التطبيق لتحليل كوده ومنطقه الداخلي عبر أدوات التفكيك الساكن مثل JADX. ويقوم الروت بكسر نظام العزل الأمني في أندرويد ليتيح الوصول لكافة الملفات وقواعد البيانات الخاصة، بينما تقوم أدوات الـ Hooking مثل Frida بحقن كود في الذاكرة أثناء التشغيل لتعديل نتائج الدوال وسرقة البيانات الحساسة مباشرة من الرام.",
        "best_answer_ar": "تمثل الهندسة العكسية مساراً منهجياً يتبعه المهاجمون لفهم بنية التطبيق واكتشاف ثغراته، وتنقسم إلى شقين رئيسيين.\n\nالشق الأول هو التحليل الساكن؛ حيث تُستخدم أدوات مثل JADX و apktool لتفكيك ملفات الـ DEX واسترجاع الأكواد البرمجية والموارد والواجهات بدقة عالية. وعندما يمتلك المستخدم صلاحيات الـ Root على الهاتف، يتغير المشهد الأمني جذرياً؛ إذ تسقط حدود العزل الأمني بين التطبيقات، ويصبح بمقدور المهاجم قراءة ملفات التطبيق الخاصة في مجلد data وقراءة قواعد بيانات SQLite غير المشفرة والتنصت على العمليات.\n\nأما الشق الأكثر خطورة فهو التحليل الديناميكي عبر أدوات الـ Hooking مثل Frida؛ حيث يقوم المهاجم بربط عمليته بالتطبيق أثناء تشغيله وحقن تعليمات برمجية في ذاكرة الرام. وتتيح هذه الأدوات تعديل نواتج الدوال في أجزاء من الثانية؛ كأن تجعل فحص البصمة أو فحص الروت يرجع نجاحاً دائماً، أو تلتقط كلمات المرور قبل تشفيرها. ولذلك لا يمكن الاعتماد على حماية العميل فقط، ويجب نقل القرارات الأمنية الحساسة إلى السيرفر.",
        "deep_answer_ar": "في النمذجة الأمنية المتقدمة للتطبيقات المالية، نفترض دائماً كقاعدة معمارية أن العميل يعمل في بيئة معادية ومخترقة بالكامل بواسطة أدوات الهندسة العكسية.\n\nيتيح التحليل الساكن للمهاجم قراءة العقود الشبكية وأسماء الـ Endpoints ونماذج البيانات بدقة تقارب قراءة الكود المصدري الأصلي. ومع وجود صلاحيات Root، تسقط حماية نواة لينكس وتفقد آليات العزل عبر الـ UID قيمتها؛ حيث يستطيع المهاجم استخدام أداة ptrace والاطلاع على قطاعات الذاكرة من خلال proc/self/mem وسحب الملفات المحفوظة محلياً.\n\nومع ذلك، تظل أدوات Dynamic Binary Instrumentation مثل Frida السلاح الأخطر في ترسانة المهاجمين؛ حيث تحقن محرك جافا سكريبت داخل عملية التطبيق وتعدل جداول توجيه الدوال في الـ ART Virtual Machine في الذاكرة الحية. هذا يعني أن أي فحص أمني محلي مثل دالة isDeviceRooted أو فحص شهادة الـ SSL يمكن تجاوزه بسكريبت بسيط من سطرين يجبر الدالة على إرجاع القيمة المطلوبة دون لمس الملفات على القرص.\n\nبناءً على ذلك، يدرك المهندس السينيور أن الفحوصات الأمنية داخل تطبيق الموبايل تمثل فقط خطاً دفاعياً أولياً لتأخير الهواة، بينما تبنى الثقة الحقيقية عبر معايير التوثيق العتادي مثل Play Integrity API. في هذه المعمارية، تطلب خدمات جوجل توكناً موقعاً عتادياً من معالج الهاتف الآمن، ويقوم السيرفر الخلفي للبيمينت بفحص التوكن للتأكد من سلامة نظام التشغيل وحزمة التطبيق قبل التصريح بأي معاملة مالية."
    }
}

# ==========================================
# SEC-11: How do you implement Keystore-backed encryption for small app secrets?
# ==========================================
DATA["SEC-11"] = {
    "concept_en": """Implementing robust Keystore-backed encryption for small application secrets (such as session tokens, user PINs, or biometric tokens) requires using Authenticated Encryption with Associated Data (AEAD), specifically the AES-256-GCM cipher suite. An AES key is generated directly inside the AndroidKeyStore provider using KeyGenParameterSpec, configured with PURPOSE_ENCRYPT and PURPOSE_DECRYPT, BLOCK_MODE_GCM, and ENCRYPTION_PADDING_NONE. A critical cryptographic invariant in AES-GCM is the Initialization Vector (IV) / Nonce uniqueness: reusing the same IV with the same encryption key completely breaks confidentiality and allows mathematical forgery of the authentication tag. Therefore, the Cipher instance must generate a fresh, cryptographically random 12-byte IV for every single encryption operation. The resulting ciphertext and the unique IV must be stored together (typically prepending the IV bytes to the ciphertext bytes or encoding both into a composite envelope) in persistent local storage like SharedPreferences or Jetpack DataStore. During decryption, the exact IV is extracted and passed via GCMParameterSpec to reconstruct the original plaintext.""",
    "walkthrough_en": """Implementing production-grade AES-GCM Keystore encryption and decryption:
```kotlin
class KeystoreSecretVault(private val context: Context) {
    private val keyAlias = "app_secret_aes_key"
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

    init {
        if (!keyStore.containsAlias(keyAlias)) {
            val keyGenerator = KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                "AndroidKeyStore"
            )
            val spec = KeyGenParameterSpec.Builder(
                keyAlias,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            ).run {
                setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                setKeySize(256)
                setRandomizedEncryptionRequired(true) // Enforces fresh IV generation
                build()
            }
            keyGenerator.init(spec)
            keyGenerator.generateKey()
        }
    }

    fun encrypt(plaintext: ByteArray): ByteArray {
        val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)
        val iv = cipher.iv // 12-byte random IV automatically generated by provider
        val ciphertext = cipher.doFinal(plaintext)
        
        // Prepend 12-byte IV to ciphertext: [IV (12 bytes)] + [Ciphertext + Tag]
        return ByteBuffer.allocate(iv.size + ciphertext.size)
            .put(iv)
            .put(ciphertext)
            .array()
    }

    fun decrypt(encryptedPayload: ByteArray): ByteArray {
        val byteBuffer = ByteBuffer.wrap(encryptedPayload)
        val iv = ByteArray(12).also { byteBuffer.get(it) }
        val ciphertext = ByteArray(byteBuffer.remaining()).also { byteBuffer.get(it) }

        val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, secretKey, GCMParameterSpec(128, iv))
        return cipher.doFinal(ciphertext)
    }
}
```""",
    "short_en": """We implement Keystore encryption for small app secrets using AES-256 in GCM block mode without padding. The secret key is generated directly inside AndroidKeystore so private bytes remain non-exportable. Each encryption generates a fresh twelve-byte initialization vector that is stored alongside the ciphertext, providing authenticated encryption that guarantees both data confidentiality and tamper detection.""",
    "structured_en": """Securing small application secrets on Android requires hardware-rooted authenticated encryption rather than legacy unauthenticated algorithms.
We initialize a 256-bit AES key using KeyGenParameterSpec within the AndroidKeyStore provider, configuring it specifically for GCM block mode and no padding.
Storing the key in AndroidKeystore ensures that the raw symmetric key material cannot be extracted by user-space processes or rooted device inspectors.
For the encryption operation, the platform requires a unique Initialization Vector for every single payload.
Reusing an IV under the same AES-GCM key destroys the cryptographic security of the authentication tag, potentially leaking plaintext.
To prevent this, the cipher generates a cryptographically random twelve-byte IV on each call.
We package the output by prepending the twelve-byte IV directly to the ciphertext and authentication tag, saving the combined byte array in SharedPreferences or DataStore.
When decrypting, we parse the first twelve bytes as the IV, configure a GCMParameterSpec with a 128-bit authentication tag length, and execute the cipher to verify integrity and retrieve the plaintext.""",
    "deep_senior_en": """When building enterprise-grade cryptographic modules in Android, correctness lies in adherence to cryptographic invariants and lifecycle awareness.
The gold standard for symmetric encryption on mobile is AES-256-GCM because it provides Authenticated Encryption with Associated Data (AEAD).
Unlike legacy modes like CBC which require a separate HMAC to detect tampering, GCM computes a 128-bit authentication tag simultaneously with ciphertext generation.
If a single bit in the stored ciphertext is modified by an attacker, the doFinal call throws an AEADBadTagException, preventing padding oracle exploits.
The most critical engineering rule in AES-GCM is nonce uniqueness.
If the same key and IV pair are ever used to encrypt two different plaintexts, the Galois field mathematics collapse, exposing both plaintexts and enabling signature forgeries.
By setting setRandomizedEncryptionRequired to true in KeyGenParameterSpec, AndroidKeystore strictly forbids manual IV initialization in encrypt mode, guaranteeing that the platform provider injects a cryptographically secure random IV from hardware entropy.
Furthermore, we must design for operational key lifecycles.
Android Keystore keys are bound to the hardware and will be permanently lost if an app is uninstalled or if lockscreen credentials are reset when setUserAuthenticationRequired is enabled.
For small secrets like session tokens, losing the key simply prompts the user to log in again.
However, if encrypting irreplaceable user documents, we must implement multi-layer envelope encryption where the data key is wrapped by a Keystore master key and recovery keys are securely escrowed.""",
    "meta_ar": {
        "id": "SEC-11",
        "questionAr": "كيف تنفذ تشفيراً مدعوماً بـ Keystore لحفظ أسرار التطبيق الصغيرة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على كتابة كود تشفير صحيح باستخدام AES-256 GCM في Android Keystore، وفهم خطورة إعادة استخدام الـ IV/Nonce، وكيفية دمج الـ IV مع النص المشفر، والتعامل مع استثناءات التلاعب بالبيانات مثل AEADBadTagException.",
        "concept_ar": "تنفيذ التشفير الآمن لأسرار التطبيق الصغيرة (مثل التوكنز والـ PIN) يعتمد على استخدام خوارزمية AES-256 بنمط GCM التوثيقي (AEAD) عبر مفتاح سري مولد ومحفوظ داخل AndroidKeystore. وتكمن القاعدة الصارمة في عدم تكرار الـ Initialization Vector (IV) نهائياً مع نفس المفتاح؛ حيث يولد الـ Cipher قيمة IV عشوائية بحجم 12 بايت لكل عملية، وتُحفظ هذه القيمة مدمجة مع النص المشفر والـ Tag في SharedPreferences أو DataStore لاستخدامها عند فك التشفير.",
        "walkthrough_ar": "كود إنتاجي لتوليد المفتاح وتشفير البيانات بـ AES-GCM وحفظ الـ IV مدمجاً مع الناتج:\n```kotlin\nval cipher = Cipher.getInstance(\"AES/GCM/NoPadding\").apply {\n    init(Cipher.ENCRYPT_MODE, secretKeyFromKeystore)\n}\nval iv = cipher.iv // 12 بايت عشوائية من العتاد\nval ciphertext = cipher.doFinal(plaintext)\n// دمج الـ IV في بداية مصفوفة البايتات لحفظها:\nval payload = ByteBuffer.allocate(iv.size + ciphertext.size).put(iv).put(ciphertext).array()\n```",
        "why_it_matters_ar": "التنفيذ الخاطئ للتشفير كإعادة استخدام الـ IV أو استخدام أنماط غير موثقة مثل AES-ECB يعرض البيانات للكسر السهل ويفقد التشفير قيمته تماماً في حماية أسرار المستخدم.",
        "worked_example_ar": "فك التشفير الآمن واستخراج الـ IV واكتشاف التلاعب بالبيانات:\n```kotlin\nfun decryptSecret(payload: ByteArray, key: SecretKey): ByteArray {\n    val buffer = ByteBuffer.wrap(payload)\n    val iv = ByteArray(12).also { buffer.get(it) }\n    val ciphertext = ByteArray(buffer.remaining()).also { buffer.get(it) }\n    return Cipher.getInstance(\"AES/GCM/NoPadding\").run {\n        init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, iv))\n        doFinal(ciphertext) // يرمي AEADBadTagException إذا تم التلاعب بالبيانات\n    }\n}\n```",
        "trade_offs_ar": "نمط AES-GCM يوفر السرية والنزاهة معاً ويدعمه العتاد بكفاءة، لكنه يفرض إدارة دقيقة لقيم الـ IV ومساحة تخزين إضافية (12 بايت للـ IV و 16 بايت للـ Tag).",
        "failure_modes_ar": "إعادة استخدام نفس الـ IV الثابت في كل عملية تشفير مما يكسر أمان خوارزمية GCM تماماً، أو تجاهل استثناء AEADBadTagException الناتج عن تلاعب خبيث بالبيانات المخزنة.",
        "production_perspective_ar": "في التطبيقات المالية، نستخدم خوارزمية AES-GCM للأسرار الصغيرة عبر مكتبة Tink أو كود Keystore مخصص، مع فرض `setRandomizedEncryptionRequired(true)` لمنع إدخال IV يدوي خاطئ.",
        "how_to_answer_ar": "ابدأ باختيار الخوارزمية المعيارية AES-256 GCM وعلل اختيارها كـ AEAD، ثم اشرح توليد المفتاح داخل Keystore، وركز بشدة على أهمية توليد IV عشوائي جديد لكل عملية ودمجه مع النص المشفر، واختم بآلية فك التشفير.",
        "talking_points_ar": "نمط AES-256 GCM وخاصية AEAD، وتوليد المفاتيح في AndroidKeyStore، وخطورة تكرار الـ IV/Nonce، ومواصفات GCMParameterSpec، واستثناء AEADBadTagException.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لو قمت بإعادة استخدام نفس الـ IV مع نفس المفتاح في نمط AES-GCM؟\"\n  **المرشح:** \"تنهار المعادلة الرياضية لنظام Galois Field، مما يسمح للمهاجم باستخراج النصوص الأصلية وتزييف الـ Authentication Tag وتمرير بيانات معدلة بنجاح.\"\n\n- **المحاور:** \"أين نحفظ الـ IV وهل يحتاج إلى تشفير؟\"\n  **المرشح:** \"الـ IV ليس سراً بل قيمة عشوائية تضمن عدم التشابه، ولا يحتاج لتشفير ويُحفظ عادة كنص صريح مدمج في أول 12 بايت من الملف المشفر.\"",
        "self_check_ar": "هل حددت AES-GCM NoPadding؟ هل شددت على عدم تكرار الـ IV؟ وهل شرحت دمج الـ IV مع النص المشفر وفكه؟",
        "references_ar": f"- [NIST Special Publication 800-38D (GCM Mode)](https://csrc.nist.gov/publications/detail/sp/800-38d/final) — المعيار الرسمي لخوارزمية وتطبيق نمط التشفير Galois/Counter Mode.\n- [Android Cryptography - SecretKey Generation](https://developer.android.com/privacy-and-security/cryptography) — التوثيق الرسمي لتوليد مفاتيح التشفير المتماثلة في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "ننفذ التشفير المدعوم بـ Keystore للأسرار الصغيرة باستخدام خوارزمية AES-256 بنمط GCM دون حشو. نولد المفتاح السري داخل AndroidKeyStore لضمان عدم خروجه للذاكرة، ويقوم التشفير بتوليد قيمة IV عشوائية بحجم 12 بايت في كل مرة لتفادي تكرارها، ثم ندمج هذه القيمة في بداية النص المشفر ونحفظهما معاً في التخزين المحلي لاستخدامها عند فك التشفير والتحقق من النزاهة.",
        "best_answer_ar": "التنفيذ الآمن والمطابق للمعايير لحفظ الأسرار الصغيرة مثل التوكنز والرموز السرية يعتمد على التشفير المتماثل الموثق AES-256-GCM داخل نظام Android Keystore.\n\nنبدأ بتوليد مفتاح سري 256 بت باستخدام KeyGenParameterSpec مع تحديد وضعية التشفير وفك التشفير ونمط GCM مع NoPadding وحفظه في مزود AndroidKeyStore. هذا يضمن بقاء المفتاح محمياً في عتاد الجهاز وعدم قدرة أي عملية على استخراجه.\n\nوفي مرحلة التشفير، تفرض الخوارزمية قاعدة ذهبية وهي عدم تكرار الـ Initialization Vector مع نفس المفتاح مطلقاً؛ لأن تكراره يدمر الأمان الرياضي للـ Tag التوثيقي. ولذلك نترك للـ Cipher مهمة توليد IV عشوائي فريد بحجم 12 بايت في كل عملية تشفير. نأخذ مصفوفة البايتات الناتجة وندمج الـ IV في بدايتها متبوعاً بالنص المشفر والـ Tag، ونحفظ هذا الدمج في DataStore. وعند فك التشفير، نستخرج أول 12 بايت كـ IV ونمررها لـ GCMParameterSpec بـ Tag 128 بت لفك التشفير والتأكد الفوري من عدم التلاعب بالبيانات.",
        "deep_answer_ar": "في تصميم المكونات التشفيرية المتقدمة لتطبيقات التكنولوجيا المالية، تكمن الدقة الهندسية في احترام القواعد الرياضية وإدارة دورة حياة المفاتيح.\n\nنعتمد معيار AES-256-GCM كخيار افتراضي لأنه يقدم ميزة Authenticated Encryption with Associated Data؛ فهو لا يكتفي بإخفاء سرية البيانات، بل يولد بصمة مصادقة بحجم 128 بت تكشف أي تلاعب. فإذا قام مهاجم بتعديل بايت واحد في التخزين، تفشل عملية فك التشفير وترمي استثناء AEADBadTagException فوراً، مما يقطع الطريق على هجمات التلاعب وتعديل القيم.\n\nوالنقطة المعمارية الحاسمة هي إدارة الـ Nonce أو الـ IV؛ فإعادة استخدام نفس الـ IV مع نفس المفتاح مرتين يكسر معادلات Galois Field الرياضية، مما يسمح للمهاجم باسترجاع النصوص الصريحة بدون معرفة المفتاح. ولحماية التطبيق من هذا الخطأ البرمجي، نفعل خيار setRandomizedEncryptionRequired في KeyGenParameterSpec، مما يجبر مكتبة التشفير على رفض أي IV يدوي والاعتماد الحصري على مولد العشوائية العتادي في النظام.\n\nأما من ناحية دورة الحياة، فيجب أن ندرك أن مفاتيح Keystore مرتبطة بالعتاد وتفقد صلاحيتها عند قيام المستخدم بإلغاء قفل الشاشة أو تغيير البصمات إذا كانت مقيدة بـ Biometrics. وبالنسبة للأسرار المؤقتة كرموز الجلسة، فإن فقدان المفتاح أمر مقبول ويُعالج ببساطة بإعادة توجيه المستخدم لتسجيل الدخول، بينما تشفير البيانات الدائمة يتطلب معمارية تشفير مغلف Envelope Encryption بمفاتيح استرجاع آمنة."
    }
}

# ==========================================
# SEC-12: What should you know about the deprecated EncryptedSharedPreferences API?
# ==========================================
DATA["SEC-12"] = {
    "concept_en": """The EncryptedSharedPreferences API (part of the androidx.security:security-crypto Jetpack library) was originally introduced to provide seamless, drop-in encrypted key-value storage backed by the Google Tink cryptographic library and Android Keystore master keys. In recent library revisions, EncryptedSharedPreferences has been formally deprecated by Google. The deprecation stems from severe underlying architectural deficiencies and edge-case reliability failures across the heterogeneous Android device ecosystem. The implementation relied on XML file parsing wrapped with cryptographic streaming ciphers, causing significant main-thread I/O latency, Application Not Responding (ANR) spikes, and deadlocks in multi-threaded environments. Furthermore, low-tier devices and specific OEM hardware variants (notably older Samsung and Huawei devices) suffered from catastrophic KeyStore corruption, throwing unrecoverable KeyStoreException, NullPointerException, or corrupted master key states that permanently locked users out of their encrypted data. The modern migration path involves adopting Jetpack DataStore (Preferences or Proto DataStore) combined with Google Tink directly, or building isolated Keystore AES-GCM serializers that decouple disk I/O from cryptographic operations.""",
    "walkthrough_en": """Safe migration pattern from deprecated EncryptedSharedPreferences to Jetpack DataStore:
```kotlin
// 1. Handling legacy EncryptedSharedPreferences corruption gracefully
class LegacyMigrationHelper(private val context: Context) {
    fun extractLegacyTokenOrNull(): String? {
        return try {
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
            val legacyPrefs = EncryptedSharedPreferences.create(
                context,
                "secure_prefs",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
            legacyPrefs.getString("auth_token", null)
        } catch (e: Exception) {
            // Catches Keystore corruption, OEM crypto bugs, or broken master keys
            null
        }
    }

    fun wipeCorruptedLegacyPrefs() {
        try {
            context.getSharedPreferences("secure_prefs", Context.MODE_PRIVATE)
                .edit().clear().commit()
        } catch (ignored: Exception) {}
    }
}

// 2. Modern recommendation: Jetpack DataStore with direct Tink / Keystore encryption
// DataStore provides non-blocking coroutine-based async I/O on Dispatchers.IO
```""",
    "short_en": """Google deprecated EncryptedSharedPreferences due to serious architectural flaws, including main-thread I/O performance bottlenecks, multi-threading deadlocks, and frequent Keystore corruption crashes on OEM devices. Production applications are migrating to Jetpack DataStore combined with Google Tink or custom Keystore AES-GCM wrappers, executing asynchronous encrypted persistence safely off the main thread.""",
    "structured_en": """While EncryptedSharedPreferences offered an easy API for securing key-value storage, Google formally deprecated it due to widespread production reliability issues.
The library wrapped traditional SharedPreferences XML files with Google Tink encryption keys anchored to an Android Keystore master key.
In production, this design created severe performance problems because SharedPreferences operations are synchronous, causing disk I/O and cryptographic computation to block the main thread and trigger ANR spikes.
More critically, the library suffered from catastrophic hardware-keystore failures on specific OEM hardware, particularly when devices rebooted or updated firmware.
Applications frequently encountered fatal crashes like KeyStoreException or broken master keys where encrypted preferences became permanently unreadable, stranding users in corrupted states.
Modern Android development replaces this deprecated class with Jetpack DataStore.
DataStore uses Kotlin Coroutines and Flow to guarantee asynchronous, thread-safe disk operations on Dispatchers.IO, separating storage mechanics from encryption and allowing teams to layer Google Tink or Keystore AES-GCM cleanly without risking main-thread freezes.""",
    "deep_senior_en": """The deprecation of EncryptedSharedPreferences represents a case study in why simply wrapping legacy, synchronous I/O abstractions with heavy cryptographic operations inevitably fails at scale.
SharedPreferences was architected in the earliest days of Android with the assumption that reading small XML files in memory is fast enough for the main thread.
When Jetpack Security layered two-level authenticated encryption over preference keys via AES-256-SIV and preference values via AES-256-GCM, every read and write operation became a cryptographic transaction.
On mid-tier and budget Android devices, hardware cryptographic accelerators in the TEE have limited throughput; invoking Keystore operations synchronously during UI rendering resulted in severe jank and measurable ANR regressions.
Beyond latency, the ecosystem encountered fatal edge-case failures.
OEM implementations of Keymaster frequently failed during concurrent multi-process writes or Direct Boot transitions, corrupting the Keystore keyset or throwing internal Keystore errors with cryptic vendor codes.
Once the master keyset was corrupted, the XML file could neither be read nor recovered, causing endless startup crashes unless the app caught the exception and wiped all local user data.
To resolve this in modern architectures, we migrate away from EncryptedSharedPreferences toward Jetpack DataStore.
DataStore operates entirely off the main thread via Kotlin coroutines, provides transactional data consistency, and allows developers to serialize encrypted protocol buffers or use Google Tink directly on Dispatchers.IO.
When performing migrations, we implement resilient try-catch fallbacks: if reading legacy EncryptedSharedPreferences fails due to Keystore corruption, we wipe the corrupt file, force a clean token re-authentication, and persist the new session safely into DataStore.""",
    "meta_ar": {
        "id": "SEC-12",
        "questionAr": "ما هي حقيقة إيقاف مكتبة EncryptedSharedPreferences ومشاكلها وبديلها الحديث؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "معرفة أسباب إيقاف جوجل لمكتبة EncryptedSharedPreferences، ومشاكل الأداء والـ ANR الناتجة عن التشفير المتزامن، وثغرات تعطل المفاتيح والـ Keystore Corruption في بعض الأجهزة، وتصميم خطة الهجرة إلى Jetpack DataStore مع Tink.",
        "concept_ar": "أوقفت جوجل مكتبة EncryptedSharedPreferences رسمياً بسبب مشاكل معمارية عميقة؛ فهي تعتمد على واجهة SharedPreferences القديمة والمتزامنة التي تعطل الخيط الرئيسي (Main Thread) وتسبب بطء و ANRs أثناء التشفير، بالإضافة إلى تعرضها المتكرر لأخطاء انهيار وتلف المفاتيح (Keystore Corruption) في بعض أجهزة OEM عند إعادة التشغيل أو التحديث. والبديل الحديث هو استخدام Jetpack DataStore غير المتزامن مع مكتبة Google Tink أو التشفير المباشر بـ Keystore.",
        "walkthrough_ar": "التعامل الآمن مع أخطاء EncryptedSharedPreferences التالفة ونقل البيانات إلى DataStore:\n```kotlin\nfun safeReadLegacyToken(context: Context): String? {\n    return try {\n        val masterKey = MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()\n        val prefs = EncryptedSharedPreferences.create(context, \"secret\", masterKey, ...)\n        prefs.getString(\"token\", null)\n    } catch (e: Exception) {\n        // التقاط أخطاء Keystore الكارثية ومسح الملف التالف لإيقاف الانهيارات المتكررة\n        context.getSharedPreferences(\"secret\", Context.MODE_PRIVATE).edit().clear().apply()\n        null\n    }\n}\n```",
        "why_it_matters_ar": "الاستمرار في استخدام هذه المكتبة الملغاة يعرض ملايين المستخدمين لانهيارات غامضة وفقدان دائم للجلسات وتجمد واجهة المستخدم بسبب عمليات التشفير المتزامنة على الخيط الرئيسي.",
        "worked_example_ar": "التصميم البديل الحديث باستخدام Jetpack Preferences DataStore في خيط الخلفية:\n```kotlin\nval Context.dataStore by preferencesDataStore(name = \"secure_settings\")\nsuspend fun saveSecureToken(context: Context, token: String) {\n    withContext(Dispatchers.IO) {\n        // حفظ غير متزامن تماماً لا يعطل واجهة المستخدم إطلاقاً\n        context.dataStore.edit { prefs -> prefs[TOKEN_KEY] = token }\n    }\n}\n```",
        "trade_offs_ar": "كانت المكتبة القديمة سهلة الاستخدام وتوفر واجهة SharedPreferences المألوفة، لكنها كانت محفوفة بمخاطر الانهيار، بينما DataStore يتطلب كود Coroutines و Flow لكنه يقدم أماناً واستقراراً وتزامناً مثالياً.",
        "failure_modes_ar": "حدوث KeyStoreException غير قابل للحل في أجهزة سامسونج أو هواوي القديمة مما يجعل التطبيق ينهار فور تشغيله في كل مرة ما لم يتم مسح بيانات التطبيق بالكامل.",
        "production_perspective_ar": "في التطبيقات الإنتاجية، وضعنا خطة هجرة صامتة تنقل التوكنز القديمة إلى DataStore عند أول فتح، مع محاذاة مسح المفاتيح التالفة بطلب تسجيل دخول جديد دون إغلاق التطبيق في وجه المستخدم.",
        "how_to_answer_ar": "ابدأ بذكر أن جوجل أوقفتها رسمياً (Deprecated)، واشرح السببين الجوهريين: مشاكل الأداء وتجمد الـ Main Thread، ومشاكل تلف الـ Keystore على مستوى أجهزة معينة، ثم قدم البديل المعماري الحديث وهو Jetpack DataStore.",
        "talking_points_ar": "إيقاف المكتبة رسمياً، ومشاكل الـ Synchronous I/O و ANR، وأخطاء Keystore Corruption في بعض المصنعين، والبديل الحديث Jetpack DataStore، ومكتبة Google Tink.",
        "follow_ups_ar": "- **المحاور:** \"لماذا تسبب EncryptedSharedPreferences تجمداً في الواجهة بينما SharedPreferences العادية سريعة؟\"\n  **المرشح:** \"لأن التشفير يتطلب عمليات حسابية معقدة ومخاطبة عتاد الـ TEE عبر Keystore، وكل هذا كان يتم بشكل متزامن وبطيء على الـ Main Thread.\"\n\n- **المحاور:** \"كيف تنقذ تطبيقك إذا كان ينهار لدى آلاف المستخدمين بسبب MasterKeyException في هذه المكتبة؟\"\n  **المرشح:** \"أحوط استدعاء التهيئة بـ try-catch لمسح الملف التالف تلقائياً وإلغاء القفل، وإجبار المستخدم على تسجيل الدخول مجدداً بدلاً من استمرار الانهيار عند التشغيل.\"",
        "self_check_ar": "هل ذكرت صراحة أنها Deprecated؟ هل شرحت مشاكل الـ ANR وتلف المفاتيح؟ وهل اقترحت الهجرة لـ DataStore؟",
        "references_ar": f"- [AndroidX Security Crypto Deprecation Notice](https://developer.android.com/jetpack/androidx/releases/security) — الإعلان الرسمي لإيقاف مكتبة security-crypto.\n- [Jetpack DataStore Documentation](https://developer.android.com/topic/libraries/architecture/datastore) — الدليل الرسمي لحفظ البيانات الحديث باستخدام DataStore.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "أوقفت جوجل مكتبة EncryptedSharedPreferences رسمياً بسبب عيوب معمارية خطيرة؛ منها تنفيذ التشفير وقراءة القرص بشكل متزامن على خيط الواجهة مما يسبب بطء التطبيق وانهيارات ANR، وتكرار تلف المفاتيح التشفيرية في بعض هواتف أندرويد مما يجعل استرجاع البيانات مستحيلاً، ويوصى بالانتقال إلى Jetpack DataStore لمعالجة البيانات المشفرة في الخلفية.",
        "best_answer_ar": "رغم أن مكتبة EncryptedSharedPreferences وفرت حلاً سهلاً لتشفير البيانات، إلا أن جوجل أوقفتها رسمياً نظراً للمشاكل المتكررة التي واجهت المطورين في بيئات الإنتاج.\n\nالمشكلة الأولى معمارية وتتعلق بالأداء؛ حيث قامت المكتبة ببناء التشفير فوق نظام SharedPreferences القديم المتزامن، مما جعل كل عملية قراءة أو كتابة تتطلب حسابات تشفيرية ومخاطبة لعتاد Keystore على الخيط الرئيسي، وهو ما نتج عنه تجمد متكرر للواجهة وارتفاع معدلات الـ ANR.\n\nأما المشكلة الثانية والأخطر فهي تلف المفاتيح التشفيرية Keystore Corruption على بعض أجهزة المستخدمين، وتحديداً في هواتف سامسونج وهواوي عند تحديث النظام أو إعادة التشغيل؛ حيث تفشل المكتبة في فك تشفير الملف وتطلق استثناءات كارثية تؤدي لانهيار التطبيق في كل مرة يفتحه المستخدم. ولذلك، تفرض المعمارية الحديثة استبدالها بـ Jetpack DataStore مع استخدام Coroutines للعمل في خيوط الخلفية، واستخدام Google Tink للتشفير بأمان واستقرار تام.",
        "deep_answer_ar": "يمثل إيقاف EncryptedSharedPreferences درساً معمارياً هاماً يوضح خطورة وضع طبقات تشفير ثقيلة فوق واجهات متزامنة قديمة صُممت في بدايات أندرويد.\n\nصُمم SharedPreferences على افتراض أن قراءة ملفات XML سريعة ولا تعطل الـ Main Thread. ولكن عندما أضافت Jetpack Security تشفير المفاتيح بـ AES-SIV وتشفير القيم بـ AES-GCM، تحولت كل عملية حفظ لصفقة تشفيرية متكاملة تستهلك دورات المعالج وتخاطب عتاد الـ TEE المحدود السرعة في الأجهزة المتوسطة والضعيفة، مما سبب هبوطاً حاداً في أداء الشاشات.\n\nوعلاوة على بطء الأداء، عانت المكتبة من عيوب قاتلة في بيئات الأجهزة الحقيقية؛ فكثيراً ما كانت خوادم Keymaster في بعض معالجات OEM تتعرض لحالات سباق أو تلف أثناء إعادة التشغيل السريع، مما يؤدي إلى تلف ملف المفاتيح MasterKey، ويصبح ملف الـ XML عاجزاً عن فك التشفير إلى الأبد. فإذا لم يكن المطور قد أدار هذا الاستثناء بذكاء، يدخل التطبيق في حلقة انهيارات لا تنتهي عند بداية التشغيل Crash Loop.\n\nلحل هذه الأزمة جذرياً، نقوم بالهجرة إلى Jetpack DataStore المبني بالكامل على Kotlin Flow والـ Coroutines، مما يضمن تنفيذ عمليات التخزين على Dispatchers.IO بعيداً عن واجهة المستخدم. وأثناء مرحلة الهجرة، نطبق استراتيجية دفاعية؛ فإذا فشلت قراءة المفاتيح القديمة من EncryptedSharedPreferences بسبب تلف المفتاح، نقوم بمسح الملف التالف برمجياً وتوجيه العميل لتسجيل الدخول بأمان، ونحفظ الجلسة الجديدة داخل DataStore المشفر لضمان موثوقية التطبيق في الإنتاج."
    }
}

# ==========================================
# SEC-13: How do you handle key invalidation, key rotation, backups, and reinstall?
# ==========================================
DATA["SEC-13"] = {
    "concept_en": """Managing cryptographic keys in production Android applications requires designing for four critical lifecycle events: key invalidation, key rotation, device backup/restore, and application reinstallation. Key invalidation occurs primarily when Keystore keys bound to user authentication (via setUserAuthenticationRequired) are permanently invalidated by the platform (KeyPermanentlyInvalidatedException) when the user removes their lockscreen PIN/password or enrolls a new biometric fingerprint. Key rotation is the operational discipline of transitioning encrypted data from an older cryptographic key to a newer key version without data loss, accomplished using versioned ciphertext envelopes. Device backups present a major security hazard: by default, Android Auto Backup may copy encrypted files or preferences to Google Drive; however, because Keystore keys are tied to physical hardware and are never included in backups, restored files on a new device or after reinstallation become permanently undecryptable. Applications must explicitly disable auto-backup for encrypted storage via android:allowBackup="false" or data extraction rules.""",
    "walkthrough_en": """Handling key invalidation and configuring backup exclusion rules:
```xml
<!-- 1. Exclude encrypted storage from Android Auto Backup in data_extraction_rules.xml -->
<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <!-- Exclude encrypted SharedPreferences / Keystore-dependent files -->
        <exclude path="shared_prefs/secure_session.xml" />
        <exclude path="databases/encrypted_vault.db" />
    </cloud-backup>
    <device-transfer>
        <exclude path="shared_prefs/secure_session.xml" />
        <exclude path="databases/encrypted_vault.db" />
    </device-transfer>
</data-extraction-rules>
```
Graceful handling of KeyPermanentlyInvalidatedException in Kotlin:
```kotlin
// 2. Catching key invalidation when biometrics change
fun executeBiometricDecryption(cipher: Cipher, encryptedData: ByteArray): Result<ByteArray> {
    return try {
        Result.success(cipher.doFinal(encryptedData))
    } catch (e: KeyPermanentlyInvalidatedException) {
        // Biometrics were altered: lockscreen changed or new fingerprint added!
        // 1. Wipe orphaned local ciphertext
        clearOrphanedCredentials()
        // 2. Request user to re-authenticate with primary credentials / password
        Result.failure(SecurityException("Cryptographic key invalidated due to security changes", e))
    }
}
```""",
    "short_en": """We handle key invalidation by catching KeyPermanentlyInvalidatedException when lockscreen or biometric enrollments change, clearing unusable ciphertext, and prompting re-authentication. For backups and reinstalls, because Keystore keys never transfer across devices, we explicitly exclude encrypted files from Android Auto Backup to prevent unrecoverable decryption failures.""",
    "structured_en": """A resilient mobile security architecture plans for inevitable key lifecycle events rather than assuming cryptographic keys live indefinitely.
Key invalidation occurs when biometric-bound Keystore keys detect that lockscreen security has changed, such as when a user adds a new fingerprint or disables their device PIN.
The platform throws a KeyPermanentlyInvalidatedException, preventing an unauthorized person who enrolled a fingerprint on a borrowed phone from unlocking the original user's sensitive data.
Applications must catch this exception, wipe the now-unusable local ciphertext, and prompt the user to re-authenticate using their master password.
Key rotation involves persisting a version header alongside encrypted data; when a key rotates, the application decrypts using the old key and re-encrypts using the new key version within an atomic transaction.
Finally, handling backups and reinstalls requires strict isolation.
Android Keystore keys are bound to device hardware and do not survive app reinstallation or cloud backup restore.
We configure XML data extraction rules to exclude encrypted preferences and databases from cloud backups, ensuring that restored apps start with a clean state rather than crashing on orphaned ciphertext.""",
    "deep_senior_en": """Production cryptographic engineering distinguishes itself by anticipating failure modes in identity and device transitions.
When keys are configured with setUserAuthenticationRequired, the Android Keymaster daemon binds key usability to the hardware biometric enrollment database.
If an attacker or unauthorized user adds their own fingerprint in system settings, the system invalidates all existing keys to maintain non-repudiation and prevent account takeover.
When KeyPermanentlyInvalidatedException is thrown, handling it gracefully is paramount: crashing the app or silently looping produces a fatal user experience.
The app must intercept the exception, purge the orphaned ciphertext, inform the user with transparent security rationale, and require a full backend challenge with password or multi-factor authentication to establish a new key pair.
The interaction between Android Keystore and Android Auto Backup is another notorious trap.
When users migrate to a new phone, Google's backup system automatically transfers files unless explicitly restricted.
However, because hardware Keystore keys cannot be backed up, the restored application inherits encrypted files on the new phone with no valid key in its new Keystore to decrypt them.
This produces silent decryption failures or startup crashes.
We eliminate this vulnerability by configuring android:dataExtractionRules in Android 12 and later, explicitly excluding all sensitive databases, credentials, and token files from cloud backups and device-to-device transfers.
If user data must be restored on a new device, we design a server-assisted key escrow or client re-sync architecture rather than relying on OS-level file transfers.""",
    "meta_ar": {
        "id": "SEC-13",
        "questionAr": "كيف تتعامل مع إبطال المفاتيح (Key Invalidation) وتدويرها والنسخ الاحتياطي وإعادة التثبيت؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التعامل مع استثناء KeyPermanentlyInvalidatedException عند تغيير البصمة أو قفل الشاشة، واستيعاب عدم انتقال مفاتيح Keystore مع النسخ الاحتياطي السحابي، وتهيئة قواعد استبعاد الملفات المشفرة من Auto Backup، واستراتيجيات تدوير المفاتيح.",
        "concept_ar": "تتعرض المفاتيح التشفيرية لدورات حياة حرجة؛ فالإبطال (Key Invalidation) يحدث تلقائياً عند تغيير قفل الشاشة أو إضافة بصمة جديدة لحماية التطبيق عبر استثناء KeyPermanentlyInvalidatedException مما يوجب مسح البيانات التالفة وإعادة التوثيق. كما أن مفاتيح Keystore مرتبطة بالعتاد المادي ولا تنتقل مع النسخ الاحتياطي (Auto Backup)؛ مما يفرض استبعاد الملفات المشفرة عبر dataExtractionRules لمنع انهيار التطبيق عند استعادته على هاتف جديد دون مفاتيحه الأصلية.",
        "walkthrough_ar": "استبعاد الملفات المشفرة من النسخ الاحتياطي والتعامل مع إبطال المفاتيح:\n```xml\n<!-- استبعاد الملفات المشفرة في data_extraction_rules.xml لمنع استعادتها بدون مفاتيحها -->\n<data-extraction-rules>\n    <cloud-backup><exclude path=\"shared_prefs/secure_tokens.xml\" /></cloud-backup>\n    <device-transfer><exclude path=\"shared_prefs/secure_tokens.xml\" /></device-transfer>\n</data-extraction-rules>\n```\nمعالجة استثناء تغيير البصمة برمجياً:\n```kotlin\ntry { cipher.doFinal(data) } \ncatch (e: KeyPermanentlyInvalidatedException) {\n    clearLocalVault() // مسح البيانات التي أصبحت بلا مفتاح\n    promptUserToReLogin(\"تم تغيير إعدادات الأمان في هاتفك، يرجى تسجيل الدخول مجدداً\")\n}\n```",
        "why_it_matters_ar": "إهمال هذه الحالات يؤدي لانهيار التطبيق لدى ملايين المستخدمين عند تغيير قفل الهاتف أو شراء هاتف جديد واستعادة النسخة الاحتياطية السحابية لعدم وجود المفاتيح الأصلية.",
        "worked_example_ar": "نمط تدوير المفاتيح التشفيرية بوجود ترويسة رقم الإصدار (Key Rotation):\n```kotlin\ndata class EncryptedEnvelope(val keyVersion: Int, val iv: ByteArray, val ciphertext: ByteArray)\nfun rotateKeyIfOld(envelope: EncryptedEnvelope, currentVersion: Int): EncryptedEnvelope {\n    if (envelope.keyVersion == currentVersion) return envelope\n    val plaintext = decryptWithVersion(envelope.ciphertext, envelope.keyVersion)\n    return encryptWithVersion(plaintext, currentVersion) // إعادة تشفير بالمفتاح الجديد\n}\n```",
        "trade_offs_ar": "ربط المفتاح بالبصمة يوفر أقصى حماية لمنع استخدام التطبيق إذا أضاف شخص غريب بصمته، لكنه يفرض إعادة توثيق المستخدم عند أي تعديل، واستبعاد النسخ الاحتياطي يمنع الانهيارات لكنه يتطلب إعادة تنزيل البيانات من السيرفر.",
        "failure_modes_ar": "استعادة ملفات Room المشفرة عبر النسخ الاحتياطي السحابي لجهاز جديد مع عدم وجود مفتاح Keystore الأصلي، مما يؤدي لحدوث Crash مستمر عند بدء تشغيل التطبيق.",
        "production_perspective_ar": "في تطبيقات البنوك، نعطل دائماً الـ Auto Backup تماماً لجميع ملفات التطبيق، ونعتمد على السيرفر كمصدر وحيد للحقيقة لإعادة بناء بيانات المستخدم عند تثبيت التطبيق من جديد.",
        "how_to_answer_ar": "قسم الإجابة إلى أربعة محاور: إبطال المفتاح عند تغيير البصمة وكيفية التعامل مع الاستثناء، مشكلة النسخ الاحتياطي لعدم انتقال مفاتيح Keystore وحلها عبر استبعاد الملفات، واستراتيجية تدوير المفاتيح، وسيناريو إعادة التثبيت.",
        "talking_points_ar": "استثناء KeyPermanentlyInvalidatedException، وتغيير قفل الشاشة والبصمات، وملف data_extraction_rules، وعدم انتقال Keystore مع Auto Backup، واستراتيجية تدوير المفاتيح عبر Versioning.",
        "follow_ups_ar": "- **المحاور:** \"لماذا يبطل أندرويد مفاتيح التشفير عند قيام المستخدم بإضافة بصمة إصبع جديدة؟\"\n  **المرشح:** \"لأنه إجراء أمني يمنع أي شخص يعرف رمز قفل الهاتف من إضافة بصمته الشخصية واستخدام التطبيق البنكي للتحويل بأنه صاحب الحساب الأصلي.\"\n\n- **المحاور:** \"ماذا يحدث لو قمت بحذف التطبيق وإعادة تثبيته؟ هل تظل مفاتيح Keystore القديمة موجودة؟\"\n  **المرشح:** \"لا، يقوم نظام أندرويد بحذف كافة مفاتيح Keystore الخاصة بالتطبيق تلقائياً عند حذفه، ولا يمكن استرجاعها نهائياً.\"",
        "self_check_ar": "هل شرحت سبب حدوث Key Invalidation؟ هل وضحت سبب فشل النسخ الاحتياطي مع Keystore؟ وهل ذكرت إعدادات data_extraction_rules؟",
        "references_ar": f"- [Android Backup Rules and Data Extraction](https://developer.android.com/identity/data/autobackup) — توثيق جوجل الرسمي لضبط قواعد النسخ الاحتياطي وحماية البيانات.\n- [KeyPermanentlyInvalidatedException Reference](https://developer.android.com/reference/android/security/keystore/KeyPermanentlyInvalidatedException) — التوثيق الرسمي لاستثناء إبطال المفاتيح عند تعديل البصمة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نتعامل مع إبطال المفاتيح بالتقاط استثناء KeyPermanentlyInvalidatedException الذي يطلقه النظام عند تغيير قفل الشاشة أو إضافة بصمة جديدة، حيث نقوم بمسح البيانات التالفة وإلزام المستخدم بتسجيل الدخول. وبالنسبة للنسخ الاحتياطي وإعادة التثبيت، ونظراً لأن مفاتيح Keystore مرتبطة بالعتاد ولا تنتقل سحابياً، نقوم باستبعاد كافة الملفات المشفرة من النسخ الاحتياطي التلقائي لتجنب الانهيارات عند فتح التطبيق على جهاز جديد.",
        "best_answer_ar": "تتطلب إدارة المفاتيح التشفيرية في بيئات الإنتاج تخطيطاً مسبقاً لدورة حياة المفاتيح لتجنب الانهيارات المفاجئة وفقدان البيانات.\n\nتحدث حالة إبطال المفاتيح Key Invalidation عندما تكون المفاتيح مرتبطة بالبصمة الحيوية ويقوم المستخدم بإضافة بصمة جديدة أو تغيير قفل الشاشة؛ حيث يطلق النظام استثناء KeyPermanentlyInvalidatedException لمنع أي شخص متطفل أضاف إصبعه من فتح حسابات العميل. والتعامل الصحيح برمجياً هو التقاط الاستثناء ومسح البيانات المشفرة محلياً والطلب من المستخدم تسجيل دخوله من جديد بكلمة المرور لإنشاء مفاتيح جديدة.\n\nأما بالنسبة للنسخ الاحتياطي وإعادة التثبيت، فإن الخطر الأكبر يتمثل في نظام النسخ الاحتياطي التلقائي لأندرويد؛ فإذا نقل النظام ملفات البيانات المشفرة إلى هاتف جديد عبر السحاب، سيفشل التطبيق في فك تشفيرها لأن مفاتيح Keystore العتادية تظل محبوسة في الهاتف القديم ولا تنتقل أبداً. ولذلك نلزم التطبيق باستبعاد الملفات المشفرة في ملف data_extraction_rules لضمان بدء التطبيق ببيانات نظيفة ومزامنة البيانات من السيرفر مباشرة.",
        "deep_answer_ar": "التميز الهندسي في إدارة التشفير يتجلى في التنبؤ بسيناريوهات الفشل عند تبديل المستخدم لأجهزته أو تعديل إعدادات أمان هاتفه.\n\nعندما نربط مفاتيح Keystore بالتحقق البيومتري عبر setUserAuthenticationRequired، فإن معالج الأمان Keymaster يربط صلاحية المفتاح بقاعدة بيانات البصمات الحالية. فإذا أضاف شخص آخر بصمة جديدة على الجهاز، يقوم النظام فوراً بإبطال المفتاح لمنع الهجمات التطفلية. والتعامل مع هذا الاستثناء يجب أن يكون واعياً؛ فلا نترك التطبيق ينهار أو يدخل في دوامة تجارب فاشلة، بل نلتقط KeyPermanentlyInvalidatedException ونحذف البايتات المشفرة التي أصبحت بلا مفتاح، ونوجه العميل لشاشة تسجيل الدخول الرئيسية لتوثيق حسابه وإنشاء زوج مفاتيح جديد في عتاد الهاتف.\n\nوالمصيدة الأخطر في تطبيقات أندرويد هي التعارض بين Android Keystore وخدمة Android Auto Backup؛ حيث يقوم النظام سحابياً بنسخ ملفات SharedPreferences وقواعد البيانات تلقائياً لهاتف العميل الجديد، ولكن المفاتيح التشفيرية تظل حبيسة الشريحة العتادية للجهاز القديم وتمحى عند بيعه. فعندما يفتح المستخدم التطبيق على هاتفه الجديد، يجد ملفات مشفرة بدون مفتاح فينهار التطبيق فوراً. لتفادي هذه الكارثة، نضبط إعدادات data_extraction_rules في أندرويد 12 فما فوق لاستبعاد كافة قواعد البيانات والرموز الحساسة من النسخ الاحتياطي السحابي، ونعتمد على إعادة مزامنة البيانات عبر خوادمنا عند تنصيب التطبيق على أي جهاز جديد."
    }
}

# ==========================================
# SEC-14: Where should access and refresh tokens be stored and how are they revoked?
# ==========================================
DATA["SEC-14"] = {
    "concept_en": """Secure token storage and revocation architecture represents the core of identity management in modern mobile applications. Access tokens are short-lived bearer credentials (typically lasting 15 to 60 minutes) used in HTTP Authorization headers. Because of their ephemeral nature, access tokens can reside in volatile in-memory repositories or securely in encrypted storage. Refresh tokens are long-lived, high-privilege credentials whose sole purpose is to exchange for new access tokens; they must be persisted securely on disk using Jetpack DataStore or EncryptedSharedPreferences backed by hardware-rooted Android Keystore master keys. Token revocation operates on two planes: client-side lifecycle and server-side invalidation. A client-side logout must cancel running background network tasks, wipe in-memory token singletons, and purge persisted ciphertext from disk. However, local deletion alone does not invalidate a bearer token across distributed systems. The client must dispatch an explicit logout request to the authorization server's OAuth 2.0 Token Revocation endpoint (RFC 7009), allowing the backend to invalidate the refresh token in Redis and trigger Refresh Token Rotation (RTR).""",
    "walkthrough_en": """Implementing secure token storage and RFC 7009 compliant token revocation:
```kotlin
class AuthenticationRepository(
    private val secureStorage: EncryptedDataStore,
    private val authApi: OAuthService,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    // 1. In-memory volatile access token cache for high-throughput OkHttp interceptors
    @Volatile private var cachedAccessToken: String? = null

    suspend fun getAccessToken(): String? = cachedAccessToken ?: withContext(ioDispatcher) {
        secureStorage.readAccessToken().also { cachedAccessToken = it }
    }

    // 2. Comprehensive Logout: Server-side RFC 7009 revocation + Local purge
    suspend fun executeCompleteLogout(): Result<Unit> = withContext(ioDispatcher) {
        try {
            val currentRefreshToken = secureStorage.readRefreshToken()
            if (!currentRefreshToken.isNullOrBlank()) {
                // Inform backend authorization server to invalidate the token in Redis
                authApi.revokeToken(
                    token = currentRefreshToken,
                    tokenTypeHint = "refresh_token"
                )
            }
        } catch (e: Exception) {
            // Even if network fails, proceed to clean local state
        } finally {
            // Guarantee local credentials are eradicated
            cachedAccessToken = null
            secureStorage.clearAllTokens()
        }
        Result.success(Unit)
    }
}
```""",
    "short_en": """We store short-lived access tokens in volatile memory or encrypted storage, while long-lived refresh tokens are securely encrypted on disk using Keystore-backed DataStore. Revocation requires a dual approach: wiping in-memory singletons and encrypted disk storage on the client, and calling the server's OAuth revocation endpoint so the refresh token is immediately blacklisted in backend caches.""",
    "structured_en": """Effective mobile token management separates storage requirements by token lifetime while enforcing robust revocation protocols.
Access tokens are short-lived bearer credentials that expire in minutes, which we maintain in volatile memory or encrypted local storage to satisfy frequent network calls with low latency.
Refresh tokens represent permanent account access; they must be encrypted on disk using Jetpack DataStore or EncryptedSharedPreferences anchored to an Android Keystore master key.
Revocation requires a coordinated effort between client state and backend infrastructure.
Simply clearing local app storage upon logout is insufficient because an exfiltrated refresh token remains valid on the authorization server until its natural expiration.
A production logout workflow first sends an authenticated request to the server's OAuth 2.0 revocation endpoint, instructing the backend to blacklist the token family in its Redis cache.
The client then cancels all running coroutines, clears in-memory token singletons, and purges the encrypted disk storage.
Additionally, the backend enforces Refresh Token Rotation, issuing a new refresh token on every exchange and invalidating the entire family if an already-consumed token is replayed.""",
    "deep_senior_en": """From an adversarial perspective, the security of an OAuth 2.0 mobile client rests entirely on the protection of its refresh token and the resilience of its revocation pathways.
If an attacker intercepts an access token, the exposure window is strictly bounded by its brief time-to-live.
However, a compromised refresh token allows persistent access to account resources.
Therefore, storing refresh tokens in plain SharedPreferences or unencrypted Room tables is a catastrophic vulnerability.
We persist refresh tokens exclusively in storage encrypted via AES-256-GCM using hardware-backed Keystore keys, while caching the access token in volatile memory to prevent repeated disk decryption overhead on every API call.
For revocation, we must design for both user-initiated logouts and automated threat mitigation.
In a user logout, deleting local records while offline is a dangerous half-measure; if the network is available, the client must notify the server's RFC 7009 revocation endpoint so distributed API gateways reject subsequent requests using that token.
More importantly, modern systems implement Refresh Token Rotation with Automatic Reuse Detection.
Every time the mobile app requests a new access token, the authorization server invalidates the current refresh token and issues a replacement pair.
If an attacker attempts to use a previously consumed refresh token, the server detects the token replay attack, recognizes that a breach has occurred, and immediately revokes all active tokens associated with that user session, neutralizing the threat automatically.""",
    "meta_ar": {
        "id": "SEC-14",
        "questionAr": "أين وكيف يجب تخزين الـ Access Tokens والـ Refresh Tokens وما هي آليات الإلغاء؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "الفهم المعماري لفصل تخزين Access Token المؤقت عن Refresh Token الحساس، واستخدام التخزين المشفر المدعوم بـ Keystore، وتطبيق الإلغاء الشامل (Client-side & Server-side RFC 7009)، وتطبيق بروتوكول تدوير الرموز وكشف إعادة الاستخدام (Token Reuse Detection).",
        "concept_ar": "تخزن رموز Access Tokens قصيرة الأجل في الذاكرة المؤقتة (RAM) أو التخزين المشفر لتفويض الطلبات الشبكية السريعة، بينما تُحفظ رموز Refresh Tokens الحساسة وطويلة الأجل حصرياً في تخزين مشفر على القرص (DataStore أو EncryptedSharedPreferences) مدعوم بمفتاح Keystore عتادي. ويتطلب إلغاء الرموز (Revocation) مساراً مزدوجاً؛ مسح الذاكرة والتخزين المحلي، مع إرسال طلب صريح لنقطة إلغاء السيرفر (RFC 7009) لوضع التوكن في القائمة السوداء، وتطبيق بروتوكول تدوير الرموز لمنع استغلال الرموز المسروقة.",
        "walkthrough_ar": "تنفيذ التخزين الآمن والإلغاء المزدوج للرموز عند تسجيل الخروج:\n```kotlin\nsuspend fun logout(secureStorage: EncryptedStore, authApi: AuthService) {\n    try {\n        val refreshToken = secureStorage.getRefreshToken()\n        // 1. إخطار السيرفر لإلغاء التوكن في Redis فوراً:\n        if (refreshToken != null) authApi.revokeToken(refreshToken)\n    } finally {\n        // 2. مسح الذاكرة الحية والتخزين المشفر محلياً:\n        cachedAccessToken = null\n        secureStorage.clearAll()\n    }\n}\n```",
        "why_it_matters_ar": "الاكتفاء بحذف الرموز من الهاتف عند تسجيل الخروج يترك الـ Refresh Token فعالاً في السيرفر، فإذا كان المخترق قد نسخ الرمز فسيظل قادراً على الوصول لحساب المستخدم لشهور طويلة.",
        "worked_example_ar": "حماية الجلسة عبر ميزة كشف إعادة استخدام الرمز (Refresh Token Rotation):\n```kotlin\n// إذا تلقى السيرفر طلباً برمز Refresh تم استهلاكه سابقاً، يدرك حدوث اختراق ويلغي العائلة كاملة:\nclass TokenInterceptor(private val repo: AuthRepository) : Interceptor {\n    override fun intercept(chain: Interceptor.Chain): Response {\n        val response = chain.proceed(chain.request())\n        if (response.code == 401 && response.header(\"Token-Reused\") == \"true\") {\n            repo.forceFullLogoutDueToBreach() // إغلاق الجلسة فوراً للاشتباه بالاختراق\n        }\n        return response\n    }\n}\n```",
        "trade_offs_ar": "الاحتفاظ بـ Access Token في الذاكرة الحية فقط يزيد من سرعة الطلبات لكنه يتطلب تجديده من القرص عند موت التطبيق، والتحقق السحابي عند الخروج يتطلب اتصالاً بالإنترنت.",
        "failure_modes_ar": "حفظ الـ Refresh Token في SharedPreferences عادية بدون تشفير، أو مسح البيانات محلياً فقط عند تسجيل الخروج دون إبلاغ السيرفر لإبطال الرمز في قواعد بياناته.",
        "production_perspective_ar": "في التطبيقات المصرفية، نطبق معيار OAuth 2.0 مع PKCE، ونحفظ الرموز في DataStore مشفر، ونطبق Refresh Token Rotation في السيرفر حيث يُلغى كل رمز بمجرد استخدامه لتوليد رمز جديد.",
        "how_to_answer_ar": "ميز أولاً بين طبيعة الرمزين وفترة بقائهما ومكان تخزينهما، ثم اشرح عملية الإلغاء الصحيحة التي تجمع بين مسح الكاش المحلي واستدعاء API الإلغاء في السيرفر، واختم ببروتوكول Refresh Token Rotation.",
        "talking_points_ar": "فصل الـ Access Token عن الـ Refresh Token، والتخزين المشفر في DataStore بـ Keystore، ومسار الإلغاء RFC 7009، وكشف إعادة الاستخدام (Token Reuse Detection)، وبروتوكول PKCE.",
        "follow_ups_ar": "- **المحاور:** \"ماذا لو كان الهاتف غير متصل بالإنترنت وقام المستخدم بالضغط على تسجيل الخروج؟\"\n  **المرشح:** \"نقوم فوراً بمسح التخزين والذاكرة محلياً لمنع الوصول للتطبيق من هذا الجهاز، ونسجل طلب الإلغاء في طابور مهام WorkManager لإرساله للسيرفر بمجرد عودة الاتصال.\"\n\n- **المحاور:** \"كيف يحمي بروتوكول Refresh Token Rotation التطبيق من سرقة الرموز؟\"\n  **المرشح:** \"عند استخدام التوكن لتجديد الجلسة، يقوم السيرفر بحرقه وإصدار توكن جديد؛ فإذا حاول المخترق استخدام نفس التوكن القديم، يكتشف السيرفر الهجوم ويلغي كل جلسات المستخدم فوراً.\"",
        "self_check_ar": "هل فرقت بين تخزين الرمزين؟ هل شرحت الإلغاء في السيرفر والمحلي؟ وهل وضحت آلية Refresh Token Rotation؟",
        "references_ar": f"- [RFC 7009 - OAuth 2.0 Token Revocation](https://datatracker.ietf.org/doc/html/rfc7009) — المعيار الدولي لإلغاء وتدمير رموز المصادقة.\n- [OAuth 2.0 for Native Apps (RFC 8252)](https://datatracker.ietf.org/doc/html/rfc8252) — أفضل الممارسات الأمنية لتطبيقات الموبايل وإدارة الجلسات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نخزن رموز الوصول المؤقتة في الذاكرة الحية أو التخزين المؤقت المشفر لسرعة الاستخدام، بينما نحفظ رموز التجديد طويلة الأجل حصرياً في تخزين محلي مشفر بمفاتيح عتادية من Keystore. ويتم الإلغاء عبر مسار مزدوج يمسح البيانات من الهاتف ويرسل طلباً صريحاً إلى خادم المصادقة لإبطال الرمز ومنع استخدامه مستقبلاً.",
        "best_answer_ar": "تعتمد الإدارة الآمنة للجلسات في تطبيقات أندرويد على التفريق الصارم بين نوعي الرموز من حيث فترة الصلاحية ومكان التخزين وطريقة الإلغاء.\n\nتعتبر Access Tokens رموز تفويض قصيرة الأجل تستمر لدقائق معدودة؛ لذا نفضل الاحتفاظ بها في الذاكرة الحية Volatile Memory لتزويد طبقة الشبكة بها بسرعة دون استهلاك القرص في كل طلب. في المقابل، تمثل Refresh Tokens مفتاح الوصول الدائم لحساب المستخدم؛ ولذلك يجب تشفيرها وحفظها على القرص باستخدام Jetpack DataStore مدعوماً بمفتاح رئيسي من Android Keystore.\n\nأما عملية إلغاء الرموز Revocation، فالخطأ الشائع هو الاكتفاء بمسح الملفات محلياً عند تسجيل الخروج؛ فالرمز المسروق يظل صالحاً للعمل على السيرفر. والتنفيذ الهندسي الصحيح يقتضي إرسال طلب إلى نقطة الإلغاء في السيرفر وفق معيار RFC 7009 لإبطال الرمز في خوادم Redis، ثم مسح الذاكرة والتخزين المشفر من الهاتف، مع تطبيق استراتيجية تدوير الرموز Refresh Token Rotation التي تلغي كافة الجلسات تلقائياً إذا حاول شخص استخدام رمز قديم تم استهلاكه.",
        "deep_answer_ar": "من منظور النمذجة التهديدية لبروتوكول OAuth 2.0، يمثل الـ Refresh Token أثمن هدف للمهاجمين؛ لأن الاستيلاء عليه يمنح المخترق وصولاً مستمراً لحساب الضحية حتى مع انتهاء توكن الوصول المؤقت.\n\nلذلك نلزم التطبيق بحفظ الـ Refresh Token داخل تخزين محلي مشفر بنمط AES-256-GCM عبر مفتاح عتادي من Keystore لا يمكن قراءته أو استخراجه من الذاكرة العادية، بينما نحتفظ بـ Access Token كمتغير Volatile في الذاكرة الحية لتقليل عمليات فك التشفير المستمرة مع كل طلب شبكي.\n\nوعند تسجيل الخروج، يعتبر مسح البيانات محلياً فقط إجراءً ناقصاً وخطيراً؛ فالرمز يظل فعالاً إذا تم تسريبه مسبقاً. لذلك يرسل التطبيق طلباً صريحاً لخادم الهوية لإدراج الـ Refresh Token في قائمة الإلغاء الفوري Blacklist، ثم يفرغ الذاكرة والتخزين المشفر على الجهاز. والأهم من ذلك هو تطبيق بروتوكول Refresh Token Rotation مع كشف إعادة الاستخدام التلقائي Automatic Reuse Detection؛ حيث يولد السيرفر زوج رموز جديد مع كل عملية تجديد ويحرق الرمز القديم.\n\nفإذا رصد السيرفر محاولة استخدام لرمز تم حرقه مسبقاً، يتعامل مع الموقف كاختراق أمني مؤكد ويسقط على الفور عائلة الرموز بالكامل ويبطل كافة جلسات المستخدم على جميع الأجهزة لحماية حسابه من السرقة. كما نضمن برمجياً إلغاء كافة وظائف Coroutines والـ WorkManager المعلقة التي تستخدم التوكن القديم لمنع إرسال طلبات مشوهة بعد اكتمال تسجيل الخروج."
    }
}

# ==========================================
# SEC-15: How do you prevent token leakage through logs, screenshots, crash reports, and analytics?
# ==========================================
DATA["SEC-15"] = {
    "concept_en": """Securing authentication credentials and personally identifiable information (PII) on Android requires defending against passive exfiltration channels that bypass encrypted disk storage. These unintended leakage vectors primarily include application logging frameworks, operating system task snapshot previews, third-party crash reporting SDKs, and behavioral analytics pipelines. System logs (Logcat) can be intercepted on older platforms or inspected via debugging tools; production builds must strip debug logs completely using R8 ProGuard rules (-assumenosideeffects) or custom Timber tree filters. Task switcher snapshots and screen recording present a physical and software shoulder-surfing vulnerability, mitigated by setting WindowManager.LayoutParams.FLAG_SECURE on sensitive activity windows. Crash reporting services (such as Firebase Crashlytics or Sentry) frequently record network traces, custom keys, or exception messages containing raw authorization headers unless intercepted by strict redaction filters. Similarly, product analytics SDKs (such as Firebase Analytics or Mixpanel) must enforce automated sanitization rules preventing tokens, passwords, or credit card numbers from entering event parameter bundles.""",
    "walkthrough_en": """Securing window previews, network logging, and crash report data exfiltration:
```kotlin
// 1. Prevent screenshots, screen recording, and task switcher previews
class SensitivePaymentActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Blanks out screen preview in Android Recents overview and blocks screenshots
        window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
    }
}

// 2. Redacting sensitive Authorization headers in OkHttp network logging
val loggingInterceptor = HttpLoggingInterceptor().apply {
    level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY else HttpLoggingInterceptor.Level.NONE
    redactHeader("Authorization")
    redactHeader("Proxy-Authorization")
    redactHeader("Cookie")
    redactHeader("Set-Cookie")
}

// 3. Sanitizing Crashlytics custom crash keys to strip PII and tokens
fun recordSafeCrashBreadcrumb(key: String, value: String) {
    val sanitizedValue = if (key.contains("token", ignoreCase = true) || key.contains("auth", ignoreCase = true)) {
        "[REDACTED]"
    } else {
        value
    }
    FirebaseCrashlytics.getInstance().setCustomKey(key, sanitizedValue)
}
```""",
    "short_en": """We prevent token leakage across side-channels by stripping debug logs via R8 in release builds, setting FLAG_SECURE on sensitive windows to block screenshots and task snapshots, redacting Authorization headers in network interceptors, and sanitizing error payloads and analytics events before sending them to third-party crash trackers.""",
    "structured_en": """Eliminating credential leakage requires securing the side-channels through which sensitive data accidentally escapes application boundaries.
The first vector is system logging; in release configurations, we configure R8 rules to remove Logcat invocations entirely and employ Timber trees that discard debug messages.
The second vector is screen capture and recent task previews.
By applying WindowManager FLAG_SECURE to our activity windows, the Android system blocks screenshots, screen recording, and renders a blank preview card in the task switcher, protecting sensitive financial data from shoulder-surfing.
The third vector is third-party crash reporting and observability SDKs like Crashlytics and Sentry.
We implement custom exception filters that sanitize stack traces and redacting interceptors in OkHttp that scrub Authorization and Cookie headers before network logs are generated.
Finally, we enforce strict payload sanitization policies in our analytics tracking layer, ensuring that user tokens and personal identifiers are never attached to event parameters.""",
    "deep_senior_en": """In high-assurance mobile engineering, side-channel data leakage often exposes sensitive credentials long before an attacker attempts to break cryptographic storage.
Developers diligently encrypt local databases while inadvertently uploading plaintext bearer tokens to third-party analytics dashboards.
To establish robust defense-in-depth, we systematically seal each exfiltration vector at the architectural layer.
For application logging, relying on developer discipline to omit Log.d statements is an antipattern.
We enforce automated removal by instructing R8 with -assumenosideeffects to strip all android.util.Log calls from the release bytecode during compilation.
For the user interface layer, the operating system routinely captures screen snapshots when users navigate home, storing unencrypted bitmap images of the application state in system caches.
Applying WindowManager.LayoutParams.FLAG_SECURE prevents these snapshots from being written to disk and renders the window black in the recent apps overview.
For observability channels like Crashlytics and network monitoring, we treat third-party servers as untrusted sinks.
In OkHttp, we configure HttpLoggingInterceptor with explicit redactHeader rules for Authorization and Cookie headers, and disable body logging entirely in release builds.
In our crash reporting and analytics abstraction layers, we run all breadcrumb metadata and event bundles through a regex-based sanitization pipeline that detects and masks JWT patterns, credit card PAN numbers, and email addresses prior to SDK ingestion.
This guarantees that an infrastructure compromise at a third-party analytics vendor does not result in a catastrophic credential breach for our customers.""",
    "meta_ar": {
        "id": "SEC-15",
        "questionAr": "كيف تمنع تسريب الـ Tokens والبيانات الحساسة عبر الـ Logs ولقطات الشاشة وتقارير الانهيار والتحليلات؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تأمين قنوات تسريب البيانات الجانبية (Side-channel leakage)، وإلغاء الـ Logs في الإنتاج عبر R8، واستخدام FLAG_SECURE لحجب الشاشة ومعاينات المهام الحديثة، وتنقية ترويسات الشبكة في OkHttp، وحجب البيانات الحساسة من تقارير Crashlytics والـ Analytics.",
        "concept_ar": "تسريب البيانات الحساسة لا يحدث فقط عبر كسر التخزين المشفر، بل يتسلل عبر قنوات جانبية غير مقصودة مثل سجلات النظام (Logcat)، ومعاينات الشاشة في الـ Recent Apps، وتقارير الانهيار (Crashlytics)، وأدوات التحليلات (Analytics). تتطلب الحماية إزالة أوامر الـ Log بالكامل في الإنتاج عبر R8، وتفعيل FLAG_SECURE لحجب لقطات الشاشة ومعاينات النظام، وتشفير أو حجب ترويسات Authorization في OkHttp، وتطبيق فلاتر تنقية صارمة قبل إرسال الأحداث لأي طرف ثالث.",
        "walkthrough_ar": "تفعيل حماية الشاشة وتنقية ترويسات الشبكة وسجلات الأخطاء:\n```kotlin\n// 1. منع لقطات الشاشة ومعاينات المهام الأخيرة:\nwindow.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)\n\n// 2. حجب ترويسة Authorization في OkHttp:\nval logging = HttpLoggingInterceptor().apply {\n    redactHeader(\"Authorization\")\n    redactHeader(\"Cookie\")\n}\n\n// 3. تنقية البيانات المرسلة لـ Crashlytics:\nFirebaseCrashlytics.getInstance().setCustomKey(\"user_role\", safeRole)\n```",
        "why_it_matters_ar": "تسريب الرموز الحساسة عبر الـ Logs أو تقارير الأخطاء يجعلها متاحة للموظفين وأي مخترق يصل للوحة تحكم الطرف الثالث، مما يعرض بيانات المستخدمين للاختراق دون أي مجهود.",
        "worked_example_ar": "حذف دوال الـ Log نهائياً من الـ Bytecode في حزم الإنتاج عبر ProGuard:\n```proguard\n# إزالة كود الطباعة تماماً من الـ APK النهائي:\n-assumenosideeffects class android.util.Log {\n    public static boolean isLoggable(java.lang.String, int);\n    public static int v(...);\n    public static int d(...);\n    public static int i(...);\n}\n```",
        "trade_offs_ar": "تفعيل FLAG_SECURE يمنع المستخدم من التقاط لقطات شاشة لمعاملاته للمشاركة، وتجريد الـ Logs في الإنتاج يجعل تصحيح بعض الأخطاء النادرة أكثر صعوبة ويتطلب أدوات تتبع مخصصة.",
        "failure_modes_ar": "طباعة كائن الـ HTTP Response كاملاً في الـ Logcat بما يحويه من Access Token، أو ظهور رقم البطاقة الائتمانية في نافذة التطبيقات الحديثة عند تصغير التطبيق.",
        "production_perspective_ar": "في التطبيقات المالية، نجعل FLAG_SECURE مفعلاً افتراضياً في BaseActivity، ونحظر طباعة الـ Body في OkHttp في الإنتاج، ونراجع أحداث التحليلات للتأكد من خلوها من أي PII.",
        "how_to_answer_ar": "صنف الإجابة إلى أربعة محاور صريحة: سجلات النظام وحذفها عبر R8، وواجهات العرض وتأمينها بـ FLAG_SECURE، وتقارير الانهيار وتنقية ترويسات الشبكة، وأدوات التحليلات وفلترة البيانات قبل الإرسال.",
        "talking_points_ar": "قنوات التسريب الجانبية (Side channels)، وأمر FLAG_SECURE لحماية الشاشة، وقواعد R8 لحذف الـ Logs، وتنقية ترويسات OkHttp، وحماية الخصوصية في Crashlytics و Analytics.",
        "follow_ups_ar": "- **المحاور:** \"ما الذي يفعله FLAG_SECURE بالتحديد على مستوى نظام أندرويد؟\"\n  **المرشح:** \"يمنع تسجيل الشاشة والتقاط لقطات الشاشة، ويجعل بطاقة معاينة التطبيق فارغة أو سوداء في شاشة التطبيقات الحديثة Recents Overview لمنع حفظ صور الشاشات على القرص.\"\n\n- **المحاور:** \"هل يكفي الاعتماد على شرط if (BuildConfig.DEBUG) لمنع طباعة الـ Logs؟\"\n  **المرشح:** \"يفضل استخدام قواعد R8 لحذف كود الـ Log من الـ Bytecode بالكامل؛ لأن الشروط البرمجية قد تتعرض للخطأ البشري أو التجاوز أثناء تجميع الكود.\"",
        "self_check_ar": "هل غطيت المحاور الأربعة (Logs, Screenshots, Crash reports, Analytics)؟ هل شرحت FLAG_SECURE؟ وهل وضحت تنقية ترويسات OkHttp؟",
        "references_ar": f"- [Android WindowManager FLAG_SECURE](https://developer.android.com/reference/android/view/WindowManager.LayoutParams#FLAG_SECURE) — التوثيق الرسمي لحماية محتوى الشاشات والـ Task Snapshots.\n- [OkHttp HttpLoggingInterceptor Redaction](https://square.github.io/okhttp/features/interceptors/) — دليل تنقية الترويسات الحساسة في مكتبة OkHttp.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نمنع تسريب الرموز والبيانات الحساسة بحذف سجلات الـ Logs تماماً من كود الإنتاج عبر R8، واستخدام خاصية FLAG_SECURE لمنع لقطات الشاشة ومعاينات النظام، وحجب ترويسات Authorization في مفسرات شبكة OkHttp، وفلترة رسائل الأخطاء وأحداث التحليلات لحذف أي بيانات شخصية قبل إرسالها للخدمات السحابية.",
        "best_answer_ar": "يتطلب منع تسريب البيانات الحساسة إغلاق كافة القنوات الجانبية التي تتسلل منها الرموز بعيداً عن أعين المطورين.\n\nالقناة الأولى هي سجلات النظام Logcat؛ ونعالجها بحذف أوامر الطباعة نهائياً من بايت كود الإنتاج باستخدام قواعد R8 بدلاً من الاعتماد على الشروط البرمجية. والقناة الثانية هي لقطات الشاشة ومعاينات التطبيقات الحديثة؛ حيث نطبق خاصية WindowManager FLAG_SECURE على شاشات التطبيق الحساسة لمنع تسجيل الشاشة وجعل بطاقة التطبيق فارغة في شاشة المهام لحماية الخصوصية من أعين المتلصصين.\n\nوالقناة الثالثة هي طبقة الشبكة وتقارير الانهيار Crashlytics؛ حيث نلزم مفسرات OkHttp بحجب ترويسات تفويض الهوية Authorization وملفات الكوكيز تماماً، ونمنع طباعة محتوى الطلبات في الإنتاج. وأخيراً، نفرض طبقة فحص وسيطة في كود التحليلات Analytics تمنع تضمين التوكنز أو بيانات الدفع في معلمات الأحداث، مما يحمي المستخدمين حتى لو تعرضت خوادم التحليلات للاختراق.",
        "deep_answer_ar": "في تطبيقات التكنولوجيا المالية، ندرك أن التسريب الجانبي للبيانات Side-Channel Leakage هو السبب الأكثر شيوعاً لاختراق بيانات المستخدمين؛ فالمطور قد يجتهد في تشفير قاعدة البيانات لكنه يسرب الـ Bearer Token صراحة في سجلات السحابة أو منصات التحليلات.\n\nلإحكام السيطرة، نتعامل مع كل قناة خروج بيانات كمنطقة خطر غير موثوقة. بالنسبة لسجلات الـ Logcat، لا نعتمد على انتباه المطور، بل نلزم محرك R8 بأمر assumenosideeffects ليقوم بحذف استدعاءات android.util.Log بالكامل أثناء بناء الـ Release. وفي طبقة الواجهات، يقوم نظام أندرويد تلقائياً بأخذ لقطة شاشة وحفظها كملف Bitmap غير مشفر على القرص عند تصغير التطبيق؛ ولذلك نفعل FLAG_SECURE في كافة الشاشات الحساسة، مما يمنع حفظ تلك الصور ويجعل الشاشة سوداء في قائمة التطبيقات الحديثة.\n\nوفي قنوات المراقبة والشبكة، نضبط OkHttp بحجب ترويسات Authorization و Cookie صراحة باستخدام redactHeader، ونعطل طباعة كتل البيانات Body تماماً في حزم الإنتاج. أما في خدمات تقارير الأخطاء مثل Crashlytics أو Sentry، فنمرر كافة الرسائل والبيانات الوصفية عبر فلاتر فحص تعتمد على التعبيرات النمطية Regex لاكتشاف أنماط الـ JWT وأرقام البطاقات الائتمانية وحجبها واستبدالها بنصوص مبهمة قبل إرسالها لشبكة الإنترنت. ونلزم المهندسين بعدم طباعة كائنات Exception الخام في واجهات المستخدم لمنع تسريب أسرار السيرفر واستعلامات SQL."
    }
}

# ==========================================
# SEC-16: Why might CharArray be preferable to String for passwords, and what are its limitations?
# ==========================================
DATA["SEC-16"] = {
    "concept_en": """In high-security Android development, handling sensitive authentication secrets (such as master passwords, encryption passphrases, and user PINs) using mutable character arrays (CharArray) is fundamentally preferable to immutable Java/Kotlin String objects. In the JVM runtime, String instances are strictly immutable; once allocated on the heap, their internal char/byte buffers cannot be modified or cleared by application code. Strings frequently enter the JVM String Intern Pool, remaining in memory indefinitely until reclaimed by the garbage collector, whose execution timing and compaction sweeps are non-deterministic. If an attacker dumps process memory via root debugging, memory analysis tools, or unencrypted crash logs, plaintext passwords can be recovered from the heap hours after entry. Conversely, a CharArray is mutable, allowing developers to explicitly overwrite its memory contents with zeroes (Arrays.fill(chars, '0')) immediately after transmitting credentials over TLS. However, practical limitations exist: Android UI components (EditText, Jetpack Compose TextField) and network libraries (Retrofit, OkHttp) historically allocate immutable Strings or CharSequences internally, requiring specialized native or low-level bindings to achieve true end-to-end memory sanitization.""",
    "walkthrough_en": """Zeroing out character arrays and navigating Android UI String conversion boundaries:
```kotlin
// 1. Safe password memory hygiene with explicit finally zeroing
fun authenticateSecurely(passwordChars: CharArray, onFinished: () -> Unit) {
    try {
        // Transmit raw bytes over TLS directly without creating String objects
        sendCredentialsToAuthEndpoint(passwordChars)
    } finally {
        // Deterministically overwrite password memory with zeroes
        passwordChars.fill('0')
    }
    onFinished()
}

// 2. Practical limitations: Jetpack Compose TextField creates String allocations internally!
@Composable
fun PasswordInputField(onPasswordReady: (CharArray) -> Unit) {
    var passwordText by remember { mutableStateOf("") } // Limitation: String is allocated here!

    TextField(
        value = passwordText,
        onValueChange = { passwordText = it },
        visualTransformation = PasswordVisualTransformation(),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password)
    )
    
    Button(onClick = {
        val chars = passwordText.toCharArray()
        passwordText = "" // Clears state variable, but String object remains in heap pool!
        onPasswordReady(chars)
    }) {
        Text("Login")
    }
}
```""",
    "short_en": """CharArray is preferable to String because Strings are immutable and remain in JVM heap memory until garbage collected, whereas a CharArray is mutable and can be immediately wiped with zeroes after use. Its limitation on Android is that standard UI widgets and networking libraries frequently convert input into immutable Strings internally, requiring extra care to minimize heap exposure.""",
    "structured_en": """Handling raw passwords using CharArray instead of String is a recognized cryptographic best practice for memory confidentiality.
In Java and Kotlin, String objects are immutable, meaning their underlying memory buffers cannot be altered once allocated.
Strings linger in the JVM heap and the internal string pool for indeterminate periods until garbage collection runs, leaving sensitive passwords vulnerable to memory dumping tools, root inspection, and crash logs.
In contrast, a CharArray is a mutable array structure.
This allows developers to explicitly overwrite the array cells with zeroes in a finally block immediately after transmitting the password over a secure TLS connection, deterministically eliminating the secret from RAM.
However, this approach faces significant practical limitations on Android.
Standard UI widgets like EditText and Jetpack Compose TextField internally generate String and CharSequence allocations during text entry.
Furthermore, standard JSON serialization and HTTP networking libraries frequently expect String parameters, creating intermediate immutable copies in heap memory unless custom byte-level streaming buffers are implemented.""",
    "deep_senior_en": """The preference for CharArray over String in password management addresses the specific threat vector of cold-boot memory dumps and runtime heap inspection.
Because Strings are immutable, calling password = null does not destroy the character data; it merely dereferences the object pointer, leaving the plaintext characters in heap memory until the garbage collector sweeps and compacts that memory region.
In high-security environments, an attacker with root privileges or physical JTAG hardware access can dump the process memory map and easily extract intact passwords.
By utilizing a mutable CharArray, we gain deterministic memory control: executing Arrays.fill(passwordArray, '0') immediately after encryption or transmission overwrites the physical memory addresses with zeroes, neutralizing heap scraping.
However, a senior engineer must understand the severe systemic limitations of this practice on the Android platform.
The Android UI framework is fundamentally built around immutable CharSequence and String abstractions.
In Jetpack Compose, the BasicTextField state machine allocates Strings on every single keystroke.
In the traditional View system, Editable and SpannableStringBuilder allocate internal buffers that are not zeroed on text change.
Similarly, popular networking libraries like Retrofit and serialization libraries like Moshi default to String serialization.
Therefore, while using CharArray is a valuable defense-in-depth measure that prevents long-lived domain state from retaining plaintext passwords, achieving absolute zero-leakage requires extreme architectural measures, such as custom native C++ input interfaces or dedicated low-level byte streaming directly to the secure socket layer.""",
    "meta_ar": {
        "id": "SEC-16",
        "questionAr": "لماذا يُفضل استخدام CharArray على String لحفظ كلمات المرور في الذاكرة وما هي حدوده في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الفرق بين عدم قابلية تعديل String وقابلية تعديل CharArray في ذاكرة الـ JVM، والقدرة على تصفير الذاكرة يدوياً لمنع هجمات تفريغ الذاكرة (Heap Dumps)، واستيعاب القيود العملية الناتجة عن تعامل واجهات Compose و Views مع نصوص String داخلياً.",
        "concept_ar": "يُفضل استخدام مصفوفة المحارف (CharArray) على كائنات النصوص (String) لحفظ كلمات المرور والرموز السرية؛ لأن String غير قابلة للتعديل وتظل في ذاكرة الـ Heap و String Pool حتى يقرر جامع القمامة تفريغها مما يتيح استخراجها عند فحص الذاكرة. بينما CharArray قابلة للتعديل ويمكن كتابة أصفار فوقها فوراً في بلوك finally لمسحها من الرام. ولكن حدودها في أندرويد تكمن في أن عناصر الواجهة مثل EditText و Compose TextField تحول المدخلات إلى نصوص String داخلياً بالفعل.",
        "walkthrough_ar": "تصفير مصفوفة المحارف فور الاستخدام وتوضيح قيود عناصر الواجهة:\n```kotlin\nfun handlePassword(chars: CharArray) {\n    try {\n        // إرسال البيانات مباشرة عبر الشبكة\n        transmitSecurely(chars)\n    } finally {\n        // مسح محتوى الذاكرة يدوياً وحتمياً بالأصفار:\n        chars.fill('0')\n    }\n}\n// القيد العملي: في Compose ينتج TextField نصوص String مؤقتة في الـ State أثناء الكتابة\n```",
        "why_it_matters_ar": "الاحتفاظ بكلمات المرور كنصوص String في كلاسات التطبيق يبقيها في ذاكرة الرام لساعات، مما يسمح لأي أداة فحص ذاكرة باستخراج كلمة مرور المستخدم بصيغتها الصريحة.",
        "worked_example_ar": "التعامل المباشر مع مصفوفات البايتات عند تحويلها لـ CharArray دون إنشاء كائنات String إضافية:\n```kotlin\nfun wipeBuffer(buffer: CharArray) {\n    java.util.Arrays.fill(buffer, '\\u0000') // الكتابة فوق كل خانة بالصفر التشفيري\n}\n```",
        "trade_offs_ar": "استخدام CharArray يوفر أماناً وتحكماً حتمياً في الذاكرة، لكنه يعقد الكود البرمجي ويتعارض مع معظم مكتبات أندرويد والـ JSON التي تشترط نصوص String كمعلمات.",
        "failure_modes_ar": "تصفير مصفوفة الـ CharArray قبل اكتمال إرسال الطلب في الـ Coroutines الخلفية مما يفسد البيانات المرسلة، أو تحويل الـ CharArray إلى String أثناء التحويل لـ JSON مما يفقد التقنية فائدتها.",
        "production_perspective_ar": "في التطبيقات المصرفية، نتعامل مع كلمات المرور كـ CharArray في طبقة الدومين ونصفرها فوراً بعد التبادل، مع إدراكنا لحدود عناصر واجهة أندرويد والعمل على تقليل فترة بقاء النصوص في الذاكرة.",
        "how_to_answer_ar": "ابدأ بشرح سبب تفضيل CharArray (عدم قابلية String للتعديل وبقاؤها في الـ Heap)، ثم وضح كيف نكتب الأصفار فوق المصفوفة في finally، واشرح بأمانة هندسية حدود هذه التقنية في أندرويد بسبب عناصر الواجهة والمكتبات.",
        "talking_points_ar": "جمود نصوص String وعدم قابليتها للمسح، ومصفوفات CharArray وإعادة الكتابة بالأصفار، وهجمات فحص الذاكرة Heap Dumps، وقيود واجهات Compose و EditText، ومكتبات الشبكة والـ JSON.",
        "follow_ups_ar": "- **المحاور:** \"إذا كان Jetpack Compose ينشئ String داخلياً عند كتابة المستخدم، فهل هناك فائدة من استخدام CharArray في باقي التطبيق؟\"\n  **المرشح:** \"نعم، يفيد في تقليل مساحة الخطر (Blast Radius)؛ فنضمن عدم بقاء كلمة المرور في الـ ViewModels أو طبقة الدومين والشبكة لفترات طويلة، حتى لو تسربت نسخة مؤقتة في طبقة الواجهة.\"\n\n- **المحاور:** \"لماذا لا يقوم جامع القمامة (Garbage Collector) بحذف الـ String فور انتهاء الدالة؟\"\n  **المرشح:** \"لأن وقت تشغيل جامع القمامة غير حتمي (Non-deterministic)، وقد تظل النصوص في الذاكرة لساعات حتى يمتلئ الـ Heap ويقرر النظام بدء دورة التنظيف.\"",
        "self_check_ar": "هل شرحت الفرق بين String و CharArray في الـ Heap؟ هل بينت طريقة التصفير بـ fill('0')؟ وهل وضحت قيود عناصر واجهة أندرويد بأمانة؟",
        "references_ar": f"- [OWASP Mobile Security - Memory Management](https://mas.owasp.org/) — إرشادات OWASP لإدارة الذاكرة والتعامل مع الأسرار في تطبيقات الموبايل.\n- [Java Cryptography Architecture Guidelines](https://docs.oracle.com/javase/8/docs/technotes/guides/security/crypto/CryptoSpec.html) — توصيات أوراكل الرسمية لاستخدام CharArray بدلاً من String لكلمات المرور.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يُفضل استخدام CharArray لأن نصوص String غير قابلة للتعديل وتظل محتجزة في ذاكرة الـ Heap حتى يقرر جامع القمامة حذفها، بينما مصفوفة CharArray قابلة للتعديل ويمكن كتابة أصفار فوقها فوراً لمسحها من الرام. وتكمن حدودها في أن عناصر واجهات أندرويد ومكتبات الشبكة تحول المدخلات داخلياً إلى نصوص String، مما يجعل التخلص التام من النصوص في الذاكرة أمراً شاقاً.",
        "best_answer_ar": "يعتبر تفضيل مصفوفات المحارف CharArray على نصوص String معياراً أمنياً معترفاً به للتحكم في سرية البيانات في الذاكرة الحية.\n\nفي بيئة تشغيل جافا وكوتلن، تعتبر نصوص String غير قابلة للتعديل نهائياً؛ فبمجرد إنشائها لا يمكن للمطور مسحها أو تعديل بايتاتها، وتظل محتجزة في الـ Heap والـ String Pool لفترات طويلة غير معلومة حتى يقرر جامع القمامة تنظيفها، مما يعرضها للاستخراج عبر تفريغ الذاكرة أو أدوات الروت. في المقابل، تعتبر CharArray مصفوفة قابلة للتعديل؛ مما يمكننا من كتابة أصفار فوق خلاياها في كتلة finally فور إرسال كلمة المرور عبر الشبكة المشفرة ومحوها تماماً من الرام.\n\nومع ذلك، تفرض بيئة أندرويد قيوداً عملية حقيقية؛ فعناصر إدخال النصوص مثل EditText وحقول Jetpack Compose تقوم بإنشاء وتخزين كائنات String تلقائياً أثناء كتابة المستخدم لكل حرف. كما أن معظم مكتبات الشبكة وتحويل الـ JSON تطلب نصوص String؛ ولذلك فإن استخدام CharArray يقلل زمن بقاء السر في طبقات التطبيق العليا لكنه لا يضمن انعدام النصوص تماماً في الذاكرة دون بناء واجهات إدخال منخفضة المستوى.",
        "deep_answer_ar": "يرتبط تفضيل CharArray على String بالنمذجة التهديدية الموجهة ضد هجمات قراءة الذاكرة الحية Heap Scraping واستخراج محتويات الرام عبر تفريغ الذاكرة أو أدوات التصحيح بوجود صلاحيات الروت.\n\nعندما نستخدم كائن String لكلمة المرور ونضع المتغير بقيمة فارغة، فنحن نحذف المرجع فقط بينما تظل الحروف الصريحة مستقرة في خلايا الذاكرة حتى يقرر الـ Garbage Collector جمعها وضغط الذاكرة، وهو أمر غير حتمي التوقيت على الإطلاق. أما باستخدام CharArray، فنحن نمتلك تحكماً فيزيائياً في الذاكرة يتيح لنا استدعاء Arrays.fill بكتابة الصفر التشفيري فوق كل خانة بمجرد اكتمال التشفير أو الإرسال، مما يعدم السر برمجياً في نفس اللحظة.\n\nلكن المهندس السينيور يجب أن ينظر للواقع العملي لنظام أندرويد بنظرة نقدية؛ فالنظام مبني تاريخياً حول تجريدات CharSequence و String غير القابلة للتعديل. ففي Jetpack Compose ينشئ BasicTextField نصوص String متكررة مع كل ضغطة زر في الـ State، ومكتبات مثل Retrofit و Moshi تعتمد على الـ String في تجميع حزم الـ HTTP. لذلك، يظل استخدام CharArray خطاً دفاعياً ممتازاً لحماية طبقات الأعمال والدومين من احتجاز كلمات المرور طويلاً، مع إدراك أن التصفير الكامل من البداية للنهاية يتطلب واجهات كتابة خاصة عبر C++ NDK للتعامل مع الذاكرة الخام مباشرة."
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

    ee.save_topic_metadata("sec_09_16", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print("\nAll 8 SEC questions (SEC-09 to SEC-16) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
