#!/usr/bin/env python3
"""
Elevation script for SEC questions: SEC-01 to SEC-08.
Topic: Android Security, Crypto & Fintech Threat Modeling (SEC)
Phase 3, Batch 1
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "أمان أندرويد والتشفير والنمذجة الأمنية لتطبيقات التكنولوجيا المالية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# SEC-01: What is the Android application sandbox and permission model?
# ==========================================
DATA["SEC-01"] = {
    "concept_en": """The Android application sandbox is the foundation of platform security, leveraging Linux kernel multi-user architecture to enforce strict isolation between applications. During installation, the package manager assigns each application a unique Linux User Identifier (UID), typically ranging within app-specific ranges like u0_a123. The Linux kernel enforces discretionary access control (DAC), ensuring that files created under an application's private directory (/data/data/<package_name>) are assigned permissions 0700 or 0750 owned by that specific UID. No other application can read or execute those files unless explicitly shared through ContentProviders or shared UID signing mechanisms. Layered on top of DAC is SEAndroid (Security-Enhanced Android), which enforces Mandatory Access Control (MAC) using SELinux policies. Applications execute within restricted domains (such as untrusted_app), preventing compromised processes from performing unauthorized system calls, accessing raw block devices, or escalating privileges. When applications communicate across process boundaries via Binder IPC, the kernel injects the verified calling UID and PID, allowing framework services and ContentProviders to enforce access rules at runtime.""",
    "walkthrough_en": """Enforcing permission checks at IPC and component boundaries in Android:
```kotlin
// 1. Verifying caller identity at custom Binder service boundaries
class SecurePaymentService : IPaymentService.Stub() {
    override fun processTransaction(amountCents: Long, recipientId: String): Boolean {
        // Enforce signature-level permission for sensitive inter-app IPC
        val callingUid = Binder.getCallingUid()
        val context = applicationContext
        
        val permissionCheck = context.checkCallingOrSelfPermission(
            "com.example.bank.permission.EXECUTE_PAYMENT"
        )
        if (permissionCheck != PackageManager.PERMISSION_GRANTED) {
            throw SecurityException("Calling UID $callingUid lacks payment permission")
        }
        
        // 2. Validate package identity matches expected trusted signer certificate
        val callerPackages = context.packageManager.getPackagesForUid(callingUid)
        val isTrusted = callerPackages?.any { pkg ->
            context.packageManager.hasSigningCertificate(
                pkg,
                TRUSTED_FINTECH_SIGNATURE_BYTES,
                PackageManager.CERT_INPUT_SHA256
            )
        } ?: false
        
        if (!isTrusted) {
            throw SecurityException("Calling package is not signed by trusted key")
        }
        return executeTransfer(amountCents, recipientId)
    }
}
```""",
    "short_en": """The Android sandbox isolates applications using Linux kernel UID separation and SELinux mandatory access controls. Each app runs as a distinct user with private storage that other apps cannot touch. The permission model layers install-time, runtime, and signature gates on top of this sandbox, requiring explicit user or cryptographic approval before an app can access sensitive hardware, personal data, or privileged system APIs.""",
    "structured_en": """Android security begins at the Linux kernel level, where each installed application receives a unique user identifier rather than running under a shared user account.
This UID separation gives the app an isolated process space and private file storage where files are non-readable by neighboring applications.
Beyond standard Linux file permissions, SEAndroid enforces SELinux mandatory access control policies that confine application domains even if an attacker manages to exploit a native memory vulnerability.
To access protected capabilities outside its sandbox, an application must request permissions through the platform model.
Install-time permissions cover normal low-risk capabilities like internet access and are granted automatically upon installation.
Runtime permissions govern privacy-sensitive resources like camera, location, and contacts, requiring explicit user consent in context and allowing runtime revocation at any point from system settings.
Signature permissions restrict sensitive integration points strictly to applications signed with the identical developer certificate, enabling secure modular communication across proprietary app suites.""",
    "deep_senior_en": """From a security architecture standpoint, Android shifts the traditional desktop trust model from trusting the user to isolating mutually untrusted applications from each other and the operating system.
The Linux kernel enforces Discretionary Access Control through assigned UIDs, while SEAndroid provides Mandatory Access Control via typed domains like untrusted_app.
This means that even if a process achieves code execution, SELinux prevents it from mapping arbitrary memory, executing raw system calls, or inspecting unauthorized IPC channels.
At the application framework layer, Inter-Process Communication occurs over Binder drivers.
Because the kernel securely passes the calling UID and PID during every Binder transaction, the operating system never relies on client-reported identifiers for access control.
Framework services query PermissionManagerService and AppOpsManager using these kernel-verified credentials.
When designing modern fintech or high-assurance applications, I treat runtime permissions as ephemeral states rather than one-time gates.
Users can revoke permissions at any moment, the system can auto-reset permissions for dormant apps, and Android 14 introduces partial photo pickers where grants are granular.
        Therefore, robust production architecture checks permissions immediately prior to invoking protected APIs, gracefully handles denials without crashing, and relies on signature-level permissions and signature certificate validation to secure inter-app IPC endpoints.
Furthermore, we minimize component attack surfaces by setting exported to false by default on all activities, services, and broadcast receivers, relying exclusively on explicit intents to prevent malicious cross-process hijacking.""",
    "meta_ar": {
        "id": "SEC-01",
        "questionAr": "ما هو نموذج العزل الأمني (Application Sandbox) ونظام الصلاحيات (Permission Model) في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم عزل العمليات عبر معرفات Linux UID، وسياسات SELinux، والتحقق من هوية المتصل عبر Binder، وتصنيفات الصلاحيات (عادية، وخطرة، وصلاحيات التوقيع الرقمي)، والتعامل الآمن مع الصلاحيات الديناميكية في الإنتاج.",
        "concept_ar": "يقوم العزل الأمني في أندرويد على تخصيص معرف مستخدم فريد (UID) لكل تطبيق في نواة لينكس، مما يعزل ملفاته الخاصة وذاكرته تماماً عن باقي التطبيقات. وتعزز سياسات SEAndroid هذا العزل عبر فرض التحكم الإلزامي في الوصول (MAC). وتعمل الصلاحيات كبوابات وصول للقدرات الحساسة، مقسمة إلى صلاحيات تثبيت تلقائية، وصلاحيات وقت التشغيل (Runtime Permissions) الخاضعة لموافقة المستخدم وإلغائه، وصلاحيات التوقيع (Signature Permissions) المقتصرة على تطبيقات المطور ذاته.",
        "walkthrough_ar": "التحقق من هوية المتصل والصلاحيات عند حدود الـ IPC في خدمة أندرويد:\n```kotlin\nclass SecurePaymentService : IPaymentService.Stub() {\n    override fun processTransaction(amountCents: Long, recipientId: String): Boolean {\n        val callingUid = Binder.getCallingUid()\n        // التحقق من الصلاحية عند حدود استدعاء الـ Binder\n        if (context.checkCallingOrSelfPermission(\"com.example.bank.EXECUTE_PAYMENT\") \n            != PackageManager.PERMISSION_GRANTED) {\n            throw SecurityException(\"Caller UID $callingUid lacks permission\")\n        }\n        // التحقق من توقيع شهادة التطبيق المتصل\n        return executeTransfer(amountCents, recipientId)\n    }\n}\n```",
        "why_it_matters_ar": "فهم العزل والصلاحيات يحمي التطبيق من ثغرات تسريب البيانات والوصول غير المصرح به للمكونات عبر تطبيقات خبيثة موجودة على نفس الجهاز، ويضمن استقرار التطبيق عند سحب المستخدم للصلاحيات فجأة.",
        "worked_example_ar": "التحقق الآمن من صلاحيات الكاميرا والتنبيهات وقت التشغيل مع مراعاة السحب التلقائي:\n```kotlin\nfun handleCameraAction(activity: ComponentActivity, onGranted: () -> Unit) {\n    when {\n        ContextCompat.checkSelfPermission(activity, Manifest.permission.CAMERA) \n            == PackageManager.PERMISSION_GRANTED -> onGranted()\n        activity.shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {\n            showEducationalUiExplainingWhyCameraIsNeeded()\n        }\n        else -> requestPermissionLauncher.launch(Manifest.permission.CAMERA)\n    }\n}\n```",
        "trade_offs_ar": "طلب الصلاحيات وقت التثبيت كان سهلاً للمطورين لكنه عرض خصوصية المستخدمين للخطر، بينما نقل الصلاحيات إلى وقت التشغيل يعزز الشفافية والأمان لكنه يفرض تعقيداً برمجياً للتعامل مع الرفض والسحب المستمر للوصول.",
        "failure_modes_ar": "افتراض بقاء الصلاحية ممنوحة للأبد بعد قبولها مرة واحدة، مما يسبب Crash فوري عند سحبها لاحقاً من الإعدادات، أو تصدير المكونات مثل Activities أو Services في Manifest بدون صلاحيات حماية مما يسمح لأي تطبيق باستدعائها.",
        "production_perspective_ar": "في التطبيقات المالية المتقدمة، نعتمد على صلاحيات التوقيع (Signature Permissions) للاتصال بين تطبيقات الشركة، ونفحص الصلاحيات الحساسة في لحظة الاستخدام بالضبط مع حصر الصلاحيات في الحد الأدنى لتقليل مساحة الهجوم.",
        "how_to_answer_ar": "ابدأ ببيان الأساس المعماري في نواة لينكس وتخصيص UID فريد لكل تطبيق وعزل مساحات التخزين، ثم اشرح دور SELinux وBinder في فحص هوية العمليات، وبعدها وضح مستويات الصلاحيات الثلاثة وكيفية إدارة صلاحيات وقت التشغيل باحترافية.",
        "talking_points_ar": "عزل Linux UID، وسياسات SEAndroid/SELinux، وفحص Binder.getCallingUid()، وتصنيف الصلاحيات (Install-time, Runtime, Signature)، والسحب التلقائي للصلاحيات في أندرويد الحديث.",
        "follow_ups_ar": "- **المحاور:** \"كيف تمنع تطبيقاً خارجياً من إرسال Intent خبيث للخدمة الخاصة بك؟\"\n  **المرشح:** \"أجعل المكون غير مصدر `exported=false` إذا كان داخلياً، أو أحميه بصلاحية من نوع `signature` إذا كان التواصل مخصصاً لتطبيقات تابعة لنفس الشركة.\"\n\n- **المحاور:** \"ماذا يحدث لو اشترك تطبيقان في نفس الـ UID عبر sharedUserId؟\"\n  **المرشح:** \"يتشاركان نفس مساحة الملفات والعمليات بشرط توقيعهما بنفس الشهادة، ولكن جوجل ألغت دعم هذه الميزة في الإصدارات الحديثة لخطورتها الأمنية.\"",
        "self_check_ar": "هل بينت دور نواة لينكس وUID؟ هل فرقت بين الصلاحيات العادية وصلاحيات وقت التشغيل والتوقيع؟ وهل شرحت التعامل الآمن مع رفض الصلاحية؟",
        "references_ar": f"- [Android Security Architecture](https://source.android.com/docs/security/architecture) — التوثيق الرسمي لمعمارية أمان أندرويد ونواة لينكس.\n- [Permissions and App Sandbox Overview](https://developer.android.com/guide/topics/permissions/overview) — دليل أندرويد الرسمي للصلاحيات وعزل التطبيقات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يقوم العزل الأمني في أندرويد على تخصيص معرف مستخدم فريد في نواة لينكس لكل تطبيق مثبت، مما يمنحه مساحة ملفات خاصة وعملية معزولة تماماً عن التطبيقات الأخرى. وتفرض سياسات SELinux قيود وصول صارمة على العتاد والنظام، بينما يتحكم نظام الصلاحيات في الوصول للبيانات الحساسة مثل الكاميرا والموقع عبر طلب إذن المستخدم وقت التشغيل.",
        "best_answer_ar": "يبدأ أمان أندرويد من نواة نظام لينكس، حيث لا يعتبر التطبيق مجرد برنامج بل مستخدماً مستقلاً له معرف UID خاص به.\n\nهذا الفصل يضمن أن مجلدات التطبيق الخاصة مشفرة ومحمية بصلاحيات ملفات تمنع أي تطبيق مجاور من قراءتها. وبالإضافة لذلك، تطبق سياسات SEAndroid تحكماً إجبارياً في الوصول يعزل التطبيقات ويمنعها من تنفيذ استدعاءات نظام غير مصرح بها حتى في حال حدوث ثغرة في الكود الأصلي.\n\nوللوصول إلى العتاد أو بيانات المستخدم الحساسة، يوفر أندرويد نموذج صلاحيات متعدد الطبقات. الصلاحيات العادية مثل الوصول للإنترنت تُمنح تلقائياً عند التثبيت لعدم خطورتها، بينما تتطلب الصلاحيات الخطرة مثل الموقع والمايكروفون إذناً صريحاً من المستخدم وقت الاستخدام الفعلي، مع إمكانية سحبها في أي لحظة. وتوجد صلاحيات التوقيع التي تضمن اقتصار الوصول على التطبيقات الموقعة بنفس شهادة المطور لتمكين التواصل الآمن بين تطبيقات المنظومة الواحدة.",
        "deep_answer_ar": "في معمارية أمان أندرويد، يتحول نموذج الثقة من الثقة في المستخدم إلى عزل التطبيقات غير الموثوقة عن بعضها وعن موارد النظام الحساسة.\n\nتعتمد النواة على آلية Discretionary Access Control من خلال معرفات UID، وتتكامل مع Mandatory Access Control عبر نطاقات SELinux مثل untrusted_app، مما يحرم أي كود مخترق من الوصول إلى أقراص التخزين الخام أو الذاكرة المحمية. وعندما يحدث اتصال بين العمليات عبر قنوات Binder، يحقن تعريف النواة معرّف UID و PID للمتصل تلقائياً وبشكل موثوق، مما يمنع انتحال الهوية البرمجية نهائياً.\n\nتتعامل خدمات النظام مع هذه الهويات الموثقة لتطبيق قيود الصلاحيات عبر PermissionManagerService. ومن منظور إنتاجي متقدم في التطبيقات البنكية، أتعامل مع صلاحيات وقت التشغيل كحالات مؤقتة متغيرة وليست حقاً دائماً؛ فالمستخدم قد يسحب الصلاحية من الإعدادات، أو يقوم النظام بإلغائها تلقائياً للتطبيقات الخاملة. لذلك نفحص الصلاحية دائماً قبل استدعاء الواجهة الحساسة مباشرة، ونتعامل مع حالات الرفض دون انهيار التطبيق، ونعتمد على صلاحيات التوقيع لفصل الخدمات الداخلية وحماية واجهات الاتصال بين تطبيقاتنا المشتركة.\n\nكما نلتزم هندسياً بإغلاق كافة المكونات بجعلها غير مصدرة افتراضياً عبر تعيين الخاصية exported إلى false، والاعتماد على Intent صريح دائماً لمنع أي تطبيق متطفل من اعتراض البيانات أو تشغيل شاشات وخدمات التطبيق بشكل غير مصرح به داخل النظام."
    }
}

# ==========================================
# SEC-02: What is Android Keystore, and what is hardware-backed key storage?
# ==========================================
DATA["SEC-02"] = {
    "concept_en": """The Android Keystore system is a specialized cryptographic security provider designed to generate, manage, and use cryptographic keys while preventing the raw key material from ever entering the application process memory or being extracted from the device. When an application generates a key via KeyGenParameterSpec, the key pairs or symmetric keys can be bound to hardware-backed security modules. In modern Android devices, hardware-backed storage is implemented via a Trusted Execution Environment (TEE) or a dedicated StrongBox Keymaster. The TEE runs in an isolated, secure world on the primary CPU (such as ARM TrustZone) with its own memory space and secure microkernel, while StrongBox utilizes an entirely separate, tamper-resistant physical security chip with isolated CPU, secure storage, and hardware true random number generator (TRNG). Cryptographic operations (encryption, decryption, digital signing, MAC generation) are executed entirely within the secure hardware boundary; the host Android operating system and application only receive the resulting ciphertext, signature, or digest.""",
    "walkthrough_en": """Generating hardware-backed cryptographic keys with biometric authentication gating:
```kotlin
fun generateBiometricProtectedSigningKey(keyAlias: String) {
    val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    if (keyStore.containsAlias(keyAlias)) return

    val keyPairGenerator = KeyPairGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_EC,
        "AndroidKeyStore"
    )

    val parameterSpec = KeyGenParameterSpec.Builder(
        keyAlias,
        KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
    ).run {
        setDigests(KeyProperties.DIGEST_SHA256)
        setAlgorithmParameterSpec(ECGenParameterSpec("secp256r1"))
        // Require user biometric authentication to unlock this private key
        setUserAuthenticationRequired(true)
        setUserAuthenticationParameters(
            0, // 0 enforces biometric per-operation authentication
            KeyProperties.AUTH_BIOMETRIC_STRONG
        )
        // Request dedicated StrongBox tamper-resistant hardware if available
        setIsStrongBoxBacked(true)
        build()
    }

    try {
        keyPairGenerator.initialize(parameterSpec)
        keyPairGenerator.generateKeyPair()
    } catch (e: StrongBoxUnavailableException) {
        // Fallback to standard TEE hardware-backed Keystore
        val fallbackSpec = KeyGenParameterSpec.Builder(parameterSpec)
            .setIsStrongBoxBacked(false)
            .build()
        keyPairGenerator.initialize(fallbackSpec)
        keyPairGenerator.generateKeyPair()
    }
}
```""",
    "short_en": """Android Keystore is a secure system service that generates and stores cryptographic keys inside isolated hardware where they cannot be exported or viewed by application code. Hardware-backed security uses a Trusted Execution Environment or a dedicated StrongBox chip to perform encryption and digital signing directly inside tamper-resistant hardware, keeping private keys safe even if the host Android OS is fully rooted.""",
    "structured_en": """Android Keystore protects sensitive cryptographic keys by ensuring that private key material never resides in normal application process RAM or persistent app storage.
Instead of storing raw keys in private app files, the application instructs the Keystore system service to generate the key directly inside secure hardware boundaries.
Hardware-backed storage on modern Android devices relies on two main implementations.
The Trusted Execution Environment executes inside an isolated CPU world such as ARM TrustZone with dedicated secure memory, running cryptographic operations away from the main Android OS.
StrongBox Keymaster takes this further by utilizing a physically separated, tamper-resistant security chip with its own microprocessor and hardware random number generator.
When the application needs to sign a financial payload or decrypt an authentication token, it passes the data to the Keystore service.
The secure hardware performs the cryptographic mathematics and returns only the final signature or plaintext to the application, preventing key exfiltration even in rooted or compromised device environments.""",
    "deep_senior_en": """In enterprise and fintech mobile engineering, Android Keystore represents the fundamental boundary between software-level data and hardware-rooted identity.
When an application uses standard cryptography providers, private keys reside in JVM heap memory during cipher operations, leaving them vulnerable to memory scraping via Frida, debuggers, or kernel compromise.
Android Keystore eliminates this attack vector through non-exportability; keys are created inside the secure enclave and the API provides no mechanism to export private key bytes.
The hardware implementation varies across device tiers.
Most modern devices feature a Trusted Execution Environment running alongside the primary kernel, whereas high-security devices feature StrongBox Keymaster.
StrongBox is a dedicated Secure Element that defends against sophisticated physical attacks, including power analysis, clock glitching, and thermal manipulation.
Beyond confidentiality, Keystore enables strict hardware-enforced access policies via KeyGenParameterSpec.
We can enforce that a private key can only sign transactions if the user successfully authenticates using Class 3 Strong Biometrics within a zero-second window.
This binds the cryptographic operation directly to the Gatekeeper and BiometricPrompt hardware components.
Architecturally, we must treat Keystore keys as device-bound and ephemeral; keys are destroyed on app uninstallation, invalidated when the user alters lockscreen credentials, and cannot be migrated to new hardware via cloud backups without explicit key-exchange protocols.""",
    "meta_ar": {
        "id": "SEC-02",
        "questionAr": "ما هو نظام Android Keystore، وما هو تخزين المفاتيح المدعوم بالعتاد المادي (Hardware-Backed Storage)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم معمارية Android Keystore، والفروق الجوهرية بين بيئة التشفير العادية وبيئات TEE و StrongBox، ومفهوم عدم قابلية المفاتيح للاستخراج، وربط المفاتيح التشفيرية بالمصادقة البيومترية.",
        "concept_ar": "نظام Android Keystore هو مزود تشفير أمني على مستوى النظام يتيح توليد واستخدام المفاتيح التشفيرية دون أن تخرج المادة السرية للمفتاح إلى ذاكرة التطبيق أو التخزين العادي. التخزين المدعوم بالعتاد المادي يعني أن المفاتيح تُحفظ وتُدار إما داخل بيئة التنفيذ الموثوقة (TEE) المنفصلة على المعالج الرئيسي، أو داخل شريحة StrongBox المستقلة تماماً والمقاومة للتلاعب المادي، حيث تُنفذ كل العمليات الرياضية داخل العتاد الآمن.",
        "walkthrough_ar": "توليد مفتاح توقيع رقمي مشروط بالمصادقة البيومترية ومدعوم بشريحة عتادية آمنة:\n```kotlin\nval spec = KeyGenParameterSpec.Builder(\n    \"fintech_signing_key\",\n    KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY\n).run {\n    setDigests(KeyProperties.DIGEST_SHA256)\n    setAlgorithmParameterSpec(ECGenParameterSpec(\"secp256r1\"))\n    setUserAuthenticationRequired(true) // القفل بالبصمة\n    setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG)\n    setIsStrongBoxBacked(true) // طلب شريحة StrongBox المستقلة\n    build()\n}\n```",
        "why_it_matters_ar": "حماية المفاتيح التشفيرية داخل العتاد تمنع استخراجها حتى لو تم كسر حماية الجهاز (Root) أو حقن أدوات تتبع الذاكرة مثل Frida، مما يمثل حجر الزاوية لتأمين المعاملات المالية الحساسة.",
        "worked_example_ar": "توقيع عملية دفع مالي داخل العتاد الآمن عبر BiometricPrompt:\n```kotlin\nval signature = Signature.getInstance(\"SHA256withECDSA\").apply {\n    val privateKey = (keyStore.getEntry(keyAlias, null) as KeyStore.PrivateKeyEntry).privateKey\n    initSign(privateKey)\n}\nval cryptoObject = BiometricPrompt.CryptoObject(signature)\n// تمرير cryptoObject للـ BiometricPrompt للتوثيق قبل إتمام التوقيع\n```",
        "trade_offs_ar": "يوفر StrongBox أعلى درجات الأمان ومقاومة الهجمات المادية لكنه أبطأ في إجراء العمليات الرياضية مقارنة بالـ TEE وغير مدعوم في جميع الأجهزة الرخيصة، مما يتطلب استراتيجية Fallback برمجية مدروسة.",
        "failure_modes_ar": "محاولة استخراج المفتاح الخاص كنص عادي مما يسبب استثناءً برمجياً، أو افتراض انتقال مفاتيح Keystore مع النسخ الاحتياطي السحابي للتطبيق، مما يؤدي لفقدان القدرة على فك التشفير عند استعادة البيانات على جهاز جديد.",
        "production_perspective_ar": "في التطبيقات المصرفية، نولد أزواج مفاتيح غير متماثلة داخل Keystore ونرسل المفتاح العام فقط للسيرفر لتوثيق الجهاز، مع اشتراط البصمة الحيوية لكل عملية توقيع دفع لمنع الاحتيال.",
        "how_to_answer_ar": "اشرح المشكلة الأساسية وهي خطر وجود المفتاح في الذاكرة العادية، ثم وضح كيف يحل Keystore المشكلة عبر عدم خروج المفتاح، ثم قارن بين معمارية TEE وشريحة StrongBox المنفصلة، واشتمال ذلك على ربط المفاتيح بالبصمة وتدميرها عند تغيير قفل الشاشة.",
        "talking_points_ar": "عدم قابلية المفاتيح للتصدير (Non-exportable keys)، والـ TEE مقابل StrongBox، و KeyGenParameterSpec، وربط المفاتيح بـ BiometricPrompt، ودورة حياة المفتاح عند حذف التطبيق.",
        "follow_ups_ar": "- **المحاور:** \"ماذا يحدث لمفاتيح Keystore عند قيام المستخدم بإلغاء قفل الشاشة أو تغيير بصمته؟\"\n  **المرشح:** \"إذا كانت المفاتيح مرتبطة بـ setUserAuthenticationRequired، فإن المفاتيح تصبح غير صالحة تلقائياً (Invalidated) كإجراء أمني لمنع المهاجم من إضافة بصمته واستخدام المفتاح.\"\n\n- **المحاور:** \"هل يمكن نقل المفاتيح المخزنة في Keystore إلى هاتف آخر عبر استعادة النسخة الاحتياطية؟\"\n  **المرشح:** \"المفاتيح مرتبطة بالعتاد المادي للجهاز الحالي ولا يمكن نقلها مطلقاً، ويجب على السيرفر إنشاء جلسة ثقة جديدة عند تسجيل الدخول من جهاز آخر.\"",
        "self_check_ar": "هل وضحت الفارق بين TEE و StrongBox؟ هل أكدت على عدم خروج المفتاح للذاكرة العادية؟ وهل شرحت سيناريوهات الفشل عند تغيير قفل الشاشة؟",
        "references_ar": f"- [Android Keystore System](https://developer.android.com/privacy-and-security/keystore) — التوثيق الرسمي لنظام حماية وتوليد المفاتيح في أندرويد.\n- [Hardware-backed Security and StrongBox](https://source.android.com/docs/security/features/keystore) — المعمارية العتادية لـ Keymaster و StrongBox.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نظام Android Keystore هو خدمة نظام أمنية تقوم بتوليد وتخزين المفاتيح التشفيرية داخل عتاد مادي معزول يمنع استخراجها نهائياً إلى ذاكرة التطبيق العادية. وتعتمد الحماية العتادية على بيئة التنفيذ الموثوقة أو شريحة StrongBox المنفصلة المقاومة للتلاعب، بحيث تُجرى جميع عمليات التشفير والتوقيع الرقمي داخل العتاد الآمن حتى لو تعرض نظام أندرويد لترويض أمني كامل.",
        "best_answer_ar": "يعالج نظام Android Keystore أكبر ثغرة في تشفير تطبيقات الموبايل، وهي بقاء المفتاح السري مكشوفاً داخل ذاكرة الرام أثناء إجراء العمليات الحسابية.\n\nبدلاً من حفظ المفاتيح في ملفات التطبيق، يطلب التطبيق من Keystore توليد المفتاح وحفظه داخل عتاد الجهاز. وتعتمد الأجهزة الحديثة على معماريتين لتأمين العتاد؛ الأولى هي بيئة التنفيذ الموثوقة TEE التي تعمل في نطاق آمن ومعزول داخل المعالج الرئيسي مثل ARM TrustZone، والثانية هي شريحة StrongBox المستقلة تماماً والتي تمتلك معالجاً وذاكرة ومولد أرقام عشوائية خاصاً بها لمقاومة الهجمات المادية الدقيقة.\n\nعندما يحتاج التطبيق إلى توقيع معاملة مالية أو تشفير بيانات، يرسل البيانات فقط إلى خدمة Keystore، حيث يقوم العتاد الآمن بالحسابات الرياضية ويعيد النتيجة المشفرة أو التوقيع دون إظهار المفتاح الخاص للتطبيق، مما يحمي أسرار المستخدم من أدوات التلصص على الذاكرة أو برمجيات الروت الخبيثة.",
        "deep_answer_ar": "في التطبيقات المالية المتقدمة، يمثل Android Keystore الخط الفاصل بين حماية البرمجيات الهشة والحماية المتجذرة في العتاد الصلب.\n\nفي التشفير البرمجي التقليدي، يستقر المفتاح السري في الـ Heap Memory أثناء عمل الـ Cipher، مما يجعله فريسة سهلة لأدوات تتبع الذاكرة مثل Frida أو فحص ملفات تفريغ الذاكرة. بينما يقدم Android Keystore ضمانة هندسية حاسمة وهي عدم قابلية المفاتيح للتصدير؛ إذ يتم إنشاء المفتاح واستخدامه داخل معالج الأمان دون توفير أي واجهة برمجية تسمح بقراءة البايتات الأصلية للمفتاح الخاص.\n\nوتبرز شريحة StrongBox كأعلى درجات التأمين المادي؛ فهي Secure Element معزول فيزيائياً عن المعالج المركزي، مما يحصنها ضد هجمات تحليل استهلاك الطاقة والتلاعب بالترددات والحرارة. وعلاوة على سرية المفاتيح، يتيح Keystore تقييد استخدام المفتاح عبر سياسات عتادية صارمة؛ كأن نشترط تحقق البصمة الحيوية القوية من الفئة الثالثة قبل السماح بتوقيع كل معاملة مالية بنكية.\n\nمعمارياً، يجب أن ندرك أن مفاتيح Keystore مرتبطة بالعتاد الفيزيائي للجهاز الحالي ولا تنتقل مع النسخ الاحتياطية السحابية، كما أنها تُدمر تلقائياً عند قيام المستخدم بإلغاء قفل الشاشة كإجراء دفاعي استباقي لحماية الهوية الرقمية للعميل. كما نتعامل برمجياً مع استثناء KeyPermanentlyInvalidatedException بإعادة توجيه المستخدم لمسار تحقق أمني إضافي مع السيرفر لإعادة توليد أزواج مفاتيح جديدة عند تسجيل بصمات أصابع جديدة."
    }
}

# ==========================================
# SEC-03: Compare cryptographic keys, access tokens, refresh tokens, API keys, and passwords.
# ==========================================
DATA["SEC-03"] = {
    "concept_en": """Secure Android application architecture requires categorizing sensitive data into distinct credential classes, each with unique lifetimes, cryptographic properties, exposure risks, and storage requirements. Cryptographic keys (such as AES symmetric keys or ECDSA asymmetric key pairs) provide mathematical confidentiality and digital signatures; they must reside inside the hardware-backed Android Keystore. Access tokens are short-lived bearer credentials (typically OAuth 2.0 JWTs valid for 15 to 60 minutes) used in HTTP headers to authorize client API requests; they are kept in secure volatile memory or encrypted storage and rotated frequently. Refresh tokens are high-value, long-lived credentials (valid for weeks or months) whose sole purpose is to authenticate with the identity provider to obtain new access tokens; they require maximum protection in EncryptedSharedPreferences backed by Keystore master keys, combined with refresh token rotation (RTR). API keys are public client identifiers used by platforms like Google Maps to track usage and quota; they are not secrets and must be restricted by package name and SHA-1 signing certificates in cloud consoles. Passwords are user-held master authentication secrets that should never be permanently persisted on mobile devices, manipulated only as ephemeral char arrays to avoid immutable JVM heap String intern pooling.""",
    "walkthrough_en": """Production token storage and secure password memory handling in Android:
```kotlin
// 1. Secure token storage using Jetpack Security EncryptedSharedPreferences
class SecureSessionManager(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        "secure_session_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveTokens(accessToken: String, refreshToken: String) {
        encryptedPrefs.edit()
            .putString("access_token", accessToken)
            .putString("refresh_token", refreshToken)
            .apply()
    }
}

// 2. Safe user password handling: zeroing out character arrays immediately
fun authenticateWithZeroablePassword(passwordChars: CharArray, onComplete: () -> Unit) {
    try {
        // Send password over TLS to exchange for OAuth token pair
        transmitCredentialsOverTls(passwordChars)
    } finally {
        // Overwrite memory buffer immediately to prevent heap dump exposure
        passwordChars.fill('0')
    }
    onComplete()
}
```""",
    "short_en": """We categorize mobile credentials into five distinct security classes: cryptographic keys stored in Keystore for mathematical operations, short-lived access tokens for daily API calls, long-lived refresh tokens securely persisted to rotate access tokens, public API keys restricted in cloud consoles for service quotas, and raw user passwords that are never persisted and zeroed from memory immediately after exchange.""",
    "structured_en": """A resilient mobile security posture treats credentials differently according to their specific blast radius, lifetime, and storage requirements.
Cryptographic keys are mathematical instruments used for encryption and digital signing, requiring non-exportable hardware protection inside Android Keystore.
Access tokens are ephemeral bearer credentials with short lifespans between fifteen and sixty minutes, used in HTTP Authorization headers to authenticate API calls without requiring persistent storage.
Refresh tokens are high-privilege credentials used exclusively with authorization servers to fetch fresh access tokens; they must be encrypted on disk using EncryptedSharedPreferences and rotated on every exchange.
API keys identify the client application for third-party platforms like Google Maps or Firebase; because they are packaged inside the APK, they are public identifiers rather than secrets and must be restricted in developer consoles using application package names and SHA-1 signing fingerprints.
User passwords represent user identity secrets that should never be written to local storage, handled in memory exclusively as ephemeral char arrays that are wiped with zeroes immediately after exchanging them over TLS for authentication tokens.""",
    "deep_senior_en": """When evaluating credential management at a staff level, the most common architectural failure is conflating client identification with client authorization.
Developers frequently embed third-party API keys in BuildConfig and treat them as secrets.
In reality, any string bundled into an APK is a public identifier easily extracted with static analysis tools.
For vendor API keys, security relies entirely on platform-level restrictions such as pinning the key to the release SHA-256 signing fingerprint and package name, combined with API quotas.
For user session management, OAuth 2.0 with Proof Key for Code Exchange (PKCE) is the industry standard.
Access tokens must have strict, short time-to-live envelopes to minimize exposure if intercepted over compromised networks.
Conversely, refresh tokens represent the real crown jewels of client authentication.
If a refresh token leaks, an attacker maintains persistent access to the user account.
Therefore, we persist refresh tokens in EncryptedSharedPreferences backed by hardware-rooted Keystore master keys, while enforcing Refresh Token Rotation on the backend.
Under this rotation pattern, using a refresh token invalidates it and issues a replacement; if an authorization server observes an already-consumed refresh token, it assumes token theft and immediately terminates the entire user session.
Finally, raw passwords must never touch disk persistence or SQLite databases.
In memory, we avoid Java Strings because they are immutable and cached in the internal string pool where garbage collection cannot guarantee timely erasure; instead, we handle passwords as mutable CharArrays and explicitly overwrite them with zeroes immediately following network transmission.""",
    "meta_ar": {
        "id": "SEC-03",
        "questionAr": "مقارنة شاملة بين 5 أنواع من بيانات الاعتماد الحساسة في أندرويد وطرق تأمينها",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصنيف بيانات الاعتماد (المفاتيح التشفيرية، Access Tokens، Refresh Tokens، API Keys، كلمات المرور)، وفهم فترات صلاحيتها، ومخاطر تسريبها، وأماكن تخزينها الصحيحة، وطرق التعامل مع الذاكرة.",
        "concept_ar": "تصنف بيانات الاعتماد في تطبيقات أندرويد إلى خمس فئات متباينة: المفاتيح التشفيرية لحساب التشفير والتوقيع وتُحفظ في Keystore، و Access Tokens القصيرة الأجل لتفويض استدعاءات الشبكة وتُحفظ في الذاكرة أو التخزين المشفر، و Refresh Tokens طويلة الأجل لتجديد الجلسات وتُخزن في EncryptedSharedPreferences، و API Keys لتعريف التطبيق لدى منصات الخدمات ولا تعتبر أسراراً بل تُقيد ببصمة SHA-1، وكلمات المرور التي لا تُخزن محلياً وتُمسح من الذاكرة فوراً.",
        "walkthrough_ar": "تخزين الرموز الحساسة في EncryptedSharedPreferences وتصفير كلمات المرور من الرام:\n```kotlin\nval masterKey = MasterKey.Builder(context)\n    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()\nval encryptedPrefs = EncryptedSharedPreferences.create(\n    context, \"session\", masterKey,\n    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,\n    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM\n)\n// التعامل مع كلمة المرور كمصفوفة محارف قابلة للتصفير فور الاستخدام:\nfun wipePassword(chars: CharArray) { chars.fill('0') }\n```",
        "why_it_matters_ar": "الخلط بين أنواع الرموز وحفظ كلمات المرور أو المفاتيح السرية في الكود أو التخزين غير المشفر يؤدي لاختراق حسابات المستخدمين وتسريب بيانات المنظومة عند تفريغ الذاكرة أو فحص الـ APK.",
        "worked_example_ar": "دورة تبديل وتدوير الـ Refresh Token (RTR) في طبقة الشبكة:\n```kotlin\nclass TokenAuthenticator(private val sessionManager: SecureSessionManager) : Authenticator {\n    override fun authenticate(route: Route?, response: Response): Request? {\n        val newTokens = refreshSession(sessionManager.getRefreshToken())\n        sessionManager.saveTokens(newTokens.access, newTokens.refresh)\n        return response.request.newBuilder()\n            .header(\"Authorization\", \"Bearer ${newTokens.access}\").build()\n    }\n}\n```",
        "trade_offs_ar": "تقصير مدة صلاحية Access Token يعزز الأمان لكنه يزيد من استدعاءات التجديد واستهلاك الشبكة، بينما جعل الـ Refresh Token طويل الأجل يريح المستخدم لكنه يتطلب آليات تدوير صارمة وحظر فوري عند الاشتباه بالتسريب.",
        "failure_modes_ar": "حفظ كلمات مرور المستخدمين كنصوص صريحة في SharedPreferences، أو اعتبار مفاتيح Google Maps أسراراً محمية في ملف BuildConfig دون تقييدها ببصمة الشهادة ونطاق التطبيق في لوحة تحكم السحاب.",
        "production_perspective_ar": "في التطبيقات الإنتاجية، نستخدم بروتوكول OAuth 2.0 مع PKCE، ونحفظ الرموز في EncryptedSharedPreferences، ونطبق استراتيجية Refresh Token Rotation لإلغاء جميع الجلسات تلقائياً إذا حاول مخترق استخدام رمز قديم تم استهلاكه.",
        "how_to_answer_ar": "صنف بيانات الاعتماد الخمسة في جدول ذهني منظم، واذكر لكل نوع: الوظيفة، وفترة الصلاحية، والمكان الآمن لحفظه، وكيفية التعامل مع مخاطر تسريبه في كود أندرويد العملي.",
        "talking_points_ar": "الفرق بين Access Token و Refresh Token، وحماية المفاتيح في Keystore، وحقيقة API Keys كمعرفات عامة، وتصفير CharArray لكلمات المرور في الذاكرة، وبروتوكول Refresh Token Rotation.",
        "follow_ups_ar": "- **المحاور:** \"لماذا نفضل استخدام CharArray لكلمات المرور بدلاً من String في أندرويد؟\"\n  **المرشح:** \"لأن نصوص String غير قابلة للتعديل وتُحفظ في String Pool داخل الرام دون معرفة موعد جمع القمامة، بينما مصفوفة CharArray يمكن إعادة كتابة أصفار فوقها فوراً بعد إرسالها.\"\n\n- **المحاور:** \"كيف نؤمن مفتاح API لخدمة طرف ثالث مثل خرائط جوجل مدمج في ملف الـ APK؟\"\n  **المرشح:** \"نعتبره معرفاً عاماً ونقيد استخدامه في Google Cloud Console بحزمة التطبيق وبصمة توقيع الـ SHA-1 فقط مع وضع قيود وحدود يومية للاستهلاك.\"",
        "self_check_ar": "هل غطيت الفئات الخمسة بالكامل؟ هل وضحت سبب عدم سرية مفاتيح الـ APK؟ وهل شرحت التعامل الآمن مع الذاكرة والتخزين المشفر؟",
        "references_ar": f"- [Jetpack Security EncryptedSharedPreferences](https://developer.android.com/topic/security/data) — دليل أندرويد لتخزين الرموز والبيانات المشفرة.\n- [OAuth 2.0 Threat Model and Security Considerations (RFC 6819)](https://datatracker.ietf.org/doc/html/rfc6819) — المعايير الدولية لحماية الرموز وإدارة الجلسات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نصنف بيانات الاعتماد في أندرويد إلى خمس فئات محددة: مفاتيح التشفير التي تُحفظ داخل Keystore لإجراء العمليات الرياضية، ورموز الوصول المؤقتة لتفويض طلبات السيرفر، ورموز التجديد المحفوظة في تخزين مشفر لتحديث الجلسات، ومفاتيح الواجهات البرمجية العامة المقيدة ببصمة التوقيع وحزمة التطبيق، وكلمات المرور التي لا تُحفظ محلياً وتُمسح من الذاكرة فور إرسالها.",
        "best_answer_ar": "يتطلب تأمين تطبيقات أندرويد تصنيفاً دقيقاً لبيانات الاعتماد وفقاً لدرجة حساسيتها وفترة بقائها ومكان تخزينها المناسب.\n\nالمفاتيح التشفيرية هي أدوات رياضية للتشفير والتوقيع، ويجب أن تُحفظ حصرياً داخل Android Keystore دون مغادرة عتاد الجهاز. وتعتبر Access Tokens رموز تفويض قصيرة الأجل تستمر بين 15 إلى 60 دقيقة وتُرسل في ترويسات الشبكة وتُدار في الذاكرة أو التخزين المؤقت المشفر.\n\nأما Refresh Tokens فهي رموز ثمينة طويلة الأجل تُستخدم حصرياً مع سيرفر الهوية لتوليد رموز وصول جديدة، ويجب تشفيرها على القرص باستخدام EncryptedSharedPreferences وتطبيق آلية تدوير الرموز مع كل استخدام. وتعتبر API Keys مثل مفاتيح الخرائط معرفات عامة وليست أسراراً؛ لأنها تُشحن داخل ملف الـ APK، ولذلك يتم تأمينها بتقييد استخدامها ببصمة توقيع SHA-1 وحزمة التطبيق في لوحات التحكم السحابية. أخيراً، تمثل كلمات المرور أسرار المستخدم الشخصية التي لا يجوز كتابتها على القرص مطلقاً، ويتم التعامل معها في الذاكرة كمصفوفات محارف قابلة للتصفير فور إرسالها عبر بروتوكول مشفر.",
        "deep_answer_ar": "أخطر خطأ معماري يقع فيه مهندسو الموبايل هو الخلط بين هوية العميل وتفويض المستخدم واعتبار الرموز المدمجة في التطبيق أسراراً محمية.\n\nعندما تضع مفتاح واجهة برمجية لخدمة طرف ثالث داخل الكود أو الـ Manifest، يجب أن تفترض هندسياً أنه أصبح عاماً لسهولة استخراجه ببرامج الهندسة العكسية. ولذلك فإن تأمين مفاتيح الـ SDK يعتمد كلياً على تقييد المفتاح في خوادم السحاب ببصمة SHA-256 وPackage Name الخاص بتطبيقك مع تحديد ميزانيات استهلاك صارمة.\n\nوفيما يتعلق بجلسات المستخدمين، يمثل معيار OAuth 2.0 مع PKCE المعيار الذهبي للأنظمة الآمنة. صُممت Access Tokens لتكون قصيرة الأجل لتقليل مساحة الضرر إذا تم اعتراضها عبر شبكة غير آمنة، بينما تمثل Refresh Tokens جوهرة التاج لجلسة العميل؛ لذا نحفظها في EncryptedSharedPreferences مدعومة بمفتاح MasterKey عتادي، ونشترط تطبيق استراتيجية Refresh Token Rotation في السيرفر؛ بحيث يؤدي أي استخدام غير متزامن لرمز قديم إلى إبطال كل جلسات المستخدم للاشتباه في سرقة الرمز.\n\nولحماية بيانات الدخول الأولية، نمتنع تماماً عن استخدام نصوص String لكلمات المرور في الـ JVM؛ لأنها نصوص غير قابلة للتعديل وتظل محتجزة في الـ String Pool حتى يقرر جامع القمامة تفريغها، ونستبدلها بمصفوفات CharArray نقوم بإعادة كتابة الأصفار فوق خلاياها فور اكتمال التبادل الشبكي لقطع الطريق على هجمات تفريغ الذاكرة."
    }
}

# ==========================================
# SEC-04: Why is local.properties not a runtime security mechanism?
# ==========================================
DATA["SEC-04"] = {
    "concept_en": """The local.properties file in an Android project is purely a build-time configuration mechanism designed to configure developer-specific workstation paths (such as the Android SDK directory) and keep private developer credentials out of shared version control repositories like Git. When developers read keys from local.properties inside Gradle build scripts and expose them through BuildConfig fields, manifest placeholders, or compiled resource values, those values are embedded directly into the compiled Dalvik Executable (classes.dex) bytecode or the resources.arsc table inside the packaged APK or Android App Bundle (AAB). A client-side APK is delivered directly into the hands of the end-user and potential adversaries. Anyone can decompile an APK using off-the-shelf reverse-engineering tools like JADX, apktool, or standard command-line utilities like strings to extract every single value compiled from local.properties within seconds. Consequently, local.properties provides zero runtime confidentiality and must never be treated as a secret-management solution for production credentials.""",
    "walkthrough_en": """Demonstrating how local.properties values are exposed in compiled APK bytecode:
```groovy
// 1. Insecure build.gradle pattern leaking local.properties into compiled binary
android {
    defaultConfig {
        Properties properties = new Properties()
        properties.load(project.rootProject.file('local.properties').newDataInputStream())
        // BAD: Payment secret gets compiled as a plaintext string in BuildConfig.java!
        buildConfigField "String", "PAYMENT_GATEWAY_SECRET", "\"${properties.getProperty('PAYMENT_SECRET')}\""
    }
}
```
Decompiling with JADX immediately reveals the plaintext secret:
```java
// Decompiled BuildConfig.java visible to any attacker using JADX or apktool:
package com.example.app;
public final class BuildConfig {
    // Completely exposed in plaintext!
    public static final String PAYMENT_GATEWAY_SECRET = "sk_live_9837492837498234";
}
```""",
    "short_en": """The local.properties file is strictly a developer build-time configuration tool that keeps workstation settings out of git. When values from local.properties are injected into BuildConfig or resource tables, they are compiled directly into the APK as plaintext strings. Anyone can extract them in seconds using decompilers, making it completely ineffective for runtime security.""",
    "structured_en": """The file local.properties serves exclusively as a build-time convenience mechanism for individual developer workstations and source control hygiene.
Its primary purpose is telling Gradle where local SDK and NDK installations live without committing local machine paths to shared Git repositories.
When development teams load API secrets or payment keys from local.properties and inject them into BuildConfig fields, those secrets are translated into constant strings in compiled Dalvik bytecode.
Because Android APK packages are distributed directly to untrusted client devices, any user can inspect the package contents.
Decompilation tools like JADX and apktool disassemble DEX files and reconstruct original Java and Kotlin source code with near-perfect fidelity, exposing compiled strings immediately.
Even enabling R8 code shrinking and ProGuard obfuscation does not protect these values because string literals remain unencrypted in the binary pool.
True runtime security dictates that sensitive secrets must never travel to client binaries, residing exclusively behind authenticated backend servers.""",
    "deep_senior_en": """A foundational principle of mobile systems engineering is recognizing that client-side obscurity never equates to security.
Teams often adopt local.properties under the mistaken belief that keeping a secret out of git makes it safe from end-users.
This confuses developer workstation hygiene with cryptographic runtime confidentiality.
Git-level hygiene prevents casual exposure in commit histories, but once Gradle processes the build script, any buildConfigField or resource mapping embeds the secret directly into classes.dex or resources.arsc.
When an adversary acquires the APK, extracting these values requires no sophisticated hardware lab.
Running the command-line strings utility or opening the APK in JADX immediately surfaces all plaintext constants.
Even attempts to obfuscate the string through byte array XOR shifting or storing it inside native C++ libraries compiled via the NDK provide only trivial barriers.
Disassemblers like Ghidra or IDA Pro disassemble native libraries effortlessly, and dynamic runtime hooking tools like Frida can intercept the string the moment it is loaded into memory.
In production architectures, sensitive credentials such as payment gateway secrets, private database tokens, and confidential signing keys must live exclusively on a trusted backend server.
The mobile app authenticates the user via short-lived bearer tokens and requests the backend to perform the privileged transaction on its behalf, completely decoupling client distribution from credential exposure.""",
    "meta_ar": {
        "id": "SEC-04",
        "questionAr": "لماذا لا يُعد ملف local.properties آلية أمان وقت التشغيل (Runtime Security) في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التمييز الدقيق بين إدارة التكوين وقت البناء (Build-time) وأمان وقت التشغيل (Runtime Confidentiality)، وفهم آلية عمل أدوات الهندسة العكسية، ومعمارية حماية الأسرار في السيرفر.",
        "concept_ar": "ملف local.properties هو ملف إعدادات محلي يُستخدم وقت البناء لتحديد مسارات أدوات التطوير ومنع رفع الإعدادات الخاصة إلى Git. عندما تُقرأ القيم منه وتُحقن في BuildConfig أو الموارد، تُدمج كنصوص صريحة داخل ملفات classes.dex أو جدول الموارد في حزمة الـ APK. ولأن التطبيق يُوزع على أجهزة غير موثوقة، يمكن لأي شخص استخراج هذه النصوص بثوانٍ عبر أدوات مثل JADX أو apktool، مما يجعله عديم الجدوى في تأمين الأسرار وقت التشغيل.",
        "walkthrough_ar": "توضيح الخطأ الشائع في حقن الأسرار وكيف يظهر في الكود بعد تفكيك الـ APK:\n```groovy\n// في build.gradle (ممارسة خاطئة):\nbuildConfigField \"String\", \"PAYMENT_SECRET\", \"\\\"${localProperties['SECRET']}\\\"\"\n```\nعند فحص الـ APK بأداة JADX يظهر الكود بوضوح تام:\n```java\npublic final class BuildConfig {\n    public static final String PAYMENT_SECRET = \"sk_live_98374982374\";\n}\n```",
        "why_it_matters_ar": "الاعتماد على local.properties لحماية المفاتيح الحساسة يعطي شعوراً زائفاً بالأمان ويؤدي لتسريب مفاتيح بوابات الدفع وقواعد البيانات وتكبيد الشركة خسائر فادحة عند نشر التطبيق.",
        "worked_example_ar": "المعمارية الصحيحة لنقل العمليات الحساسة إلى خادم وسيط (BFF Pattern):\n```kotlin\n// التطبيق يطلب المعاملة من السيرفر بتوكن المستخدم فقط دون لمس المفتاح السري:\nclass PaymentRepository(private val api: BankingApi) {\n    suspend fun executePayment(amount: Long): Result<PaymentResponse> {\n        return api.createPaymentIntent(PaymentRequest(amount)) // السيرفر هو من يوقع بالمفتاح السري\n    }\n}\n```",
        "trade_offs_ar": "حقن المفاتيح في الكود يجعل التطبيق يعمل مباشرة بدون بنية تحتية سحابية وسيطة لكنه يضحي بالأمان كلياً، بينما المعمارية الآمنة تتطلب إنشاء خوادم وسيطة وصيانتها لحماية الأسرار الحساسة.",
        "failure_modes_ar": "تضمين مفاتيح بوابات الدفع السرية (Stripe/Paymob Secret Keys) في ملف local.properties ثم تصديرها للـ APK، مما يتيح لأي مخترق سحب المفتاح وتنفيذ عمليات استرداد وسحب أموال غير مصرح بها.",
        "production_perspective_ar": "في بيئات العمل الاحترافية، تُحظر كتابة أي أسرار في local.properties أو BuildConfig بواسطة أدوات الفحص الثابت (Static Analysis)، وتُنفذ كل العمليات المالية عبر خوادم خلفية مؤمنة.",
        "how_to_answer_ar": "ابدأ ببيان الفرق بين حماية الكود من الرفع على Git وأمان التطبيق الفعلي، واشرح كيف تترجم الحقول إلى نصوص صريحة داخل الـ DEX، ثم وضح سهولة الهندسة العكسية، واختم بالمعمارية البديلة عبر خادم وسيط.",
        "talking_points_ar": "الفرق بين Build-time و Runtime، وطبيعة ملف classes.dex، واستخراج النصوص عبر JADX و apktool، وحتمية نقل الأسرار إلى السيرفر، ونمط Backend-for-Frontend.",
        "follow_ups_ar": "- **المحاور:** \"هل يؤدي تفعيل R8 أو ProGuard إلى تشفير النصوص المستخرجة من local.properties؟\"\n  **المرشح:** \"لا، R8 يغير أسماء الكلاسات والدوال فقط لكنه يترك النصوص الثابتة كما هي تماماً كنصوص صريحة يمكن استخراجها بأمر strings بسيط.\"\n\n- **المحاور:** \"إذا كنا بحاجة ماسة لاستدعاء خدمة لا توفر لنا سيرفر وسيط، كيف نحمي المفتاح؟\"\n  **المرشح:** \"نستخدم مفاتيح عميل محدودة الصلاحيات جداً مقيدة بحزمة التطبيق وبصمة التوقيع، مع تفعيل خدمات التحقق من نزاهة التطبيق مثل Play Integrity API.\"",
        "self_check_ar": "هل وضحت الفرق بين إخفاء الملف عن Git وأمان الـ Runtime؟ هل شرحت كيفية استخراج النصوص من الـ APK؟ وهل قدمت الحل المعماري بالسيرفر الوسيط؟",
        "references_ar": f"- [OWASP Mobile Top 10 - Insecure Data Storage and Hardcoded Keys](https://owasp.org/www-project-mobile-top-10/) — معايير OWASP لتحذير المطورين من تضمين المفاتيح في التطبيقات.\n- [Configure build variants and BuildConfig](https://developer.android.com/build/build-variants) — توثيق جوجل الرسمي لكيفية توليد حقول البناء ومحدداتها.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "ملف local.properties هو مجرد أداة إعدادات محلية على جهاز المطور لمنع رفع المسارات الخاصة إلى Git أثناء مرحلة البناء. وعندما تُحقن قيمه في الكود عبر BuildConfig، تُترجم إلى نصوص صريحة داخل ملفات البايت كود الخاصة بالتطبيق، مما يتيح لأي شخص تفكيك التطبيق واستخراج هذه النصوص في ثوانٍ معدودة.",
        "best_answer_ar": "يخلط الكثير من المطورين بين إجراءات النظافة البرمجية في مستودعات Git وبين معايير الأمان التشفيري أثناء وقت التشغيل.\n\nملف local.properties صُمم خصيصاً لمساعدة المطور على ضبط مسارات SDK المحلية على جهازه دون إرسالها إلى الزملاء في Git. ولكن عندما يقوم المطور بقراءة مفتاح سري من هذا الملف وحقنه في متغيرات BuildConfig، فإن نظام Gradle يترجم تلك القيمة إلى نص ثابت صريح داخل ملفات classes.dex المجمعة داخل حزمة التطبيق.\n\nولأن حزمة الـ APK تُسلم بالكامل إلى بيئة غير موثوقة وهي هاتف المستخدم، فإن أي شخص يمتلك التطبيق يستطيع استخدام أدوات تفكيك مجانية مثل JADX أو apktool لرؤية الأكواد والنصوص الصريحة كما كُتبت تماماً. ولا تمنع أدوات التشويش مثل R8 استخراج النصوص لأنها تشوش أسماء الكلاسات فقط وتترك النصوص سليمة، ولذلك لا يمكن اعتبار local.properties آلية أمان نهائياً، ويجب إبقاء الأسرار داخل خوادم مؤمنة.",
        "deep_answer_ar": "القاعدة الأساسية في هندسة أمان أنظمة الموبايل تنص على أن إخفاء الكود لا يمت للأمان الحقيقي بصلة على الإطلاق.\n\nاستخدام local.properties يمنع تسريب المفتاح إلى سجل تعديلات Git، وهو إجراء جيد لإدارة الكود المصدري، لكنه لا يوفر أي سرية تشفيرية بمجرد الضغط على زر بناء التطبيق. فبمجرد اكتمال البناء، تصبح كل قيمة محقونة عبر buildConfigField جزءاً من مصفوفة النصوص الثابتة في الـ DEX أو ملف resources.arsc، وهي مناطق تقرأها أبسط أوامر الطرفية مثل أداة strings دون الحاجة حتى لأدوات هندسة عكسية متقدمة.\n\nوحتى المحاولات التقليدية لتجاوز هذه العقبة؛ مثل تقسيم النص البرمجي إلى أجزاء، أو حفظه داخل مكتبات C++ مبنية عبر NDK، تمثل مجرد عوائق شكلية يسهل اختراقها باستخدام أدوات التحليل الديناميكي ومراقبة الذاكرة مثل Frida التي تقرأ النص لحظة فك تشفيره في الرام قبل استدعاء الشبكة مباشرة.\n\nفي المعماريات المؤسسية الناضجة، نطبق مبدأ Zero-Trust Client؛ حيث لا يحتوي تطبيق الموبايل على أي مفتاح سري لبوابات الدفع أو قواعد البيانات. وبدلاً من ذلك، يتصل التطبيق بخادم وسيط خاص بالشركة Backend-for-Frontend باستخدام توكن جلسة مؤقت، ويقوم السيرفر الموثوق بإجراء المعاملة المالية والتوقيع عليها بالمفتاح السري المحفوظ في بيئة سحابية معزولة. كما ندمج أدوات الفحص الأمني المؤتمتة مثل GitLeaks و MobSF في خطوط البناء المستمر CI/CD لاكتشاف أي مفاتيح محقونة بالخطأ ووقف النشر الفوري قبل وصول الحزم لمتجر جوجل بلاي."
    }
}

# ==========================================
# SEC-05: Can an API secret bundled into an APK ever be fully secret?
# ==========================================
DATA["SEC-05"] = {
    "concept_en": """An API secret bundled into an Android client binary (APK or AAB) can never be fully secret or protected from extraction. In mobile security threat modeling, the client application runs on hardware physically controlled by an untrusted user who possesses full administrative privileges, hardware debuggers, kernel instrumentation, and decompilation toolchains. If an application must possess a secret in order to authenticate a network call, decrypt local data, or invoke a third-party SDK, the decryption logic and the corresponding keys must execute inside the untrusted client environment. Techniques like string encryption, XOR obfuscation, splitting bytes across multiple files, and embedding secrets inside native C/C++ shared libraries (.so files) via the Android NDK merely raise the work factor for casual attackers without solving the cryptographic paradox. Advanced attackers bypass static obfuscation entirely by using dynamic instrumentation frameworks like Frida to hook memory buffers immediately before transmission or attaching debuggers to dump decrypted secrets directly from process memory.""",
    "walkthrough_en": """Why native NDK shared libraries fail to protect bundled secrets against dynamic hooking:
```cpp
// 1. Native C++ implementation attempting to hide secret in native library
#include <jni.h>
extern "C" JNIEXPORT jstring JNICALL
Java_com_example_bank_SecurityBridge_getSecretKey(JNIEnv* env, jobject /* this */) {
    // Easily discovered via 'strings libnative.so' or decompilation in Ghidra!
    return env->NewStringUTF("sk_live_secret_embedded_in_binary_981273");
}
```
Attackers bypass this in seconds using a dynamic Frida memory hook:
```javascript
// 2. Trivial Frida script intercepting the secret at runtime
Java.perform(function() {
    var SecurityBridge = Java.use("com.example.bank.SecurityBridge");
    SecurityBridge.getSecretKey.implementation = function() {
        var secret = this.getSecretKey();
        console.log("[!] Intercepted API Secret from memory: " + secret);
        return secret;
    };
});
```""",
    "short_en": """No bundled API secret in an APK can ever remain truly secret. The mobile application runs on client-controlled hardware where attackers have root privileges, decompilers, and dynamic memory hooking tools like Frida. Any secret that the client can read or decrypt can also be extracted by an adversary, requiring sensitive operations to be moved to a secure backend server.""",
    "structured_en": """In mobile application security, embedding an API secret into an APK is fundamentally insecure because the client environment is completely untrusted.
Because the device hardware and operating system are in the physical possession of the user, attackers can inspect, debug, and modify the execution environment at will.
Common defensive strategies like string obfuscation, mathematical XOR masking, and hiding strings in compiled C++ NDK shared libraries provide only superficial deterrence.
Static analysis tools like Ghidra and IDA Pro disassemble native libraries to reveal hardcoded byte arrays with minimal effort.
More decisively, dynamic instrumentation frameworks like Frida and eBPF allow adversaries to hook function calls at runtime.
Even if a secret is heavily obfuscated on disk, the application must eventually reconstruct the plaintext string in memory to pass it into HTTP request headers or cryptographic ciphers.
An attacker simply hooks the network dispatch or cipher initialization method and captures the plaintext secret from RAM.
Production security requires adopting the Backend-for-Frontend architecture, where third-party secrets remain securely stored on enterprise servers while the mobile app authenticates using short-lived user tokens.""",
    "deep_senior_en": """The belief that an APK can securely safeguard a shared symmetric secret violates Kerckhoffs's principle and fundamental threat modeling.
In cryptographic systems, security must rely entirely on the secrecy of the key, not on the obscurity of the algorithm.
When a symmetric secret is shipped inside an APK, both the encrypted ciphertext and the algorithmic key distribution logic reside within the adversary's laboratory.
Native code via the Android NDK is frequently cited as a security barrier, but compiled C and C++ binaries are subject to straightforward disassembly.
Tools like Ghidra readily locate string tables, reconstruct symbol tables, and trace assembly routines back to their output registers.
Furthermore, static analysis is not even required when dynamic inspection exists.
Using dynamic binary instrumentation platforms such as Frida, an adversary can hook Java methods, native function addresses, or OpenSSL SSL_write calls.
Because the operating system must ultimately assemble the raw HTTP request packet, the secret must exist in plaintext memory buffers prior to encryption and transmission over the network socket.
To build a resilient enterprise system, we eliminate client-side secrets entirely.
We implement Backend-for-Frontend proxies that authenticate the mobile client using OAuth 2.0 with PKCE and hardware-backed device attestation through the Play Integrity API.
The backend server validates the integrity verdict, confirms the genuine identity of the application package, and attaches the confidential vendor API secret on the server side before communicating with downstream payment or enterprise APIs.""",
    "meta_ar": {
        "id": "SEC-05",
        "questionAr": "هل يمكن لأي مفتاح سري (API Secret) مدمج داخل ملف APK أن يظل سرياً ومحمياً تماماً من الاستخراج؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "استيعاب نموذج التهديد في تطبيقات الموبايل (Threat Modeling)، وحتمية عدم الثقة في بيئة العميل، وأسباب فشل إخفاء المفاتيح في كود C++ NDK، وآليات الاستخراج الديناميكي عبر Frida، والحلول المعمارية عبر السيرفر الوسيط.",
        "concept_ar": "لا يمكن لأي مفتاح سري مدمج داخل ملف APK أن يظل سرياً بأي شكل من الأشكال؛ لأن التطبيق يعمل على جهاز يقع تحت السيطرة المادية الكاملة للمستخدم والمهاجمين. وكل تقنيات التمويه مثل إخفاء النصوص أو تشفيرها أو وضعها داخل مكتبات C++ NDK تفشل حتماً؛ لأن التطبيق يحتاج لفك تشفيرها في الذاكرة لاستخدامها، مما يتيح للمهاجمين قراءتها بسهولة عبر أدوات الهندسة العكسية والاعتراض الديناميكي مثل Frida.",
        "walkthrough_ar": "فشل حماية المفتاح داخل مكتبة C++ واعتراضه بسهولة عبر سكريبت Frida في ثوانٍ:\n```cpp\n// محاولة إخفاء المفتاح في كود C++:\nJNIEXPORT jstring JNICALL Java_com_bank_Security_getSecret(JNIEnv* env, jobject) {\n    return env->NewStringUTF(\"sk_live_very_secret_key\");\n}\n```\nاعتراض القيمة برمجياً في الرام عبر Frida:\n```javascript\nJava.perform(function() {\n    Java.use(\"com.bank.Security\").getSecret.implementation = function() {\n        var key = this.getSecret();\n        console.log(\"Captured Secret from RAM: \" + key); // يظهر المفتاح فوراً\n        return key;\n    };\n});\n```",
        "why_it_matters_ar": "الاعتقاد بإمكانية حماية الأسرار داخل الـ APK يقود إلى كوارث أمنية؛ إذ يقوم المهاجمون بتفكيك التطبيق واستخراج مفاتيح خدمات الدفع والذكاء الاصطناعي واستنزاف أموال وحسابات الشركة.",
        "worked_example_ar": "المعمارية البديلة الآمنة: خادم وسيط (BFF) مع التحقق من نزاهة التطبيق عبر Play Integrity:\n```kotlin\nclass SecurePaymentClient(private val bffApi: BffService) {\n    suspend fun pay(orderId: String, userToken: String) {\n        // التطبيق لا يعرف سر بوابة الدفع نهائياً، يرسل فقط معرف الطلب وتوكن الجلسة\n        bffApi.processOrder(orderId, \"Bearer $userToken\")\n        // السيرفر هو من يمتلك المفتاح السري ويتصل ببوابة الدفع بأمان\n    }\n}\n```",
        "trade_offs_ar": "محاولات التمويه المعقدة في C++ تزيد من حجم التطبيق وصعوبة صيانته دون أي فائدة أمنية حقيقية، بينما نقل العمليات للسيرفر يفرض تكلفة استضافة لكنه يوفر أماناً مطلقاً وموثوقاً.",
        "failure_modes_ar": "تشفير المفتاح داخل الـ APK بمفتاح تشفير آخر مدمج أيضاً داخل الـ APK، وهو ما يمثل حلقة مفرغة وفشلاً ذريعاً لأن الكود البرمجي الذي يفك التشفير متاح بالكامل للمهاجم.",
        "production_perspective_ar": "في بنوك التكنولوجيا المالية، نعتبر العميل بيئة معادية تماماً (Zero-Trust)، ونمنع وجود أي مفاتيح سرية في الكود، ونعتمد على Play Integrity للتحقق من سلامة التطبيق والجهاز قبل تنفيذ العمليات الحساسة.",
        "how_to_answer_ar": "أجب بحسم قاطع: 'مستحيل تماماً'، ثم فسر نموذج التهديد وسيطرة المستخدم على العتاد، واشرح فشل التمويه والـ NDK أمام أدوات مثل Frida، واختم بالحل المعماري الصحيح وهو الخادم الوسيط.",
        "talking_points_ar": "مبدأ كيركهوفس (Kerckhoffs's principle)، وبيئة العميل غير الموثوقة (Untrusted Client)، وفشل حماية C++ NDK أمام Ghidra، وتلصص الذاكرة عبر Frida، ونمط BFF مع Play Integrity.",
        "follow_ups_ar": "- **المحاور:** \"ماذا لو قمنا بتقسيم المفتاح إلى 10 أجزاء في أماكن متفرقة ودمجناها أثناء التشغيل؟\"\n  **المرشح:** \"سيظل الكود الذي يجمع الأجزاء موجوداً في نفس التطبيق، وبمجرد أن تتجمع الأجزاء في نص واحد لإرسالها للشبكة، سيلتقطها المخترق من الرام بأداة Frida في سطر واحد.\"\n\n- **المحاور:** \"كيف تؤمن شركات الدفع مثل Stripe عملها داخل تطبيقات الموبايل؟\"\n  **المرشح:** \"تستخدم Stripe مفتاحاً عاماً (Publishable Key) محدد الصلاحيات لإنشاء توكن لبطاقة العميل فقط، بينما يبقى المفتاح السري الحقيقي (Secret Key) لتنفيذ السحب داخل سيرفر الشركة حصراً.\"",
        "self_check_ar": "هل أجبت بحسم بعدم إمكانية الحماية؟ هل شرحت كيفية تجاوز التمويه عبر Frida؟ وهل وضحت نمط السيرفر الوسيط BFF؟",
        "references_ar": f"- [OWASP Mobile Security Testing Guide - Tampering and Reverse Engineering](https://mas.owasp.org/MASTG/) — دليل OWASP لاختبار وفحص الهندسة العكسية لتطبيقات الموبايل.\n- [Play Integrity API Documentation](https://developer.android.com/google/play/integrity) — التوثيق الرسمي لخدمة جوجل للتحقق من نزاهة التطبيقات والأجهزة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "لا يمكن لأي مفتاح سري مدمج داخل ملف APK أن يظل سرياً أو محمياً على الإطلاق. فتطبيق الموبايل يعمل على هاتف يملكه المستخدم وتحت سيطرته الكاملة، مما يتيح له استخدام أدوات الهندسة العكسية وتفكيك الكود واعتراض الذاكرة عبر أدوات مثل Frida لاستخراج أي مفتاح بمجرد استخدامه، والحل الوحيد هو نقل العمليات الحساسة إلى خادم وسيط مؤمن.",
        "best_answer_ar": "الإجابة القاطعة هي لا؛ لا يوجد أي مفتاح سري مدمج في ملف الـ APK يمكن اعتباره محمياً أو مستحيلاً استخراجه.\n\nالسبب الهندسي الجوهري هو أن تطبيق الموبايل يوزع ويعمل داخل بيئة غير موثوقة يملك فيها المهاجم تحكماً كاملاً في العتاد ونظام التشغيل وأدوات الروت وتصحيح الأخطاء. وكل الحيل التي يلجأ إليها المطورون مثل تجزئة النصوص، أو تشفيرها، أو إخفائها داخل مكتبات C++ مبنية عبر NDK، تمثل مجرد عوائق تافهة أمام أدوات التحليل العكسي الحديثة مثل Ghidra.\n\nوالأهم من ذلك هو وجود أدوات التلصص الديناميكي على الذاكرة مثل أداة Frida؛ فمهما كانت درجة تعقيد تشفير المفتاح على القرص، فإن التطبيق مضطر في النهاية لفك تشفيره وتجميعه في الذاكرة كنص صريح لتمريره في ترويسة الطلب الشبكي، وهناك يستطيع المخترق اعتراض الدالة وقراءة المفتاح من الرام بضغطة زر. ولذلك، تفرض المعمارية السليمة إبقاء الأسرار في السيرفر الوسيط والتواصل عبر رموز تفويض قصيرة الأجل.",
        "deep_answer_ar": "الاعتقاد بإمكانية حماية مفتاح سري متماثل داخل تطبيق موزع للعامة يناقض المبادئ التأسيسية لأمن المعلومات مثل مبدأ كيركهوفس ونمذجة التهديدات البرمجية.\n\nفي التشفير الحقيقي، يجب أن يعتمد أمان النظام على سرية المفتاح فقط وليس على غموض الخوارزمية. وعندما تشحن مفتاحاً داخل الـ APK، فأنت تسلم النص المشفر وخوارزمية فك التشفير معاً إلى يد المهاجم في معمله الخاص. وكثيراً ما يتوهم المطورون أن لغات التجميع والـ C++ توفر حصناً منيعاً، في حين أن أدوات الهندسة العكسية مثل IDA Pro و Ghidra تستخرج مصفوفات البايتات وجداول الرموز في دقائق معدودة.\n\nوعلاوة على التحليل الساكن، فإن أدوات الاعتراض الديناميكي Binary Instrumentation مثل Frida و eBPF تجعل محاولات التمويه عديمة القيمة تماماً؛ إذ يستطيع المهاجم ربط دوال الشبكة مثل OkHttp أو استدعاءات OpenSSL SSL_write مباشرة والتقاط البايتات الصريحة قبل خروجها للبطاقة الشبكية بدقة بالغة.\n\nفي الأنظمة المؤسسية الكبرى، نتخلص من فكرة حفظ الأسرار في العميل تماماً ونتبنى نمط Backend-for-Frontend مدعوماً بمصادقة OAuth 2.0 وتقييم نزاهة التطبيق والجهاز عبر Play Integrity API. فيقوم السيرفر بالتحقق من أن الطلب قادم من نسخة أصلية غير مروّتة، ثم يقوم هو بإرفاق المفاتيح السرية للبوابات المالية وإتمام المعاملات في بيئة سحابية آمنة لا يراها العميل أبداً."
    }
}

# ==========================================
# SEC-06: What are encryption at rest and encryption in transit?
# ==========================================
DATA["SEC-06"] = {
    "concept_en": """Encryption at rest and encryption in transit are the two complementary pillars of end-to-end data confidentiality on Android, protecting sensitive information across distinct operational states. Encryption at rest secures persistent data stored on non-volatile physical flash storage against offline extraction, device theft, and unauthorized access. Modern Android implements this at the system level via File-Based Encryption (FBE), partitioning storage into Credential Encrypted (CE) storage (accessible only after the user unlocks the device with their PIN or biometrics) and Device Encrypted (DE) storage (accessible during Direct Boot before unlock for critical services like alarms). At the application level, developers layer additional cryptographic security using the Jetpack Security library (EncryptedSharedPreferences and EncryptedFile) or SQLCipher for encrypted Room databases, binding encryption keys to the Android Keystore. Encryption in transit protects data moving across volatile public and private networks between the mobile client and remote backend services against eavesdropping, interception, and man-in-the-middle (MITM) tampering. It relies on Transport Layer Security (TLS 1.3), robust cipher suites, and Android Network Security Configuration.""",
    "walkthrough_en": """Implementing layered encryption at rest and encryption in transit in Android:
```kotlin
// 1. Encryption at rest: EncryptedSharedPreferences backed by hardware Keystore
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val securePreferences = EncryptedSharedPreferences.create(
    context,
    "user_pii_vault",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// 2. Encryption in transit: Strict TLS 1.3 enforcement via OkHttpClient
val secureHttpClient = OkHttpClient.Builder()
    .connectionSpecs(listOf(
        ConnectionSpec.MODERN_TLS // Enforces TLS 1.2 and TLS 1.3 with secure cipher suites
    ))
    .certificatePinner(
        CertificatePinner.Builder()
            .add("api.bank.com", "sha256/k2oTQLj4nsdKmSOGKEUbhwEYfEuDYV5R6g28AzERdOk=")
            .build()
    )
    .build()
```""",
    "short_en": """Encryption at rest secures data stored on the device's physical disk using File-Based Encryption, EncryptedSharedPreferences, or SQLCipher so stolen or dumped storage remains unreadable. Encryption in transit protects data travelling over the network using TLS 1.3 and certificate pinning, preventing eavesdropping and man-in-the-middle tampering during transmission.""",
    "structured_en": """Comprehensive mobile confidentiality demands securing data both when it resides persistently on device hardware and while it traverses network pathways.
Encryption at rest protects stored bytes against offline extraction, forensic dumping, and device theft.
At the operating system level, Android employs File-Based Encryption with two cryptographic zones: Device Encrypted storage available during Direct Boot before user unlock, and Credential Encrypted storage unlocked only when the user enters their lockscreen credentials.
Within the application, developers protect sensitive records using EncryptedSharedPreferences for key-value pairs and SQLCipher for Room databases, anchoring symmetric encryption keys directly in the hardware-backed Android Keystore.
Encryption in transit protects data packets moving over public cellular and Wi-Fi networks against interception, tampering, and eavesdropping.
This is implemented using modern Transport Layer Security protocols, specifically TLS 1.2 and TLS 1.3, which negotiate authenticated key exchange and symmetric payload ciphers.
To harden transit security against compromised certificate authorities and rogue corporate proxies, applications configure Android Network Security Configuration to disallow cleartext traffic and implement public key certificate pinning.""",
    "deep_senior_en": """When analyzing threat models for enterprise and financial applications, understanding the precise boundary where encryption at rest ends and encryption in transit begins is essential for operational security.
A common failure mode is assuming that because Android provides platform-level File-Based Encryption, application-level encryption is unnecessary.
While FBE protects physical flash partitions if a powered-off device is stolen, once the user unlocks their phone, the Credential Encrypted partition is mounted and decrypted in the Linux kernel.
If an attacker exploits a local vulnerability or gains privileged execution in an adjacent process, raw files in the application sandbox become accessible unless protected by an application-level layer such as Jetpack Security or SQLCipher backed by Keystore master keys.
Conversely, encryption in transit guarantees that packets flowing between the client socket and the cloud load balancer remain confidential and tamper-proof.
However, transport encryption terminates at the network endpoint.
If an application transmits sensitive payloads over HTTPS without certificate pinning, a user on a managed enterprise network with an installed root CA certificate or an attacker using a rogue cellular base station can execute a Man-in-the-Middle attack.
Therefore, a defense-in-depth architecture enforces TLS 1.3 with Certificate Pinning for transit, uses EncryptedSharedPreferences backed by hardware Keystore keys for local data at rest, and rigorously zeroes out sensitive memory buffers so credentials are protected even while resident in RAM.""",
    "meta_ar": {
        "id": "SEC-06",
        "questionAr": "ما هو الفرق بين التشفير في حالة السكون (At Rest) والتشفير أثناء النقل (In Transit) في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم معمارية حماية البيانات في حالتي التخزين والنقل، ومعمارية تشفير الملفات FBE ومناطق CE و DE في أندرويد، واستخدام مكتبة Jetpack Security و SQLCipher، وتطبيق بروتوكول TLS و Certificate Pinning في قنوات الشبكة.",
        "concept_ar": "التشفير في حالة السكون (Encryption at Rest) يحمي البيانات المخزنة على الذاكرة الدائمة للجهاز ضد استخراجها عند سرقة الهاتف أو فحص الذاكرة، ويشمل File-Based Encryption على مستوى النظام، ومكتبات مثل EncryptedSharedPreferences و SQLCipher على مستوى التطبيق مدعومة بـ Keystore. بينما التشفير أثناء النقل (Encryption in Transit) يحمي البيانات أثناء حركتها عبر الشبكات من التنصت والتلاعب بواسطة بروتوكولات TLS 1.3 وتثبيت الشهادات.",
        "walkthrough_ar": "تأمين البيانات المخزنة عبر EncryptedSharedPreferences وتأمين الشبكة بـ TLS 1.3 و Certificate Pinner:\n```kotlin\n// تشفير البيانات محلياً بمفتاح عتادي من Keystore:\nval masterKey = MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()\nval securePrefs = EncryptedSharedPreferences.create(\n    context, \"vault\", masterKey,\n    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,\n    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM\n)\n// تأمين النقل عبر الشبكة بربط الشهادة ومنع الترافيك غير المشفر:\nval client = OkHttpClient.Builder()\n    .connectionSpecs(listOf(ConnectionSpec.MODERN_TLS))\n    .certificatePinner(CertificatePinner.Builder().add(\"api.bank.com\", \"sha256/...\").build())\n    .build()\n```",
        "why_it_matters_ar": "إهمال أي من المحورين يعرض المستخدم للاختراق؛ فحماية الشبكة وحدها لا تمنع سرقة البيانات من الهاتف المسروق، وحماية التخزين وحدها تسمح باعتراض البيانات والتلاعب بها عبر شبكات الواي فاي العامة.",
        "worked_example_ar": "استخدام مساحة التخزين المشفرة قبل الفتح (Device Encrypted Storage) للخدمات الحيوية:\n```kotlin\n// الوصول لتخزين DE المتاح أثناء إقلاع الجهاز وقبل إدخال كود القفل:\nval deContext = context.createDeviceProtectedStorageContext()\nval dePrefs = deContext.getSharedPreferences(\"alarm_triggers\", Context.MODE_PRIVATE)\n```",
        "trade_offs_ar": "تشفير البيانات محلياً عبر SQLCipher يستهلك موارد المعالج ويزيد زمن القراءة والكتابة مقارنة بقواعد البيانات العادية، كما أن تثبيت الشهادات يعقد عمليات تدوير المفاتيح في السيرفر ويتطلب إدارة محكمة.",
        "failure_modes_ar": "السماح بمرور حركة المرور غير المشفرة (Cleartext HTTP) في تطبيق الإنتاج، أو حفظ البيانات البنكية في ملفات SharedPreferences عادية اعتماداً فقط على عزل النظام دون تشفير إضافي.",
        "production_perspective_ar": "في التطبيقات المصرفية، نفرض سياسة Network Security Config تحظر أي اتصال غير مشفر، ونستخدم SQLCipher لحفظ قواعد بيانات Room محلياً، ونربط مفاتيح التشفير بـ Android Keystore مع تفعيل TLS 1.3 حصراً.",
        "how_to_answer_ar": "قسم الإجابة إلى شقين متوازنين: اشرح مفهوم التشفير في حالة السكون وأدواته في أندرويد (FBE, EncryptedPrefs, SQLCipher)، ثم اشرح التشفير أثناء النقل وأدواته (TLS 1.3, Network Security Config, Pinning)، واختم بالدفاع في العمق.",
        "talking_points_ar": "تشفير الملفات FBE ومناطق CE و DE، ومكتبة Jetpack Security، وقواعد بيانات SQLCipher، وبروتوكول TLS 1.3، وتثبيت الشهادات Certificate Pinning، ومفهوم الدفاع في العمق (Defense in Depth).",
        "follow_ups_ar": "- **المحاور:** \"لماذا نحتاج لتشفير قاعدة بيانات SQLite بتطبيق SQLCipher إذا كان نظام أندرويد يطبق FBE بالفعل؟\"\n  **المرشح:** \"لأن FBE يفك تشفير القرص بمجرد فتح المستخدم لقفل الشاشة، فإذا استغل مهاجم ثغرة محلية داخل النظام والجهاز مفتوح يمكنه قراءة الملفات، بينما SQLCipher يظل مشفراً بمفتاحه الخاص دائماً.\"\n\n- **المحاور:** \"ما هو تخزين Device Encrypted (DE) ومتى تحتاجه؟\"\n  **المرشح:** \"هو مساحة تخزين مشفرة تتاح قبل قيام المستخدم بإلغاء قفل الشاشة عند إعادة تشغيل الهاتف (Direct Boot)، ونحتاجها في خدمات المنبه وتلقي المكالمات الطارئة وإشعارات التنبيه الحرجة.\"",
        "self_check_ar": "هل غطيت الشقين بوضوح؟ هل ذكرت FBE ومناطق CE/DE؟ وهل شرحت TLS وتثبيت الشهادات في النقل؟",
        "references_ar": f"- [Android Direct Boot and File-Based Encryption](https://developer.android.com/privacy-and-security/direct-boot) — توثيق جوجل الرسمي لتشفير الملفات ومناطق التخزين.\n- [Network Security Configuration](https://developer.android.com/privacy-and-security/security-config) — إعدادات أمان الشبكة وحظر الاتصالات غير المشفرة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "التشفير في حالة السكون يحمي البيانات المحفوظة على ذاكرة الهاتف من الاستخراج في حال سرقة الجهاز أو فحصه جنائياً، وذلك عبر تشفير الملفات FBE ومكتبات التشفير مثل EncryptedSharedPreferences و SQLCipher. أما التشفير أثناء النقل فيحمي البيانات أثناء سفرها عبر شبكات الإنترنت من التنصت والتلاعب بواسطة بروتوكولات TLS الحديثة وتثبيت الشهادات الرقمية.",
        "best_answer_ar": "يرتكز أمان البيانات في تطبيقات أندرويد على ركيزتين متكاملتين تغطيان حالتي بقاء البيانات وانتقالها.\n\nالتشفير في حالة السكون يعني تأمين البيانات المخزنة على الذاكرة الوميضية للجهاز. ويطبق نظام أندرويد تقنية تشفير الملفات FBE التي تقسم الذاكرة إلى منطقتين؛ منطقة CE المشفرة ببيانات دخول المستخدم والتي تظل مقفلة حتى يفتح الشاشة، ومنطقة DE المتاحة أثناء بدء التشغيل المباشر Direct Boot للمهام الحرجة كالمنبهات. وعلى مستوى التطبيق، نستخدم مكتبة Jetpack Security وقواعد بيانات SQLCipher لتشفير البيانات الحساسة بمفاتيح مولدة داخل Android Keystore.\n\nوعلى الجانب الموازي، يعني التشفير أثناء النقل حماية حزم البيانات أثناء عبورها شبكات الواي فاي والمحمول للوصول إلى السيرفر. ويتم ذلك من خلال بروتوكول TLS 1.3 الذي يضمن تشفير القناة والتأكد من عدم التلاعب بالبيانات، ونعزز ذلك بملف Network Security Config لمنع الاتصالات غير المشفرة كلياً، واستخدام Certificate Pinning لمنع هجمات اعتراض حركة المرور من قبل شهادات خبيثة.",
        "deep_answer_ar": "في النمذجة الأمنية المتقدمة للتطبيقات البنكية، نعتبر التشفير في حالة السكون والتشفير أثناء النقل خطين دفاعيين متكاملين ضمن استراتيجية الدفاع في العمق Defense-in-Depth.\n\nالخطأ الشائع هو افتراض أن تشفير نظام أندرويد للملفات FBE يغني المطور عن تشفير بيانات تطبيقه محلياً؛ فحقيقة الأمر أن تشفير FBE يحمي الجهاز وهو مغلق، لكن بمجرد قيام العميل بفتح قفل الشاشة يتم فك تشفير قطاع Credential Encrypted في كيرنل لينكس. وإذا نجح تطبيق خبيث في استغلال ثغرة تصعيد صلاحيات على الجهاز، فإنه سيتمكن من قراءة ملفات التطبيق غير المشفرة؛ ولذلك نحرص على تشفير قاعدة بيانات Room عبر مكتبة SQLCipher واستخدام EncryptedSharedPreferences بمفاتيح عتادية غير قابلة للاستخراج.\n\nأما في مسار التشفير أثناء النقل، فإن الهدف هو تحصين الاتصال الشبكي ضد هجمات الوسيط Man-in-the-Middle. ولأن الاتصال عبر HTTPS العادي يثق بأي جهة إصدار شهادات CA مثبتة في جهاز المستخدم، يستطيع المهاجم أو شبكات الشركات تنصيب شهادة جذرية مخصصة وفك تشفير الاتصال بالكامل. لذلك نقوم بتطبيق Certificate Pinning لتثبيت تجزئة المفتاح العام لخوادمنا، مع فرض بروتوكول TLS 1.3 وحظر بروتوكولات التشفير القديمة، بالإضافة لتصفير البيانات الحساسة من ذاكرة الوصول العشوائي فور استخدامها لإحكام غلق دائرة الأمان. ونعزز ذلك بإيقاف الكاش الشبكي للردود الحساسة في OkHttp وتعطيل النسخ الاحتياطي التلقائي في ملف الـ Manifest لضمان عدم تسريب البيانات غير المشفرة لأي وسيط خارجي."
    }
}

# ==========================================
# SEC-07: Compare encryption, hashing, HMAC, and digital signatures.
# ==========================================
DATA["SEC-07"] = {
    "concept_en": """Modern cryptography provides four fundamental mathematical primitives, each addressing distinct security objectives: confidentiality, integrity, authenticity, and non-repudiation. Encryption transforms plaintext into ciphertext using a key, providing confidentiality; it is reversible when the corresponding decryption key is possessed. Encryption is divided into symmetric ciphers (such as AES-GCM, where the same key is used for both operations, making it extremely fast for bulk data) and asymmetric ciphers (such as RSA or ECC, where a public key encrypts and a private key decrypts). Hashing is a one-way mathematical function (such as SHA-256) that maps arbitrary-length inputs to a fixed-size digest, providing integrity verification; it uses no keys and cannot be reversed. HMAC (Hash-based Message Authentication Code) combines a cryptographic hash with a shared secret key, providing both integrity and authenticity; it verifies that the message has not been tampered with and was produced by an entity holding the shared key. Digital signatures combine asymmetric cryptography with hashing; the sender signs a message digest using their private key, and any verifier holding the corresponding public key can verify authenticity, integrity, and non-repudiation.""",
    "walkthrough_en": """Comparing cryptographic primitives implementation in Kotlin:
```kotlin
// 1. Symmetric Authenticated Encryption (AES-GCM): Confidentiality + Integrity
fun encryptAesGcm(plaintext: ByteArray, secretKey: SecretKey): Pair<ByteArray, ByteArray> {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.ENCRYPT_MODE, secretKey)
    val iv = cipher.iv // 12-byte initialization vector
    val ciphertext = cipher.doFinal(plaintext)
    return Pair(iv, ciphertext)
}

// 2. Cryptographic Hash (SHA-256): One-way Integrity check (No Key)
fun computeSha256(data: ByteArray): ByteArray =
    MessageDigest.getInstance("SHA-256").digest(data)

// 3. HMAC (HMAC-SHA256): Symmetric Authenticity + Integrity (Shared Key)
fun computeHmac(data: ByteArray, sharedKey: SecretKey): ByteArray {
    val mac = Mac.getInstance("HmacSHA256")
    mac.init(sharedKey)
    return mac.doFinal(data)
}

// 4. Digital Signature (ECDSA): Asymmetric Authenticity + Integrity + Non-repudiation
fun signPayloadEcdsa(data: ByteArray, privateKey: PrivateKey): ByteArray {
    val signer = Signature.getInstance("SHA256withECDSA")
    signer.initSign(privateKey)
    signer.update(data)
    return signer.sign()
}
```""",
    "short_en": """We distinguish four cryptographic primitives by their mathematical goals: encryption uses keys to hide data reversibly for confidentiality, hashing creates fixed one-way digests without keys to check integrity, HMAC combines hashing with a shared secret key for symmetric authenticity, and digital signatures use asymmetric private keys to guarantee authenticity, integrity, and non-repudiation.""",
    "structured_en": """Selecting the correct cryptographic primitive depends strictly on whether the engineering requirement is confidentiality, integrity, authenticity, or non-repudiation.
Encryption provides confidentiality by rendering data unreadable to anyone lacking the decryption key.
It exists as symmetric encryption like AES-GCM, which uses a single shared key for rapid bulk data processing, and asymmetric encryption like RSA, which uses mathematically paired public and private keys.
Hashing provides integrity verification without using any keys.
A cryptographic hash function like SHA-256 takes input of any length and produces a deterministic, fixed-size digest that cannot be reversed, exhibiting an avalanche effect where changing one bit completely alters the digest.
HMAC provides message integrity and authenticity by combining a cryptographic hash function with a pre-shared secret key, proving that the sender possessed the key and the payload was not altered.
Digital signatures provide the highest level of trust by combining asymmetric cryptography with hashing.
The sender hashes the payload and encrypts the digest with their private key; recipients verify the signature using the sender's public key, proving authenticity, message integrity, and mathematical non-repudiation.""",
    "deep_senior_en": """In enterprise system design, choosing the wrong cryptographic primitive or misunderstanding its mathematical guarantees introduces catastrophic vulnerabilities.
A classic anti-pattern is storing passwords using raw cryptographic hashes like SHA-256 or MD5.
Because cryptographic hashes are designed for high throughput, attackers can compute billions of guesses per second using GPUs and rainbow tables; password hashing requires slow, memory-hard key derivation functions like Argon2id or PBKDF2 with unique salts.
Another frequent mistake is confusing encryption with authentication.
Using unauthenticated symmetric encryption like AES-CBC without an integrity tag leaves the ciphertext vulnerable to padding oracle attacks and bit-flipping manipulation.
Modern engineering mandates Authenticated Encryption with Associated Data (AEAD), such as AES-256-GCM, which generates an authentication tag alongside the ciphertext to detect tampering.
When comparing HMAC to Digital Signatures, the distinction centers on key distribution and non-repudiation.
HMAC relies on a symmetric shared secret; because both the sender and receiver hold the identical key, either party could mathematically forge the HMAC, meaning HMAC cannot provide legal non-repudiation.
Digital signatures solve this through asymmetric key pairs.
In mobile banking, we use hardware-backed ECDSA keys generated inside Android Keystore.
The client signs a financial transaction digest using its hardware-isolated private key, and the banking server verifies the signature using the registered public key.
Because the private key can never leave the client's secure hardware, the signature provides indisputable cryptographic non-repudiation.""",
    "meta_ar": {
        "id": "SEC-07",
        "questionAr": "مقارنة رياضية ومعمارية بين التشفير، والتجزئة (Hashing)، وHMAC، والتوقيع الرقمي (Digital Signatures)",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "التمييز بين أهداف الأمان الأربعة (السرية، والنزاهة، والمصادقة، وعدم الإنكار)، ومعرفة الاستخدام الصحيح لكل أداة تشفيرية، وتجنب الأخطاء الشائعة مثل استخدام التجزئة البسيطة لكلمات المرور أو التشفير غير الموثق.",
        "concept_ar": "تنقسم أدوات التشفير الرياضية إلى أربع ركائز أساسية: التشفير (Encryption) ويوفر السرية وهو قابل للانعكاس بمفتاح (متماثل كـ AES أو غير متماثل كـ RSA)، والتجزئة (Hashing) وتوفر النزاهة دون مفاتيح وهي دالة أحادية الاتجاه (مثل SHA-256)، و HMAC ويوفر النزاهة والمصادقة بدمج التجزئة مع مفتاح سري مشترك، والتوقيع الرقمي (Digital Signatures) ويوفر النزاهة والمصادقة وعدم الإنكار باستخدام زوج مفاتيح غير متماثل (مفتاح خاص للتوقيع وعام للتحقق).",
        "walkthrough_ar": "تطبيق الأدوات التشفيرية الأربعة عملياً في كود Kotlin:\n```kotlin\n// 1. التشفير المتماثل الموثق (AES-GCM) للسرية والنزاهة:\nval cipher = Cipher.getInstance(\"AES/GCM/NoPadding\").apply { init(Cipher.ENCRYPT_MODE, aesKey) }\nval ciphertext = cipher.doFinal(data)\n\n// 2. التجزئة (SHA-256) لفحص النزاهة دون مفتاح:\nval digest = MessageDigest.getInstance(\"SHA-256\").digest(data)\n\n// 3. كود HMAC للمصادقة بمفتاح مشترك:\nval mac = Mac.getInstance(\"HmacSHA256\").apply { init(secretKey) }.doFinal(data)\n\n// 4. التوقيع الرقمي (ECDSA) لعدم الإنكار:\nval signature = Signature.getInstance(\"SHA256withECDSA\").apply {\n    initSign(privateKey)\n    update(data)\n}.sign()\n```",
        "why_it_matters_ar": "فهم الفروق الرياضية يمنع الوقوع في كوارث برمجية كاستخدام التجزئة لحفظ كلمات المرور دون Salt أو استخدام التشفير دون التحقق من سلامة البيانات وتعديلها أثناء النقل.",
        "worked_example_ar": "التحقق من عدم الإنكار في المعاملات المالية باستخدام التوقيع الرقمي:\n```kotlin\nfun verifyTransactionSignature(payload: ByteArray, signatureBytes: ByteArray, publicKey: PublicKey): Boolean {\n    return Signature.getInstance(\"SHA256withECDSA\").run {\n        initVerify(publicKey)\n        update(payload)\n        verify(signatureBytes)\n    }\n}\n```",
        "trade_offs_ar": "التشفير المتماثل فائق السرعة لكنه يعاني من مشكلة توزيع المفتاح السري، بينما التشفير غير المتماثل والتوقيع الرقمي يحلان توزيع المفاتيح وعدم الإنكار لكنهما يستهلكان موارد معالجة أكبر بكثير.",
        "failure_modes_ar": "استخدام دوال التجزئة العادية مثل SHA-256 لتخزين كلمات المرور مما يسمح بكسرها السريع عبر جداول Rainbow Tables، أو استخدام نمط التشفير AES-ECB أو AES-CBC غير الموثق مما يسمح بالتلاعب بالبيانات المشفرة.",
        "production_perspective_ar": "في النظم المصرفية، نستخدم AES-256 GCM لتشفير البيانات المخزنة محلياً، ونستخدم خوارزمية Argon2id أو PBKDF2 لكلمات المرور في السيرفر، ونعتمد على توقيعات ECDSA الرقمية المنفذة في Keystore لتوثيق التحويلات المالية.",
        "how_to_answer_ar": "ارسم جدولاً ذهنياً يحدد لكل أداة: الهدف الأمني (سرية، نزاهة، مصادقة، عدم إنكار)، وهل تستخدم مفتاحاً أم لا، وقابليتها للانعكاس، ومثال تطبيقي واقعي في أندرويد لكل منها.",
        "talking_points_ar": "السرية والنزاهة والمصادقة وعدم الإنكار (Non-repudiation)، والـ AEAD و AES-GCM، ودوام التجزئة أحادية الاتجاه، والـ HMAC مقابل التوقيع الرقمي، وحفظ كلمات المرور بـ PBKDF2/Argon2.",
        "follow_ups_ar": "- **المحاور:** \"لماذا لا يعتبر كود HMAC كافياً لإثبات عدم الإنكار (Non-Repudiation)؟\"\n  **المرشح:** \"لأن HMAC يعتمد على مفتاح سري مشترك يمتلكه الطرفان؛ وبالتالي يمكن للمستقبل نفسه تزييف الرسالة، بينما التوقيع الرقمي يعتمد على مفتاح خاص يملكه المرسل فقط مما يمنعه من إنكار توقيعه.\"\n\n- **المحاور:** \"لماذا نفضل AES-GCM على AES-CBC في تشفير البيانات؟\"\n  **المرشح:** \"لأن AES-GCM هو تشفير موثق (AEAD) يولد Authentication Tag يضمن السرية والنزاهة معاً، ويحمي من هجمات Padding Oracle والتلاعب بالبايتات المشفرة.\"",
        "self_check_ar": "هل شرحت المفاهيم الأربعة بالتفصيل؟ هل وضحت مفهوم عدم الإنكار بدقة؟ وهل ميزت بين وظيفة التجزئة ووظيفة التشفير؟",
        "references_ar": f"- [NIST Cryptographic Standards and Guidelines](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines) — المعايير الفيدرالية لاختيار خوارزميات التشفير والتجزئة.\n- [Android Cryptography Guide](https://developer.android.com/privacy-and-security/cryptography) — توثيق جوجل الرسمي لمكتبات التشفير في بيئة أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "نفرق بين الأدوات التشفيرية الأربع وفقاً لأهدافها الرياضية: التشفير يوفر السرية وهو قابل للانعكاس بمفتاح، والتجزئة توفر فحص النزاهة وهي دالة أحادية الاتجاه دون مفاتيح، و HMAC يدمج التجزئة مع مفتاح مشترك لإثبات النزاهة والمصادقة، والتوقيع الرقمي يجمع التجزئة مع المفاتيح غير المتماثلة ليضمن النزاهة والمصادقة وعدم الإنكار القانوني.",
        "best_answer_ar": "يعتمد اختيار الأداة التشفيرية في هندسة النظم على الهدف الأمني المطلوب تحقيقه بدقة، سواء كان السرية، أو النزاهة، أو المصادقة، أو عدم الإنكار.\n\nالتشفير يحقق هدف السرية بجعل البيانات غير مقروءة إلا لمن يمتلك مفتاح فك التشفير، وينقسم إلى تشفير متماثل سريع مثل AES-GCM لحماية البيانات الكبيرة، وتشفير غير متماثل مثل RSA لتبادل المفاتيح بأمان. والتجزئة Hashing توفر النزاهة فقط دون مفاتيح عبر دوال مثل SHA-256 تحول أي بيانات إلى بصمة رقمية فريدة وثابتة لا يمكن عكسها إطلاقاً.\n\nأما HMAC فهو كود مصادقة يدمج دالة التجزئة مع مفتاح سري مشترك بين الطرفين، ليثبت أن الرسالة لم تتغير وصادرة ممن يعرف المفتاح، لكنه لا يوفر عدم الإنكار لأن كلا الطرفين يمتلكان نفس المفتاح. أخيراً، يمثل التوقيع الرقمي أرقى درجات الثقة؛ حيث يقوم المرسل بتجزئة الرسالة وتشفير البصمة بمفتاحه الخاص، ويستطيع أي شخص يمتلك المفتاح العام التحقق من صحة التوقيع وإثبات النزاهة والمصادقة وعدم الإنكار بشكل قاطع.",
        "deep_answer_ar": "في تصميم البنى التحتية للتطبيقات المالية، يمثل الخلط بين المفاهيم التشفيرية مصدراً لثغرات بالغة الخطورة تؤدي لتسريب البيانات وكسر منظومة الحماية.\n\nمن أشهر الأخطاء الشائعة استخدام دوال التجزئة السريعة مثل SHA-256 لتخزين أو فحص كلمات المرور؛ فتلك الدوال صُممت لتكون سريعة جداً مما يتيح للمهاجم تجربة مليارات التخمينات في الثانية باستخدام كروت الشاشة وجداول Rainbow Tables. والحل الهندسي الصحيح هو استخدام دوال اشتقاق المفاتيح البطيئة والمستهلكة للذاكرة مثل Argon2id أو PBKDF2 مع إضافة Salt عشوائي لكل مستخدم.\n\nوعلاوة على ذلك، يجب التفريق الصارم بين التشفير المجرد والتشفير الموثق. استخدام خوارزمية AES بنمط CBC دون كود نزاهة يعرض النظام لهجمات تلاعب وتعديل في بايتات النص المشفر؛ ولذلك تفرض المعايير الحديثة نمط Authenticated Encryption with Associated Data مثل AES-GCM الذي ينتج Authentication Tag يضمن السرية والنزاهة في آن واحد.\n\nوعند المقارنة بين HMAC والتوقيع الرقمي، يكمن الفارق الجوهري في معيار عدم الإنكار Non-Repudiation. في HMAC يتشارك الطرفان نفس المفتاح، وبالتالي يمكن لأي منهما ادعاء أن الآخر هو من اصطنع الرسالة. أما في التوقيع الرقمي، فالمفتاح الخاص لا يغادر عتاد Keystore بهاتف العميل مطلقاً، وعند توقيع معاملة مالية بخوارزمية ECDSA، لا يمكن للعميل إنكار قيامه بالعملية لأن التوقيع الرياضي لا يمكن إنتاجه إلا بواسطة ذلك المفتاح الخاص المحمي عتادياً."
    }
}

# ==========================================
# SEC-08: What is TLS and what does certificate pinning add?
# ==========================================
DATA["SEC-08"] = {
    "concept_en": """Transport Layer Security (TLS) is the industry-standard cryptographic protocol that secures communication over the internet, providing channel encryption, data integrity, and endpoint authentication for HTTPS traffic. During the TLS handshake, the client verifies the server's identity using a public key infrastructure (PKI) certificate chain anchored to trusted Certificate Authorities (CAs) pre-installed in the Android system trust store. Certificate Pinning is an advanced security hardening mechanism that restricts acceptable server credentials beyond standard PKI validation. Instead of trusting any of the hundreds of CAs in the operating system's trust store, the application pins against specific cryptographic identifiers—ideally the SHA-256 hash of the Subject Public Key Info (SPKI) of the server's leaf or intermediate certificate. This prevents Man-in-the-Middle (MITM) attacks resulting from compromised public CAs, rogue government certs, or malicious enterprise proxy certificates installed in the device's user credential store.""",
    "walkthrough_en": """Implementing certificate pinning declaratively and programmatically in Android:
```xml
<!-- 1. Declarative pinning via res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.bank.com</domain>
        <pin-set expiration="2027-01-01">
            <!-- Primary production leaf SPKI pin -->
            <pin digest="SHA-256">k2oTQLj4nsdKmSOGKEUbhwEYfEuDYV5R6g28AzERdOk=</pin>
            <!-- Critical backup pin for disaster recovery / cert rotation -->
            <pin digest="SHA-256">rFjc3AbGqmDTUWBGoWrfNflFreUm7bmyG4520975WTu=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```
Programmatic pinning using OkHttp CertificatePinner:
```kotlin
// 2. Programmatic pinning with fallback pins in OkHttpClient
val secureClient = OkHttpClient.Builder()
    .certificatePinner(
        CertificatePinner.Builder()
            .add("api.bank.com", "sha256/k2oTQLj4nsdKmSOGKEUbhwEYfEuDYV5R6g28AzERdOk=")
            .add("api.bank.com", "sha256/rFjc3AbGqmDTUWBGoWrfNflFreUm7bmyG4520975WTu=")
            .build()
    )
    .build()
```""",
    "short_en": """TLS encrypts network communication and verifies server identity using standard certificate authorities. Certificate pinning hardens this by restricting the application to trust only specific public key hashes for your backend domain, defeating man-in-the-middle attacks from compromised certificate authorities or user-installed proxy inspection certificates while requiring backup pins to prevent app outages during key rotation.""",
    "structured_en": """Transport Layer Security establishes an encrypted and authenticated communication tunnel over TCP, serving as the cryptographic backbone of HTTPS.
Under standard Android TLS validation, the system verifies that the server's digital certificate chains back to any globally trusted Certificate Authority pre-installed in the operating system's root store.
While robust, this model assumes all hundreds of global root CAs remain trustworthy and uncompromised.
Certificate pinning adds a critical defense layer by binding the mobile application directly to the server's specific cryptographic identity.
Instead of accepting any certificate signed by any recognized authority, the application enforces that the server present a certificate matching hardcoded Subject Public Key Info (SPKI) hashes.
This defeats Man-in-the-Middle attacks launched via compromised authorities, malicious Wi-Fi portals, or user-installed proxy debugging certificates like Charles or mitmproxy.
However, pinning introduces operational bricking risks if server certificates rotate without updated pins in distributed client binaries.
Resilient production implementations mitigate this by pinning public keys rather than full certificates and always including offline backup pins for emergency key rotation.""",
    "deep_senior_en": """From an adversarial perspective, the standard PKI trust model on Android possesses a significant attack surface: a single compromised Certificate Authority anywhere in the world can issue fraudulent certificates for your domain that all standard Android clients will silently trust.
Furthermore, on rooted devices or enterprise-managed environments where users install custom CA certificates into the system or user trust store, adversaries can easily intercept, decrypt, and manipulate API traffic.
Certificate pinning eliminates these attack vectors by constraining trust to explicit cryptographic identifiers.
In modern Android architecture, best practice dictates pinning the Subject Public Key Info (SPKI) rather than the leaf certificate itself.
Pinning the SPKI pins the underlying public key; this allows the backend team to renew the certificate with the same key pair upon expiration without breaking running client applications.
The supreme operational hazard of certificate pinning is the self-inflicted denial of service.
If the server's private key is compromised and the operations team issues a new certificate with a new key pair, all active mobile applications will reject connections and fail permanently until users download an updated APK from the store.
To eliminate this catastrophic failure mode, senior engineers enforce two mandatory practices.
First, we always configure at least one offline backup pin corresponding to an unreleased key pair stored in an air-gapped corporate vault.
Second, for mission-critical fintech apps, we combine network security configuration with dynamic pinning mechanisms managed via secure remote configuration or Play Integrity attestation, allowing emergency pin updates without waiting for Google Play store review cycles.""",
    "meta_ar": {
        "id": "SEC-08",
        "questionAr": "ما هو بروتوكول TLS، وما هي القيمة الإضافية لتثبيت الشهادات (Certificate Pinning) ومخاطره التشغيلية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم طريقة عمل بروتوكول TLS وسلسلة الثقة PKI، والدافع الأمني لتثبيت الشهادات (منع هجمات MITM والشهادات المزيفة)، والفرق بين تثبيت الشهادة وتثبيت المفتاح العام SPKI، والمخاطر التشغيلية وكيفية تجنب شلل التطبيق عند تدوير المفاتيح.",
        "concept_ar": "بروتوكول TLS هو المعيار الأمني لتشفير وتأمين الاتصالات الشبكية والتحقق من هوية السيرفر عبر سلاسل شهادات موقعة من جهات موثوقة (CAs). وتثبيت الشهادات (Certificate Pinning) هو طبقة أمان إضافية تلزم التطبيق برفض أي شهادة لا تطابق بصمة تشفير محددة مسبقاً (يفضل تجزئة المفتاح العام SPKI)، مما يحمي من هجمات الوسيط (MITM) حتى لو تم اختراق إحدى جهات الـ CA العالمية أو تثبيت شهادات تجسس على جهاز المستخدم.",
        "walkthrough_ar": "تثبيت الشهادات بأسلوب الـ SPKI في ملف network_security_config وفي OkHttp:\n```xml\n<network-security-config>\n    <domain-config>\n        <domain includeSubdomains=\"true\">api.bank.com</domain>\n        <pin-set expiration=\"2027-01-01\">\n            <!-- المفتاح الأساسي الفعال -->\n            <pin digest=\"SHA-256\">k2oTQLj4nsdKmSOGKEUbhwEYfEuDYV5R6g28AzERdOk=</pin>\n            <!-- مفتاح احتياطي للطوارئ لتفادي توقف التطبيق -->\n            <pin digest=\"SHA-256\">rFjc3AbGqmDTUWBGoWrfNflFreUm7bmyG4520975WTu=</pin>\n        </pin-set>\n    </domain-config>\n</network-security-config>\n```",
        "why_it_matters_ar": "تثبيت الشهادات يحمي تطبيقات التكنولوجيا المالية من فك تشفير اتصالاتها والتنصت عليها عبر أدوات مثل Charles Proxy أو الشبكات المشبوهة، لكن تنفيذه الخاطئ قد يتسبب في شلل كامل للتطبيق إذا انتهت الشهادة.",
        "worked_example_ar": "إعداد CertificatePinner في OkHttpClient مع مفتاح احتياطي:\n```kotlin\nval okHttpClient = OkHttpClient.Builder()\n    .certificatePinner(\n        CertificatePinner.Builder()\n            .add(\"api.bank.com\", \"sha256/k2oTQLj4nsdKmSOGKEUbhwEYfEuDYV5R6g28AzERdOk=\")\n            .add(\"api.bank.com\", \"sha256/rFjc3AbGqmDTUWBGoWrfNflFreUm7bmyG4520975WTu=\")\n            .build()\n    )\n    .build()\n```",
        "trade_offs_ar": "يوفر Pinning أماناً فائقاً ضد هجمات الوسيط، لكنه يفرض مخاطرة تشغيلية كبرى؛ فإذا تغيرت شهادة السيرفر دون وجود مفتاح احتياطي في التطبيق، سيتوقف التطبيق عن العمل كلياً حتى ينزل تحديث جديد.",
        "failure_modes_ar": "تثبيت شهادة واحدة فقط دون وضع Backup Pin، ثم قيام فريق السيرفر بتجديد الشهادة بمفتاح جديد؛ مما يؤدي إلى فشل جميع اتصالات العملاء وتعطل الخدمة عالمياً (Self-inflicted DoS).",
        "production_perspective_ar": "في التطبيقات المصرفية، نقوم دائماً بتثبيت تجزئة المفتاح العام (SPKI) بدلاً من الشهادة الكاملة، ونحتفظ بمفتاحين احتياطيين على الأقل في خزنة مشفرة غير متصلة بالإنترنت (Cold Vault) للطوارئ.",
        "how_to_answer_ar": "ابدأ بشرح دور TLS العادي وسلسلة ثقة الـ PKI، ثم فسر ثغرة الثقة في كل CAs العالم، ثم وضح كيف يحل التثبيت المشكلة، وركز على أفضل الممارسات بتثبيت SPKI ووضع مفاتيح احتياطية لتفادي توقف الخدمة.",
        "talking_points_ar": "سلسلة ثقة PKI والـ Root CAs، وهجمات Man-in-the-Middle، وتثبيت المفتاح العام SPKI مقابل تثبيت الشهادة، ومخاطر شلل التطبيق (Bricking the app)، والمفاتيح الاحتياطية (Backup Pins).",
        "follow_ups_ar": "- **المحاور:** \"لماذا نفضل تثبيت الـ Subject Public Key Info (SPKI) على تثبيت الشهادة الورقية بالكامل؟\"\n  **المرشح:** \"لأن الشهادة الورقية تنتهي صلاحيتها وتتغير سنوياً حتى لو ظل المفتاح نفسه، بينما تثبيت SPKI يثبت المفتاح العام، مما يسمح بتجديد الشهادة بنفس المفتاح دون كسر التطبيقات المثبتة لدى المستخدمين.\"\n\n- **المحاور:** \"كيف تتعامل مع انتهاء أو تسريب شهادة السيرفر إذا كان التطبيق يطبق Pinning؟\"\n  **المرشح:** \"نقوم فوراً بتفعيل المفتاح الاحتياطي (Backup Pin) المحفوظ مسبقاً في كود التطبيق وربطه بالسيرفر، أو الاعتماد على تحديث ديناميكي للمفاتيح عبر قنوات آمنة مدعومة بـ Play Integrity.\"",
        "self_check_ar": "هل بينت دور TLS؟ هل فرقت بين تثبيت الشهادة وتثبيت SPKI؟ وهل شرحت المخاطر التشغيلية وخطة الإنقاذ بالمفاتيح الاحتياطية؟",
        "references_ar": f"- [Android Network Security Configuration](https://developer.android.com/privacy-and-security/security-config) — دليل جوجل الرسمي لتهيئة أمان الشبكة وتثبيت الشهادات.\n- [OkHttp CertificatePinner Documentation](https://square.github.io/okhttp/features/calls/#certificate-pinning) — التوثيق الرسمي لربط الشهادات في مكتبة OkHttp.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "بروتوكول TLS هو المعيار الأساسي لتشفير الاتصال الشبكي والتحقق من هوية السيرفر عبر جهات الشهادات الموثوقة عالمياً. ويضيف تثبيت الشهادات طبقة أمان تلزم التطبيق بالاتصال فقط بسيرفر يطابق بصمة مفتاح عام محددة مسبقاً، مما يمنع هجمات اعتراض حركة المرور والشهادات المزيفة، مع ضرورة تضمين مفاتيح احتياطية لتفادي تعطل التطبيق عند تجديد الشهادات.",
        "best_answer_ar": "يوفر بروتوكول TLS نفقاً مشفراً لحماية حركة البيانات عبر الإنترنت، ويعتمد في صورته القياسية على منظومة الشهادات العامة PKI؛ حيث يقبل التطبيق أي شهادة صادرة من مئات جهات الاعتماد الجذرية الموثوقة مسبقاً في نظام أندرويد.\n\nولكن تكمن المشكلة في إمكانية اختراق إحدى هذه الجهات أو قيام المستخدم بتثبيت شهادة تتبع خاصة على هاتفه لفك تشفير البيانات. وهنا تأتي القيمة الأمنية لتثبيت الشهادات Certificate Pinning؛ حيث يرفض التطبيق الاعتماد الأعمى على جهات الـ CA، ويشترط مطابقة السيرفر لبصمة مفتاح محددة ومبرمجة مسبقاً في كود التطبيق، مما يحصن الاتصال تماماً ضد هجمات الوسيط Man-in-the-Middle.\n\nورغم أهميته الأمنية، إلا أنه يحمل مخاطرة تشغيلية كبرى؛ فإذا تم تغيير شهادة السيرفر دون توفير مفتاح بديل متطابق في التطبيق، سيتوقف التطبيق عن العمل كلياً عند جميع المستخدمين. ولتفادي ذلك، نحرص في البيئات الإنتاجية على تثبيت بصمة المفتاح العام SPKI بدلاً من الشهادة كاملة، وتضمين مفتاح احتياطي للطوارئ دائماً في الإعدادات.",
        "deep_answer_ar": "من منظور النمذجة التهديدية للأنظمة المالية، يمتلك نموذج الثقة القياسي لبروتوكول TLS ثغرة هيكلية؛ وهي أن التطبيق يثق في مئات الجهات المصدرة للشهادات حول العالم، ويكفي اختراق جهة واحدة أو إجبارها على إصدار شهادة مزيفة لاعتراض كل حركة بيانات التطبيق دون أي تحذير أمني.\n\nوعلاوة على ذلك، في بيئات العمل أو الأجهزة المروّتة، يستطيع المهاجم تثبيت شهادة جذرية مخصصة في مساحة المستخدم والتقاط حركة المرور عبر أدوات مثل Proxyman. يلغي تثبيت الشهادات هذا التهديد تماماً عبر قصر الثقة على معرفات تشفيرية صريحة. وأفضل ممارسة هندسية معتمدة هي تثبيت تجزئة Subject Public Key Info بدلاً من الشهادة الورقية؛ لأن ذلك يثبت المفتاح العام ذاته، مما يتيح تجديد الشهادة عند انتهائها السنوي دون التأثير على عمل التطبيقات في الإنتاج.\n\nولكن الخطر الأكبر لتثبيت الشهادات هو التسبب في شلل ذاتي للخدمة Self-inflicted Denial of Service في حال اضطرار فريق البنية التحتية لتغيير المفاتيح بشكل طارئ. ولمواجهة هذه الكارثة التشغيلية، نلزم المعمارية بوجود مفتاح احتياطي Backup Pin على الأقل مخزن في خزنة باردة غير متصلة بالإنترنت، مع دراسة استخدام التحديث الديناميكي للمفاتيح عبر قنوات مصادقة موثوقة ومدعومة باختبارات النزاهة من Play Integrity لضمان استمرارية الأعمال بأعلى درجات الأمان."
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

    ee.save_topic_metadata("sec_01_08", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print("\nAll 8 SEC questions (SEC-01 to SEC-08) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
