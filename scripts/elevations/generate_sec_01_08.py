#!/usr/bin/env python3
"""Generator for SEC-01 through SEC-08 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sec.json"

SEC_01_08 = [
    {
        "id": "SEC-01",
        "arabic_explanation": (
            "ما هو نموذج العزل الأمني (Application Sandbox) ونظام الصلاحيات (Permission Model) في Android، وما هي حدوده الحقيقية؟\n\n"
            "1. معمارية الـ Application Sandbox على مستوى نواة Linux:\n   - كل تطبيق أندرويد يتم تثبيته يُعامل كـ **مستخدم نظام Linux مستقل تماماً** وله معرف مستخدم فريد (Unique Linux UID مثل `u0_a145`).\n   - يعمل كل تطبيق داخل عملية مستقلة (Isolated Process) ومساحة ذاكرة خاصة به، ويمتلك مجلداً خاصاً مشفراً للملفات (`/data/data/<package_name>/`) بأذونات حصرية (`rwx------`).\n   - لا يستطيع أي تطبيق آخر على الهاتف قراءة ملفات تطبيقك أو التجسس على الذاكرة أو حقن كود، إلا إذا اشترك التطبيقان في نفس شهادة التوقيع (Shared User ID).\n   - كل اتصال بين التطبيقات يمر عبر **Binder IPC** الذي يفحص هوية المتصل (`Binder.getCallingUid()`).\n\n"
            "2. نظام الصلاحيات (Android Permission Model):\n   - **صلاحيات عادية (Normal Permissions)**: تُمنح تلقائياً عند التثبيت (مثل الوصول للإنترنت `android.permission.INTERNET`).\n   - **صلاحيات خطرة (Dangerous / Runtime Permissions)**: تتطلب موافقة المستخدم الصريحة أثناء التشغيل (الموقع، الكاميرا، الميكروفون، الإشعارات).\n   - **صلاحيات خاصة (Special Permissions)**: تتطلب توجيه المستخدم لصفحة إعدادات النظام (مثل ظهور فوق التطبيقات `SYSTEM_ALERT_WINDOW` أو إدارة الملفات `MANAGE_EXTERNAL_STORAGE`).\n\n"
            "3. حدود الـ Sandbox والافتراضات الخاطئة (The Sandbox Boundaries):\n   - الـ Sandbox يحمي التطبيق من **التطبيقات الأخرى العادية**، ولكنه **لا يحمي التطبيق إذا كان الجهاز نفسه مخترقاً (Rooted Device)** أو إذا كان نظام التشغيل معدلاً (Compromised OS).\n   - مستخدم الـ Root يمتلك UID 0، ويستطيع تجاوز صلاحيات Linux وقراءة مجلد `/data/data/` بالكامل وتفريغ الذاكرة (RAM Dump) واستخراج التوكنز غير المشفرة!"
        ),
        "practical_walkthrough": (
            "التحقق من هوية المتصل عبر Binder IPC ومنع الثغرات الأمنية في المكونات المصدرة:\n"
            "```kotlin\n"
            "// ❌ ثغرة أمنية: تصدير Service أو ContentProvider بدون فحص UID المتصل:\n"
            "class VulnerablePaymentService : Service() {\n"
            "    override fun onBind(intent: Intent): IBinder = object : IPaymentService.Stub() {\n"
            "        override fun transferMoney(amount: Long, toAccount: String) {\n"
            "            // أي تطبيق خبيث على الهاتف يستطيع استدعاء هذه الدالة وسرقة الأموال!\n"
            "            executeTransfer(amount, toAccount)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ تأمين Binder IPC بفحص UID والتحقق من التوقيع الرقمي للمتصل (Signature Permission):\n"
            "class SecurePaymentService : Service() {\n"
            "    override fun onBind(intent: Intent): IBinder = object : IPaymentService.Stub() {\n"
            "        override fun transferMoney(amount: Long, toAccount: String) {\n"
            "            val callingUid = Binder.getCallingUid()\n"
            "            val callingPackage = packageManager.getNameForUid(callingUid)\n"
            "            \n"
            "            // 1. فحص الصلاحية عبر Signature-level permission:\n"
            "            if (checkCallingOrSelfPermission(\"com.example.permission.TRUSTED_PAYMENT\") != PackageManager.PERMISSION_GRANTED) {\n"
            "                throw SecurityException(\"Unauthorized caller: UID $callingUid ($callingPackage)\")\n"
            "            }\n"
            "            \n"
            "            executeTransfer(amount, toAccount)\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Android's application sandbox enforces process and storage isolation at the Linux kernel level by assigning each app a unique Linux UID and private directory. The permission model gates device capabilities across install-time, runtime, and special tiers. However, the sandbox only protects against peer apps; on rooted devices, root access bypasses UID isolation completely.",
        "best_answer": (
            "The Android security sandbox is built on multi-user Linux kernel primitives rather than JVM boundaries:\n\n"
            "1. **Linux UID Isolation**: During installation, Android assigns each application a unique, non-privileged Linux User ID (e.g. `u0_a145`). The process runs with this UID, and its internal storage directory (`/data/data/<package>/`) is restricted with file permissions `0700`. Other apps running under different UIDs are blocked by the kernel from reading memory, inspecting files, or intercepting threads.\n\n"
            "2. **Binder IPC Mediation**: Inter-process communication across components (Activities, Services, Providers) is brokered by the Linux Binder driver. Binder guarantees the cryptographic authenticity of `Binder.getCallingUid()`, allowing services to enforce permission checks before executing sensitive methods.\n\n"
            "3. **Permission Hierarchy**: Access to hardware and sensitive user data is gated by permissions: Normal (granted at install), Dangerous/Runtime (biometrics, camera, location required explicit user prompt), and Special App Access (exact alarms, all-files access).\n\n"
            "The critical boundary to understand: **The sandbox assumes the underlying kernel and hardware are uncompromised**. On rooted devices or emulators with UID 0 (root), kernel boundaries dissolve: an attacker can dump app RAM, attach debuggers, and read private files directly."
        ),
        "deep_answer": (
            "From an OS security architecture perspective, Android adds multiple layers beyond pure UID isolation:\n\n"
            "1. **SELinux (Security-Enhanced Linux)**: Enforces Mandatory Access Control (MAC) in enforcing mode. Even if an attacker finds an exploit giving them UID 0 inside a sandboxed daemon, SELinux domain policies restrict what files, device nodes, and system calls that domain can access, preventing privilege escalation into the core kernel.\n\n"
            "2. **Seccomp Filters**: Restricts available system calls for app processes. Zygote installs a restrictive BPF filter blocking dangerous syscalls (like raw socket creation or kernel module loading) before forking an application process.\n\n"
            "Despite these defenses, senior engineers adopt a **Zero Trust Client Model**: never treat client-side validation as authoritative. A modified APK on a rooted device can hook Binder, patch Dalvik bytecode, or alter memory variables. All business authorization, price checks, and security invariants must be verified on the server."
        ),
        "follow_ups": [
            {
                "question": "Can two different apps share the same Linux UID?",
                "answer": "Historically yes, using `sharedUserId` in the Manifest if signed with the exact same developer certificate; however, Google deprecated `sharedUserId` in API 29 due to security and update risks."
            },
            {
                "question": "What is the difference between `checkCallingPermission` and `enforceCallingPermission`?",
                "answer": "`checkCallingPermission` returns `PERMISSION_GRANTED` or `PERMISSION_DENIED` as an integer; `enforceCallingPermission` immediately throws a `SecurityException` if the caller lacks the permission."
            }
        ]
    },
    {
        "id": "SEC-02",
        "arabic_explanation": (
            "ما هو Android Keystore وما هو التخزين المدعوم عتادياً (Hardware-Backed Key Storage - TEE / StrongBox)؟\n\n"
            "1. ما هو Android Keystore ولماذا يختلف عن التخزين العادي؟\n   - في التشفير العادي، إذا أنشأت مفتاح تشفير في كود Kotlin، فإن مصفوفة البايتات (`ByteArray`) الخاصة بالمفتاح تكون موجودة في ذاكرة الـ RAM الخاصة بالتطبيق. إذا كان الجهاز Rooted، يمكن للمهاجم استخراج المفتاح من الـ RAM بسهولة!\n   - **Android Keystore System** صُمم لحل هذه المشكلة جذرياً: **المفتاح لا يدخل ذاكرة التطبيق إطلاقاً (Non-Exportable Key Material)**.\n   - يتم إنشاء المفتاح وحفظه داخل مخزن مشفر خاص بالنظام. التطبيق لا يملك المفتاح؛ بل يملك فقط مرجعاً له (Alias/Handle). عندما يريد التطبيق تشفير أو فك تشفير نص، يرسل النص إلى الـ Keystore، فيقوم الـ Keystore بإجراء التشفير داخلياً وإعادة النص المشفر للتطبيق دون أن يرى التطبيق بايتات المفتاح الحقيقية أبداً!\n\n"
            "2. مستويات الأمان العتادي (Hardware-Backed TEE vs. StrongBox):\n   - **Software Fallback (برمجي)**: في الهواتف القديمة أو المحاكيات، يُخزن المفتاح برمجياً (أقل أماناً).\n   - **TEE (Trusted Execution Environment)**: بيئة تنفيذ معزولة عتادياً تعمل على معالج مستقل (مثل ARM TrustZone) داخل نفس شريحة الـ SoC. نظام Android الرئيسي (Linux) لا يملك وصولاً لذاكرة الـ TEE.\n   - **StrongBox Keymaster (أعلى درجات الأمان)**: شريحة عتادية مادية منفصلة تماماً ومقاومة للتلاعب الفيزيائي (Dedicated Secure Hardware / HSM مثل شريحة Titan M في هواتف Pixel). تمتلك معالجها الخاص وذاكرتها الخاصة وساعتها الخاصة."
        ),
        "practical_walkthrough": (
            "توليد مفتاح AES-256 مشفر مدعوم عتادياً داخل Android Keystore مع دعم StrongBox:\n"
            "```kotlin\n"
            "class KeystoreManager {\n"
            "    private val KEY_ALIAS = \"user_auth_secret_key\"\n"
            "    private val ANDROID_KEYSTORE = \"AndroidKeyStore\"\n"
            "\n"
            "    fun getOrCreateSecretKey(context: Context): SecretKey {\n"
            "        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }\n"
            "        \n"
            "        // 1. التحقق مما إذا كان المفتاح موجوداً مسبقاً:\n"
            "        if (keyStore.containsAlias(KEY_ALIAS)) {\n"
            "            val entry = keyStore.getEntry(KEY_ALIAS, null) as KeyStore.SecretKeyEntry\n"
            "            return entry.secretKey\n"
            "        }\n"
            "\n"
            "        // 2. توليد مفتاح AES-256 جديد غير قابل للاستخراج داخل العتاد:\n"
            "        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE)\n"
            "        val keyGenSpec = KeyGenParameterSpec.Builder(\n"
            "            KEY_ALIAS,\n"
            "            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT\n"
            "        )\n"
            "            .setBlockModes(KeyProperties.BLOCK_MODE_GCM) // الوضع الآمن Authenticated Encryption\n"
            "            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)\n"
            "            .setKeySize(256)\n"
            "            // طلب تخزين المفتاح في StrongBox المادي إذا كان عتاد الجهاز يدعمه (Android 9+):\n"
            "            .setIsStrongBoxBacked(context.packageManager.hasSystemFeature(PackageManager.FEATURE_STRONGBOX_KEYSTORE))\n"
            "            .build()\n"
            "\n"
            "        keyGenerator.init(keyGenSpec)\n"
            "        return keyGenerator.generateKey() // المفتاح تم إنشاؤه داخل العتاد ولا يمكن تصديره أبداً!\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Android Keystore generates and stores cryptographic keys in isolated environments so key material is never exposed in the app's RAM. Hardware-backed storage leverages a TEE (ARM TrustZone) or a dedicated StrongBox chip (hardware HSM), preventing key extraction even if the device's Android OS or Linux kernel is fully rooted.",
        "best_answer": (
            "The Android Keystore system fundamentally changes key management by making cryptographic key material **non-exportable**:\n\n"
            "1. **Non-Exportable Key Material**: In software cryptography, AES keys exist in JVM heap memory as raw byte arrays, easily dumpable via Frida or memory dump tools on rooted devices. With Android Keystore, the private/secret key never enters the application process. The app receives an opaque handle (`Key`), delegating encryption/decryption operations to system security daemons.\n\n"
            "2. **Hardware-Backed Isolation Tiers**:\n   - **TEE (Trusted Execution Environment)**: Runs on the primary SoC using hardware virtualization (e.g., ARM TrustZone). Cryptographic operations run under a microkernel isolated from the Android Linux kernel.\n   - **StrongBox Keymaster (API 28+)**: A physically separate, tamper-resistant hardware security module (HSM, such as Google Titan M or Samsung Knox Vault). StrongBox has its own dedicated CPU, secure storage, and true random number generator, resisting physical hardware side-channel attacks.\n\n"
            "3. **Security Boundary Distinction**: Hardware-backed Keystore protects **keys from extraction**, but it does not protect the plaintext data *after* decryption in application RAM."
        ),
        "deep_answer": (
            "How does Keymaster/KeyMint verify hardware backing programmatically?\n\n"
            "Senior engineers inspect key properties using the `KeyFactory` / `SecretKeyFactory` info spec:\n\n"
            "```kotlin\n"
            "val factory = SecretKeyFactory.getInstance(key.algorithm, \"AndroidKeyStore\")\n"
            "val keyInfo = factory.getKeySpec(key, KeyInfo::class.java) as KeyInfo\n"
            "val isInsideSecureHardware = keyInfo.isInsideSecureHardware\n"
            "val securityLevel = keyInfo.securityLevel // SECURITY_LEVEL_TRUSTED_ENVIRONMENT or STRONGBOX\n"
            "```\n\n"
            "If `isInsideSecureHardware` returns false, the key is stored in software (legacy software Keymaster emulation), which is vulnerable to kernel-level exploitation on rooted devices. In high-assurance fintech and banking apps, policies can mandate that high-value operations proceed only when `keyInfo.isInsideSecureHardware == true`."
        ),
        "follow_ups": [
            {
                "question": "Can you backup and restore Android Keystore keys to Google Drive?",
                "answer": "No. Hardware-backed Keystore keys are tied physically to the specific device's secure hardware and can never be exported or restored onto another device."
            },
            {
                "question": "What happens if a user removes their device lockscreen PIN?",
                "answer": "Keys generated with `.setUserAuthenticationRequired(true)` are permanently invalidated and deleted by the Keystore system."
            }
        ]
    },
    {
        "id": "SEC-03",
        "arabic_explanation": (
            "مقارنة شاملة بين 5 أنواع من بيانات الاعتماد الحساسة في Android:\nالمفاتيح التشفيرية، و Access Tokens، و Refresh Tokens، و API Keys، وكلمات المرور:\n\n"
            "1. Cryptographic Keys (المفاتيح التشفيرية - مثل AES / RSA / ECC):\n   - **طبيعتها**: أرقام باينري عشوائية تُستخدم للعمليات الرياضية (تشفير، فك تشفير، توقيع رقمي HMAC أو RSA).\n   - **مكان حفظها**: حصرياً داخل `AndroidKeyStore` المدعوم عتادياً.\n   - **فترة البقاء**: طويلة جداً (أشهر أو سنوات) حتى إعادة تثبيت التطبيق أو إبطالها.\n\n"
            "2. Access Tokens (توكنز الوصول المؤقتة - مثل JWT Bearer Tokens):\n   - **طبيعتها**: تصريح دخول قصير المدى يحمله العميل في كل طلب شبكة (`Authorization: Bearer <token>`).\n   - **مكان حفظها**: في الذاكرة (RAM) أو في تخزين مشفر بمفتاح Keystore (Encrypted DataStore).\n   - **فترة البقاء**: قصيرة جداً (15 دقيقة إلى ساعة واحدة) لتقليل ضرر التسريب.\n\n"
            "3. Refresh Tokens (توكنز التجديد طويلة المدى):\n   - **طبيعتها**: بيانات اعتماد سرية تُستخدم فقط لاستدعاء سيرفر المصادقة لإصدار Access Token جديد.\n   - **مكان حفظها**: مخزن مشفر عالي الحماية (Android Keystore + Encrypted Storage).\n   - **فترة البقاء**: طويلة (أيام أو أسابيع)، ويتم تجديدها مع كل استخدام (Refresh Token Rotation).\n\n"
            "4. API Keys (مفاتيح واجهات الطرف الثالث - مثل Google Maps API Key):\n   - **طبيعتها**: معرفات عامة للمشروع (Public Identifiers) لتتبع الاستهلاك وإصدار الفواتير لدى Google أو Firebase.\n   - **تحذير خطير**: **ليست أسراراً (Not Secrets)**! أي مفتاح مدمج في ملف الـ APK يمكن استخراجه في 3 ثوانٍ بواسطة `apktool`! يجب تقييدها عبر لوحة تحكم Google Cloud بقيود الحزمة وبصمة التوقيع (Package Name + SHA-1 Restriction).\n\n"
            "5. Passwords / PINs (كلمات المرور والرموز السرية للمستخدم):\n   - **طبيعتها**: بيانات اعتماد يدخلها المستخدم لإثبات هويته.\n   - **قاعدة ذهبية**: لا تحفظ كلمات المرور كـ Plaintext في التخزين المحلي أبداً! استبدلها بـ Session Tokens فور تسجيل الدخول، ومسح الـ CharArray من الذاكرة فوراً."
        ),
        "practical_walkthrough": (
            "جدول المقارنة المعمارية بين أنواع بيانات الاعتماد الخمسة في Android:\n"
            "```text\n"
            "┌────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬─────────────────────────┐\n"
            "│ نوع الاعتماد       │ الغرض المعماري       │ فترة الحياة (TTL)    │ مكان التخزين الآمن   │ الإجراء عند التسريب     │\n"
            "├────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤\n"
            "│ Cryptographic Key  │ تشفير وتوقيع رقمي    │ دائمة (حتى الإلغاء)  │ Android Keystore (HW)│ إبطال وإعادة توليد محلي │\n"
            "│ Access Token       │ مصادقة طلبات الشبكة  │ قصيرة (15-60 دقيقة)  │ Encrypted DataStore  │ انتهاء الصلاحية التلقائي│\n"
            "│ Refresh Token      │ تجديد Access Token   │ متوسطة (14-30 يوماً) │ Encrypted DataStore  │ إبطال الجلسة في السيرفر │\n"
            "│ API Key (APK)      │ تتبع الاستهلاك والفوترة│ دائمة                │ BuildConfig/Manifest │ قيود SHA-1 + PackageName│\n"
            "│ Password / PIN     │ إثبات هوية المستخدم  │ عابرة في الذاكرة     │ لا تُخزن أبداً محلياً│ تغيير كلمة المرور فوراً │\n"
            "└────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴─────────────────────────┘\n"
            "```"
        ),
        "quick_answer": "Cryptographic keys perform local crypto inside Keystore. Access tokens authenticate API requests with short lifespans (15-60m). Refresh tokens obtain new access tokens and require rotation and secure storage. APK API keys are public client identifiers (not secrets) secured via Google Cloud SHA-1 restrictions. Passwords authenticate users and must never be stored locally.",
        "best_answer": (
            "A senior engineer establishes strict threat models and retention boundaries across these five distinct credential types:\n\n"
            "1. **Cryptographic Keys (AES/RSA/ECC)**: Mathematical keys used to encrypt data or sign tokens. Protected exclusively inside hardware-backed `AndroidKeyStore`. They never leave secure hardware and cannot be inspected over the network.\n\n"
            "2. **Access Tokens (JWT / Bearer Tokens)**: Ephemeral proofs of authorization granted to an authenticated client. They have short lifespans (15 to 60 minutes) to minimize damage if intercepted in memory. Kept in memory or encrypted persistent storage.\n\n"
            "3. **Refresh Tokens**: Long-lived credentials (days to months) used solely to issue fresh access tokens. Held in encrypted storage and rotated on every use (Refresh Token Rotation). Revocable server-side.\n\n"
            "4. **API Keys (Embedded in APK)**: Client identifiers (Google Maps, Mixpanel, Firebase). **These are never secrets**. Anyone who downloads the APK can decompile it and read the string. They must be protected on the cloud provider side via IP, Package Name, and SHA-1 signing certificate restrictions.\n\n"
            "5. **Passwords / PINs**: User-provided secrets used to establish identity. Never store raw passwords on the device. Transmit over TLS to exchange for session tokens, wiping password buffers from RAM immediately."
        ),
        "deep_answer": (
            "The Architectural Fallacy of 'Hiding' Third-Party Backend Secrets in an APK:\n\n"
            "Teams frequently ask: 'Where should I store our Stripe Secret Key or OpenAI Private API Key in our Android app? In NDK C++? Obfuscated with XOR? In local.properties?'\n\n"
            "**The Senior Answer: Nowhere in the APK!**\n"
            "A distributed Android APK is entirely in the hands of the client (attacker). No amount of ProGuard, NDK C++ compilation, or XOR encoding will prevent an attacker with Frida, Ghidra, or Wireshark from extracting the private key. "
            "Private API keys must reside **exclusively on your backend server**. The Android client authenticates to your backend with a user session token, and your backend proxies requests to Stripe or OpenAI using the private key."
        ),
        "follow_ups": [
            {
                "question": "Why is an APK API key like Google Maps safe to ship in an APK?",
                "answer": "Because Google Maps verifies requests by checking the client's HTTP Referer or Android Package Name and SHA-1 certificate fingerprint against the Google Cloud Console allowlist."
            },
            {
                "question": "What is the difference between an Access Token and an API Key?",
                "answer": "An API key identifies the client application or project; an Access token identifies a specific authenticated user session with specific scopes."
            }
        ]
    },
    {
        "id": "SEC-04",
        "arabic_explanation": (
            "لماذا لا يعتبر ملف `local.properties` آلية أمان في وقت التشغيل (Runtime Security Mechanism) في Android؟\n\n"
            "1. ما هو ملف `local.properties` الحقيقي؟\n   - هو ملف نصي محلي على جهاز المطور يُستخدم لتكوين مسار الـ Android SDK وتخزين متغيرات البناء المحلية دون رفعها إلى نظام التحكم بالنسخ Git (`.gitignore`).\n   - إذا قمت بقراءة مفتاح من `local.properties` في ملف `build.gradle.kts` وحقنه في `BuildConfig`:\n     `buildConfigField(\"String\", \"API_KEY\", \"\\\"$apiKey\\\"\")`\n\n"
            "2. لماذا لا يوفر أي أمان على الإطلاق في وقت التشغيل؟\n   - أثناء عملية التجميع (Build Time)، يقوم مترجم Gradle بتوليد كلاس Java عادي يسمى `BuildConfig.java`.\n   - يتم تضمين القيمة كنص صريح (Plaintext String) داخل ملف الـ `classes.dex` النهائي داخل الـ APK!\n   - أي شخص يقوم بتنزيل تطبيقك يستطيع فتح الـ APK بأداة مثل `jadx-gui` أو كتابة أمر واحد في سطر الأوامر:\n     `strings classes.dex | grep \"my_secret_key\"`\n     ويحصل على المفتاح في 2 ثانية فقط!\n\n"
            "3. الفائدة الحقيقية لـ `local.properties`:\n   - هو فقط آلية لمنع تسريب المفاتيح في مستودعات Git العامة (Git Leak Prevention). لا علاقة له بأمان الـ APK ضد الهندسة العكسية."
        ),
        "practical_walkthrough": (
            "توضيح كيفية استخراج أي مفتاح موضوع في BuildConfig من ملف APK مجمع:\n"
            "```kotlin\n"
            "// ❌ الوهم الأمني: المطور يعتقد أن حقن المفتاح من local.properties يجعله آمناً:\n"
            "// في build.gradle.kts:\n"
            "val secretKey = gradleLocalProperties(rootDir, providers).getProperty(\"PAYMENT_GATEWAY_SECRET\")\n"
            "android.defaultConfig {\n"
            "    buildConfigField(\"String\", \"PAYMENT_SECRET\", \"\\\"$secretKey\\\"\")\n"
            "}\n"
            "\n"
            "// في كود التطبيق:\n"
            "val apiSecret = BuildConfig.PAYMENT_SECRET\n"
            "\n"
            "// كيف يستخرجه أي مهاجم أو فاحص أمني في ثانيتين؟\n"
            "// 1. فك ضغط ملف الـ APK:\n"
            "// unzip app-release.apk\n"
            "// 2. البحث عن النصوص الصريحة في ملف الـ DEX المجمع:\n"
            "// strings classes.dex | grep \"sk_live_\"\n"
            "// -> النتيجة: sk_live_51MzaB... (المفتاح السري مكشوف بالكامل بدون الحاجة حتى لأدوات Decompiler!)\n"
            "```"
        ),
        "quick_answer": "local.properties keeps secrets out of Git version control during development, but compiling values into BuildConfig embeds them as plaintext strings inside the APK's classes.dex file. Anyone can extract them in seconds using standard tools like jadx or strings.",
        "best_answer": (
            "A pervasive misconception among Android developers is conflating **Source Control Hygiene** with **Runtime Binary Confidentiality**:\n\n"
            "1. **What `local.properties` Actually Does**: It prevents developers from accidentally committing credentials to public or shared Git repositories. It is strictly a build-time configuration tool for the local developer machine.\n\n"
            "2. **Why It Provides Zero Runtime Security**: When Gradle reads a property from `local.properties` and injects it via `buildConfigField`, the Kotlin/Java compiler embeds the raw string literal directly into `BuildConfig.class`. During D8/R8 compilation, the string literal is placed into the APK's `classes.dex` string constant pool.\n\n"
            "3. **Trivial Extraction**: An attacker does not need sophisticated reverse engineering skills. Running `jadx` or executing `strings classes.dex | grep -i key` on the distributed APK dumps the secret in plain text.\n\n"
            "Private backend API secrets (payment gateway private keys, database master credentials, encryption secret seeds) must **NEVER** be present anywhere in the Android build system. They must reside exclusively on authenticated backend servers."
        ),
        "deep_answer": (
            "Does using Native NDK C++ (`CMake` / `.so` libraries) hide secrets injected from Gradle?\n\n"
            "Some teams inject secrets from `local.properties` into C/C++ files via CMake compiler flags, believing that compiling to native machine code (`.so`) protects the secret.\n\n"
            "This is also completely ineffective. Running `strings libnative-lib.so | grep -i secret` or opening the library in Ghidra / IDA Pro reveals the string in the `.rodata` (read-only data) section of the ELF binary in seconds. "
            "Even if obscured with XOR masking in C++, dynamic hooking tools like Frida intercept the function that returns the decoded buffer at runtime with a 3-line JavaScript script. Client-side secrecy in distributed binaries is fundamentally impossible."
        ),
        "follow_ups": [
            {
                "question": "What is the only valid way to protect a private payment API key?",
                "answer": "Keep the private key on your company's backend server; the Android app authenticates to your backend, and your backend communicates with the payment provider."
            },
            {
                "question": "Should Google Maps API keys be kept in `local.properties`?",
                "answer": "Yes, to keep them out of Git, but remember that the key is public in the APK and must be secured via Google Cloud SHA-1 restrictions."
            }
        ]
    },
    {
        "id": "SEC-05",
        "arabic_explanation": (
            "هل يمكن لأي مفتاح سري (API Secret) مدمج داخل ملف APK أن يظل سرياً ومحمياً تماماً من الاستخراج؟\n\n"
            "1. الإجابة الهندسية القاطعة: **لا، مستحيل فيزيائياً وبرمجياً (Mathematically & Architecturally Impossible)**.\n   - السبب الأساسي: **الـ Threat Model للأجهزة الطرفية (Untrusted Client Environment)**.\n   - عندما تنشر ملف الـ APK في متجر التطبيقات، فإنك تسلم كود التطبيق، وبياناته، وبيئة تشغيله بالكامل للمستخدم/المهاجم.\n   - المهاجم يمتلك العتاد الفيزيائي، والـ Root، والـ Kernel، والـ Memory، ونظام التشغيل.\n\n"
            "2. لماذا تفشل جميع حيل إخفاء الأسرار على الكلاينت؟\n   - **التعتيم بـ ProGuard/R8**: يعيد تسمية الكلاسات والدوال، لكنه **لا يشفر النصوص الصريحة (String Literals)**.\n   - **التخزين في مكتبات C++ NDK**: تظهر النصوص فوراً في قسم `.rodata` باستخدام أمر `strings` أو في برنامج Ghidra.\n   - **تشفير النصوص بـ XOR أو AES داخل الكود**: لكي يستخدم التطبيق المفتاح لإرسال طلب HTTP، يجب أن يفك تشفيره أولاً في الـ RAM. يستطيع المهاجم استخدام أداة **Frida** لربط الدالة (`hook`) وقراءة المفتاح بعد فك تشفيره في لحظة واحدة!\n   - **مراقبة الشبكة (Network Interception)**: إذا تم استخدام المفتاح كـ Header، يراه المهاجم في Charles Proxy أو Burp Suite.\n\n"
            "3. القاعدة المعمارية المطلقة لمهندسي Android الكبار:\n   - **أي شيء داخل الـ APK هو كود علني للجميع (Public Knowledge)**.\n   - لا تضع في الـ APK سوى **معرفات عامة مقيدة (Restricted Identifiers)**.\n   - الأسرار الحقيقية مكانها الوحيد هو **الخوادم المؤمنة (Secure Backend Servers)**."
        ),
        "practical_walkthrough": (
            "كيف يستخرج المهاجم أي مفتاح سري مهما كانت حيل التعتيم المعقدة المستخدمة عبر Frida:\n"
            "```kotlin\n"
            "// كلاس أندرويد يحاول إخفاء المفتاح بتشفير معقد ومكتبة C++:\n"
            "class ObfuscatedSecretProvider {\n"
            "    external fun getDecryptedApiKey(): String // كود C++ يفك تشفير المفتاح بمصفوفات XOR معقدة\n"
            "}\n"
            "```\n"
            "\n"
            "```javascript\n"
            "// سكربت Frida من سطرين يكتبه أي باحث أمني لتجاوز كل هذا التعتيم في ثانية واحدة:\n"
            "Java.perform(function () {\n"
            "    var SecretProvider = Java.use('com.example.ObfuscatedSecretProvider');\n"
            "    SecretProvider.getDecryptedApiKey.implementation = function () {\n"
            "        var secret = this.getDecryptedApiKey(); // استدعاء الدالة الأصلية\n"
            "        console.log('[+] EXTRACTED SECRET KEY: ' + secret); // طباعة المفتاح بعد فك تشفيره!\n"
            "        return secret;\n"
            "    };\n"
            "});\n"
            "// النتيجة: طباعة المفتاح فوراً في شاشة المهاجم بمجرد فتح التطبيق!\n"
            "```"
        ),
        "quick_answer": "No API secret bundled into an APK can ever be fully secret. The client device is an untrusted environment where attackers control memory, kernel, and storage. Tools like jadx, Ghidra, and Frida can extract any embedded key, regardless of NDK C++ placement or custom obfuscation algorithms.",
        "best_answer": (
            "In mobile application threat modeling, it is an established axiom that **no secret embedded in a client binary can remain confidential**:\n\n"
            "1. **The Untrusted Client Reality**: The moment an APK is downloaded, the attacker controls the execution environment. They possess physical possession, kernel root privileges, memory inspection tools, and debuggers. Cryptographic keys bundled into an app must eventually be decrypted into memory to be transmitted across HTTP headers.\n\n"
            "2. **Failure of Client Obfuscation Schemes**:\n   - **BuildConfig & Assets**: Plaintext in `classes.dex` or `/assets/`.\n   - **NDK C++ Shared Libraries (`.so`)**: Plaintext in the ELF binary's `.rodata` section, decompilable in Ghidra in seconds.\n   - **XOR / Custom Splitting**: Dynamically hooked via Frida with a 3-line JavaScript script at the boundary where the decrypted string is handed to OkHttp.\n   - **TLS Interception**: Extracted directly over the wire using proxy tools (mitmproxy, Burp Suite) on devices with root CA trust.\n\n"
            "3. **Architectural Rule**: Treat the APK strictly as a public artifact. Embed only restricted public tokens (Firebase Project IDs, Maps API keys with SHA-1 restrictions). Private third-party secrets must live behind backend API gateways."
        ),
        "deep_answer": (
            "Differentiating Public Identifiers from Private Secrets:\n\n"
            "- **Public Client Identifiers (Allowed in APK)**: Client IDs whose compromise cannot result in privileged data access. For instance, a Stripe Publishable Key (`pk_live_...`) is designed to be public; it can only tokenize raw card numbers on the client without the ability to read customer lists or execute refund payouts. Even if extracted, it grants zero unauthorized capability.\n\n"
            "- **Private Credentials (Forbidden in APK)**: Stripe Secret Keys (`sk_live_...`), AWS IAM secret keys, or OpenAI API keys. These grant unrestricted administrative or billable access. Shipping these in an APK exposes your company to total infrastructure takeover and unbounded financial liability."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between Stripe Publishable Key and Stripe Secret Key?",
                "answer": "Publishable Key only tokenizes payment cards on the client (safe for APKs); Secret Key charges cards and accesses account balances (strictly backend only)."
            },
            {
                "question": "Can commercial code obfuscators (like DexGuard) guarantee secret protection?",
                "answer": "No. They raise the bar and slow down amateur attackers, but they cannot guarantee confidentiality against determined reverse engineers with dynamic instrumentation tools."
            }
        ]
    },
    {
        "id": "SEC-06",
        "arabic_explanation": (
            "ما هو التشفير في حالة السكون (Encryption at Rest) والتشفير في حالة النقل (Encryption in Transit) في Android؟\n\n"
            "1. التشفير في حالة السكون (Encryption at Rest - حماية البيانات المخزنة):\n   - **ما هو**: حماية البيانات المخزنة محلياً على ذاكرة الجهاز (Flash Storage / Disk) عند إغلاق التطبيق أو قفل الهاتف.\n   - **مستوياته في Android**:\n     * **تشفير مستوى النظام (File-Based Encryption - FBE)**: مدمج في Android 7.0+. يقسم الذاكرة إلى مساحتين مشفرتين بمفتاح الجهاز: مساحة `Device Encrypted (DE)` ومساحة `Credential Encrypted (CE)` التي لا تُفتح إلا بعد قيام المستخدم بإدخال رمز القفل (PIN/Password).\n     * **تشفير مستوى التطبيق (App-Level Encryption)**: تشفير قواعد البيانات الحساسة (مثل Room عبر **SQLCipher**) ومفاتيح التفضيلات الحساسة عبر **Android Keystore** لضمان حمايتها حتى لو تم كسر حماية الـ FBE على جهاز Rooted.\n\n"
            "2. التشفير في حالة النقل (Encryption in Transit - حماية البيانات أثناء السير عبر الشبكة):\n   - **ما هو**: حماية حزم البيانات أثناء انتقالها عبر كابلات وأبراج الاتصالات وشبكات الـ Wi-Fi العامة بين الهاتف والسيرفر.\n   - **كيف يُطبق في Android**:\n     * استخدام **TLS 1.3 / HTTPS** الإلزامي.\n     * حظر الاتصالات غير المشفرة (Cleartext HTTP) في `network_security_config.xml` (`cleartextTrafficPermitted=\"false\"`).\n     * تطبيق **Certificate Pinning** لمنع هجمات Man-In-The-Middle (MITM) إذا قام المهاجم بتثبيت شهادة Root خبيثة على الهاتف.\n\n"
            "3. الثغرة المشتركة (The Plaintext in Use Window):\n   - كلا النوعين يحميان البيانات وهي مخزنة أو وهي مسافرة، لكن عند استخدامها داخل كود Kotlin، تكون البيانات **Plaintext في ذاكرة الـ RAM**! يجب مسح المخازن المؤقتة الحساسة بعد استخدامها فوراً."
        ),
        "practical_walkthrough": (
            "تطبيق التشفير في السكون (SQLCipher) والتشفير في النقل (Network Security Config):\n"
            "```xml\n"
            "<!-- 1. التشفير في النقل: منع الـ Cleartext HTTP وفرض TLS في res/xml/network_security_config.xml -->\n"
            "<network-security-config>\n"
            "    <base-config cleartextTrafficPermitted=\"false\">\n"
            "        <trust-anchors>\n"
            "            <certificates src=\"system\" /> <!-- الثقة في شهادات النظام فقط وحظر شهادات المستخدم في Release -->\n"
            "        </trust-anchors>\n"
            "    </base-config>\n"
            "</network-security-config>\n"
            "```\n"
            "\n"
            "```kotlin\n"
            "// 2. التشفير في السكون: تشفير ملف قاعدة بيانات Room بالكامل عبر SQLCipher بمفتاح من Keystore:\n"
            "val passphrase = KeystoreManager.getOrCreateDatabasePassphrase()\n"
            "val supportFactory = SupportFactory(passphrase)\n"
            "\n"
            "val secureDatabase = Room.databaseBuilder(context, AppDatabase::class.java, \"secure_app.db\")\n"
            "    .openHelperFactory(supportFactory) // تشفير كامل للـ SQLite بـ AES-256 CBC\n"
            "    .build()\n"
            "```"
        ),
        "quick_answer": "Encryption at rest protects stored data on disk (via File-Based Encryption, SQLCipher, and Keystore). Encryption in transit protects network payloads traveling over the wire (via TLS 1.3, Network Security Config, and Certificate Pinning). Both protect data outside of active use, but plaintext inevitably resides in RAM while being processed.",
        "best_answer": (
            "A comprehensive defense-in-depth architecture secures data across both rest and transit states:\n\n"
            "1. **Encryption in Transit (Over the Wire)**:\n   - Guarantees confidentiality and integrity across public cellular and Wi-Fi networks.\n   - Enforced via **TLS 1.2 / TLS 1.3** exclusively. Configured in Android via `res/xml/network_security_config.xml` with `cleartextTrafficPermitted=\"false\"` to prevent accidental HTTP fallback.\n   - Hardened with **Certificate Pinning** in OkHttp to defeat Man-in-the-Middle (MITM) interception from rogue CAs.\n\n"
            "2. **Encryption at Rest (On Flash Storage)**:\n   - **OS Level**: Modern Android uses **File-Based Encryption (FBE)**. User data is partitioned into Credential Encrypted (CE) storage, unlocked only after the user enters their lockscreen PIN/pattern.\n   - **App Level**: Sensitive local databases are encrypted with **SQLCipher (AES-256)**, while tokens and keys are encrypted with **AES-GCM** using keys managed by `AndroidKeyStore`. If an attacker copies the SQLite file via ADB backup or file extraction, the file is unreadable binary ciphertext.\n\n"
            "3. **Plaintext in Use**: Plaintext exists in application heap memory while being actively processed by the CPU, demanding careful buffer management and redaction in logging."
        ),
        "deep_answer": (
            "Differentiating Device-Encrypted (DE) vs. Credential-Encrypted (CE) Storage in FBE:\n\n"
            "Starting in Android 7.0 (API 24), Android replaced Full-Disk Encryption (FDE) with File-Based Encryption (FBE):\n\n"
            "- **CE Storage (`context.createCredentialProtectedStorageContext()`)**: The default storage for applications. Encrypted with a key derived from the user's lockscreen PIN and hardware Keystore. Unavailable after device reboot until the user enters their PIN for the first time (Direct Boot mode).\n\n"
            "- **DE Storage (`context.createDeviceProtectedStorageContext()`)**: Encrypted with a key tied to the device hardware, available **before** the user unlocks the screen. Reserved strictly for components that must operate immediately after reboot before user unlock (alarm clocks, incoming call receivers, accessibility services).\n\n"
            "Fintech and banking apps must never store financial records or auth tokens in DE storage; always retain credentials strictly in CE storage."
        ),
        "follow_ups": [
            {
                "question": "What is Direct Boot in Android?",
                "answer": "A mode where the device has booted up but the user has not yet entered their lockscreen PIN; only Device Protected (DE) storage is accessible."
            },
            {
                "question": "Can an attacker read SQLCipher databases if they steal the phone while it's turned off?",
                "answer": "No. Without the device lockscreen PIN and Keystore hardware key derivation, SQLCipher ciphertext cannot be decrypted."
            }
        ]
    },
    {
        "id": "SEC-07",
        "arabic_explanation": (
            "مقارنة رياضية ومعمارية بين 4 مفاهيم أساسية في أمن المعلومات:\nالتشفير (Encryption)، والتجزئة (Hashing)، و HMAC، والتوقيع الرقمي (Digital Signatures):\n\n"
            "1. التشفير (Encryption - السرية القابلة للعكس):\n   - **الهدف**: تحقيق السرية والخصوصية (Confidentiality). تحويل النص الصريح إلى نص غير مفهوم، مع **إمكانية فك التشفير واستعادة النص الأصلي** باستخدام مفتاح سري.\n   - **الأنواع**: متماثل (Symmetric مثل AES-256) بمفتاح واحد، أو غير متماثل (Asymmetric مثل RSA/ECC) بمفتاح عام وخاص.\n   - **أفضل استخدام**: تشفير قاعدة البيانات المحلية، وتشفير رسائل المحادثة.\n\n"
            "2. التجزئة (Hashing - البصمة الرقمية أحادية الاتجاه):\n   - **الهدف**: التحقق من سلامة البيانات (Integrity). تحويل نص بأي طول إلى بصمة ثابتة الطول (Digest) مثل SHA-256.\n   - **خاصية حتمية**: **أحادية الاتجاه رياضياً (One-Way)**؛ من المستحيل رياضياً استعادة النص الأصلي من الـ Hash.\n   - **أفضل استخدام**: التحقق من سلامة تنزيل ملف APK (Checksum)، وحفظ كلمات المرور على السيرفر مع Salt (عبر bcrypt/Argon2).\n\n"
            "3. HMAC (Hash-based Message Authentication Code - التجزئة بالمفتاح السري):\n   - **الهدف**: التحقق من سلامة البيانات ومصدرها الموثوق (Integrity + Authenticity) باستخدام مفتاح سري مشترك متماثل.\n   - **كيف يعمل**: دمج النص مع مفتاح سري مشترك قبل التجزئة: `HMAC = Hash(Key + Message)`.\n   - **أفضل استخدام**: توقيع طلبات الـ Webhooks والـ API لمنع التلاعب بالبيانات أثناء النقل بين طرفين يعرفان نفس المفتاح.\n\n"
            "4. التوقيع الرقمي (Digital Signatures - إثبات المصدر وعدم الإنكار):\n   - **الهدف**: التحقق من المصدر، وسلامة المحتوى، **وعدم القدرة على الإنكار (Non-Repudiation)**.\n   - **كيف يعمل**: تشفير الـ Hash الخاص بالرسالة باستخدام **المفتاح الخاص (Private Key)** للراسل. يستطيع أي شخص في العالم التحقق من التوقيع باستخدام **المفتاح العام (Public Key)**.\n   - **أفضل استخدام**: توقيع ملفات الـ APK (APK Signature Scheme v2/v3)، وتوقيع المعاملات المالية في البنوك عبر مفاتيح Keystore الخاصة."
        ),
        "practical_walkthrough": (
            "المقارنة البرمجية بين التشفير التوثيقي (AES-GCM)، والتجزئة، والتوقيع الرقمي في Kotlin:\n"
            "```kotlin\n"
            "// 1. Hashing: بصمة أحادية الاتجاه للتحقق من سلامة ملف:\n"
            "fun calculateSha256(data: ByteArray): String {\n"
            "    val digest = MessageDigest.getInstance(\"SHA-256\").digest(data)\n"
            "    return digest.joinToString(\"\") { \"%02x\".format(it) }\n"
            "}\n"
            "\n"
            "// 2. HMAC: توقيع رسالة بمفتاح سري مشترك للتحقق من عدم التلاعب:\n"
            "fun generateHmac(key: ByteArray, message: ByteArray): ByteArray {\n"
            "    val mac = Mac.getInstance(\"HmacSHA256\")\n"
            "    mac.init(SecretKeySpec(key, \"HmacSHA256\"))\n"
            "    return mac.doFinal(message)\n"
            "}\n"
            "\n"
            "// 3. التوقيع الرقمي (Digital Signature): توقيع بمفتاح خاص داخل Keystore لا يمكن إنكاره:\n"
            "fun signTransaction(privateKey: PrivateKey, transactionBytes: ByteArray): ByteArray {\n"
            "    val signature = Signature.getInstance(\"SHA256withECDSA\")\n"
            "    signature.initSign(privateKey)\n"
            "    signature.update(transactionBytes)\n"
            "    return signature.sign() // يرسل للسيرفر مع المعاملة ليتحقق منه بالمفتاح العام\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Encryption provides reversible confidentiality using keys (AES/RSA). Hashing produces an irreversible one-way digest to verify data integrity (SHA-256). HMAC adds a shared secret key to hashing to verify both integrity and authenticity. Digital signatures use asymmetric cryptography (Private/Public key) to provide integrity, authenticity, and non-repudiation.",
        "best_answer": (
            "Selecting the correct cryptographic primitive depends on whether the security goal is confidentiality, integrity, authenticity, or non-repudiation:\n\n"
            "1. **Encryption (Confidentiality - Reversible)**: Transforms plaintext into ciphertext. Requires a key to decrypt back to plaintext. Symmetric encryption (AES-256 GCM) is fast for local data storage and payload encryption. Asymmetric encryption (RSA/ECC) encrypts data with a public key that only the matching private key can decrypt.\n\n"
            "2. **Hashing (Integrity - Irreversible)**: A deterministic, one-way mathematical function mapping arbitrary-length inputs to a fixed-length digest (e.g. SHA-256). Changing a single bit completely changes the hash. Used for APK checksum verification and password hashing (with salt and slow KDFs like Argon2).\n\n"
            "3. **HMAC (Keyed Integrity & Authenticity - Symmetric)**: Computes a hash combined with a shared secret key (`HmacSHA256`). Confirms that the message was not modified in transit AND that it was created by an entity possessing the shared secret.\n\n"
            "4. **Digital Signatures (Authenticity & Non-Repudiation - Asymmetric)**: Signs a message hash with a private key; verifiable by anyone using the corresponding public key (e.g. ECDSA, RSA). Guarantees **non-repudiation**: the signer cannot claim they didn't author the message, making it mandatory for financial payment authorizations and APK code signing."
        ),
        "deep_answer": (
            "Cryptographic Failure Modes in Android Applications:\n\n"
            "1. **Using Unauthenticated Encryption (AES-CBC without HMAC)**: Susceptible to **Padding Oracle Attacks** and bit-flipping attacks. Always use **Authenticated Encryption with Associated Data (AEAD)**, specifically **AES-GCM (Galois/Counter Mode)**, which generates a cryptographic authentication tag validating both ciphertext integrity and payload confidentiality.\n\n"
            "2. **Hashing Passwords with Fast Hashes**: Using SHA-256 or MD5 for passwords is an immediate security vulnerability because modern GPUs compute billions of SHA-256 hashes per second via rainbow tables. Password hashing must use slow, memory-hard Key Derivation Functions (PBKDF2 with 100,000+ iterations, bcrypt, or Argon2id)."
        ),
        "follow_ups": [
            {
                "question": "What is Non-Repudiation in digital signatures?",
                "answer": "The inability of the sender to deny having sent the message, because only their hardware-held private key could have generated the valid signature."
            },
            {
                "question": "Why does AES-GCM require a unique IV (Initialization Vector) for every encryption?",
                "answer": "Reusing an IV with the same AES key completely destroys GCM security, allowing an attacker to recover both plaintext and the authentication subkey."
            }
        ]
    },
    {
        "id": "SEC-08",
        "arabic_explanation": (
            "ما هو بروتوكول TLS، وما الذي يضيفه تثبيت الشهادة (Certificate Pinning)؟ وما هي مخاطره التشغيلية الحقيقية؟\n\n"
            "1. كيف يعمل بروتوكول TLS العادي في Android؟\n   - عند اتصال تطبيقك بـ `https://api.example.com`، يقوم نظام Android بالتحقق من شهادة السيرفر عبر سلسلة الثقة (Chain of Trust):\n     * يفحص هل الشهادة صادرة من جهة معتمدة (Certificate Authority - CA) موجودة في قائمة الـ Trusted CAs المدمجة في نظام التشغيل (يحتوي أندرويد على أكثر من 130 جهة CA معتمدة حول العالم).\n     * يتحقق من صحة تاريخ الشهادة ومطابقة اسم النطاق (Hostname Verification).\n   - **المشكلة الأمنية للـ TLS العادي**:\n     * إذا تم اختراق أي واحدة من الـ 130 جهة CA حول العالم، يستطيع المهاجم إصدار شهادة مزورة باسم موقعك!\n     * أو إذا قام مستخدم (أو جهة رقابية أو شبكة تجسس) بتثبيت شهادة CA خبيثة على الهاتف نفسه (Root Certificate Injection)، يمكنهم اعتراض كل اتصالات التطبيق وفك تشفيرها (Man-In-The-Middle - MITM Attack).\n\n"
            "2. ما الذي يضيفه تثبيت الشهادة (Certificate Pinning)؟\n   - **تقييد الثقة**: بدلاً من الثقة في 130 جهة CA عامة، يُعلن التطبيق صراحة: 'أنا لا أثق إلا في البصمة الرقمية المحددة لمفتاح سيرفري العام (Subject Public Key Info - SPKI Pin)'.\n   - إذا أرجع أي شخص شهادة موقعة من أي CA أخرى (حتى لو كانت جهة رسمية أو شهادة Proxy على هاتف Rooted)، يرفض التطبيق الاتصال فوراً ويغلق السوكيت!\n\n"
            "3. المخاطر التشغيلية القاتلة (Operational Risks):\n   - **تعطيل التطبيق بالكامل (Bricking the App)**: إذا انتهت صلاحية شهادة السيرفر وتم تجديدها بمفتاح جديد، ولم يكن التطبيق يمتلك البصمة الجديدة (Backup Pin)، سيتوقف التطبيق عن العمل لدى 100% من المستخدمين ولن يستطيع الاتصال بالسيرفر حتى تنشر تحديثاً في متجر Google Play!"
        ),
        "practical_walkthrough": (
            "تنفيذ Certificate Pinning بأمان مع مفاتيح احتياطية في OkHttp:\n"
            "```kotlin\n"
            "// 1. إعداد CertificatePinner مع مفتاح أساسي ومفتاحي نسخ احتياطي إلزامي (Backup Pins):\n"
            "val certificatePinner = CertificatePinner.Builder()\n"
            "    .add(\n"
            "        \"api.example.com\",\n"
            "        // المفتاح الأساسي الحالي للسيرفر:\n"
            "        \"sha256/k2oTQLGen4KpWh9Flu2hQGS3CrU5guYlhLPARYrZOO4=\",\n"
            "        // ⚠️ إلزامي: مفتاح احتياطي أول لمكتب التشفير البديل:\n"
            "        \"sha256/WoiWRyIOVNa9ihaBciRSC7XHjliYS9VwUGOIud4PB18=\",\n"
            "        // ⚠️ إلزامي: مفتاح احتياطي ثنائي للطوارئ (Disaster Recovery Key):\n"
            "        \"sha256/r/mIkG3eEpVdm+u/ko/cwxzOMo1bk4TyHIlByIBA5Pa=\"\n"
            "    )\n"
            "    .build()\n"
            "\n"
            "// 2. ربط الـ Pinner بـ OkHttpClient:\n"
            "val okHttpClient = OkHttpClient.Builder()\n"
            "    .certificatePinner(certificatePinner)\n"
            "    .build()\n"
            "```"
        ),
        "quick_answer": "TLS provides encrypted transport authenticated by public Certificate Authorities (CAs). Certificate Pinning hardcodes the server's public key fingerprint (SPKI hash) into the app, rejecting all unauthorized certificates even if signed by trusted CAs. However, pinning risks bricking the app if server certificates rotate without pre-configured backup pins in client binaries.",
        "best_answer": (
            "Standard TLS relies on a hierarchical Chain of Trust anchored in over 130 root Certificate Authorities (CAs) embedded in the Android OS. While secure against passive eavesdropping, standard TLS has an inherent architectural vulnerability:\n\n"
            "1. **The MITM Threat**: If any single global CA is compromised or compelled to issue fraudulent certificates, or if an attacker installs a user CA certificate on a corporate or rooted device, they can proxy and inspect all application network traffic (MITM).\n\n"
            "2. **What Certificate Pinning Adds**: It enforces an additional zero-trust constraint. The client hardcodes the cryptographic hash of the server's Subject Public Key Info (SPKI). Even if a proxy returns a certificate signed by a valid root CA, OkHttp verifies that `sha256/hash` matches its internal allowlist, aborting the connection with an `SSLPeerUnverifiedException` if mismatched.\n\n"
            "3. **Operational Risks & Bricking**: Pinning is an operational double-edged sword. If an operations team rotates the server's TLS certificate in an emergency and the new key was not pre-pinned as a backup inside released client binaries, **the application is permanently bricked** for all existing users until they download an APK update from Google Play."
        ),
        "deep_answer": (
            "Pinning Best Practices: **Pin the Public Key (SPKI), Never the Certificate**.\n\n"
            "A server's X.509 certificate expires annually and contains serial numbers and validity dates. If you pin the certificate bytes, you must update the app every single year.\n\n"
            "Instead, pin the **Subject Public Key Info (SPKI)** hash (`sha256/...`). When renewing the TLS certificate, the server operations team can generate a new certificate using the **same private key and CSR (Certificate Signing Request)**. The public key remains mathematically identical, so existing mobile clients continue functioning seamlessly without requiring an APK update.\n\n"
            "Furthermore, always ship at least **two backup pins** generated from offline cold-storage private keys for emergency failover."
        ),
        "follow_ups": [
            {
                "question": "Can Certificate Pinning be bypassed on a rooted device?",
                "answer": "Yes. A reverse engineer using Frida or Xposed can easily hook OkHttp's `CertificatePinner.check()` method and return true, bypassing pinning in seconds."
            },
            {
                "question": "How does `network_security_config.xml` support native certificate pinning?",
                "answer": "Via the `<pin-set>` tag containing `<pin digest=\"SHA-256\">` entries, enforcing pinning at the platform Android network layer."
            }
        ]
    }
]

def main() -> None:
    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in existing}
    else:
        by_id = {}

    for item in SEC_01_08:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions SEC-01 to SEC-08. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
