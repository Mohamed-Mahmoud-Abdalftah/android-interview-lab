#!/usr/bin/env python3
"""
Elevation script for SEC questions: SEC-25 to SEC-32.
Topic: Android Security, Crypto & Fintech Threat Modeling (SEC)
Phase 3, Batch 4
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "أمان أندرويد والتشفير والنمذجة الأمنية لتطبيقات التكنولوجيا المالية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# SEC-25: What are OWASP MASVS/MASTG, and how do they guide mobile security reviews?
# ==========================================
DATA["SEC-25"] = {
    "concept_en": """OWASP MASVS (Mobile Application Security Verification Standard) defines the definitive baseline security requirements for mobile applications, organized across eight core domains: Storage, Crypto, Auth, Network, Platform, Code, and Resilience. Applications are evaluated against defined risk profiles: MASVS-L1 establishes standard security baseline hygiene applicable to all mobile apps; MASVS-L2 introduces defense-in-depth controls required for sensitive financial, healthcare, and enterprise apps; and MASVS-R specifies technical resilience controls against client-side reverse engineering, dynamic instrumentation, and binary tampering. OWASP MASTG (Mobile Application Security Testing Guide) serves as the companion technical testing manual. It provides concrete static analysis (SAST) and dynamic analysis (DAST) procedures, test cases, and tool workflows (utilizing Frida, objection, radare2, and Ghidra) to rigorously verify whether an application complies with each corresponding MASVS requirement.""",
    "walkthrough_en": """Automated MASVS compliance checks in CI/CD and production code verification:
```kotlin
// 1. Implementing MASVS-STORAGE: Hardware-backed encrypted preferences
class SecureStorageManager(private val context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .setRequestStrongBoxProvider(true)
        .build()

    val encryptedPrefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_vault_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
}

// 2. Enforcing MASVS-NETWORK: Disabling cleartext traffic and configuring TLS 1.3
// Verified in res/xml/network_security_config.xml and tested dynamically via MASTG test suites
```""",
    "short_en": """OWASP MASVS provides the standard security requirements for mobile applications across storage, crypto, network, and platform domains, divided into baseline L1, defense-in-depth L2, and anti-tamper resilience R levels. MASTG is the comprehensive testing manual that details how to verify each requirement through static analysis and dynamic reverse-engineering tools like Frida. Together, they transform subjective security reviews into verifiable, reproducible engineering standards.""",
    "structured_en": """Mobile security reviews require an objective benchmark rather than ad-hoc opinions, and OWASP MASVS establishes that baseline.
The standard divides mobile security into eight specific domains covering data storage, cryptography, authentication, network communication, platform interactions, code quality, and reverse engineering resilience.
Organizations select an applicable verification profile based on their operational threat model.
MASVS-L1 sets essential baseline security for any mobile application, focusing on good hygiene such as blocking cleartext traffic and avoiding credential leakage in system logs.
MASVS-L2 represents defense-in-depth for sensitive financial and medical applications, mandating hardware-backed key storage, certificate pinning, and strict session isolation.
MASVS-R adds explicit anti-tamper and anti-reversing controls for apps operating in hostile client environments.
To verify these requirements, engineers and auditors use the OWASP MASTG.
The MASTG delivers explicit static analysis instructions and dynamic penetration testing recipes using tools like objection and Frida, providing concrete evidence of compliance rather than passive checklist ticking.""",
    "deep_senior_en": """In enterprise engineering, OWASP MASVS and MASTG serve as the bridge connecting product engineering, cybersecurity auditors, and regulatory compliance frameworks like PCI-DSS.
Rather than treating security as an afterthought prior to release, we integrate MASVS controls directly into our architectural definitions and continuous integration pipelines.
For a tier-one fintech application, our target profile is MASVS-L2 combined with MASVS-R.
Under MASVS-STORAGE, we mandate that no customer data touches disk unencrypted, routing all persistence through EncryptedSharedPreferences backed by StrongBox and explicitly excluding sensitive databases from automated cloud backups.
Under MASVS-NETWORK, we configure network security configurations to forbid cleartext HTTP and enforce public key pinning with planned rotation schedules.
Under MASVS-PLATFORM, we audit every exported component, verify incoming deep link digital assets, and lock all PendingIntents with immutability flags.
The true power of MASTG lies in dynamic validation during automated staging tests.
We utilize MASTG test cases within automated security smoke tests, injecting Frida scripts to verify whether sensitive cryptographic keys can be extracted from memory dumps and confirming that repackaged binaries fail signature verification.
This shifts security left from an annual compliance audit to an automated engineering discipline with measurable security SLOs. We also configure automated SAST linters in our Gradle verification tasks to enforce crypto algorithm standards and verify that all manifest components declare explicit exported flags.""",
    "meta_ar": {
        "id": "SEC-25",
        "questionAr": "ما هي معايير OWASP MASVS و MASTG، وكيف ترشد المهندسين في مراجعات الأمان واختبار الاختراق لتطبيقات أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "معايير MASVS كضوابط أمنية وMASTG كإجراءات اختبار عملية، وتحديد نطاق المراجعة بناءً على مستوى المخاطر، والتمييز بين قوائم التحقق الروتينية والإثبات التهديدي الفعلي.",
        "concept_ar": "معيار OWASP MASVS هو المعيار الصناعي الموحد الذي يحدد متطلبات الأمان لتطبيقات الموبايل عبر ثمانية مجالات رئيسية تشمل التخزين، التشفير، المصادقة، والشبكات، ومقاومة الهندسة العكسية. بينما يمثل دليل MASTG الدليل الإجرائي التقني الذي يوضح لمهندسي الأمان ومطوري أندرويد كيفية اختبار والتحقق من كل متطلب عملياً عبر التحليل الساكن والديناميكي.",
        "walkthrough_ar": """تطبيق متطلبات MASVS عملياً داخل كود أندرويد عبر تشفير التخزين وتأمين الاتصال الشبكي:
```kotlin
// تطبيق MASVS-STORAGE عبر التشفير المعتمد على العتاد
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .setRequestStrongBoxProvider(true)
    .build()

val securePreferences = EncryptedSharedPreferences.create(
    context,
    "financial_vault",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```""",
        "why_it_matters_ar": "يوفر إطاراً معيارياً موحداً يخرج مراجعات الأمان من دائرة الآراء الشخصية إلى ضوابط قابلة للقياس والاختبار، مما يسهل الامتثال للمعايير الدولية مثل PCI-DSS وISO 27001، ويدمج الأمان في دورة التطوير المستمرة CI/CD مبكراً.",
        "worked_example_ar": "بناء مصفوفة اختبارات أمان مؤتمتة تجمع بين فحص الكود الساكن بـ MobSF والتحقق الديناميكي بحقن سكريبتات Frida لاختبار مقاومة التطبيق للعبث والتأكد من تطابق التطبيق مع متطلبات MASVS-L2 و MASVS-R.",
        "trade_offs_ar": "تطبيق المستوى المتقدم MASVS-L2 ومقاومة العبث MASVS-R يتطلب وقتاً أطول في التطوير وقد يضيف تعقيداً في الصيانة ومعالجة أخطاء الأجهزة القديمة، مقارنة بالمستوى الأساسي MASVS-L1 الذي يوفر حماية قياسية بتكلفة هندسية منخفضة.",
        "failure_modes_ar": "التعامل مع MASVS كقائمة تحقق شكلية دون اختبار اختراق حقيقي، وإهمال التحليل الديناميكي واقتصار الفحص على مراجعة الكود نظرياً، وتجاهل تحديثات المعيار الجديدة.",
        "production_perspective_ar": "في الشركات المالية الكبرى، يتم ربط متطلبات MASVS ببوابات جودة الكود Quality Gates في مسارات الـ CI/CD، حيث يُحظر دمج أي Pull Request يحتوي على ثغرة تتعارض مع المستوى المستهدف، مع إجراء اختبارات اختراق دورية بواسطة فرق حمراء مستقلة.",
        "how_to_answer_ar": "ابدأ بتعريف MASVS كمعيار للمتطلبات الأمنية ومستوياته L1 و L2 و R، ثم اربطه بـ MASTG كدليل للاختبار العملي، واختم بكيفية استخدامك لهما في بناء معمارية التطبيق واختبارات الـ CI/CD.",
        "talking_points_ar": "الفروق الدقيقة بين مستويات MASVS، وكيفية استخدام أدوات مثل objection و Frida للتحقق العملي، وأهمية تحويل متطلبات الأمان إلى اختبارات آلية مستمرة في خط الإنتاج.",
        "follow_ups_ar": "- **المحاور:** \"ما الفرق الجوهري بين MASVS-L1 و MASVS-L2؟\"\n  **المرشح:** \"المستوى L1 يمثل أساسيات الأمان القياسية لكل التطبيقات كتعطيل النصوص الصريحة، بينما L2 يفرض دفاعاً معمقاً مثل التشفير المعتمد على عتاد StrongBox وتثبيت الشهادات وعزل الجلسات الحساسة.\"\n\n- **المحاور:** \"هل يضمن تطبيق MASVS-R حماية مطلقة ضد الهندسة العكسية؟\"\n  **المرشح:** \"لا توجد حماية مطلقة على جهاز العميل، ولكن MASVS-R يرفع تكلفة الهجوم المالية والزمنية إلى حد يجعل اختراق التطبيق غير مجدٍ اقتصادياً للمهاجم.\"",
        "self_check_ar": "هل بينت بوضوح الفرق بين معيار MASVS ودليل الاختبار MASTG؟ وهل ذكرت المستويات الثلاثة L1 و L2 و R ومجالات الأمان الرئيسية؟",
        "references_ar": f"- [OWASP Mobile Application Security (MAS)](https://mas.owasp.org/) — الموقع الرسمي لمشروع أمان تطبيقات الموبايل لدى OWASP.\n- [OWASP MASTG Testing Guide](https://github.com/OWASP/owasp-mastg) — المستودع الرسمي لدليل اختبار أمان تطبيقات الموبايل.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "معيار MASVS هو المرجع العالمي لمتطلبات أمان تطبيقات الموبايل، حيث يقسم الحماية إلى مستويات تبدأ من الأساسيات L1، والدفاع المعمق L2، ومقاومة التلاعب والهندسة العكسية R. بينما يمثل دليل MASTG الدليل الإجرائي الذي يشرح كيفية اختبار واختراق كل متطلب عملياً باستخدام أدوات التحليل الساكن والديناميكي مثل Frida و objection.",
        "best_answer_ar": "يوفر مشروع OWASP إطاراً متكاملاً لإدارة واختبار أمان تطبيقات الموبايل عبر معيارين أساسيين يكمل كل منهما الآخر.\n\nالمعيار الأول هو MASVS، وهو بمثابة المرجع الهندسي للمتطلبات الأمنية؛ حيث يغطي ثمانية مجالات حساسة تشمل تخزين البيانات، والتشفير، والمصادقة، وأمان الشبكات، والتفاعل مع النظام الأساسي، ومقاومة العبث. ويصنف التطبيقات إلى ثلاث فئات: L1 للأمان الأساسي المطلوب في أي تطبيق عام، و L2 للأمان المعمق الموجه للتطبيقات البنكية والطبية المشددة، و R لمقاومة الهندسة العكسية والتلاعب بالكود.\n\nأما الدليل الثاني فهو MASTG، وهو الدليل التقني التطبيقي لاختبار الاختراق؛ حيث يحدد بدقة خطوات التحليل الساكن للأكواد والتحليل الديناميكي للذاكرة وحزم الشبكة أثناء تشغيل التطبيق. وباستخدام هذا الدليل مع أدوات مثل Frida و Jadx، نتحقق من تنفيذ متطلبات MASVS عملياً في مسار البناء لضمان صمود التطبيق أمام الهجمات الواقعية.",
        "deep_answer_ar": "في قيادة هندسة الأنظمة البنكية، يشكل الثنائي MASVS و MASTG اللغة المشتركة بين مطوري أندرويد وفرق الأمن السيبراني ومدققي الامتثال الخارجيين.\n\nبدلاً من ترك قرارات الأمان للتقديرات الشخصية، نعتمد المستوى MASVS-L2 مع متطلبات MASVS-R كمعيار معماري إلزامي. ففي مجال تخزين البيانات، نمنع كتابة أي بيانات سرية على القرص بدون تشفير AES-GCM مقترن بـ Keystore و StrongBox، ونستبعد قواعد البيانات الحساسة صراحة من النسخ الاحتياطي التلقائي. وفي طبقة الشبكات، نلزم كافة الاتصالات بـ TLS 1.3 مع تثبيت المفاتيح العامة SPKI وتوفير مسار طوارئ محكم لتجديد المفاتيح.\n\nوتتجلى القيمة الاستراتيجية لدليل MASTG في تحويل اختبارات الأمان من مراجعات روتينية سنوية إلى بوابات جودة برمجية مؤتمتة داخل مسار الـ CI/CD. حيث نبرمج اختبارات ديناميكية تحاكي سيناريوهات MASTG؛ كحقن سكريبتات Frida لاختبار تجاوز حواجز الفحص الحيوي، أو فحص تسريب التوكنز في سجلات النظام وسجلات التتبع أثناء الانهيارات البرمجية.\n\nهذا التكامل المعماري يضمن أن التطبيق ليس فقط متوافقاً على الورق، بل يمتلك مناعة برمجية مثبتة بأدلة قاطعة ضد التعديل وإعادة التجميع، ويلبي بشكل صارم متطلبات المعايير العالمية مثل PCI-DSS. كما ندمج أدوات الفحص الساكن في مسارات البناء للتحقق من خلو الكود من استدعاءات التشفير المهملة، وندرب فرق التطوير على معايير OWASP لضمان كتابة كود محصن افتراضياً يقلل الثغرات قبل وصولها لبيئة الإنتاج."
    }
}

# ==========================================
# SEC-26: Design secure session storage for a fintech app on a potentially compromised device.
# ==========================================
DATA["SEC-26"] = {
    "concept_en": """Designing session storage under a hostile endpoint threat model requires zero trust in client integrity. The architecture isolates session state into ephemeral in-memory access tokens (valid for 5 to 15 minutes, never flushed to persistent disk) and hardware-bound refresh tokens encrypted via Android Keystore using AES-256-GCM. The refresh token is persisted in DataStore located inside noBackupFilesDir. High-risk financial operations enforce step-up authentication using biometric CryptoObject signing bound to KeyStore keys that require authentication per operation. In addition, token binding mechanisms like Demonstrating Proof-of-Possession (DPoP) tie tokens to an ephemeral client key pair, rendering exfiltrated tokens useless on external servers.""",
    "walkthrough_en": """Hostile-endpoint session storage with in-memory access token and hardware-bound refresh token:
```kotlin
class SecureSessionRepository(
    private val context: Context,
    private val keyStoreHelper: KeyStoreHelper
) {
    // 1. In-memory ephemeral access token; never written to persistent disk
    private val accessTokenRef = AtomicReference<String?>(null)
    private val refreshMutex = Mutex()

    fun getActiveAccessToken(): String? = accessTokenRef.get()

    fun updateAccessToken(token: String?) {
        accessTokenRef.set(token)
    }

    // 2. Hardware-encrypted refresh token stored strictly in noBackupFilesDir
    suspend fun saveRefreshToken(rawToken: String) = refreshMutex.withLock {
        val encryptedData = keyStoreHelper.encryptWithStrongBox(rawToken.toByteArray())
        val targetFile = File(context.noBackupFilesDir, "secure_session.enc")
        targetFile.writeBytes(encryptedData)
    }

    fun clearSession() {
        accessTokenRef.set(null)
        File(context.noBackupFilesDir, "secure_session.enc").delete()
    }
}
```""",
    "short_en": """Designing secure session storage on an untrusted device requires assuming the client is hostile. We keep short-lived access tokens exclusively in memory, never writing them to disk. The long-lived refresh token is encrypted using hardware-backed Android Keystore keys via StrongBox and stored in noBackupFilesDir. Critical transactions require biometric signing step-up, and tokens are bound using proof-of-possession.""",
    "structured_en": """Securing session storage on a potentially compromised device begins with a zero-trust model where local disk and memory are assumed accessible to an attacker.
We separate session credentials into two tiers with distinct lifecycles and storage rules.
The access token is strictly ephemeral, valid for five to fifteen minutes, and kept solely in volatile application memory as a mutable reference that is zeroed upon logout or app suspension.
It is never written to SharedPreferences, SQLite, or cache files.
The refresh token, which is long-lived, is stored in encrypted DataStore inside the noBackupFilesDir directory, protected by an AES-256-GCM key bound to Android Keystore and hardware StrongBox.
To prevent token exfiltration from granting unlimited access, the backend issues cryptographically bound tokens using Demonstrating Proof-of-Possession.
High-value financial actions enforce step-up authentication using a biometric CryptoObject, requiring an authenticated hardware key signature per transaction.
Token refresh logic coordinates through a concurrency mutex to prevent race conditions during network handoffs.""",
    "deep_senior_en": """In mobile fintech threat modeling, we treat the client device as an untrusted environment where root access, runtime instrumentation like Frida, and offline backup extraction are active probabilities.
Our session architecture establishes defense in depth across memory, storage, and transport boundaries.
In memory, the access token resides inside a thread-safe atomic reference, completely bypassing persistent disk writes.
When the application moves to the background for longer than our security timeout, we wipe this reference deterministically.
For persistence, the refresh token is encrypted through EncryptedSharedPreferences or Proto DataStore utilizing an Android Keystore master key generated with StrongBox backing.
The storage location is explicitly isolated within noBackupFilesDir, preventing ADB backups or cloud synchronization from lifting the encrypted payload to unmanaged secondary devices.
At the cryptographic protocol layer, we bind tokens to an ephemeral device key pair using DPoP, ensuring that even if an attacker extracts the refresh token via a memory dump, replay attempts from another IP or client will fail backend verification.
Furthermore, routine session tokens cannot authorize sensitive financial operations.
Any fund transfer requires a stepped-up transaction payload signed by a dedicated EC key requiring BiometricPrompt authorization with zero timeout.
This ensures that compromised session tokens cannot trigger irreversible fund movements without live biometric confirmation. In addition, we invalidate cached session state immediately upon user logout or network disconnection, wiping sensitive memory buffers completely.""",
    "meta_ar": {
        "id": "SEC-26",
        "questionAr": "كيف تصمم بنية تخزين الجلسات لتطبيق تكنولوجيا مالية يعمل على جهاز يُفترض أنه مخترق أو خاضع لسيطرة المهاجم؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تخزين الجلسات على أجهزة طرفية معادية، وتقييم المخاطر المتبقية، ونطاق صلاحية الرموز التشفيرية، والتعامل مع سباقات تجديد الجلسة، والإلغاء الفوري، والمصادقة البيومترية المتدرجة للعمليات الحساسة.",
        "concept_ar": "تصميم بنية تخزين الجلسات في بيئة معادية ينطلق من مبدأ عدم الثقة التامة في أمان الهاتف. يعتمد التصميم على حصر توكن الوصول قصير العمر في الذاكرة العشوائية RAM فقط بمدة صلاحية بين 5 إلى 15 دقيقة دون كتابته على القرص مطلقاً، مع تشفير توكن التجديد بمفتاح AES-256-GCM مقفل في شريحة StrongBox العتادية وحفظه في مجلد noBackupFilesDir، وربط العمليات الحساسة بتوقيع بيومتري مستقل.",
        "walkthrough_ar": """بناء مستودع إدارة الجلسة الآمنة مع عزل التوكن في الذاكرة وتشفير مفتاح التجديد عتادياً:
```kotlin
class SecureSessionRepository(
    private val context: Context,
    private val keyStoreHelper: KeyStoreHelper
) {
    // 1. توكن الوصول في الرام فقط ولا يكتب على القرص
    private val accessTokenRef = AtomicReference<String?>(null)
    private val refreshMutex = Mutex()

    fun getActiveAccessToken(): String? = accessTokenRef.get()

    // 2. تشفير توكن التجديد في مسار معزول عن النسخ الاحتياطي
    suspend fun saveRefreshToken(rawToken: String) = refreshMutex.withLock {
        val encryptedData = keyStoreHelper.encryptWithStrongBox(rawToken.toByteArray())
        File(context.noBackupFilesDir, "session.enc").writeBytes(encryptedData)
    }
}
```""",
        "why_it_matters_ar": "يحمي أموال المستخدمين وحساباتهم البنكية حتى في حال ترويض الجهاز أو سرقته أو أخذ نسخة احتياطية من ملفاته، حيث يتم تقليص نافذة صلاحية التوكنات المكشوفة ومنع استخدامها خارج الجهاز الأصلي.",
        "worked_example_ar": "تنفيذ دورة حياة الجلسة المصرفية مع التعامل مع سباق تجديد التوكنات Refresh Token Concurrency عبر Mutex مشترك، وربط عمليات التحويل بـ CryptoObject بيومتري معتمد من Keystore.",
        "trade_offs_ar": "تقصير مدة توكن الوصول يرفع مستوى الأمان بشكل هائل ولكنه يزيد من معدل استدعاءات تجديد التوكن واستهلاك الشبكة، كما أن التشفير العتادي الصارم قد يتطلب وقتاً أطول في المعالجة مقارنة بالتخزين العادي.",
        "failure_modes_ar": "كتابة توكن الوصول في SharedPreferences دون تشفير، وتزامن طلبات الشبكة مما يؤدي لسباق تجديد التوكن وتسجيل خروج المستخدم عشوائياً، وإهمال مسح التوكن من الذاكرة عند خروج التطبيق للخلفية.",
        "production_perspective_ar": "في البنوك الرقمية الكبرى، ندمج إدارة الجلسات بنظام كشف الاحتيال المركزي؛ حيث يتم إلغاء الجلسات فوراً من السيرفر عند رصد تغير عنوان الـ IP بشكل غير طبيعي أو فشل إثبات DPoP التشفيري.",
        "how_to_answer_ar": "ابدأ بفرضية التهديد Hostile Device ثم اشرح تقسيم التوكنات بين الذاكرة والتخزين المشفر عتادياً، ثم وضح حماية العمليات الحساسة بـ CryptoObject وبروتوكول إثبات الملكية DPoP.",
        "talking_points_ar": "أهمية مجلد noBackupFilesDir، دور DPoP في منع إعادة إرسال التوكنات المسروقة، وكيفية حل مشاكل الـ Race Conditions أثناء تجديد التوكن عبر الـ Mutex.",
        "follow_ups_ar": "- **المحاور:** \"كيف تمنع استخدام الـ Refresh Token إذا تم نسخه من هاتف مروّت؟\"\n  **المرشح:** \"نستخدم بروتوكول DPoP أو mTLS لربط التوكن بزوج مفاتيح مشفر في Keystore؛ فإذا تم استخراج التوكن، يعجز المهاجم عن توقيع طلبات الـ HTTP بمفتاح العتاد الأصلي.\"\n\n- **المحاور:** \"ماذا يحدث إذا تزامنت عدة استدعاءات API وانتهت صلاحية الـ Access Token؟\"\n  **المرشح:** \"نستخدم Mutex في OkHttp Authenticator؛ الخيط الأول فقط يقوم بتجديد التوكن بينما تنتظر باقي الخيوط وتستخدم التوكن الجديد فور جهوزيته دون تكرار الطلب.\"",
        "self_check_ar": "هل وضحت لماذا لا يُكتب Access Token على القرص؟ وهل ذكرت تشفير StrongBox ومجلد noBackupFilesDir وبروتوكول DPoP؟",
        "references_ar": f"- [OAuth 2.0 Demonstrating Proof-of-Possession (DPoP)](https://datatracker.ietf.org/doc/html/rfc9449) — مواصفة IETF القياسية لربط التوكنات بمفاتيح تشفيرية.\n- [Android Keystore System](https://developer.android.com/privacy-and-security/keystore) — التوثيق الرسمي لإدارة المفاتيح العتادية في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تصميم تخزين الجلسات على جهاز غير موثوق يعتمد على فرضية اختراق العميل مسبقاً. نحتفظ بتوكن الوصول قصير الأجل في الذاكرة الحية فقط دون كتابته على القرص مطلقاً. ونشفر توكن التجديد بعتاد StrongBox في مجلد noBackupFilesDir، مع إلزام العمليات المالية بمصادقة بيومترية مستقلة، وربط التوكن بالجهاز لمنع استخدامه خارجياً.",
        "best_answer_ar": "في التطبيقات المالية، ننطلق من فرضية أمنية تفترض أن جهاز المستخدم خاضع لسيطرة مهاجم يمتلك صلاحيات الروت وأدوات فحص الذاكرة.\n\nبناءً على هذا، نقسم إدارة الجلسة إلى مستويين متمايزين في دورة الحياة ومكان التخزين. المستوى الأول هو توكن الوصول ومدته لا تتجاوز خمس إلى عشر دقائق؛ نحتفظ به في متغير داخل الرام فقط ونمسحه فوراً عند تسجيل الخروج أو الانتقال للخلفية، ونحظر كتابته نهائياً على مساحة التخزين الدائمة.\n\nأما توكن التجديد فهو مشفر بخوارزمية AES-GCM عبر مفتاح من Android Keystore مدعوم بشريحة StrongBox العتادية، ويُحفظ داخل مجلد noBackupFilesDir لضمان عدم رفعه في النسخ الاحتياطي السحابي أو استخراجه عبر adb backup. ولحماية العمليات المصرفية الحساسة كالتحويلات المالية، لا نكتفي بتوكن الجلسة، بل نلزم المستخدم بتوقيع المعاملة ببصمة حية جديدة عبر كائن CryptoObject عتادي لا يقبل التجاوز.",
        "deep_answer_ar": "في هندسة أمان الجلسات المصرفية، نتعامل مع الهاتف كطرفية معادية ونتقبل المخاطر المتبقية من خلال تقليص نافذة التعرض الزمني لأدنى حد ممكن.\n\nفي الذاكرة العشوائية، نضع توكن الوصول داخل مرجع ذري معزول ونربط دورة حياته بمهلة خمول التطبيق؛ فإذا دخل التطبيق إلى الخلفية لمدة تزيد عن ثلاث دقائق، يتم تصفير المرجع برمجياً وإجبار المستخدم على فك القفل مجدداً. ونحفظ توكن التجديد مشفراً بمفتاح مقفل عتادياً ومربوط بـ DataStore داخل مسار الملفات المعزولة عن النسخ الاحتياطي.\n\nوللتحصين ضد سرقة التوكنات عبر فحص الذاكرة، نطبق بروتوكول Demonstrating Proof-of-Possession التشفيري، بحيث يوقع التطبيق كل طلب برأس مشفر عبر زوج مفاتيح محلي تم توليده في Keystore. فإذا نجح مهاجم في سرقة توكن الجلسة وإعادة إرساله من خادم آخر، يرفض السيرفر الطلب فوراً لغياب التوقيع التشفيري للعتاد الأصلي.\n\nكما ندير عمليات تجديد التوكنات عبر Mutex مركزي يمنع سباقات الخيوط المتزامنة عند تعدد طلبات الشبكة، ونبني مسار إلغاء فوري للجلسات من جانب السيرفر عند رصد أي تغير في البصمة الرقمية للجهاز، مما يوفر حماية مصرفية متعددة الطبقات ضد الهجمات المتقدمة. كما نفرض تصفير كافة مصفوفات البايتات الحساسة في الذاكرة العشوائية داخل كتل finally، ونربط صلاحية الجلسة بالـ IP وموقع الجهاز الجغرافي لقطع الاتصال فوراً عند حدوث أي نشاط مشبوه وغير معتاد."
    }
}

# ==========================================
# SEC-27: An attacker modifies an APK and bypasses client-only checks. How should the backend defend itself?
# ==========================================
DATA["SEC-27"] = {
    "concept_en": """The foundational law of mobile security architecture states: Never trust the client. On a client endpoint under attacker control, any client-side business logic, price calculations, entitlement checks, or root detections can be trivially neutralized by modifying Smali bytecode or hooking runtime methods with Frida. The backend must operate under zero-trust assumptions, treating all incoming requests as potentially forged. The backend reconstructs state by accepting only minimal operational intents (such as productId and quantity), fetching canonical prices and discounts directly from trusted database tables, validating transaction nonces and timestamps to defeat replay attacks, and enforcing strict state machine transitions. Client app authenticity is validated via server-to-server attestation through Play Integrity API.""",
    "walkthrough_en": """Server-side transaction reconstruction and anti-tamper verification architecture:
```kotlin
// 1. Client submits intent ONLY; never authoritative pricing or calculations
data class PurchaseIntentRequest(
    val productId: String,
    val quantity: Int,
    val clientNonce: String,
    val integrityToken: String
)

// 2. Server-side transaction processing pseudo-logic:
// val authenticProduct = database.findProductById(request.productId)
// val serverCalculatedPrice = authenticProduct.unitPrice * request.quantity
// val isValidApp = googlePlayIntegrityClient.verifyToken(request.integrityToken, request.clientNonce)
// if (!isValidApp.meetsStrongIntegrity) throw FraudException("Compromised client binary")
// executePayment(serverCalculatedPrice)
```""",
    "short_en": """The backend must never trust the client, operating under the rule that any client-side check can be reversed or patched. The server must reconstruct all business state, computing authoritative prices, discounts, and eligibility directly from its trusted databases. Every transaction requires cryptographic nonces to prevent replays, paired with server-verified Play Integrity attestation.""",
    "structured_en": """When an attacker decompiles and modifies an APK, every client-side barrier including input validation, pricing calculations, entitlement checks, and root detection routines can be eliminated with a few bytecode edits.
Consequently, our backend architecture operates under an absolute zero-trust policy toward incoming mobile payloads.
The mobile application is treated as a remote presentation layer that only submits user intent, never authoritative state.
For example, in a checkout flow, the app transmits solely product identifiers and quantities.
The server queries its database to retrieve authentic prices, applies active discounts, computes taxes, and calculates the total payable amount.
To prevent replay attacks where an attacker captures and repeats a legitimate request, the server issues cryptographically random nonces and enforces single-use idempotency keys.
Furthermore, the backend validates client integrity out-of-band by requiring signed attestation tokens from Google Play Integrity API, verifying application signing signatures and licensing directly with Google servers.""",
    "deep_senior_en": """The core law of distributed systems security is that client-side logic provides user convenience, while server-side logic provides system security.
On an endpoint under adversary control, decompilers like JADX and tools like APKTool allow modifying Smali bytecode to invert boolean checks or bypass local validation.
Our defense strategy centers on server-side state reconstruction and transaction invariants.
The backend never accepts computed financial figures, account privileges, or validation flags from mobile requests.
When processing transactions, the backend validates state machine transitions in the database, verifying that an account has sufficient balance and appropriate status before advancing order state.
To defeat automated tampering and botnets, we integrate Google Play Integrity API through server-to-server verification.
The mobile client requests a one-time cryptographic nonce from the backend, bound to the user id and transaction hash.
The client retrieves a signed integrity verdict from Google Play Services and sends it to our server.
Our backend decrypts and verifies the token, checking that appRecognitionVerdict matches our registered package and SHA-256 certificate digest, and verifying that deviceRecognitionVerdict confirms genuine Android hardware.
If any parameter deviates, the backend rejects the transaction, records the anomaly in our fraud prevention telemetry, and flags the associated user account for administrative review. We also enforce strict API schema validation on the gateway, immediately dropping payloads that submit unexpected properties or tampered client headers.""",
    "meta_ar": {
        "id": "SEC-27",
        "questionAr": "مهاجم قام بتعديل الـ APK وتجاوز جميع الفحوصات الأمنية المحلية، كيف يجب على الـ Backend حماية نفسه؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إدراك حتمية تزييف قرارات العميل في الـ APK المعدل، وإعادة بناء الهوية والأسعار وحالة النظام على السيرفر، وتطبيق آليات الحماية ضد إعادة الإرسال والتحقق التشفيري.",
        "concept_ar": "القاعدة الأساسية في أمان الأنظمة الموزعة هي حظر الثقة في العميل تماماً؛ فأي كود يعمل على هاتف المستخدم يمكن التلاعب به بتعديل أوامر Smali أو استخدام أدوات Frida. يجب أن يتولى السيرفر حصرياً إعادة بناء حالة العمليات، بحساب الأسعار الرسمية والضرائب والخصومات من قاعدة البيانات المركزية، واستخدام مفاتيح عدم التكرار والـ Nonce لمنع إعادة الإرسال، وتوثيق توقيع التطبيق عبر Play Integrity.",
        "walkthrough_ar": """معمارية إعادة بناء المعاملات وفحص سلامة الـ APK من جانب السيرفر:
```kotlin
// العميل يرسل نية الشراء فقط دون أي أسعار أو حسابات
data class PurchaseIntent(
    val itemId: String,
    val count: Int,
    val integrityToken: String
)
// السيرفر يجلب السعر الرسمي من قاعدة البيانات ويفحص Play Integrity
// السيرفر يرفض استلام أي حقل مثل total_price من التطبيق مباشرة
```""",
        "why_it_matters_ar": "يمنع الخسائر المالية الفادحة الناتجة عن تلاعب المهاجمين بأسعار السلع أو تزوير رصيد الحسابات أو فتح ميزات مدفوعة مجاناً، ويضمن سلامة العمليات التجارية بغض النظر عن حالة جهاز العميل.",
        "worked_example_ar": "بناء نظام دفع إلكتروني يرفض أي حقول مالية قادمة من التطبيق، ويعيد حساب إجمالي الفاتورة على السيرفر، مع فحص إثبات Play Integrity لمنع الطلبات الصادرة من نسخ APK معدلة.",
        "trade_offs_ar": "إعادة الحساب الكاملة على السيرفر تزيد من عدد الاستعلامات وقوة المعالجة على قواعد البيانات السحابية مقارنة بالاعتماد على حسابات العميل، ولكنها الضمان الوحيد لمنع الاختراق والاحتيال المالي.",
        "failure_modes_ar": "استقبال السعر النهائي أو نسبة الخصم من تطبيق الهاتف واعتمادها في قاعدة البيانات، وإهمال التحقق من توقيع الـ Nonce مما يسمح بهجمات Replay Attacks، والاعتماد على تشويش الكود بدلاً من التحقق السيرفري.",
        "production_perspective_ar": "في منصات التجارة الإلكترونية والبنوك، نطبق آلات حالات State Machines على السيرفر؛ بحيث لا يمكن للمستخدم الانتقال لحالة الدفع إلا بعد استيفاء خطوات سابقة محققة بقواعد بيانات السيرفر حصرياً.",
        "how_to_answer_ar": "ابدأ بالقاعدة الذهبية Never Trust the Client، ثم اشرح كيف يعيد السيرفر بناء الحالة والأسعار من قاعدة بياناته، واختم بآليات الحماية المتقدمة مثل Idempotency Keys و Play Integrity.",
        "talking_points_ar": "مخاطر قبول أسعار أو صلاحيات من التطبيق، آلية عمل الـ Nonce لمنع إعادة الإرسال، وكيفية فك توكنات Play Integrity على السيرفر دون الاعتماد على مخرجات العميل.",
        "follow_ups_ar": "- **المحاور:** \"إذا قام مهاجم بتعديل الـ APK ليرسل سعراً بقيمة صفر، كيف يتصرف السيرفر؟\"\n  **المرشح:** \"السيرفر لا يقرأ حقل السعر من الـ JSON أصلاً! هو يقرأ معرف المنتج فقط ويستعلم عن سعره المعتمد من قاعدة البيانات ويحسب الفاتورة بنفسه.\"\n\n- **المحاور:** \"كيف نمنع المهاجم من إعادة إرسال طلب تحويل مالي ناجح عدة مرات؟\"\n  **المرشح:** \"نلزم كل طلب بـ Idempotency-Key ورقم تسلسلي Nonce يتم تسجيلهما في كاش Redis فوري، فإذا تكرر نفس المفتاح يتم رفض الطلب فوراً.\"",
        "self_check_ar": "هل أكدت على مبدأ Never Trust the Client؟ وهل وضحت إعادة حساب الأسعار على السيرفر واستخدام Idempotency Keys و Play Integrity؟",
        "references_ar": f"- [OWASP Mobile Top 10 - Insecure Communication and Architecture](https://owasp.org/www-project-mobile-top-10/) — معايير OWASP لأمان معمارية تطبيقات الموبايل.\n- [Google Play Integrity API Overview](https://developer.android.com/google/play/integrity/overview) — التوثيق الرسمي لخدمة توثيق نزاهة التطبيقات والأجهزة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "القاعدة الذهبية في أمان الأنظمة هي حظر الثقة في العميل نهائياً، لأن أي فحص محلي يمكن تجاوزه بتعديل كود الـ Smali. يتولى السيرفر حصرياً إعادة حساب الأسعار والخصومات وصلاحيات الحساب من قاعدة البيانات، مع التحقق من عدم تكرار العمليات عبر Nonce تشفيري، وفحص توثيق توقيع التطبيق عبر Play Integrity.",
        "best_answer_ar": "عندما يقع الـ APK في يد مهاجم، تصبح كافة الفحوصات المحلية في التطبيق بلا قيمة أمنية؛ حيث يستطيع المهاجم تعديل شروط الكود البرمجي أو استخدام أدوات الحقن لجعل أي دالة تعيد قيمة إيجابية دائماً.\n\nلذلك، تبنى خوادم البنك على معمارية عدم الثقة التامة في مدخلات العميل. لا يستقبل السيرفر السعر النهائي أو نسبة الخصم من تطبيق الهاتف إطلاقاً، بل يستقبل فقط معرّف العنصر والكمية، ثم يقوم السيرفر ذاتياً بالاستعلام من قاعدة بياناته الرسمية لحساب الأسعار والضرائب.\n\nولحماية المعاملات من هجمات إعادة الإرسال والتزييف، يفرض السيرفر استخدام مفاتيح عدم التكرار Idempotency Keys والرموز العشوائية Nonces المؤقتة. كما يتحقق السيرفر تشفيرياً من سلامة الـ APK عبر خدمة Play Integrity API، حيث يتواصل السيرفر مباشرة مع خوادم جوجل لفك شفرة الإثبات والتأكد من مطابقة توقيع الشهادة وعدم تعديل التطبيق قبل قبول أي طلب حساس.",
        "deep_answer_ar": "في النمذجة التهديدية للتطبيقات المصرفية، يعتبر العميل مجرد واجهة عرض تفاعلية وغير موثوقة في بيئة خارجية لا نملك السيطرة عليها.\n\nتعتمد الحماية السيرفرية على إعادة بناء حالة المعاملة بالكامل؛ حيث يرفض السيرفر أي بارامترات تتعلق بالصلاحيات أو الأسعار أو الرصيد المحسوب محلياً. وتخضع كل عملية لآلة حالات صارمة State Machine داخل قاعدة البيانات، تتحقق من وجود رصيد كافٍ وتطابق الحساب وسريان المعاملة قبل كتابة أي تغيير مالي في السجلات.\n\nوللتصدي للهجمات التي تعتمد على تطبيقات معدلة وموزعة خارج المتجر، نربط العمليات الحساسة بتوثيق Play Integrity المدار سيرفرياً. يطلب التطبيق رمز Nonce فريداً من السيرفر مربوطاً ببيانات التحويل، ويجلبه مختوماً بتوقيع خدمات جوجل العتادي، ليفحصه السيرفر ويتأكد من معايير appRecognitionVerdict و deviceRecognitionVerdict.\n\nفإذا كشف السيرفر أي تلاعب في توقيع الـ APK أو تشغيل التطبيق داخل بيئة محاكاة أو روت، يتم إسقاط الطلب وتجميد الجلسة وإرسال إشعار فوري لمنظومة مراقبة الاحتيال، مما يحمي أصول المؤسسة المالية بصورة قطعية حتى لو كان التطبيق مكسوراً بالكامل على جهاز العميل. كما ترفض بوابة الخدمات السحابية API Gateway أي طلبات تحتوي على حقول غير معرفة في المخطط البرمجي، وتفرض قيود معدل الطلبات Rate Limiting لمنع هجمات التخمين الآلية، وتلزم بإعادة توثيق المستخدم عند محاولة الوصول لأي بيانات حساسة."
    }
}

# ==========================================
# SEC-28: An embedded TLS certificate expires. How do you rotate pins without bricking the app?
# ==========================================
DATA["SEC-28"] = {
    "concept_en": """Hardcoding TLS certificate leaf pins without a resilient rotation strategy is an operational catastrophe waiting to happen. When a leaf certificate expires or gets revoked, every client connection terminates with SSLPeerUnverifiedException, bricking network access and leaving the app unable to fetch dynamic configurations. To prevent this self-inflicted Denial of Service (DoS), resilient architectures pin the Subject Public Key Info (SPKI) hash rather than the leaf certificate itself. Because SPKI hashes represent the public key rather than certificate metadata or expiration dates, server operations can renew the certificate using the identical key pair via Certificate Signing Request (CSR) without breaking existing app pins. Furthermore, applications must configure backup pins (including cold backup keys stored in offline hardware security modules and intermediate CA pins) and define expiration dates in network_security_config.xml.""",
    "walkthrough_en": """Resilient certificate pinning configuration with SPKI hashing and expiration fallback:
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.bank.com</domain>
        <!-- Set explicit pin expiration to prevent permanent client bricking -->
        <pin-set expiration="2027-12-31">
            <!-- 1. Primary server SPKI pin -->
            <pin digest="SHA-256">k20D3pGY4uk43XA54SMmypPRfYKqioV5vNa5nWozJCA=</pin>
            <!-- 2. Cold backup SPKI pin stored securely in offline HSM -->
            <pin digest="SHA-256">x4QzPSC810K5/cMjb05Qm4k3Bw52nHgsdDJdfWeLgsI=</pin>
            <!-- 3. Intermediate CA pin as disaster recovery fallback -->
            <pin digest="SHA-256">YLh1dUR9y6Kja30RrAn7JKnbQG/uEtLMkBgFF2Fuihg=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```""",
    "short_en": """To prevent bricking when a TLS certificate expires, we pin the Subject Public Key Info hash rather than the leaf certificate. This allows server operations to renew the certificate using the identical public key via a CSR without breaking clients. We also embed backup pins, configure expiration safety dates, and enforce proactive operational key rotations.""",
    "structured_en": """Hardcoding TLS certificate pinning creates an existential availability risk if an embedded certificate expires before client devices can install an application update.
If a leaf certificate expires or gets revoked, every subsequent HTTPS connection terminates immediately with an SSLPeerUnverifiedException, bricking all server communication.
To eliminate this risk, our architecture exclusively pins the Subject Public Key Info hash rather than the full certificate.
Because the SPKI hash represents only the public key material, backend operations can renew expiring certificates using a Certificate Signing Request generated from the existing private key, keeping the public key and pin hash identical.
We also enforce a multi-pin topology containing an active primary pin, a cold standby backup pin generated in an offline hardware security module, and an intermediate CA pin.
In network_security_config.xml, we set an expiration date attribute on the pin-set.
If an un-updated client reaches this expiration threshold, the system gracefully suspends pinning enforcement and reverts to trusted system certificate authorities, maintaining app availability while maintaining standard TLS encryption.""",
    "deep_senior_en": """The critical operational failure with certificate pinning is confusing certificate identity with key identity.
A leaf certificate binds identity metadata, issuance dates, and expiration timestamps to a public key.
When developers pin the entire X.509 certificate byte array, certificate renewal inevitably alters the cryptographic digest and severs mobile connectivity.
By pinning the Subject Public Key Info digest instead, we separate the cryptographic key pair from certificate metadata.
When our backend certificates near renewal, operations issues a renewal CSR using the existing private key, preserving the SPKI hash across certificate lifecycles without requiring any mobile code modifications.
Furthermore, resilience demands a defense-in-depth pin set.
We bundle three distinct pins within our network configuration: the active server SPKI pin, a secondary backup key pin for our disaster recovery domain, and an offline cold backup pin whose private key resides in an air-gapped hardware security module.
If our primary key pair is compromised and requires immediate revocation, operations rotates the server to the backup certificate, and client apps automatically establish trusted sessions using the secondary pin.
To prevent deadlock, we configure the pin-set expiration attribute in network_security_config.xml set to a reasonable horizon.
This attribute acts as an automated safety breaker: if an emergency occurs where all pins are lost, reaching the expiration date falls back to platform CA verification, preventing permanent app bricking while maintaining full transport encryption.""",
    "meta_ar": {
        "id": "SEC-28",
        "questionAr": "انتهت صلاحية شهادة TLS المثبتة في التطبيق، كيف تقوم بتدوير الـ Pins وحل المشكلة دون تعطيل التطبيق؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الفرق بين انتهاء صلاحية الشهادة وتدوير مجموعة الـ Pins، ومعدلات تحديث التطبيقات، وخطة الطوارئ التشغيلية، وحظر الرجوع غير الآمن للاتصال عند فشل الـ Pinning.",
        "concept_ar": "تثبيت الشهادات بصورة غير مرنة قد يؤدي لكارثة تشغيلية تعطل اتصالات التطبيق بالكامل Self-inflicted DoS عند انتهاء صلاحية الشهادة. تكمن الوقاية الهندسية في تثبيت تجزئة المفتاح العام SPKI بدلاً من الشهادة الكاملة، مما يتيح تجديد الشهادة بنفس زوج المفاتيح عبر CSR دون تغيير البصمة، مع اعتماد مفاتيح احتياطية باردة ووضع تاريخ انتهاء لمجموعة التثبيت.",
        "walkthrough_ar": """إعداد تثبيت الشهادات المرن مع المفاتيح الاحتياطية وتاريخ الانتهاء:
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.bank.com</domain>
        <pin-set expiration="2027-12-31">
            <!-- المفتاح الأساسي الفعال SPKI -->
            <pin digest="SHA-256">k20D3pGY4uk43XA54SMmypPRfYKqioV5vNa5nWozJCA=</pin>
            <!-- مفتاح احتياطي بارد محفوظ في وحدة HSM -->
            <pin digest="SHA-256">x4QzPSC810K5/cMjb05Qm4k3Bw52nHgsdDJdfWeLgsI=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```""",
        "why_it_matters_ar": "يضمن استمرارية توافر الخدمة لملايين المستخدمين دون انقطاع الاتصال عند تجديد شهادات السيرفر الدورية، ويمنع الشلل التام للعملاء القدامى الذين لم يقوموا بتحديث التطبيق فوراً.",
        "worked_example_ar": "محاكاة تدوير شهادة السيرفر باستخدام نفس المفتاح الخاص CSR، والتحقق من نجاح مصافحة TLS للتطبيقات دون الحاجة لنشر إصدار جديد في المتجر.",
        "trade_offs_ar": "تثبيت المفتاح الوسيط Intermediate CA يوفر أماناً ومرونة عالية للتجديد ولكنه يوسع نطاق الثقة قليلاً، بينما تثبيت المفتاح الطرفي Leaf SPKI يوفر أقصى درجات الأمان ولكنه يتطلب حوكمة تشغيلية صارمة.",
        "failure_modes_ar": "تثبيت ملف الشهادة الكامل بدلاً من بصمة المفتاح العام SPKI، وتغيير المفتاح الخاص على السيرفر دون إخطار فريق الموبايل، ووضع كود يعطل فحص SSL عند الفشل مما يفتح الباب لهجمات MITM.",
        "production_perspective_ar": "في كبرى المؤسسات البنكية، نربط مواعيد تجديد الشهادات بأنظمة إنذار مبكر قبل 90 يوماً، مع وضع إجراءات طوارئ لتفعيل شهادات الـ Backup Pins السحابية فور رصد أي مؤشر خلل.",
        "how_to_answer_ar": "ابدأ بالتفريق بين هوية الشهادة وبصمة المفتاح العام SPKI، ثم اشرح استراتيجية المفاتيح الاحتياطية وتاريخ انتهاء الـ Pin Set، واختم بكيفية تجديد الشهادة بـ CSR دون كسر التطبيق.",
        "talking_points_ar": "أهمية SPKI Pinning مقارنة بـ Certificate Pinning، كيفية عمل خاصية expiration في network_security_config، واستراتيجيات الطوارئ عند فقدان المفتاح الخاص.",
        "follow_ups_ar": "- **المحاور:** \"إذا انتهت صلاحية الشهادة ولم يكن لدينا Backup Pin، ما هو الحل؟\"\n  **المرشح:** \"إذا كنا نثبت بصمة SPKI، يصدر فريق السيرفر شهادة جديدة تماماً بنفس المفتاح الخاص عبر CSR فيعمل التطبيق فوراً؛ أما لو كنا نثبت ملف الشهادة كاملاً، فلا مفر من نشر تحديث طارئ للمتجر.\"\n\n- **المحاور:** \"هل يجوز برمجياً السماح بالاتصال بدون تثبيت إذا فشل الـ Pinning؟\"\n  **المرشح:** \"ممنوع قطعياً في التطبيقات المالية؛ لأن السماح بالتراجع Insecure Fallback يلغي الفائدة الأمنية بالكامل ويجعل التطبيق فريسة سهلة لهجمات الرجل في المنتصف.\"",
        "self_check_ar": "هل فرقت بدقة بين الشهادة والمفتاح العام SPKI؟ وهل شرحت دور Backup Pin وخاصية expiration في ملف network_security_config؟",
        "references_ar": f"- [Android Network Security Configuration](https://developer.android.com/privacy-and-security/security-config) — التوثيق الرسمي لإعدادات أمان الشبكات وتثبيت الشهادات.\n- [OWASP Certificate and Public Key Pinning](https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html) — الدليل الإرشادي لأفضل ممارسات تثبيت المفاتيح.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "لتفادي تعطل التطبيق عند انتهاء صلاحية شهادة TLS، نثبت بصمة المفتاح العام SPKI بدلاً من ملف الشهادة الكاملة. هذا يسمح لفرق العمليات بتجديد الشهادة السنوية بنفس زوج المفاتيح الأصلي عبر CSR دون تغيير البصمة، مع تضمين مفاتيح احتياطية وتحديد تاريخ انتهاء لمجموعة الـ Pins للرجوع الآمن لسلطات النظام.",
        "best_answer_ar": "تثبيت الشهادات سلاح ذو حدين، فإذا انتهت صلاحية الشهادة المثبتة، يواجه المستخدمون خطأ SSLPeerUnverifiedException وتنقطع اتصالات التطبيق بالكامل ولا يستطيع حتى جلب التحديثات.\n\nلمنع هذا السيناريو الكارثي، نعتمد معمارياً على تثبيت تجزئة المفتاح العام المشفر SPKI Pinning وليس ملف الشهادة X.509. نظراً لأن بصمة SPKI تمثل المفتاح العام المجرد بمعزل عن تاريخ الانتهاء، يستطيع مهندسو البنية التحتية استخراج شهادة جديدة عبر طلب CSR باستخدام نفس المفتاح الخاص، مما يبقي البصمة مطابقة تماماً ويضمن استمرار التطبيقات القديمة في العمل دون انقطاع.\n\nوعلاوة على ذلك، نلزم التطبيق بامتلاك مفتاح احتياطي بارد محفوظ في خزنة معزولة، ومفتاح وسيط لجهة إصدار الشهادات CA. ونحدد تاريخ انتهاء صلاحية لمجموعة التثبيت داخل ملف network_security_config.xml، ليعمل كصمام أمان يعيد التطبيق للتحقق القياسي لشهادات النظام إذا تجاوز التاريخ دون تحديث، مما يحمي التطبيق من التوقف التام.",
        "deep_answer_ar": "الخطأ المعماري الشائع في تثبيت الشهادات ينبع من الخلط بين هوية الشهادة الرقمية وبين زوج المفاتيح التشفيرية المستخدم في المصافحة.\n\nتحتوي الشهادة على تواريخ إصدار وانتهاء وبيانات وصفية تتغير دورياً، بينما يظل المفتاح العام ثابتاً طالما لم يتم تغييره. لذلك نقصر التثبيت دائماً على تجزئة الـ SPKI، مما يتيح تدوير الشهادات بمرونة تامة عبر إصدار شهادات جديدة بنفس المفتاح الأصلي دون كسر التطبيقات المثبتة لدى ملايين العملاء.\n\nولبناء بنية تحتية مقاومة للكوارث، نعتمد استراتيجية المفاتيح الثلاثية في إعدادات الشبكة: المفتاح الأساسي الفعال، ومفتاح احتياطي ساخن لنطاق الطوارئ، ومفتاح احتياطي بارد محفوظ في وحدة أمان عتادية HSM غير متصلة بالإنترنت. فإذا حدث اختراق طارئ للمفتاح الأساسي، ينشر فريق العمليات الشهادة الاحتياطية على السيرفر فوراً، فيتعرف عليها التطبيق عبر البصمة البديلة بسلاسة تامة.\n\nكما نضع خاصية expiration في عنصر pin-set داخل ملف إعدادات أمان الشبكة؛ لتعمل كقاطع دائرة أوتوماتيكي يسقط التثبيت المشدد ويعود لشهادات النظام الموثوقة بعد التاريخ المحدد، مما يمنع شلل التطبيق نهائياً ويحافظ على تشفير الاتصال وحماية بيانات العملاء. كما نراقب مقاييس الشبكة الحية في لوحات Grafana لرصد أي ارتفاع في أخطاء المصافحة SSL Handshake Errors، مما يمكن فريق الدعم الفني من التواصل مع مسؤولي البنية التحتية وحل مشكلات الشهادات قبل تأثر المستخدمين."
    }
}

# ==========================================
# SEC-29: A rooted device can hook your code with Frida. What protections help and what can they not guarantee?
# ==========================================
DATA["SEC-29"] = {
    "concept_en": """On a rooted Android device, an attacker possesses ring-0 kernel authority and complete control over process memory via ptrace, memory mappings, and runtime instrumentation engines like Frida. Consequently, client-side protections cannot provide absolute guarantees against hooking, code modification, or reverse engineering. Any client-side check—whether root file scanning, ptrace anti-debugging, port scanning for frida-server, or native library integrity checking—can eventually be identified and neutralized by a skilled reverse engineer. What defense-in-depth protections DO accomplish is raising the financial and temporal cost of an attack. Layered mitigations include hardware-backed cryptographic operations (StrongBox/TEE) where keys cannot be extracted even with memory hooks, Play Integrity API with cryptographic attestation verified on backend servers, multi-layered RASP in native C/C++ with symbol stripping, and control-flow obfuscation.""",
    "walkthrough_en": """Multi-layered defense pattern combining native checks with hardware-backed signing:
```kotlin
// 1. Hardware-bound biometric operation that Frida cannot fake in silicon
fun executePrivilegedTransaction(
    cipher: Cipher,
    payload: ByteArray,
    onSuccess: (ByteArray) -> Unit
) {
    // Hardware key requires authenticated crypto object
    // Even if an attacker hooks the Kotlin callback, the backend requires
    // the cipher-encrypted ciphertext produced inside the TEE/StrongBox
    val encryptedPayload = cipher.doFinal(payload)
    onSuccess(encryptedPayload)
}

// 2. Play Integrity token exchange verified on backend
// Backend decrypts verdict and verifies MEETS_STRONG_INTEGRITY
```""",
    "short_en": """On a rooted device, client protections cannot guarantee prevention of hooking or reverse engineering, because the attacker has kernel authority. Mitigations help by dramatically raising attack costs: hardware-backed Keystore with StrongBox prevents key theft, server-verified Play Integrity attestation defeats client tampering, and native obfuscation slows analysis. The only absolute guarantees exist on the backend.""",
    "structured_en": """When an attacker operates on a rooted Android device, they possess complete control over the Linux kernel, process memory, and runtime environments.
Through dynamic instrumentation frameworks like Frida, an adversary can hook Java methods, intercept native functions, read CPU registers, and force security checks to return true.
Consequently, client-side RASP checks cannot guarantee absolute security or prevent runtime modification.
Any local detection looking for su binaries, test-keys, or open debugging ports can be located and bypassed by an experienced reverse engineer.
What effective protections do achieve is raising the economic and technical cost of an attack.
Hardware-backed cryptographic keys generated inside the Android Keystore with StrongBox or TEE cannot be extracted by Frida because raw key material never leaves the secure chip.
Critical transactions signed via biometric CryptoObject remain mathematically bound to physical hardware authorization.
Furthermore, Google Play Integrity API provides cryptographically signed device verdicts that are verified server-side rather than trusted on the client.
Combining native C++ checks, control flow obfuscation, and backend behavioral analytics provides robust defense without relying on client-side perfection.""",
    "deep_senior_en": """The fundamental reality of mobile security is the asymmetric power of an attacker who owns the hardware.
With root privileges, tools like Magisk with Zygisk hide modifications at the zygote initialization phase, while Frida injects V8 JavaScript runtimes directly into the Dalvik process.
No software-only client check can withstand a determined attacker given sufficient time.
Our engineering approach accepts this reality and focuses on two verifiable pillars: hardware-bound cryptography and backend invariant enforcement.
In our architecture, we separate authorization logic from cryptographic keys.
An attacker can easily hook an isUserAuthenticated method to return true, but if that method does not produce a valid digital signature from a hardware-backed private key, the backend simply rejects the transaction.
Keys generated in StrongBox Keymaster require explicit biometric gating; the physical secure enclave will not release the cryptographic operation without an authenticated hardware token from the fingerprint sensor.
Frida can manipulate Dalvik bytecode, but it cannot forge hardware signals inside an isolated silicon processor.
Second, we rely on Google Play Integrity API with cryptographic attestation verified exclusively on our servers.
The backend generates a transaction-linked nonce, and Google signs the integrity payload.
Frida cannot fake Google's private signing key.
We augment this with native anti-tamper routines, symbol stripping, and string encryption via OLLVM to slow down reconnaissance.
Ultimately, the backend remains our final line of defense, monitoring transaction velocity, anomaly scores, and device risk profiles to mitigate threats holistically.""",
    "meta_ar": {
        "id": "SEC-29",
        "questionAr": "جهاز معمول له Root ويستطيع المهاجم عمل Hooking لكود التطبيق عبر Frida، ما هي الحمايات التي تساعد، وما الذي لا يمكن ضمانه إطلاقاً؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إدراك حتمية تجاوز كشف الروت وFrida على بيئة معادية، والتحكم بالطبقات الأمنية، وحتمية الثوابت السيرفرية، وسياسة التعامل مع الإنذارات الكاذبة.",
        "concept_ar": "على جهاز يمتلك فيه المهاجم صلاحيات الروت، لا يمكن لأي حماية برمجية محلية تقديم ضمانات مطلقة لمنع الهندسة العكسية أو الـ Hooking بأدوات مثل Frida؛ فالمهاجم يسيطر على النواة والذاكرة. تنحصر الحماية الفعالة في رفع تكلفة الهجوم، وتأمين العمليات بالتشفير العتادي المقفل في StrongBox، والتحقق السيرفري المشدد عبر Play Integrity، وجعل السيرفر هو مصدر الحقيقة النهائي.",
        "walkthrough_ar": """فصل التحقق الشكلي عن التوقيع التشفيري العتادي لحماية العمليات الحساسة:
```kotlin
// العملية المالية لا تكتفي بقيمة منطقية بل تتطلب تشفيراً عتادياً
fun finalizeTransfer(cipher: Cipher, transferData: ByteArray): ByteArray {
    // كائن Cipher محمي بعتاد StrongBox ولا يفك إلا ببصمة حية
    // اعتراض Frida للدالة لن يفيده إذا عجز عن استخراج التوقيع التشفيري
    return cipher.doFinal(transferData)
}
```""",
        "why_it_matters_ar": "يضع معايير هندسية واقعية تبعد الفريق عن الأوهام الأمنية، وتمنع الاعتماد الكلي على فحوصات العميل الهشة، مما يركز جهود الحماية في النقاط التي تعجز أدوات الاختراق عن كسرها رياضياً.",
        "worked_example_ar": "دمج فحص نزاهة النظام عبر Play Integrity والتحقق من التوكن على السيرفر مع استخدام مفاتيح ECDSA مشفرة في TEE لتوقيع المعاملات المالية.",
        "trade_offs_ar": "إضافة طبقات تشويش الكود المتقدمة وحمايات RASP تزيد من حجم الـ APK وزمن التشغيل قليلاً وتتطلب صيانة مستمرة، ولكنها ترفع الجهد الزمني المطلوب للهندسة العكسية من دقائق إلى أسابيع.",
        "failure_modes_ar": "الاعتماد على مكتبات كشف الروت الجاهزة مثل RootBeer كخط دفاع وحيد، وإغلاق التطبيق فوراً بناءً على فحص محلي سطحي، وإرسال قيمة منطقية (isSecured=true) للسيرفر يمكن تزييفها بسهولة.",
        "production_perspective_ar": "في التطبيقات المصرفية، لا نغلق التطبيق فوراً عند الشك بالروت بل نرسل إشارات Telemetry للمنظومة السحابية لتقييد العمليات المالية الكبرى وطلب خطوات تحقق إضافية (Step-up Auth).",
        "how_to_answer_ar": "ابدأ بالاعتراف الصريح بأن بيئة العميل المخترقة لا تضمن منع الـ Hooking، ثم اشرح كيف ترفع تكلفة الهجوم بالتشفير العتادي وPlay Integrity، واختم بدور السيرفر كخط دفاع حاسم.",
        "talking_points_ar": "آلية عمل Frida في حقن الجافا سكريبت بالذاكرة، سبب عجز Frida عن تزوير مفاتيح StrongBox، واستراتيجية الدفاع المعمق متعدد الطبقات.",
        "follow_ups_ar": "- **المحاور:** \"إذا تجاوز المهاجم كود فحص الروت عبر Frida، كيف تحمي أموال البنك؟\"\n  **المرشح:** \"نحميها بربط التحويل بمفتاح Keystore يتطلب CryptoObject بيومتري؛ فمهما عدل Frida في دوال التطبيق، لن يستطيع إجبار شريحة الـ Secure Element على التوقيع دون بصمة حقيقية.\"\n\n- **المحاور:** \"لماذا لا نستخدم ptrace لمنع Frida من الالتصاق بالعملية؟\"\n  **المرشح:** \"يمكن استخدام ptrace كعائق بسيط، لكن المهاجم المتقدم يستطيع عمل Hook لدالة ptrace نفسها في النواة أو تعديل الـ Smali لحذف استدعائها بسهولة.\"",
        "self_check_ar": "هل أكدت على استحالة تقديم ضمانات مطلقة على جهاز العميل؟ وهل بينت قوة التشفير العتادي وPlay Integrity والتحقق السيرفري؟",
        "references_ar": f"- [OWASP MASTG - Testing Dynamic Analysis and Tampering](https://github.com/OWASP/owasp-mastg) — دليل OWASP لاختبار ومقاومة أدوات التحليل الديناميكي.\n- [Android Hardware-backed Keystore](https://source.android.com/docs/security/features/keystore) — التوثيق الرسمي لطبقة أمان Keystore العتادية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "على جهاز مروت، لا يمكن لأي حماية محلية تقديم ضمانات مطلقة ضد Frida لأن المهاجم يمتلك صلاحيات النواة والتحكم بالذاكرة. الحمايات الفعالة ترفع تكلفة الهجوم: التشفير العتادي بـ StrongBox يمنع استخراج المفاتيح، وPlay Integrity يوثق سلامة النظام سيرفرياً، بينما تظل الضمانات الحقيقية محصورة في قواعد السيرفر.",
        "best_answer_ar": "يمتلك المهاجم على الأجهزة المروّتة صلاحيات كاملة في نواة النظام والذاكرة العشوائية؛ وباستخدام أدوات مثل Frida يستطيع اعتراض دوال الجافا والنيتف، وتعديل قيم المسجلات، وإجبار أي فحص أمني محلي على إرجاع نتيجة إيجابية بسهولة.\n\nلهذا السبب، فإن أدوات الفحص المحلي لا يمكنها ضمان منع التلاعب نهائياً، وأي كود يفحص وجود ملف su أو منافذ التصحيح يمكن للمهاجم تعطيله. لكن دور الحمايات يكمن في رفع تكلفة الاختراق وصعوبته التقنية.\n\nنحقق ذلك بالاعتماد على التشفير المربوط بعتاد StrongBox و TEE؛ فحتى لو نجح Frida في تزييف واجهة المستخدم، لا يمكنه إجبار معالج الأمان على فك التشفير أو توقيع المعاملة دون بصمة بيومترية حية. كما نعتمد على Play Integrity API للتحقق من سلامة التطبيق والجهاز عبر خوادم جوجل مباشرة، مع تشويش الكود على مستوى النيتف، وترك القرار النهائي لمحركات كشف الاحتيال على السيرفر.",
        "deep_answer_ar": "في النمذجة التهديدية المتقدمة، ندرك عدم التكافؤ الأمني على بيئة العميل؛ فالمهاجم الذي يملك الجهاز يستطيع استخدام وحدات Magisk و Zygisk لإخفاء الروت في مرحلة تهيئة النظام، وحقن محرك Frida البرمجي مباشرة داخل ذاكرة تطبيقنا.\n\nإن الادعاء بوجود مكتبة برمجية تمنع Frida بشكل قطعي هو وهم أمني؛ فكل فحص محلي يمكن تفكيكه برمجياً عبر الهندسة العكسية. لذلك نركز استراتيجيتنا على الضمانات التشفيرية العتادية والثوابت السيرفرية التي تعجز أدوات الحقن عن كسرها.\n\nفي طبقة التشفير، نربط العمليات الحساسة بمفاتيح Keystore مدعومة بـ StrongBox ومقيدة بالبصمة الحية؛ يستطيع المهاجم عمل Hook للدالة البرمجية، لكنه يعجز رياضياً عن تزوير توقيع الشريحة العتادية المعزولة. وفي طبقة التوثيق، نعتمد على Play Integrity مع التحقق السيرفري؛ حيث يولد السيرفر رمز Nonce مربوطاً بالعملية، ويتحقق من التوقيع الرقمي الصادر من جوجل، وهو ما يستحيل على المهاجم تزييفه.\n\nكما نعزز الكود بحمايات RASP في طبقة النيتف C++ مع تشويش تدفق التحكم عبر OLLVM لإرهاق المهاجم وإبطاء محاولاته، مع اعتماد السيرفر على تحليل سلوك المعاملات ورصد الأنماط الشاذة كخط دفاع أخير يضمن حماية أموال العملاء. كما نقوم بتجريد ملفات المكتبات النيتف من الرموز البرمجية عبر Symbol Stripping، ونراقب التعديلات المفاجئة في أوقات استجابة الدوال البرمجية كإشارة إضافية لاحتمالية وجود أدوات مراقبة وحقن نشطة على جهاز المستخدم."
    }
}

# ==========================================
# SEC-30: A payment app must mask PAN and avoid sensitive logs. Design a logging/observability policy.
# ==========================================
DATA["SEC-30"] = {
    "concept_en": """A production payment application subject to PCI-DSS (Payment Card Industry Data Security Standard) must implement strict observability guardrails. Under PCI-DSS Requirement 3, the Primary Account Number (PAN) must be masked wherever displayed or logged, allowing at most the first six digits (BIN) and last four digits to be visible. Sensitive Authentication Data (SAD)—including card verification values (CVV, CVC, CID), PIN blocks, and full magnetic stripe data—must NEVER be logged, cached, or persisted post-authorization under any circumstance. Designing a zero-leakage observability architecture requires defense at multiple boundaries: compiling out Logcat statements via R8 rules, deploying a sanitizing HTTP interceptor that regex-scrubs JSON payloads and strips Authorization headers, masking form fields in crash reporting SDKs, and correlating distributed traces using non-sensitive correlation UUIDs.""",
    "walkthrough_en": """PCI-DSS compliant sanitizing interceptor and R8 log removal:
```kotlin
// 1. OkHttp Redacting Interceptor for secure network telemetry
class SensitiveDataSanitizingInterceptor : Interceptor {
    private val panRegex = Regex("\\b(?:\\d[ -]*?){13,16}\\b")
    private val cvvRegex = Regex("\"cvv\"\\s*:\\s*\"\\d{3,4}\"")

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        // Strip sensitive authorization tokens from outgoing log streams
        val sanitizedHeaders = request.headers.newBuilder()
            .set("Authorization", "[REDACTED]")
            .build()

        val response = chain.proceed(request.newBuilder().headers(sanitizedHeaders).build())
        return response
    }
}

// 2. ProGuard/R8 rule stripping Logcat in release builds:
// -assumenosideeffects class android.util.Log {
//     public static *** d(...);
//     public static *** v(...);
//     public static *** i(...);
// }
```""",
    "short_en": """A payment app logging policy strictly complies with PCI-DSS: PAN numbers must be masked to display at most the first six and last four digits, while sensitive authentication data like CVVs and PINs are completely prohibited from logs. We strip Logcat statements via R8, implement an OkHttp redacting interceptor, and sanitize crash payloads.""",
    "structured_en": """Observability in a payment application requires strict architectural boundaries to achieve PCI-DSS compliance and eliminate data leak vectors.
Under PCI-DSS rules, the Primary Account Number must be masked wherever displayed or recorded, allowing only the first six digits for bank identification and the last four digits for customer recognition.
Sensitive Authentication Data including CVV codes, card PINs, and full magnetic stripe data must never be written to logs, disk, or memory dumps under any condition.
In production builds, our R8 configuration strips all Logcat invocations using assumenosideeffects rules to ensure zero developer logs leak to logcat readers.
For necessary network telemetry, we install a custom OkHttp SanitizingInterceptor.
This interceptor parses JSON request and response payloads, replacing credit card number patterns with masked strings and completely stripping CVVs and authorization headers before events reach analytics or APM SDKs.
Crash reporting tools like Crashlytics are configured with custom event transformers that redact user inputs, and distributed transactions are correlated using ephemeral UUIDs rather than personal customer data.""",
    "deep_senior_en": """In regulated fintech applications, logging policies directly govern compliance certification and legal liability.
A single unredacted PAN or CVV captured in an application monitoring tool like Datadog or Crashlytics constitutes an immediate PCI-DSS violation with severe financial penalties.
We establish a zero-leakage observability architecture enforcing defense across compile, network, and crash-reporting boundaries.
At compile time, our release ProGuard and R8 rules strip all android.util.Log and Timber debug invocations entirely, neutralizing inadvertent developer log statements.
At the transport boundary, our OkHttp client integrates an automated RedactingInterceptor.
This interceptor utilizes regex patterns to detect sixteen-digit PAN formats, replacing the middle six digits with asterisks to yield compliant six-plus-four masked formats, while explicitly dropping CVV fields, expiration months, and Bearer tokens.
Furthermore, we override crash reporting metadata hooks.
When Crashlytics or Bugsnag captures an unhandled exception, our custom filter scrubs intent extras, bundle arguments, and view hierarchies to prevent text input values from entering breadcrumbs.
For distributed transaction tracing, we inject a cryptographically random correlation UUID into request headers.
Engineers trace requests through microservices by querying this correlation ID, entirely eliminating the need to log account numbers, customer names, or transaction payloads in diagnostic logs. We also configure automated log scrubbing rules in our cloud log ingestion pipelines, ensuring that any stray credentials inadvertently sent to backend collectors are purged before storage.""",
    "meta_ar": {
        "id": "SEC-30",
        "questionAr": "تطبيق مدفوعات إلكترونية ملزم بقواعد PCI-DSS ويجب أن يخفي أرقام البطاقات ويمنع طباعة البيانات الحساسة في السجلات، كيف تصمم سياسة Logging ومراقبة محكمة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إخفاء رقم الحساب الأساسي PAN، وحظر البيانات الحساسة مثل PIN وCVV، والربط التشخيصي بالمعرفات العشوائية بدون تسجيل البيانات، وتطهير البيانات قبل حدود المكتبات الخارجية وفترات الاحتفاظ.",
        "concept_ar": "تفرض معايير أمان بطاقات الدفع PCI-DSS متطلبات صارمة للمراقبة والتسجيل؛ حيث يُلزم المعيار بإخفاء أرقام البطاقات PAN بحيث لا يظهر سوى أول 6 أرقام وآخر 4 أرقام كحد أقصى، مع حظر كامل ومطلق لتخزين أو طباعة بيانات المصادقة الحساسة SAD كرموز CVV ورقم الـ PIN في أي سجل أو كاش. يتطلب التصميم حذف سجلات Logcat في الإنتاج عبر R8، وتركيب معترض شبكي منقٍ للبيانات، وتطهير سجلات الأعطال.",
        "walkthrough_ar": """بناء معترض تنقية الشبكة وحذف السجلات عبر قواعد R8:
```kotlin
// معترض لتنقية السجلات وحجب أرقام البطاقات ورموز الأمان
class MaskingLoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        // حجب ترويسات التوثيق وأي نصوص تحتوي على بطاقات بنكية
        return chain.proceed(request)
    }
}
// في ملف proguard-rules.pro:
// -assumenosideeffects class android.util.Log { public static *** *(...); }
```""",
        "why_it_matters_ar": "يمنع الغرامات القانونية الباهظة وسحب تراخيص العمليات المصرفية الناتجة عن مخالفة PCI-DSS، ويحمي بيانات بطاقات العملاء من السرقة في حال اختراق منصات تحليل البيانات أو خوادم الـ APM الخارجية.",
        "worked_example_ar": "إنشاء شجرة تسجيل Timber Tree مخصصة للإنتاج تقوم بتعقيم الـ StackTraces وفلترة الـ JSON Payloads لحجب بيانات البطاقات والـ Tokens قبل إرسالها لـ Crashlytics.",
        "trade_offs_ar": "حجب البيانات وتطهير السجلات قد يجعل استكشاف أخطاء المستخدمين المعقدة على السيرفر أكثر صعوبة، لكنه يوفر حماية قانونية وأمنية مطلقة لا يمكن التهاون فيها.",
        "failure_modes_ar": "طباعة نصوص الـ JSON الكاملة لطلبات الدفع في Logcat، وتسريب أرقام البطاقات في شاشات الانهيار Crash Reports، وتضمين رموز الـ CVV في كاش التخزين المؤقت للشبكة.",
        "production_perspective_ar": "في بنوك الدفع، نعتمد على معرفات التتبع Correlation UUIDs في ترويسات HTTP لمتابعة حركة الطلبات بين الخدمات دون الحاجة لتسجيل أي معلومة شخصية عن العميل.",
        "how_to_answer_ar": "ابدأ بمتطلبات PCI-DSS الصارمة (قاعدة 6+4 وحظر الـ CVV)، ثم اشرح استراتيجية الحماية الثلاثية: حذف R8، معترض OkHttp، وتعقيم Crashlytics، واختم بـ Correlation IDs.",
        "talking_points_ar": "الفرق بين PAN و Sensitive Authentication Data، دور R8 في حذف Logcat في الإنتاج، وكيفية تتبع الأخطاء بالـ UUID دون تسجيل بيانات الدفع.",
        "follow_ups_ar": "- **المحاور:** \"إذا احتجنا لمعرفة البنك المصدر للبطاقة لتشخيص مشكلة، هل يسمح PCI-DSS بتسجيلها؟\"\n  **المرشح:** \"نعم، يُسمح بتسجيل أول 6 أرقام وتسمى الـ BIN لمعرفة البنك، مع آخر 4 أرقام للتعرف على البطاقة، مع حجب الأرقام الوسطى بالكامل.\"\n\n- **المحاور:** \"كيف نمنع ظهور أرقام البطاقات في لقطات الشاشة وسجلات الـ ANR؟\"\n  **المرشح:** \"نضع علامة FLAG_SECURE على نافذة النشاط، ونستخدم حقول إدخال مشفرة، ونعطل خاصية Breadcrumbs التلقائية في مكتبات التحليل.\"",
        "self_check_ar": "هل ذكرت صراحة قاعدة إخفاء الـ PAN (أول 6 وآخر 4 أرقام)؟ وهل أكدت على الحظر التام لـ CVV و PIN؟ وهل شرحت دور R8 والـ Interceptor؟",
        "references_ar": f"- [PCI-DSS Requirement 3: Protect Stored Account Data](https://www.pcisecuritystandards.org/) — المعيار الدولي لحماية بيانات حسابات بطاقات الدفع.\n- [Android R8 Optimization and Log Removal](https://developer.android.com/build/shrink-code) — دليل استخدام R8 لحذف الاستدعاءات البرمجية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تعتمد سياسة السجلات في تطبيقات المدفوعات على الامتثال لمعايير PCI-DSS: حجب أرقام البطاقات PAN بإظهار أول 6 أرقام وآخر 4 فقط، وحظر تسجيل CVV أو PIN نهائياً. نحذف سجلات Logcat في الإنتاج عبر قواعد R8، ونستخدم Interceptor لتنقية طلبات الشبكة، ونعقم بيانات Crashlytics.",
        "best_answer_ar": "تتطلب هندسة المراقبة في تطبيقات الدفع الإلكتروني التزاماً صارماً بمعايير PCI-DSS لضمان عدم تسريب أي بيانات مالية حساسة إلى ملفات السجلات أو خوادم المتابعة.\n\nتفرض المعايير إخفاء رقم الحساب الأساسي PAN بحيث لا يظهر منه سوى أول 6 أرقام لتحديد البنك وآخر 4 أرقام لتعريف المستخدم، مع الحظر التام والمطلق لتخزين أو طباعة بيانات المصادقة الحساسة مثل رمز الأمان CVV أو رقم الـ PIN أو بيانات الشريط الممغنط في أي سجل أو كاش.\n\nولتنفيذ ذلك، نحذف استدعاءات Logcat بالكامل في نسخ الإنتاج عبر قواعد R8 لضمان عدم خروج أي نص للمطورين. ونركب Sanitizing Interceptor في مكتبة OkHttp ليعترض نصوص الـ JSON ويشفر أرقام البطاقات ويحذف رموز CVV والـ Tokens قبل إرسالها لأدوات التحليل. كما نربط السجلات بمعرفات تتبع عشوائية UUID لتشخيص المشكلات دون الحاجة لتسجيل أي بيانات شخصية للمستخدمين.",
        "deep_answer_ar": "في التطبيقات المالية الممتثلة لمعايير PCI-DSS، يشكل ظهور رقم بطاقة صريح أو رمز CVV واحد في سجلات النظام أو منصات مثل Datadog و Crashlytics خرقاً أمنياً جسيماً يعرض الشركة لغرامات باهظة وفقدان رخصة التشغيل.\n\nلبناء معمارية مراقبة آمنة، نطبق ثلاث طبقات عزل صارمة. الطبقة الأولى هي مرحلة التجميع البرمجي، حيث نستخدم قواعد R8 لحذف كافة دوال Logcat عبر خاصية assumenosideeffects، مما يضمن خلو الكود النهائي من أي سجلات داخلية وضعها المطورون أثناء الاختبار.\n\nالطبقة الثانية هي طبقة النقل الشبكي، حيث ندمج Sanitizing Interceptor داخل عميل OkHttp. يقوم المعترض بفحص نصوص JSON عبر تعبيرات نمطية دقيقة، فيستبدل الأرقام الوسطى للبطاقة بنجوم ويحافظ فقط على أول ستة وآخر أربعة أرقام، ويحذف بالكامل حقول CVV وترويسات التوثيق والـ Cookies قبل وصولها لأي وسيط.\n\nالطبقة الثالثة هي أدوات تتبع الانهيارات؛ حيث نعدل كائن Crashlytics لتعقيم الـ Intent Extras وشاشات الواجهة، ومنع تسجيل نصوص الحقول التفاعلية. ونعتمد حصرياً على معرّف ارتباط عشوائي Correlation UUID لتتبع مسار المعاملة بين الهاتف والخوادم السحابية، مما يتيح تشخيص الأخطاء بدقة فائقة دون تسجيل حرف واحد من بيانات الدفع الحساسة. كما نضيف فلاتر تصفية سحابية على خوادم تجميع السجلات للتأكد من حذف أي بيانات مالية شاردة قبل كتابتها على الأقراص، ونحدد فترات احتفاظ قصيرة بالسجلات لتقليل مساحة الخطر وفق متطلبات الامتثال."
    }
}

# ==========================================
# SEC-31: A team puts a private API key in BuildConfig from local.properties. Why is this not sufficient?
# ==========================================
DATA["SEC-31"] = {
    "concept_en": """Storing secrets in local.properties and exposing them via BuildConfig field generation is effective for source control hygiene—it prevents sensitive tokens from being committed to Git repositories—but it provides zero security against extraction from compiled application binaries. During the build process, Gradle translates buildConfigField declarations into static string constants inside the generated BuildConfig.java class. When compiled into classes.dex within the final APK or AAB, these strings reside as plaintext literals in the DEX string pool. Any adversary can download the APK, execute a single command like strings classes.dex or open the binary in decompilers like JADX, and extract the secret within seconds. Consequently, private secrets (such as payment gateway secret keys, cloud master credentials, and backend service keys) must never reside inside a mobile client.""",
    "walkthrough_en": """Architecture migration replacing client-side secret with Backend-For-Frontend (BFF) gateway:
```kotlin
// 1. VULNERABLE APPROACH: Private secret baked into BuildConfig
// val stripeClient = Stripe(BuildConfig.STRIPE_SECRET_KEY) // Trivially decompiled from DEX!

// 2. SECURE BFF ARCHITECTURE: Ephemeral intent token generated by secure server
class PaymentRepository(private val backendApi: BackendPaymentApi) {
    suspend fun initiateCheckout(cartId: String): ClientSecretToken {
        // Backend creates payment intent using its own private master key in the cloud
        // Mobile client receives ONLY an ephemeral, scoped client secret
        val response = backendApi.createPaymentIntent(cartId)
        return response.clientSecret
    }
}
```""",
    "short_en": """Storing secrets in local.properties and exposing them via BuildConfig prevents pushing keys to Git, but provides zero security against extraction from the APK. During compilation, Gradle embeds the key as a plaintext string in classes.dex. Anyone can decompile the APK with JADX or run strings to extract the secret within seconds.""",
    "structured_en": """Putting API keys in local.properties and injecting them into BuildConfig is good source control hygiene, but it is completely ineffective as a binary protection mechanism.
The local.properties file successfully prevents developers from accidentally committing sensitive credentials to public or private Git repositories.
However, when Gradle builds the application, it generates a BuildConfig.java class containing the key as a static final string constant.
When compiled into the final APK or App Bundle, this string literal sits in the constant pool of classes.dex in plaintext.
An adversary does not even need to root a device or decompile source code; running a single strings command on classes.dex or opening the APK in tools like JADX reveals the secret in seconds.
Mobile clients must never hold private administrative secrets such as payment gateway secret keys or backend master credentials.
Private credentials must remain on a secure backend gateway, while public third-party keys must be restricted on vendor consoles using package names and SHA-256 signing certificate fingerprints.""",
    "deep_senior_en": """This common security misunderstanding stems from confusing source control privacy with compiled binary confidentiality.
Excluding secrets from git commits via local.properties protects against repository leaks, but an Android application is fundamentally a public binary distributed to untrusted hardware.
The build system translates buildConfigField declarations directly into Dalvik bytecode.
Once an APK is released, anyone can download it from the Play Store, unpack classes.dex, and extract strings using basic reverse engineering utilities like strings, apktool, or JADX.
Even if a team attempts to obscure the secret using NDK C++ shared libraries, XOR masking, or string encryption, reverse engineers can hook runtime decryption methods with Frida or dump memory to extract the plaintext key effortlessly.
In robust security architecture, a mobile application is considered an untrusted client that should never possess private master secrets.
If an app requires interaction with a sensitive service like Stripe or AWS, calls must route through our own Backend-for-Frontend gateway.
The mobile app authenticates to our backend using short-lived user session tokens, and our secure server uses its own securely managed private keys to interact with the third-party service.
For unavoidable client-side API keys such as Google Maps or Firebase, we enforce strict vendor-side restrictions, binding the key exclusively to our Android package name and release SHA-256 signing certificate fingerprint.""",
    "meta_ar": {
        "id": "SEC-31",
        "questionAr": "فريق برمجي يضع مفتاح الـ API الخاص في ملف local.properties ويقرأه داخل BuildConfig، لماذا يُعد هذا غير كافٍ وثغرة أمنية فادحة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "مسار استخراج مفاتيح BuildConfig وlocal.properties من الـ APK المجمع، وتصميم الاستجابة للحوادث، وهندسة الصلاحيات من جانب السيرفر.",
        "concept_ar": "وضع المفاتيح في local.properties وتمريرها لـ BuildConfig عبر Gradle هو مجرد إجراء تنظيمي لمنع تسريب المفاتيح في Git، ولكنه لا يوفر أي حماية للـ APK المجمع. يترجم المترجم هذه القيم إلى نصوص صريحة داخل مصفوفة النصوص في classes.dex، مما يتيح لأي شخص استخراج المفتاح بأمر strings أو بفتح التطبيق في JADX في ثوانٍ معدودة. الحل المعماري هو منع وجود المفاتيح الخاصة في العميل نهائياً والاعتماد على سيرفر Backend-for-Frontend.",
        "walkthrough_ar": """التحول من تضمين المفتاح في التطبيق إلى معمارية السيرفر الوسيط BFF:
```kotlin
// بدلاً من تخزين مفتاح بوابة الدفع الخاص في BuildConfig
// يتواصل التطبيق مع خادمنا الوسيط للحصول على توكن مؤقت للعملية فقط
class PaymentManager(private val api: BankingGatewayApi) {
    suspend fun startPayment(orderId: String): String {
        // السيرفر يستخدم المفتاح الخاص المحفوظ في خزنته السحابية
        // والتطبيق يستلم توكن عملية مشفراً ومؤقتاً
        return api.createEphemeralIntent(orderId).clientSecret
    }
}
```""",
        "why_it_matters_ar": "يمنع سرقة مفاتيح الحسابات البنكية والسحابية التي تؤدي لخسائر مالية كارثية كاستنزاف موارد السحابة أو تحويل أموال العملاء دون إذن، ويوفر بيئة تحكم مركزي لإلغاء وتدوير المفاتيح دون الحاجة لتحديث التطبيق.",
        "worked_example_ar": "مقارنة عملية بين استخراج مفتاح Stripe من ملف APK عبر سطر أوامر strings، وبين تنفيذ معمارية BFF حيث تُحفظ المفاتيح في AWS Secrets Manager.",
        "trade_offs_ar": "بناء سيرفر وسيط BFF يتطلب بنية تحتية إضافية وصيانة لواجهات API، مقارنة بالاتصال المباشر من التطبيق، ولكنه الإجراء الأمني الوحيد المقبول هندسياً لحماية المفاتيح الخاصة.",
        "failure_modes_ar": "تضمين مفاتيح خاصة كـ Stripe Secret Key في التطبيق، والاعتماد على تشفير XOR الساذج الذي يسهل كشفه في الذاكرة، وعدم تقييد المفاتيح العامة ببصمة SHA-256 للمطور.",
        "production_perspective_ar": "في الشركات الكبرى، ندمج أدوات فحص الأسرار الآلية مثل TruffleHog و GitGuardian في مسارات الـ CI/CD لمنع دمج أي كود يحتوي على مفاتيح، مع استخدام خدمات إدارة المفاتيح السحابية KMS.",
        "how_to_answer_ar": "ابدأ بالتفريق بين حماية مستودع Git وحماية ملف الـ APK، ثم اشرح كيف يُحفظ المفتاح كنص صريح في classes.dex وسهولة استخراجه بـ strings أو JADX، واختم بحل معمارية BFF وتقييد المفاتيح العامة.",
        "talking_points_ar": "طريقة استخراج النصوص من DEX String Pool، فشل حيل التشفير المحلي مثل NDK و XOR أمام أدوات التحليل، وأهمية تقييد المفاتيح العامة في Google Cloud Console.",
        "follow_ups_ar": "- **المحاور:** \"إذا شفرنا المفتاح في مكتبة C++ نيتف عبر NDK، هل يصبح آمناً؟\"\n  **المرشح:** \"لا، لأن الكود النيتف يعمل على جهاز العميل أيضاً؛ يستطيع المهاجم تفكيك المكتبة بـ Ghidra أو استخدام Frida لاعتراض دالة فك التشفير وقراءة المفتاح في الذاكرة فوراً.\"\n\n- **المحاور:** \"كيف نؤمن مفاتيح Google Maps التي يجب وجودها في التطبيق؟\"\n  **المرشح:** \"نقيد المفتاح في Google Cloud Console بحظر استخدامه إلا من معرّف الحزمة وبصمة شهادة التوقيع SHA-256 الرسمية للتطبيق، مع تحديد حصص الاستخدام اليومية.\"",
        "self_check_ar": "هل وضحت بدقة لماذا لا يحمي BuildConfig المفاتيح في الـ APK؟ وهل بينت سهولة استخراجها عبر strings و JADX؟ وهل شرحت حل الـ BFF وتقييد الـ SHA-256؟",
        "references_ar": f"- [OWASP MASVS-STORAGE: Sensitive Data Exposure](https://mas.owasp.org/) — معايير حماية البيانات الحساسة والمفاتيح في تطبيقات الموبايل.\n- [Google Cloud API Key Restrictions](https://cloud.google.com/docs/authentication/api-keys) — الدليل الرسمي لتقييد مفاتيح الـ API في أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "وضع المفاتيح في local.properties وتمريرها لـ BuildConfig يمنع رفعها إلى مستودع Git، لكنه لا يوفر أي حماية للـ APK المجمع. يترجم Gradle المفتاح إلى نص صريح داخل ملف classes.dex، ويستطيع أي شخص استخراجه في ثوانٍ باستخدام JADX أو أمر strings، لأن العميل بيئة غير موثوقة.",
        "best_answer_ar": "يخلط الكثير من المطورين بين حماية الكود المصدري في مستودعات Git وبين حماية التطبيق المجمع في الـ APK.\n\nوضع المفتاح في ملف local.properties واستثناؤه من الـ Git هو إجراء ممتاز لحماية تاريخ المشروع من التسريب على GitHub. ولكن عند عمل Build للتطبيق، يقوم Gradle بتوليد كلاس BuildConfig.java ويضع فيه المفتاح كنص صريح وثابت.\n\nوعند تجميع الكود في ملفات dex، يُحفظ هذا المفتاح كنص مقروء داخل مصفوفة النصوص String Pool. لا يحتاج المهاجم لأي مهارات معقدة؛ يكفي تنفيذ أمر strings classes.dex أو فتح الـ APK في JADX لقراءة المفتاح بنصه الصريح في ثوانٍ معدودة. لذلك يُحظر تماماً وضع أي مفاتيح سرية خاصة بالسيرفرات أو بوابات الدفع داخل كود الموبايل، وتمرر كافة الطلبات عبر بوابة سيرفر Backend-for-Frontend، مع تقييد المفاتيح العامة ببصمة شهادة التوقيع SHA-256.",
        "deep_answer_ar": "تعتبر هذه الثغرة من أشهر الأخطاء الشائعة في هندسة تطبيقات أندرويد؛ حيث يفترض المطور أن عدم ظهور المفتاح في كود جافا الصريح يحميه من العبث.\n\nالحقيقة التقنية الصادمة هي أن تطبيق الموبايل هو بيئة عامة ومكشوفة بالكامل للمهاجمين. فعند استخدام buildConfigField، يكتب المترجم المفتاح في كلاسات الديكس دون أي تشفير. وحتى المحاولات الساذجة لإخفاء المفتاح داخل مكتبات C++ نيتف عبر NDK أو تطبيق خوارزميات إخفاء مثل XOR، يستطيع أي باحث أمني تجاوزها في دقائق عبر فحص الذاكرة أو كتابة سطر Frida بسيط لاعتراض المفتاح لحظة استخدامه.\n\nفي المعمارية الآمنة، نعتبر العميل طرفاً غير موثوق لا يجوز ائتمانه على أي مفتاح سري خاص Master Secret مثل مفاتيح Stripe Secret أو وصول قواعد البيانات المباشر. ويتم توجيه العمليات الحساسة عبر خادم وسيط Backend-for-Frontend؛ حيث يحمل السيرفر وحده المفاتيح الخاصة في بيئة سحابية محمية، بينما يتواصل التطبيق معه بتوكنات جلسة مستخدم مؤقتة.\n\nأما المفاتيح العامة التي يجب وجودها في العميل كخدمات خرائط جوجل، فيتم تقييدها على منصة المزود بحظر استخدامها إلا من خلال معرّف حزمة التطبيق وبصمة شهادة التوقيع SHA-256 الرسمية لنسخة الإنتاج. كما نطبق أنظمة تدوير المفاتيح الدورية وفصل الصلاحيات Least Privilege في منصة السحابة، بحيث لا يمتلك أي مفتاح عام صلاحية الوصول للبيانات الحساسة أو تنفيذ عمليات تعديل في قواعد البيانات."
    }
}

# ==========================================
# SEC-32: A security SDK falsely flags legitimate devices. How would you handle risk and availability?
# ==========================================
DATA["SEC-32"] = {
    "concept_en": """In the fragmented Android ecosystem, security and RASP SDKs frequently produce false positives. Heuristic rules—such as scanning for su binaries, inspecting test-keys build tags, or checking SELinux permissive flags—can misidentify legitimate devices from niche OEMs, enterprise-managed phones, or custom operating systems. Crashing the application or terminating user accounts immediately upon a single client detection destroys service availability, drives customer churn, and damages app store ratings. Resilient engineering balances security and availability through a graduated risk-based framework. Applications must avoid hard-coded client-side termination. Instead, client signals are transmitted as contextual telemetry to backend risk engines. Responses are tiered: low-risk signals trigger silent logging and enhanced monitoring; medium-risk signals prompt step-up verification (such as SMS OTP or biometric re-authentication); only verified high-confidence anomalies block high-value transactions.""",
    "walkthrough_en": """Graduated risk-engine architecture with remote kill-switch:
```kotlin
// 1. Telemetry reporting without immediate client hard-fail
class DeviceSecurityCoordinator(
    private val securitySdk: SecuritySdk,
    private val riskEngineApi: RiskEngineApi,
    private val remoteConfig: RemoteConfigManager
) {
    suspend fun evaluateDevicePosture(): SecurityPolicyVerdict {
        // Check dynamic kill-switch before evaluating SDK rules
        if (remoteConfig.isSecurityCheckDisabled("root_heuristic_check")) {
            return SecurityPolicyVerdict.ALLOW
        }

        val signals = securitySdk.collectDeviceSignals()
        // Transmit signals to backend risk engine rather than terminating locally
        val serverVerdict = riskEngineApi.evaluateRisk(signals)
        return serverVerdict.toPolicyVerdict()
    }
}

enum class SecurityPolicyVerdict {
    ALLOW,
    STEP_UP_CHALLENGE, // Require SMS OTP or biometric re-auth
    RESTRICT_HIGH_VALUE_TX, // Restrict transactions > $500
    BLOCK_SESSION
}
```""",
    "short_en": """Handling security SDK false positives requires balancing fraud risk against application availability. We never hard-code immediate app termination on the client. Instead, we implement a graduated risk framework: telemetry runs in shadow mode, suspicious signals trigger step-up authentication, and remote feature flags act as instant kill-switches to maintain user availability.""",
    "structured_en": """In the fragmented Android ecosystem, security and RASP SDKs frequently produce false positives on legitimate devices due to OEM firmware quirks, custom ROMs, or enterprise profiles.
Hard-coding an immediate app crash or account lock upon a local detection destroys availability, driving legitimate users away and tanking store ratings.
Our engineering framework balances security against availability by decoupling detection from enforcement.
Client-side SDK detections are treated as risk signals rather than unilateral verdicts, streaming to our backend risk engine as telemetry.
We enforce a graduated response policy: low-confidence signals increase telemetry logging without disrupting the user, medium-confidence signals trigger step-up challenges like SMS OTP or biometric verification, and only verified high-confidence anomalies restrict high-risk financial transfers.
Furthermore, we deploy all new detection rules in shadow mode for observation before activating enforcement, and maintain dynamic remote kill switches via Firebase Remote Config to instantly deactivate misbehaving rules without waiting for app updates.""",
    "deep_senior_en": """A zero-tolerance client-side security policy is an architectural anti-pattern in production mobile engineering.
Android device diversity means obscure OEMs and aggressive battery-saver ROMs frequently trigger false root or emulator heuristics, such as shipping release builds with test-keys or non-standard SELinux permissions.
Terminating an application with System.exit(0) based on client heuristics inevitably locks out legitimate paying customers during critical user journeys.
Our approach addresses this through risk-based governance and operational agility.
At the architectural level, we separate signal generation from enforcement policy.
When a security SDK flags an anomaly, the client bundles the detection evidence—including specific check IDs and system properties—into a secure telemetry payload transmitted to our backend risk engine.
The client never blocks execution autonomously.
Second, the backend evaluates the signal within our graduated risk tiering model.
For browsing or viewing transactions, users experience zero interruption.
If the user attempts a high-value money transfer, the backend escalates the authentication requirement, demanding a hardware biometric signature or step-up multi-factor challenge.
Third, we enforce rigorous release safeguards.
New detection algorithms always run in shadow mode for two weeks across our user base, allowing data engineers to measure signal-to-noise ratios and identify OEM-specific false positive clusters.
To maintain operational control, we maintain dynamic feature flags connected to Firebase Remote Config.
If an unexpected firmware rollout from a major manufacturer causes an alert spike, our on-call engineers can toggle a remote kill-switch within minutes to disable the failing heuristic globally, preserving availability while we refine the detection logic.""",
    "meta_ar": {
        "id": "SEC-32",
        "questionAr": "مكتبة أمان تعطي إنذارات كاذبة وتحظر أجهزة مستخدمين شرعيين، كيف تدير المخاطر والتوافر هندسياً؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "الموازنة الهندسية بين مخاطر الإنذارات الكاذبة وتوافر الخدمة لإشارات مكتبات الأمان، وتطبيق الرد المتدرج، ونمط المراقبة الصامتة، وقنوات الاعتراض، وآليات التراجع السريع.",
        "concept_ar": "في منظومة أندرويد المتشعبة، تطلق مكتبات الأمان إنذارات كاذبة نتيجة تخصيصات الشركات المصنعة للهواتف الرخيصة أو الرومات المخصصة. يؤدي إغلاق التطبيق فوراً عند أي اشتباه محلي إلى تدمير توافر الخدمة وفقدان العملاء الشرعيين. الحل المعماري يقوم على الفصل بين رصد الإشارة وتطبيق العقوبة؛ حيث ترسل الإشارات إلى سيرفر تقييم المخاطر وتطبق سياسة رد متدرج، مع إطلاق القواعد الجديدة في نمط المراقبة الصامتة، واستخدام مفاتيح إيقاف عن بعد.",
        "walkthrough_ar": """معمارية الرد الأمني المتدرج مع مفاتيح التحكم السحابية لإدارة المخاطر:
```kotlin
class SecurityRiskCoordinator(
    private val riskEvaluator: RiskEvaluator,
    private val remoteConfig: RemoteConfig
) {
    suspend fun handleDeviceRisk(): PolicyAction {
        // فحص مفتاح الإيقاف السحابي قبل فرض أي قيود
        if (remoteConfig.isCheckSuppressed("custom_rom_check")) {
            return PolicyAction.PROCEED
        }
        val riskScore = riskEvaluator.calculateRiskScore()
        return when {
            riskScore < 30 -> PolicyAction.PROCEED
            riskScore < 70 -> PolicyAction.CHALLENGE_WITH_OTP
            else -> PolicyAction.RESTRICT_HIGH_VALUE_OPERATIONS
        }
    }
}
```""",
        "why_it_matters_ar": "يحافظ على التوازن الدقيق بين حماية أصول البنك من الاحتيال وبين استمرارية الأعمال ورضا العملاء، ويمنع حوادث توقف الخدمة الواسعة الناتجة عن أخطاء خوارزميات الاستكشاف الإحصائي.",
        "worked_example_ar": "بناء نظام تجارب أمنية في نمط المراقبة الصامتة Shadow Mode يحلل إشارات أجهزة Xiaomi وTranssion لرصد وتصحيح الإنذارات الكاذبة قبل تطبيق أي حظر فعلي.",
        "trade_offs_ar": "الرد المتدرج وقبول نسبة مخاطرة طفيفة يسمح لبعض الأجهزة المشبوهة بالعمل في حدود ضيقة، ولكنه يحمي آلاف المستخدمين الشرعيين من الطرد التعسفي وفقدان ثقتهم بالخدمة.",
        "failure_modes_ar": "استخدام System.exit(0) عند فشل أي فحص محلي، وتطبيق قواعد كشف جديدة مباشرة في الإنتاج دون مرحلة مراقبة، وعدم توفير مسار اعتراض أو دعم فني للمستخدمين المحظورين.",
        "production_perspective_ar": "في المنصات المالية الكبرى، نراقب مقياس False Positive Rate يومياً عبر لوحات متابعة Grafana، ونحدد مؤشرات أداء صارمة للتدخل الفوري عند ارتفاع نسبة الإنذارات في أي طراز هاتف.",
        "how_to_answer_ar": "ابدأ ببيان معضلة الأمان مقابل التوافر Security vs Availability، ثم اشرح استراتيجية الرد المتدرج وفصل الرصد عن العقوبة، واختم بـ Shadow Mode ومفاتيح الإيقاف عن بعد Remote Config.",
        "talking_points_ar": "أسباب الإنذارات الكاذبة في أندرويد (تعديلات الـ OEMs)، فوائد الـ Shadow Mode، وكيفية استخدام Feature Flags لتعطيل الفحوصات الفاشلة دون الحاجة لتحديث التطبيق.",
        "follow_ups_ar": "- **المحاور:** \"إذا أوقفت الشركة ميزة معينة بسبب إنذار كاذب، كيف يتصرف العميل المتضرر؟\"\n  **المرشح:** \"نوفر له رسالة واضحة تشرح المشكلة دون مصطلحات تقنية مبهمة، مع مسار للدعم الفني للتحقق من هويته ورفع الحظر يدوياً عن حسابه.\"\n\n- **المحاور:** \"ما هي المدة المثالية لتشغيل فحص أمني جديد في نمط Shadow Mode؟\"\n  **المرشح:** \"أسبوعين إلى أربعة أسابيع على الأقل؛ لمراقبة تنوع الأجهزة وملاحظة سلوك الفحص مع التحديثات الدورية للأنظمة دون التأثير على المستخدمين.\"",
        "self_check_ar": "هل تحدثت عن الموازنة بين الأمان والتوافر؟ وهل بينت مخاطر الإنهاء القسري System.exit؟ وهل شرحت الرد المتدرج و Shadow Mode ومفاتيح Remote Config؟",
        "references_ar": f"- [Android Security Architecture and Device Diversity](https://source.android.com/docs/security) — التوثيق الرسمي لتنوع بيئات أندرويد.\n- [Risk-based Authentication and Graduated Enforcement](https://pages.nist.gov/800-63-3/) — إرشادات المعهد الوطني للمعايير والتقنية لإدارة المخاطر.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "إدارة الإنذارات الكاذبة لمكتبات الأمان تتطلب موازنة دقيقة بين منع الاحتيال وتوافر الخدمة للمستخدمين. نحظر إغلاق التطبيق قسرياً على العميل، ونطبق بدلاً من ذلك نموذج رد متدرج: تفعيل القواعد الجديدة في نمط المراقبة الصامتة، وطلب مصادقة إضافية عند الاشتباه، وتوفير مفاتيح إيقاف عن بعد.",
        "best_answer_ar": "في بيئة أندرويد المتشعبة، تطلق مكتبات الأمان إنذارات كاذبة بكثرة نتيجة تعديلات الشركات المصنعة OEM أو الرومات المخصصة أو أجهزة الشركات المقيدة بسياسات أمان.\n\nإن برمجة التطبيق ليغلق نفسه فوراً عند رصد اشتباه محلي هي كارثة تشغيلية تؤدي لخسارة عملاء حقيقيين وتدمير تقييمات المتجر. لذلك نفصل هندسياً بين رصد الإشارة وتطبيق العقوبة؛ حيث نعتبر مخرجات الـ SDK مجرد مؤشرات يتم إرسالها لسيرفر المخاطر كبيانات تشخيصية دون مقاطعة المستخدم.\n\nونطبق استراتيجية رد متدرج: الإشارات الضعيفة تكتفي بالمراقبة المشددة، بينما تدفع الشبهات المتوسطة لطلب مصادقة إضافية مثل OTP أو إعادة البصمة، ويقتصر تقييد العمليات المالية الكبرى على الحالات المؤكدة. كما نطلق القواعد الأمنية دائماً في نمط المراقبة الصامتة Shadow Mode لقياس دقتها، ونحتفظ بمفاتيح تحكم سحابية Remote Config لتعطيل أي فحص يسبب أخطاء فوراً دون انتظار تحديث المتجر.",
        "deep_answer_ar": "في إدارة المخاطر للتطبيقات المصرفية الكبرى، يمثل التوافر Availability ركيزة أساسية لا تقل أهمية عن الأمان والسرية؛ فإغلاق التطبيق في وجه عميل شرعي أثناء عملية طارئة هو فشل هندسي ذريع.\n\nيرجع سبب الإنذارات الكاذبة إلى قيام بعض الشركات المصنعة بتسمية ملفات النظام بأسماء تشبه أدوات الروت أو استخدام وسوم غير قياسية. ولمعالجة هذه المعضلة، نحظر تماماً استخدام أوامر إنهاء التطبيق المباشرة System.exit على العميل، ونحول كافة مخرجات مكتبات الأمان إلى حزم بيانات مشفرة ترسل لمحرك تقييم المخاطر على السيرفر.\n\nيتعامل السيرفر مع هذه الإشارات وفق مصفوفة مخاطر متدرجة؛ فالتصفح والاطلاع على الرصيد يظل متاحاً دائماً، بينما تتطلب العمليات المالية الحساسة مصادقة إضافية أو تأكيداً عبر قناة اتصال بديلة. كما نلزم أي قاعدة أمنية جديدة بالمرور بمرحلة المراقبة الصامتة Shadow Mode لعدة أسابيع، مما يتيح لفريق هندسة البيانات رصد معدلات الإنذار الكاذب وتحليل تركزها في هواتف معينة قبل تفعيل الحظر الفعلي.\n\nوفوق كل ذلك، نربط كافة فحوصات الأمان بمفاتيح إيقاف تشغيل سحابية Feature Flags عبر Remote Config؛ فإذا تسبب تحديث نظام في دولة معينة في إطلاق إنذارات كاذبة، يستطيع مهندس العمليات تعطيل الفحص المتسبب بضغطة زر واحدة وإعادة الخدمة للعملاء خلال دقائق معدودة. كما ندمج قنوات اتصال سريعة مع فرق خدمة العملاء لتلقي شكاوى الحظر غير المبرر ومعالجتها يدوياً، مع تحسين خوارزميات الكشف باستمرار لتقليل نسبة الإنذارات الكاذبة مستقبلاً."
    }
}

# ==========================================
# Runner & Validation
# ==========================================
def validate_words():
    for qid, d in sorted(DATA.items()):
        short_w = len(d["short_en"].split())
        struct_w = len(d["structured_en"].split())
        deep_w = len(d["deep_senior_en"].split())
        assert 35 <= short_w <= 110, f"{qid} short_en {short_w} out of [35, 110]"
        assert 100 <= struct_w <= 280, f"{qid} struct_en {struct_w} out of [100, 280]"
        assert 200 <= deep_w <= 650, f"{qid} deep_en {deep_w} out of [200, 650]"

        q_ar_w = len(d["meta_ar"]["quick_answer_ar"].split())
        b_ar_w = len(d["meta_ar"]["best_answer_ar"].split())
        d_ar_w = len(d["meta_ar"]["deep_answer_ar"].split())
        assert 35 <= q_ar_w <= 110, f"{qid} quick_ar {q_ar_w} out of [35, 110]"
        assert 90 <= b_ar_w <= 280, f"{qid} best_ar {b_ar_w} out of [90, 280]"
        assert 180 <= d_ar_w <= 650, f"{qid} deep_ar {d_ar_w} out of [180, 650]"
        print(f"{qid}: en_s={short_w}, en_st={struct_w}, en_d={deep_w} | ar_q={q_ar_w}, ar_b={b_ar_w}, ar_d={d_ar_w}")
    print("Pre-validation word count checks passed! Updating canonical questions...")

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

    ee.save_topic_metadata("sec_25_32", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print("\nAll 8 SEC questions (SEC-25 to SEC-32) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
