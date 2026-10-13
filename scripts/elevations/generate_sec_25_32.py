#!/usr/bin/env python3
"""Generator for SEC-25 through SEC-32 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sec.json"

SEC_25_32 = [
    {
        "id": "SEC-25",
        "arabic_explanation": (
            "ما هي معايير OWASP MASVS و MASTG، وكيف ترشد المهندسين في مراجعات الأمان واختبار الاختراق لتطبيقات أندرويد؟\n\n"
            "1. ما هو OWASP MASVS (Mobile Application Security Verification Standard)؟\n"
            "   - هو المعيار الصناعي العالمي الموحد لمتطلبات أمان تطبيقات الموبايل.\n   - يقسم متطلبات الأمان إلى 8 مجالات رئيسية:\n     * **MASVS-STORAGE**: أمان تخزين البيانات، تشفير قواعد البيانات، منع التسريب في الـ Logs والـ Backups.\n     * **MASVS-CRYPTO**: استخدام خوارزميات التشفير القياسية (AES-GCM)، توليد المفاتيح في Keystore، حظر الخوارزميات الضعيفة (MD5, SHA1, DES, ECB).\n     * **MASVS-AUTH**: إدارة الجلسات، التوكنز، وحماية المصادقة البيومترية.\n     * **MASVS-NETWORK**: تشفير الاتصالات عبر TLS 1.3، تثبيت الشهادات (Pinning)، وتأمين WebViews.\n     * **MASVS-PLATFORM**: أمان مكونات النظام (Exported components, App Links, PendingIntents).\n     * **MASVS-CODE**: جودة الكود، إعدادات المترجم، وتحديث المكتبات.\n     * **MASVS-RESILIENCE**: مقاومة الهندسة العكسية، فحص الـ Root، وحماية الـ Binary.\n\n"
            "2. مستويات التقييم (Verification Levels):\n   - **MASVS-L1 (Standard Security)**: المتطلبات الأساسية لجميع التطبيقات (حماية البيانات، HTTPS، منع الـ Logs غير الآمنة).\n   - **MASVS-L2 (Defense-in-Depth)**: مخصص للتطبيقات الحساسة (Fintech, Banking, Healthcare) ويتطلب تشفيراً عتادياً و Play Integrity.\n   - **MASVS-R (Resilience)**: متطلبات إضافية لمقاومة الهندسة العكسية والـ Tampering.\n\n"
            "3. ما هو OWASP MASTG (Mobile Application Security Testing Guide)؟\n   - هو الدليل العملي لاختبار كل بند في الـ MASVS، ويحتوي على أوامر الاختبار العملية وأكواد Frida وأدوات الفحص (MobSF, apktool, jadx) للتأكد من استيفاء المتطلبات."
        ),
        "practical_walkthrough": (
            "تطبيق قائمة فحص (Checklist) برمجية مستوحاة من OWASP MASVS-L2 أثناء الـ Code Review:\n"
            "```kotlin\n"
            "// فحص برمجي مستوحى من MASVS-STORAGE و MASVS-CRYPTO:\n"
            "object SecurityReviewChecklist {\n"
            "    // 1. MASVS-STORAGE: التأكد من عدم استخدام Plaintext SharedPreferences للأسرار\n"
            "    fun auditStorage(sharedPrefsName: String, context: Context): Boolean {\n"
            "        val prefsFile = File(context.filesDir.parent, \"shared_prefs/$sharedPrefsName.xml\")\n"
            "        // فحص الملف للتأكد من خلوه من أي كلمات مرور أو مفاتيح صريحة\n"
            "        val content = prefsFile.readText()\n"
            "        val hasExposedTokens = content.contains(\"token\") || content.contains(\"password\")\n"
            "        return !hasExposedTokens\n"
            "    }\n"
            "\n"
            "    // 2. MASVS-CRYPTO: التحقق من رفض خوارزميات التشفير الممنوعة أمنياً\n"
            "    fun validateCipherTransformation(transformation: String) {\n"
            "        val forbidden = listOf(\"DES\", \"ECB\", \"MD5\", \"RC4\")\n"
            "        if (forbidden.any { transformation.contains(it, ignoreCase = true) }) {\n"
            "            throw SecurityException(\"MASVS-CRYPTO Violation: Insecure cipher $transformation is strictly forbidden!\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "OWASP MASVS defines the security standard across storage, crypto, network, platform, and resilience tiers, evaluated at L1 (baseline), L2 (defense-in-depth for fintech), and R (tamper resistance). MASTG provides practical testing guides, test cases, and penetration testing tools to verify each requirement.",
        "best_answer": (
            "OWASP MASVS and MASTG serve as the authoritative security verification framework for modern mobile engineering:\n\n"
            "1. **MASVS (Specification)**: Defines actionable requirements organized across core security domains:\n"
            "   - **MASVS-STORAGE**: Sensitive data at rest, cache clearing, backup exclusion, keyboard cache suppression.\n   - **MASVS-CRYPTO**: Hardware-backed keys, AES-GCM, cryptographically secure PRNGs, eliminating broken primitives.\n   - **MASVS-NETWORK**: Modern TLS configuration, certificate pinning, WebView network boundary hardening.\n   - **MASVS-PLATFORM**: Restricting exported components, validating deep links, and securing IPC.\n   - **MASVS-RESILIENCE**: Anti-tampering, integrity verification, and root/instrumentation mitigations.\n\n"
            "2. **Security Levels**:\n"
            "   - **MASVS-L1**: Baseline hygiene required for any commercial application.\n   - **MASVS-L2**: Deep defense-in-depth mandatory for fintech, banking, and healthcare applications.\n   - **MASVS-R**: Optional resilience layer providing client hardening against dynamic reverse engineering.\n\n"
            "3. **MASTG (Testing Guide)**: Provides concrete white-box source code audits, dynamic runtime analysis scripts (Frida), and static tooling (MobSF, JADX) to verify compliance against every MASVS control."
        ),
        "deep_answer": (
            "From an architectural governance perspective, senior engineers operationalize MASVS/MASTG throughout the software development lifecycle:\n\n"
            "1. **Threat Modeling & Architecture Phase**: Map every new feature against MASVS controls during design. If a feature introduces biometric authentication, align directly with `MASVS-AUTH` and `MASVS-CRYPTO` by mandating hardware-bound `CryptoObject` patterns.\n\n"
            "2. **Automated CI/CD Verification**: Embed automated compliance gates into CI pipelines using tools like MobSF CLI, Android Lint with custom security rules, and Semgrep scanning for cryptographic misconfigurations (e.g. hardcoded IVs, `allowBackup=true`, or `FLAG_MUTABLE` PendingIntents).\n\n"
            "3. **Vendor & Penetration Testing Alignment**: Use MASTG test identifiers (e.g. `MASTG-TEST-0001`) as the contract benchmark for third-party penetration testing audits, ensuring repeatable, evidence-based security verification rather than subjective vendor opinions."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between MASVS-L1 and MASVS-L2?",
                "answer": "L1 focuses on standard mobile data hygiene and best practices; L2 enforces advanced threat defense, including hardware-backed cryptographic attestation, strict zeroization, and multi-factor authorization."
            },
            {
                "question": "Does achieving MASVS-R guarantee an app cannot be hacked?",
                "answer": "No; MASVS-R raises the economic and time cost for reverse engineers, but client execution on a hostile device can never be mathematically guaranteed secure."
            }
        ]
    },
    {
        "id": "SEC-26",
        "arabic_explanation": (
            "كيف تصمم بنية تخزين الجلسات (Session Storage) لتطبيق بنكي (Fintech) يعمل على جهاز يُفترض أنه مخترق أو خاضع لسيطرة المهاجم؟\n\n"
            "1. فرضية التهديد (Hostile Device Threat Model):\n"
            "   - نفترض أن الجهاز معمول له Root، ويحتوي على أدوات مراقبة (Frida, Magisk)، ومساحة الذاكرة والقرص مكشوفة للمهاجم.\n   - **الاستنتاج المعماري**: لا يمكن الاعتماد على أمان الهاتف بنسبة 100%؛ الأمان يجب أن ينبع من تقليص نافذة الخطر والتحقق السيرفري المشدد.\n\n"
            "2. ركائز التصميم المعماري للجلسة الآمنة:\n   - **Access Token قصير العمر في الـ RAM فقط**: مدة صلاحيته 5 دقائق. لا يُكتب على القرص أبداً لتقليص خطر استخراجه.\n   - **Refresh Token مشفر عتادياً**: يُشفر بمفتاح AES-GCM من Android Keystore مدعوم بشريحة StrongBox/TEE. يُحفظ مشفراً في DataStore داخل مجلد `noBackupFilesDir`.\n   - **العمليات المالية الحساسة محمية بـ CryptoObject بيومتري**: تحويل الأموال يتطلب توقيع المعاملة بمفتاح Keystore لا يفتح إلا ببصمة حية جديدة.\n   - **Cryptographic Request Signing (DPoP / Asymmetric Signature)**: في كل طلب، يوقع التطبيق المعاملة بمفتاح خاص (Private Key) موجود في الـ Keystore. حتى لو سرق المهاجم الـ Token من الشبكة، لا يستطيع استخدامه بدون المفتاح الخاص المحبوس داخل عتاد الهاتف!\n   - **Auto-Logout & Memory Purge**: عند وضع التطبيق في الخلفية لمدة دقيقتين، يتم مسح الـ Access Token ومصفوفات الذاكرة فوراً."
        ),
        "practical_walkthrough": (
            "تصميم مستودع جلسة بنكية آمن مع إدارة الذاكرة والتشفير العتادي والمسح التلقائي عند الخلفية:\n"
            "```kotlin\n"
            "class SecureFintechSessionManager(\n"
            "    private val keystoreStorage: KeystoreSecretStorage,\n"
            "    private val sessionDataStore: DataStore<Preferences>\n"
            ") : DefaultLifecycleObserver {\n"
            "    // 1. الـ Access Token يعيش في الذاكرة فقط (RAM) ويُصفر برمجياً:\n"
            "    @Volatile private var inMemoryAccessToken: String? = null\n"
            "    private var backgroundTimestamp: Long = 0\n"
            "    private val SESSION_TIMEOUT_MS = 2 * 60 * 1000L // دقيقتان كحد أقصى في الخلفية\n"
            "\n"
            "    fun updateSession(accessToken: String, refreshToken: String) {\n"
            "        inMemoryAccessToken = accessToken\n"
            "        // 2. الـ Refresh Token يُشفر عتادياً بالـ Keystore ويُخزن في DataStore\n"
            "        val encryptedRefresh = keystoreStorage.encrypt(refreshToken.toByteArray(Charsets.UTF_8))\n"
            "        CoroutineScope(Dispatchers.IO).launch {\n"
            "            sessionDataStore.edit { it[stringPreferencesKey(\"enc_refresh\")] = Base64.encodeToString(encryptedRefresh, Base64.NO_WRAP) }\n"
            "        }\n"
            "    }\n"
            "\n"
            "    override fun onStop(owner: LifecycleOwner) {\n"
            "        backgroundTimestamp = System.currentTimeMillis()\n"
            "    }\n"
            "\n"
            "    override fun onStart(owner: LifecycleOwner) {\n"
            "        if (backgroundTimestamp > 0 && (System.currentTimeMillis() - backgroundTimestamp) > SESSION_TIMEOUT_MS) {\n"
            "            // 3. انتهاء مدة الجلسة؛ مسح الذاكرة وتوجيه المستخدم لتسجيل الدخول\n"
            "            purgeSessionMemory()\n"
            "        }\n"
            "    }\n"
            "\n"
            "    fun purgeSessionMemory() {\n"
            "        inMemoryAccessToken = null\n"
            "        backgroundTimestamp = 0\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design secure session storage on hostile devices by keeping short-lived access tokens strictly in RAM, storing refresh tokens encrypted via Android Keystore AES-GCM in noBackupFilesDir, signing requests with hardware-bound asymmetric keys (DPoP), and deterministically zeroing in-memory tokens upon a 2-minute background timeout.",
        "best_answer": (
            "Designing fintech session storage on potentially compromised devices assumes a zero-trust posture toward the client OS:\n\n"
            "1. **In-Memory Short-Lived Access Tokens**: Retain access tokens exclusively in volatile RAM with brief 5-minute lifetimes. Never persist access tokens to disk. If the process is killed or backgrounded past timeout, the token vanishes naturally.\n\n"
            "2. **Hardware-Bound Refresh Token Storage**: Persist the long-lived refresh token encrypted with a 256-bit AES-GCM key backed by Android Keystore and StrongBox Keymaster. Store the ciphertext inside `context.noBackupFilesDir` to prevent extraction via adb or cloud backups.\n\n"
            "3. **Demonstrating Proof-of-Possession (DPoP)**: Bind the session to an asymmetric EC keypair generated inside Keystore. For critical API calls, the client signs a payload containing the current timestamp, request URI, and server nonce with the hardware-locked private key. Intercepting the bearer token alone is useless to an attacker because they cannot forge the hardware signature.\n\n"
            "4. **Lifecycle-Aware Background Eviction**: Monitor app foreground/background lifecycle. After 120 seconds in the background, aggressively purge all memory pointers and cached session states, forcing biometric or passcode re-authentication on resume."
        ),
        "deep_answer": (
            "From an end-to-end security architecture viewpoint, fintech resilience depends on continuous risk telemetry and backend orchestration:\n\n"
            "1. **Server-Side Session Invalidation**: The server maintains a distributed state table tracking device fingerprint hashes, IP geographic velocity, and integrity verdicts. If a refresh request originates from an anomalous ASN or fails Play Integrity attestation, the server immediately revokes the token family and pushes a silent FCM wake-up to terminate the local session.\n\n"
            "2. **Step-Up Authentication Gates**: High-value transactions (e.g. transfers over $1,000) are never authorized solely by existing session tokens. They require just-in-time biometric unlocking using a `CryptoObject`-bound Keystore key paired with a server-issued one-time transaction nonce.\n\n"
            "3. **Anti-Screen-Scraping**: The host Activity enforces `FLAG_SECURE` to prevent accessibility-based overlays, screen recording, and task preview dumping from capturing session states while the app is transitioning."
        ),
        "follow_ups": [
            {
                "question": "What is DPoP and how does it prevent token replay?",
                "answer": "DPoP (Demonstrating Proof-of-Possession) binds access tokens to a client's private key; each request includes a JWT signed by that key, making stolen tokens non-reusable without the hardware private key."
            },
            {
                "question": "Why should session tokens never be stored in static variables across Application subclasses?",
                "answer": "Static references persist across Activity lifecycles without automatic garbage collection, extending the attack window for heap inspection."
            }
        ]
    },
    {
        "id": "SEC-27",
        "arabic_explanation": (
            "مهاجم قام بتعديل الـ APK وتجاوز جميع الفحوصات الأمنية المحلية (Client-Side Checks). كيف يجب على الـ Backend حماية نفسه؟\n\n"
            "1. وهم الأمان من جانب العميل (The Fallacy of Client-Only Validation):\n"
            "   - أي فحص محلي يتم داخل كود أندرويد (مثل فحص الأسعار، فحص الرصيد، فحص الكوبونات، أو فحص الـ Root) يمكن لمهاجم تجاوزه بسهولة بتعديل سطر Smali واحد أو استخدام Frida.\n   - **القاعدة الذهبية في هندسة الأمان**: **Never Trust the Client** (لا تثق في العميل أبداً؛ العميل هو بيئة معادية ومخترقة افتراضياً).\n\n"
            "2. كيف يدافع الـ Backend عن نفسه بشكل قطعي؟\n   - **إعادة حساب كل العمليات المنطقية على السيرفر**: السيرفر لا يستقبل \"السعر النهائي\" من التطبيق! يستقبل فقط معرّف المنتج (`productId`) والكمية، ويقوم السيرفر بجلب السعر من قاعدة البيانات وحساب الخصم والضرائب بنفسه.\n   - **التحقق من توقيع التطبيق وسلامته عبر Play Integrity API**: يرسل السيرفر Nonce عشوائي، ويطلب من التطبيق شهادة Play Integrity. السيرفر يتحقق من Google أن الطلب قادم من APK أصلي موقع بشهادة الإنتاج ولم يتم التلاعب بملف الـ DEX.\n   - **فحص الصلاحيات والـ RBAC على السيرفر**: كل API Endpoint تفحص هل الـ User ID المستخرج من الـ Token المصادق عليه يملك صلاحية الوصول لهذا المورد أم لا.\n   - **كشف الشذوذ السلوكي (Behavioral Anomaly Detection)**: مراقبة سرعة الطلبات (Rate Limiting)، وفحص الموقع الجغرافي المستحيل (Impossible Travel)، وحظر الحسابات التي ترسل طلبات غير متناسقة."
        ),
        "practical_walkthrough": (
            "المقارنة بين API معيب يثق في العميل و API مؤمن يفرض سلطة السيرفر المطلقة:\n"
            "```kotlin\n"
            "// ❌ تصميم كارثي: السيرفر يثق في حسابات العميل ومدخلاته الحساسة:\n"
            "// إذا عدل المهاجم الكود وجعل totalAmount = 0.01$، السيرفر سيقبل العملية!\n"
            "data class InsecureCheckoutRequest(\n"
            "    val productId: String,\n"
            "    val totalAmount: Double, // ثغرة: العميل يحدد المبلغ!\n"
            "    val isDiscountApplied: Boolean // ثغرة: العميل يحدد الخصم!\n"
            ")\n"
            "\n"
            "// ✅ المعمارية الاحترافية: السيرفر هو مصدر الحقيقة الأوحد ولا يثق في العميل:\n"
            "data class SecureCheckoutRequest(\n"
            "    val productId: String,\n"
            "    val quantity: Int,\n"
            "    val promoCode: String?,\n"
            "    val clientNonce: String\n"
            ")\n"
            "\n"
            "// منطق السيرفر (Backend Logic):\n"
            "// 1. استخراج userId من الـ Cryptographically Verified JWT Token\n"
            "// 2. جلب سعر المنتج الحقيقي من الـ Database\n"
            "// 3. التحقق من صلاحية الكوبون ومطابقته للشروط في السيرفر\n"
            "// 4. فحص الـ Nonce لمنع هجمات التكرار (Replay Attacks)\n"
            "// 5. التحقق من شهادة Play Integrity المرفقة في هيدر الطلب\n"
            "```"
        ),
        "quick_answer": "The backend must enforce a Zero-Trust architecture: never trust client-calculated prices, roles, or checks. Recalculate business invariants entirely on the server, validate Google-signed Play Integrity attestation tokens bound to server nonces, enforce strict rate limiting, and use cryptographic transaction signing.",
        "best_answer": (
            "When an attacker tampers with an APK to bypass client validations, backend security controls form the true line of defense:\n\n"
            "1. **Server Authoritative Business Logic**: \n"
            "   - Clients submit intentions (e.g. `productId`, `quantity`), never outcomes (e.g. `price`, `discountedTotal`). The server looks up product costs in authoritative databases, computes taxes and discounts, and initiates charges based solely on its own calculations.\n\n"
            "2. **Cryptographic Attestation Verification**:\n"
            "   - The backend validates the Google Play Integrity token provided with critical requests. The server verifies Google's cryptographic signature, checking that `appRecognitionVerdict` equals `PLAY_RECOGNIZED` and the signing certificate SHA-256 matches the official release keystore. Modified/repackaged APKs will return `UNRECOGNIZED_VERSION`.\n\n"
            "3. **Idempotency & Replay Protection**:\n"
            "   - Critical requests require a server-issued one-time cryptographically random nonce or UUID idempotency key stored in Redis with short TTL. Replayed requests are rejected.\n\n"
            "4. **Strict Server-Side Authorization (RBAC/ABAC)**:\n"
            "   - Every request verifies that the authenticated user identity extracted from the verified session token has explicit permission to access the target entity ID (preventing IDOR vulnerabilities)."
        ),
        "deep_answer": (
            "From an enterprise fraud and threat modeling perspective, backend defenses incorporate multi-signal behavioral analytics:\n\n"
            "1. **Behavioral Fraud Scoring**: Even if an attacker successfully patches an APK and mimics API payloads, machine learning fraud engines analyze request velocity, header entropy, TLS client fingerprinting (JA3/JA4 signatures), and impossible geographic travel intervals to score transaction risk.\n\n"
            "2. **Step-Up Authentication Challenges**: When risk signals indicate an anomalous client environment, the backend refuses to execute the requested action directly. Instead, it challenges the client with step-up verification (e.g., FIDO2 / Passkey biometric challenge or out-of-band push notification to a trusted secondary device).\n\n"
            "3. **Tarpitting and Honeypots**: Backend APIs can embed decoy parameters or obscure endpoints. Modified clients invoking hidden deprecated endpoints expose automated tampering tools, triggering silent shadow-banning without alerting the attacker."
        ),
        "follow_ups": [
            {
                "question": "What is an IDOR vulnerability and how does server-side auth prevent it?",
                "answer": "Insecure Direct Object Reference occurs when a client changes an ID parameter (e.g., /account/123 -> /account/124); server-side auth validates that the token's user owns that specific ID."
            },
            {
                "question": "What is TLS JA3 fingerprinting?",
                "answer": "It analyzes the client's TLS ClientHello packet (ciphers, extensions, curves) to identify the underlying HTTP client library, detecting automated python/curl bots masquerading as official Android apps."
            }
        ]
    },
    {
        "id": "SEC-28",
        "arabic_explanation": (
            "انتهت صلاحية شهادة TLS المثبتة (Pinned Certificate) في التطبيق. كيف تقوم بتدوير الـ Pins وحل المشكلة دون تعطيل التطبيق (Bricking)؟\n\n"
            "1. سيناريو الكارثة:\n"
            "   - تطبيق مثبت لدى ملايين المستخدمين يحتوي على Certificate Pinning لشهادة انتهت صلاحيتها، أو اضطر السيرفر لتغييرها فجأة.\n   - النتيجة: كل مستخدم يفتح التطبيق يواجه خطأ `SSLPeerUnverifiedException`، وتفشل كل الاتصالات بالكامل!\n   - لا يستطيع التطبيق حتى الاتصال بالسيرفر لمعرفة الـ Pin الجديد!\n\n"
            "2. خطوات الإنقاذ الفوري (Disaster Recovery Operations):\n   - **السيناريو الأفضل: استخدام نفس الـ Key Pair**: إذا كان التطبيق يثبت الـ Public Key (SPKI Pinning) وليس ملف الشهادة، يمكن لفريق السيرفر إصدار شهادة جديدة تماماً بنفس المفتاح الخاص الأصلي (CSR)! في هذه الحالة، تستمر كل التطبيقات في العمل فوراً بدون أي مشكلة!\n   - **تفعيل المفتاح الاحتياطي (Backup Pin)**: إذا كانت المعمارية تحتوي على Backup Pin في الكود، يقوم فريق البنية التحتية بنشر الشهادة الاحتياطية على خوادم الـ Load Balancer فوراً.\n   - **انتهاء الصلاحية المبرمج في Network Security Config**: إذا كان ملف `network_security_config.xml` يحتوي على تاريخ انتهاء (`expiration=\"YYYY-MM-DD\"`)، فإن النظام يتوقف تلقائياً عن فرض الـ Pinning بعد ذلك التاريخ ويعود للتحقق عبر الـ CAs الطبيعية.\n\n"
            "3. إذا كان التطبيق معطلاً بالكامل ولا يوجد مفتاح احتياطي:\n   - **التواصل عبر قنوات بديلة**: إرسال إشعار FCM فوري للمستخدمين (خوادم FCM تتبع Google ولا تتأثر بالـ Pinning الخاص بتطبيقك) لإبلاغهم بضرورة تحديث التطبيق.\n   - **إطلاق تحديث طارئ (Emergency Hotfix Release)** على Google Play مع رفع نسبة التوزيع إلى 100% وتفعيل ميزة In-App Update فور استعادة الاتصال."
        ),
        "practical_walkthrough": (
            "استراتيجية معالجة أخطاء الـ Pinning وتوفير دومين احتياطي (Fallback Domain) للإنعاش:\n"
            "```kotlin\n"
            "class ResilientNetworkClient {\n"
            "    // 1. عميل الشبكة الأساسي المزود بـ Certificate Pinning الصارم:\n"
            "    val primaryClient: OkHttpClient = OkHttpClient.Builder()\n"
            "        .certificatePinner(\n"
            "            CertificatePinner.Builder()\n"
            "                .add(\"api.example.com\", \"sha256/PRIMARY_KEY_HASH=\")\n"
            "                .add(\"api.example.com\", \"sha256/BACKUP_KEY_HASH=\") // مفتاح احتياطي للطوارئ\n"
            "                .build()\n"
            "        )\n"
            "        .build()\n"
            "\n"
            "    // 2. دومين طوارئ مستقل ومعزول (Disaster Recovery Endpoint) لا يعتمد على الـ Pinning:\n"
            "    // يُستخدم فقط عند فشل الـ Pinning لجلب توجيهات التحديث أو إظهار شاشة Force Update\n"
            "    val disasterRecoveryClient: OkHttpClient = OkHttpClient.Builder()\n"
            "        .connectTimeout(10, TimeUnit.SECONDS)\n"
            "        .build()\n"
            "\n"
            "    suspend fun executeSafeRequest(request: Request): Response {\n"
            "        return try {\n"
            "            primaryClient.newCall(request).execute()\n"
            "        } catch (e: SSLPeerUnverifiedException) {\n"
            "            // فشل التحقق من الشهادة! التحقق من دومين الطوارئ هل هناك تحديث إجباري للشهادات؟\n"
            "            handlePinningFailure(e)\n"
            "            throw e\n"
            "        }\n"
            "    }\n"
            "\n"
            "    private fun handlePinningFailure(e: SSLPeerUnverifiedException) {\n"
            "        // تسجيل تقرير الحادث في الـ Telemetry وإظهار واجهة للمستخدم بضرورة التحديث\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "If SPKI pinning was used, immediately re-issue the server certificate using the original private key to restore connectivity without app updates. If backup pins exist, activate the backup certificate on the server. If pinned via network_security_config with an expiration attribute, pinning auto-expires. Otherwise, push an emergency Google Play hotfix and notify users via FCM.",
        "best_answer": (
            "Recovering from an expired or mismatched TLS pin requires a prioritized recovery playbook:\n\n"
            "1. **Re-issue Certificate with Identical SPKI**: If the app pinned the Subject Public Key Info (SPKI SHA-256 hash)—which is industry best practice—the ops team can immediately re-issue a fresh TLS certificate signed by any CA using the original private key CSR. Because the public key remains unchanged, client pins match instantly with zero app updates required.\n\n"
            "2. **Activate Backup Keys on Load Balancers**: If the private key was lost or compromised, deploy the pre-generated offline backup certificate to production servers. Because resilient pinning architectures embed at least one backup pin, apps connect seamlessly.\n\n"
            "3. **Rely on Network Security Config Expiration**: If configured via Android's `<pin-set expiration=\"...\">`, the OS automatically disables pin enforcement once the expiration date passes, falling back to trusted system CAs.\n\n"
            "4. **Emergency App Hotfix & FCM Broadcast**: If the app is bricked without backup keys, deploy an expedited hotfix APK removing the dead pin via Google Play Console with Priority Review. Send high-priority Firebase Cloud Messages (FCM)—which route over Google's unaffected servers—to notify active clients to update."
        ),
        "deep_answer": (
            "From an infrastructure resilience perspective, senior architects design proactive safeguards to eliminate certificate bricking risks entirely:\n\n"
            "1. **Dual-Pin Policy Enforcement in CI/CD**: Implement CI build linters that fail APK generation if fewer than two distinct pin hashes are defined for any production domain in `network_security_config.xml` or `CertificatePinner`.\n\n"
            "2. **Intermediate CA Pinning Strategy**: Instead of pinning volatile leaf public keys, pin the public keys of the organization's dedicated Intermediate Certificate Authorities. This allows the backend team to rotate leaf certificates weekly without modifying client pins, while retaining defense against rogue public CAs.\n\n"
            "3. **Dedicated Unpinned Configuration Subdomains**: Maintain an isolated, unpinned fallback subdomain (e.g., `status.example.com`) purely relying on standard system CA trust. If all pinned endpoints fail with `SSLPeerUnverifiedException`, the app queries this endpoint to display a user-friendly 'Maintenance / Update Required' screen rather than crashing with unhandled network exceptions."
        ),
        "follow_ups": [
            {
                "question": "Why does FCM still work when an app's API is bricked by certificate pinning?",
                "answer": "FCM maintains its own persistent TCP socket connection directly to Google Play Services servers, completely independent of the application's OkHttp client or network configuration."
            },
            {
                "question": "What is the primary trade-off of pinning an Intermediate CA rather than a Leaf Certificate?",
                "answer": "Intermediate pinning allows seamless leaf rotations on the server, but marginally lowers security because any certificate issued by that intermediate is accepted."
            }
        ]
    },
    {
        "id": "SEC-29",
        "arabic_explanation": (
            "جهاز معمول له Root ويستطيع المهاجم عمل Hooking لكود التطبيق عبر Frida. ما هي الحمايات التي تساعد، وما الذي لا يمكن ضمانه إطلاقاً؟\n\n"
            "1. ماذا يستطيع المهاجم فعله عبر Frida على جهاز Rooted؟\n   - حقن كود JavaScript في ذاكرة التطبيق، اعتراض دوال Java/Kotlin/Native، تعديل قيم المتغيرات في الـ Registers، قراءة الـ Keys في الـ RAM، وجعل أي دالة أمنية تعيد `true` دائماً (مثل تجاوز فحص الـ Root أو الـ SSL Pinning).\n\n"
            "2. الحمايات التي تساعد وترفع تكلفة الهجوم (Helpful Mitigations):\n   - **التشفير المقفل عتادياً (Hardware-Gated Keystore & StrongBox)**: لا يمكن لـ Frida إجبار شريحة الـ Secure Element على فك تشفير البيانات إلا بوجود بصمة حقيقية؛ هو يستطيع عمل Hook للـ Callback البرمجي لكنه لا يستطيع تزوير إشارة العتاد!\n   - **Play Integrity API مع التحقق السيرفري**: السيرفر يتأكد من شهادة Google الموقعة رقمياً؛ المهاجم لا يستطيع تزوير توقيع Google السيرفري.\n   - **فحوصات RASP المتعددة في Native Code**: فحص منافذ Frida الافتراضية (Port 27042)، فحص خرائط الذاكرة `/proc/self/maps` بحثاً عن `frida-agent.so`، واستخدام `ptrace` لمنع الـ Debugging.\n\n"
            "3. ما الذي لا يمكن ضمانه إطلاقاً؟ (What Cannot Be Guaranteed):\n   - **لا يمكن ضمان سلامة أي كود يعمل على العميل بنسبة 100%**: المهاجم يملك الجهاز ونواة النظام (Kernel). يستطيع إعادة تجميع Frida بأسماء منافذ عشوائية وحذف أسماء الـ Symbols، واستخدام أدوات مثل Magisk Zygisk/Shamiko لإخفاء الـ Root كلياً عن الـ Sandbox.\n   - **أي شرط برمجي محلي يمكن تجاوزه** إذا كان المهاجم يملك وقتاً وخبرة كافية."
        ),
        "practical_walkthrough": (
            "تنفيذ فحص لوجود Frida والتحقق من حماية الذاكرة عبر Native/Kotlin كطبقة دفاعية أولية:\n"
            "```kotlin\n"
            "object FridaDetectionHeuristics {\n"
            "    // 1. فحص خرائط الذاكرة بحثاً عن مكتبات Frida المحقونة في الـ Process:\n"
            "    fun isFridaInMemory(): Boolean {\n"
            "        return try {\n"
            "            val mapsFile = File(\"/proc/self/maps\")\n"
            "            mapsFile.useLines { lines ->\n"
            "                lines.any { line ->\n"
            "                    line.contains(\"frida-agent\", ignoreCase = true) ||\n"
            "                    line.contains(\"gadget.so\", ignoreCase = true) ||\n"
            "                    line.contains(\"xposed\", ignoreCase = true)\n"
            "                }\n"
            "            }\n"
            "        } catch (e: Exception) {\n"
            "            false\n"
            "        }\n"
            "    }\n"
            "\n"
            "    // 2. فحص المنافذ الافتراضية لخادم Frida المحلي:\n"
            "    fun isFridaServerListening(): Boolean {\n"
            "        return try {\n"
            "            val socket = Socket()\n"
            "            socket.connect(InetSocketAddress(\"127.0.0.1\", 27042), 200)\n"
            "            socket.close()\n"
            "            true // الخادم قيد الاستماع!\n"
            "        } catch (e: Exception) {\n"
            "            false\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Frida can hook methods, patch returns, and inspect RAM. Helpful mitigations include hardware-backed Keystore crypto, server-verified Play Integrity verdicts, and multi-layered RASP heuristics. However, no client-side check can guarantee security on a rooted device against a skilled reverse engineer.",
        "best_answer": (
            "Root access and dynamic instrumentation frameworks like Frida alter the threat landscape by breaking process boundaries:\n\n"
            "1. **Attacker Capabilities with Frida**: An attacker injects code into the runtime via `ptrace` or `frida-gadget`. They can hook any Java/Kotlin method, bypass SSL pinning by intercepting `TrustManager`, replace return values (e.g. forcing `isRooted()` to return `false`), and log plaintext arguments passing through cryptographic methods.\n\n"
            "2. **Protections That Help (Defense in Depth)**:\n"
            "   - **Hardware-Enforced Cryptography**: Android Keystore with StrongBox/TEE. Even if Frida hooks the app's `onAuthenticationSucceeded()` UI callback, hardware key release cannot be simulated in software.\n   - **Server-Side Play Integrity**: Verified on the backend with dynamic nonces; an attacker cannot forge Google's cryptographic attestation signature.\n   - **RASP Heuristics**: Scanning `/proc/self/maps` for injected libraries (`frida-agent.so`), scanning default TCP ports (27042), and checking `/proc/self/status` for debugging tracers.\n\n"
            "3. **What Cannot Be Guaranteed**: You cannot guarantee code integrity on a hostile device. Dedicated attackers can rename Frida binaries, change TCP ports, inject via custom kernel modules, and patch client detection routines out of existence."
        ),
        "deep_answer": (
            "From an adversarial modeling perspective, senior engineers view client RASP protections purely as friction mechanisms rather than security guarantees:\n\n"
            "1. **The Cat-and-Mouse Game of RASP**: Client-side root and Frida detections filter out script kiddies and commodity automated botnets. However, advanced adversaries employ Zygisk modules (such as Shamiko) that unmount root traces and intercept syscalls before the app's process even begins executing, rendering standard `/proc` or `su` file checks blind.\n\n"
            "2. **Asymmetric Economic Advantage**: The defensive team must protect every potential entry point, whereas the attacker only needs to locate and hook the single critical decision branch. Therefore, relying on client-side kill-switches is dangerous.\n\n"
            "3. **Holistic Backend Defense**: The proper response to rooted devices is risk-based authorization on the backend. When risk indicators suggest a rooted or instrumented environment, the backend restricts high-risk actions (wire transfers, crypto withdrawals) while permitting low-risk browsing, backed by anomaly detection and transaction velocity rules."
        ),
        "follow_ups": [
            {
                "question": "What is Frida Gadget?",
                "answer": "A shared library (.so) patched directly into an APK's lib folder, allowing Frida instrumentation on non-rooted devices without needing a background frida-server."
            },
            {
                "question": "How can Frida hook methods in Kotlin that are marked internal or private?",
                "answer": "Frida operates at runtime using ART reflection and direct memory method table patching, ignoring all compile-time Kotlin visibility modifiers."
            }
        ]
    },
    {
        "id": "SEC-30",
        "arabic_explanation": (
            "تطبيق مدفوعات إلكترونية (Payment App) ملزم بقواعد PCI-DSS ويجب أن يخفي أرقام البطاقات (PAN) ويمنع طباعة البيانات الحساسة في السجلات. كيف تصمم سياسة Logging ومراقبة محكمة؟\n\n"
            "1. متطلبات PCI-DSS الصارمة للتعامل مع بيانات الدفع:\n   - **رقم الحساب الأساسي (PAN - Primary Account Number)**: يجب إخفاء أرقامه (Masking) عند العرض أو التسجيل؛ يُسمح فقط بعرض أول 6 أرقام (BIN) وآخر 4 أرقام كحد أقصى (مثل `4111 11** **** 1111`).\n   - **البيانات الحساسة المحظورة قطعياً (Sensitive Authentication Data - SAD)**: يُمنع منعاً باتاً تخزين أو طباعة رمز الأمان (CVV/CVC)، أو رقم الـ PIN، أو بيانات الشريط المغناطيسي (Track 2) بعد إتمام تفويض العملية تحت أي ظرف!\n\n"
            "2. بنية الـ Logging الآمنة في التطبيق:\n   - **تعطيل سجلات الـ Logcat في الـ Release**: استخدام R8 لحذف استدعاءات `Log.*` بالكامل.\n   - **Sanitizing Interceptor في OkHttp**: اعتراض ومعالجة الـ JSON Request/Response Bodies واستبدال أي حقل يحمل اسم `pan`, `cardNumber`, `cvv`, `password` بـ `[REDACTED]`.\n   - **Crashlytics Scrubbing**: فحص جميع الـ Breadcrumbs وتقارير الـ Crash وتصفيتها قبل إرسالها إلى Firebase أو Sentry.\n   - **قواعد الـ CI Linter**: بناء Custom Lint Rule تفحص الكود وتفشل الـ Build إذا قام مطور بكتابة كود يطبع متغيراً باسم `pan` أو `cvv`."
        ),
        "practical_walkthrough": (
            "تنفيذ OkHttp Masking Interceptor و دوال مسك الـ PAN المتوافقة مع PCI-DSS:\n"
            "```kotlin\n"
            "object PaymentMaskingUtil {\n"
            "    // 1. دالة إخفاء أرقام البطاقات المتوافقة مع PCI-DSS:\n"
            "    fun maskPan(pan: String): String {\n"
            "        val clean = pan.replace(\" \", \"\").replace(\"-\", \"\")\n"
            "        if (clean.length < 10) return \"*\" * clean.length\n"
            "        val first6 = clean.take(6)\n"
            "        val last4 = clean.takeLast(4)\n"
            "        val maskedMiddle = \"*\".repeat(clean.length - 10)\n"
            "        return \"$first6$maskedMiddle$last4\"\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. OkHttp Interceptor لتطهير السجلات ومنع تسريب بيانات البطاقات:\n"
            "class PciCompliantLoggingInterceptor : Interceptor {\n"
            "    private val sensitivePatterns = listOf(\n"
            "        Regex(\"\\\"cvv\\\"\\\\s*:\\\\s*\\\"[^\\\"]+\\\"\") to \"\\\"cvv\\\": \\\"***\\\"\",\n"
            "        Regex(\"\\\"cardNumber\\\"\\\\s*:\\\\s*\\\"(\\\\d{6})\\\\d+(\\\\d{4})\\\"\") to \"\\\"cardNumber\\\": \\\"$1******$2\\\"\"\n"
            "    )\n"
            "\n"
            "    override fun intercept(chain: Interceptor.Chain): Response {\n"
            "        val request = chain.request()\n"
            "        if (BuildConfig.DEBUG) {\n"
            "            // تطهير الـ URL والهيدرز قبل الطباعة\n"
            "            val sanitizedUrl = request.url.toString().replace(Regex(\"token=[^&]+\"), \"token=REDACTED\")\n"
            "            // تسجيل الـ URL الآمن فقط\n"
            "        }\n"
            "        return chain.proceed(request)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design a PCI-DSS compliant logging policy by masking PANs to display only the first 6 and last 4 digits, strictly prohibiting CVV/PIN logging, stripping all Logcat output in release builds via R8, deploying sanitizing HTTP interceptors that scrub card fields, and filtering crash reporting breadcrumbs before dispatch.",
        "best_answer": (
            "A PCI-DSS compliant observability policy on Android requires strict controls across the data ingestion and transmission pipeline:\n\n"
            "1. **PCI-DSS Masking Requirements**:\n"
            "   - **PAN (Primary Account Number)**: Display at most the first 6 (BIN) and last 4 digits (e.g. `411111******1111`). All intermediate digits must be obscured.\n   - **SAD (Sensitive Authentication Data)**: CVV/CVC, full magnetic stripe data, and PIN blocks must **never** be logged, cached on disk, or retained post-authorization under any circumstances.\n\n"
            "2. **Network Interceptor Sanitation**:\n"
            "   - Configure custom OkHttp interceptors that parse JSON payloads before logging. Apply regex filters replacing `cvv`, `cardNumber`, and `pin` fields with `[REDACTED]`. Set `HttpLoggingInterceptor.Level.NONE` in release variants.\n\n"
            "3. **Crash Reporting and Analytics Sanitization**:\n"
            "   - Implement a Crashlytics/Sentry `BeforeSendCallback`. Programmatically scrub event messages, stack traces, and breadcrumb trails for 13-19 digit sequences matching the Luhn algorithm.\n\n"
            "4. **Build-Time Enforcement**:\n"
            "   - Enforce ProGuard/R8 `-assumenosideeffects` rules to strip standard `android.util.Log` invocations from release binaries entirely."
        ),
        "deep_answer": (
            "Senior engineers treat compliance not as a documentation exercise, but as an automated architectural boundary:\n\n"
            "1. **Custom Android Lint Rules in CI**: Implement a custom AST-based Android Lint check that flags any invocation of `Log.*`, `Timber.*`, or `println()` accepting parameters containing substrings like `pan`, `card`, `cvv`, `expiry`, or `token`. Fail CI pipelines on lint warnings.\n\n"
            "2. **Card Tokenization (Hosted Fields / SDKs)**: The most effective security pattern is ensuring the mobile application never touches raw PAN or CVV at all. Integrate direct payment processor SDKs (e.g., Stripe, Adyen, Braintree) where credit card inputs are rendered inside isolated tokenization iframes or encrypted SDK views that return an ephemeral single-use token directly from the processor's PCI-certified servers.\n\n"
            "3. **Memory Scrubber Verifications**: Ensure custom credit card input fields in Compose or Views wipe the underlying character buffers immediately after tokenization is completed, preventing memory dump leakage during audit inspections."
        ),
        "follow_ups": [
            {
                "question": "What is the Luhn Algorithm?",
                "answer": "A checksum formula (modulus 10) used to validate credit card numbers; logging scrubbers use it to distinguish real card numbers from random digits."
            },
            {
                "question": "Can an app be PCI-DSS compliant if it logs masked PAN numbers?",
                "answer": "Yes; PCI-DSS allows logging and displaying masked PANs (first 6, last 4), provided Sensitive Authentication Data like CVV is never logged."
            }
        ]
    },
    {
        "id": "SEC-31",
        "arabic_explanation": (
            "فريق برمجي يضع مفتاح الـ API الخاص (Private API Key) في ملف `local.properties` ويقرأه داخل `BuildConfig`. لماذا يُعد هذا غير كافٍ وثغرة أمنية فادحة؟\n\n"
            "1. ما الذي يفعله `local.properties` وما الذي لا يفعله؟\n   - وضع المفتاح في `local.properties` يمنع رفعه إلى مستودع الـ Git (GitHub/GitLab) إذا كان الملف مستثنى في `.gitignore`. هذا إجراء تنظيمي جيد لحماية الـ Git History فقط.\n   - **لكن**: عند قراءة المفتاح وتمريره إلى `buildConfigField`, يقوم Gradle بتوليد كلاس جافا اسمه `BuildConfig.java` يحتوي على سطر صريح:\n     `public static final String STRIPE_SECRET = \"sk_live_1234567890\";`.\n\n"
            "2. كيف يتم استخراج هذا المفتاح من الـ APK في 5 ثوانٍ؟\n   - عند تجميع الـ APK، يُترجم كلاس `BuildConfig` إلى Dalvik Bytecode داخل `classes.dex`.\n   - يستطيع أي شخص تنزيل الـ APK من المتجر وتنفيذ أمر سطر واحد في الـ Terminal:\n     `strings classes.dex | grep sk_live`\n     أو فتح الـ APK في `JADX-GUI` وقراءة المفتاح بنصه الصريح فوراً!\n\n"
            "3. الفرق بين المفاتيح العامة (Public Keys) والمفاتيح الخاصة (Private Secrets):\n   - **المفاتيح العامة (Allowed on Client)**: مفاتيح مثل Google Maps API Key أو Firebase Public Key. هذه المفاتيح مخصصة لتعريف التطبيق ومحمية من جهة Google Console بقيود الباكدج والبصمة الرقمية (Package Name + SHA-1 Restriction).\n   - **المفاتيح الخاصة (Strictly Forbidden on Client)**: مفاتيح مثل OpenAI Secret Key, Stripe Secret Key, AWS S3 Master Credentials. هذه المفاتيح **ممنوع تماماً وضعها في أي تطبيق موبايل**! يجب أن تظل حصرياً على خادم الـ Backend (BFF - Backend for Frontend)، ويقوم الموبايل بالاتصال بالسيرفر الخاص بك والسيرفر هو من يتصل بتلك الخدمات."
        ),
        "practical_walkthrough": (
            "المقارنة بين الطريقة الساذجة المكشوفة في الـ APK والمعمارية الصحيحة باستخدام Backend for Frontend:\n"
            "```groovy\n"
            "// ❌ ثغرة أمنية فادحة في build.gradle: توليد المفتاح الخاص في كود الـ APK:\n"
            "android {\n"
            "    defaultConfig {\n"
            "        // يتم تضمين هذا المفتاح كنص صريح في ملف DEX ويمكن استخراجه في ثوانٍ!\n"
            "        buildConfigField \"String\", \"OPENAI_SECRET_KEY\", \"\\\"sk-proj-998877665544332211\\\"\"\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "```kotlin\n"
            "// ✅ المعمارية الصحيحة: العميل لا يملك المفتاح السري، بل يتصل بـ Backend Proxy:\n"
            "class AiAssistantRepository(\n"
            "    private val companyBackendApi: CompanyBackendApi\n"
            ") {\n"
            "    suspend fun generateSummary(userPrompt: String): String {\n"
            "        // التطبيق يرسل الطلب لسيرفر شركتك موثقاً بـ User Session Token:\n"
            "        val response = companyBackendApi.requestAiSummary(\n"
            "            prompt = userPrompt\n"
            "        )\n"
            "        // سيرفر شركتك (الـ Backend) هو من يحتفظ بـ OPENAI_SECRET_KEY في بيئة آمنة\n"
            "        // ويتحقق من رصيد المستخدم وصلاحياته قبل استدعاء OpenAI API\n"
            "        return response.summary\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Putting keys in local.properties keeps them out of git, but defining them in BuildConfig bakes them into classes.dex as plaintext strings. Anyone can extract them in seconds via JADX or strings CLI. Private secrets must never exist on mobile clients; they belong exclusively on an authoritative backend proxy.",
        "best_answer": (
            "Using `local.properties` with `BuildConfig` addresses version control hygiene, but offers zero cryptographic confidentiality against reverse engineering:\n\n"
            "1. **Compilation into Plaintext DEX**: Gradle generates a Java constant in `BuildConfig.java` (`public static final String API_KEY = \"...\";`). During compilation, this string constant is placed directly into the `classes.dex` string pool. Anyone who downloads the APK can run `strings classes.dex` or inspect `BuildConfig` in JADX to extract the secret immediately.\n\n"
            "2. **Public vs. Private API Keys**:\n"
            "   - **Public Client Keys**: Identifiers like Google Maps keys or Firebase App IDs are designed to be public. They rely on server-side restrictions (e.g. Google Cloud package name + SHA-1 fingerprint whitelisting) rather than secrecy.\n   - **Private Secrets**: Keys providing privileged administrative access, billing capabilities, or third-party paid API quotas (OpenAI, Stripe Secret, AWS IAM credentials) must **never** be packaged into a mobile application.\n\n"
            "3. **Architectural Remedy (Backend-for-Frontend)**:\n"
            "   - Deploy a backend proxy / BFF. The mobile client authenticates against your backend using short-lived user session tokens. Your backend holds the private API secret securely in environment variables or an enterprise secret manager and proxies requests to third-party providers."
        ),
        "deep_answer": (
            "From a threat modeling perspective, understanding client-side secret exposure reveals common misconceptions:\n\n"
            "1. **The Native C/C++ Illusion**: Some teams attempt to bypass this by moving the string into a C++ JNI library (`libkeys.so`) or breaking the string into byte arrays combined with XOR masks. These are merely obfuscation speed bumps. An analyst running Frida or Ghidra can locate the assembly instructions and extract the recombined string from memory during execution in minutes.\n\n"
            "2. **Credential Stuffing & Quota Exhaustion**: When third-party private secrets are leaked from an APK, attackers scrape them to make automated API requests on the developer's billing account or exfiltrate private database records, causing massive financial and reputational liability.\n\n"
            "3. **Rule of Thumb for Mobile Architects**: Treat any code and asset shipped inside an APK as publicly published on the internet. If exposing a key compromises customer data, financial balances, or cloud infrastructure, that key must never be compiled into the mobile build."
        ),
        "follow_ups": [
            {
                "question": "Why is Google Maps API key safe to keep in AndroidManifest.xml?",
                "answer": "Because Google Maps APIs restrict usage by verifying the calling app's package name and SHA-1 signing certificate fingerprint on Google servers."
            },
            {
                "question": "Can R8 obfuscation hide BuildConfig strings?",
                "answer": "No; R8 renames class and variable identifiers, but literal string constants remain completely unencrypted in the DEX string pool."
            }
        ]
    },
    {
        "id": "SEC-32",
        "arabic_explanation": (
            "مكتبة أمان (Security / RASP SDK) تعطي إنذارات كاذبة (False Positives) وتحظر أجهزة مستخدمين شرعيين. كيف تدير المخاطر والتوافر (Availability) هندسياً؟\n\n"
            "1. معضلة الأمان مقابل التوافر (Security vs. Availability Trade-off):\n"
            "   - مكتبات كشف الـ Root والـ Emulators تعتمد غالباً على Heuristics استكشافية (مثل فحص أسماء ملفات معينة، أو فحص خصائص `Build.FINGERPRINT`).\n   - في عالم أندرويد المتشعب، تقوم بعض الشركات المصنعة للهواتف الرخيصة (OEMs) أو الرومات المخصصة الشرعية بتسمية ملفات النظام بأسماء تشبه الـ Root أو استخدام Build tags غير قياسية، مما يجعل الـ SDK يعتقد أن الجهاز مخترق!\n   - إذا كان التطبيق مبرمجاً ليغلق نفسه فوراً (Hard Fail / Crash)، ستفقد آلاف العملاء الحقيقيين وتتلقى تقييمات كارثية على متجر التطبيقات.\n\n"
            "2. الحلول الهندسية وإدارة المخاطر (Risk-Based Approach):\n   - **التدرج في رد الفعل (Graduated Risk Response)**: بدلاً من الحظر الكلي، يتم تصنيف الخطر:\n     * خطر منخفض/غير مؤكد: السماح باستخدام التطبيق مع تسجيل Telemetry وتكثيف المراقبة السيرفرية.\n     * خطر متوسط: طلب خطوة تحقق إضافية (Step-up Authentication مثل SMS OTP أو Email confirmation).\n     * خطر عالي مؤكد (Debuggers, Hooking نشط أثناء عملية دفع): تجميد العملية المالية فقط مع رسالة واضحة للمستخدم.\n   - **التحكم عن بُعد عبر الـ Feature Flags**: إمكانية تعطيل أو تخفيف قواعد الـ SDK فورياً من السيرفر بدون الحاجة لإطلاق تحديث جديد للتطبيق.\n   - **مراقبة معدل الإنذارات الكاذبة (False Positive Rate Alerting)**: تتبع نسبة الحظر؛ إذا تجاوزت النسبة 0.5% من المستخدمين، يتم إطلاق إنذار هندسي فوري للتحقيق في المشكلة."
        ),
        "practical_walkthrough": (
            "تنفيذ نظام تقييم مخاطر متدرج ومدار عبر الـ Remote Config لمنع حظر المستخدمين الشرعيين:\n"
            "```kotlin\n"
            "enum class SecurityAction {\n"
            "    ALLOW,              // تشغيل طبيعي\n"
            "    STEP_UP_AUTH,       // طلب تأكيد إضافي (OTP / Biometric)\n"
            "    RESTRICT_PAYMENT,   // تعطيل المدفوعات فقط مع إتاحة باقي التطبيق\n"
            "    BLOCK_SESSION       // حظر كامل فقط للحالات القصوى المؤكدة\n"
            "}\n"
            "\n"
            "class RiskEngine(\n"
            "    private val remoteConfig: RemoteConfigRepository,\n"
            "    private val telemetryLogger: SecurityTelemetryLogger\n"
            ") {\n"
            "    fun evaluateRisk(securitySdkScore: Int, detectedSignals: List<String>): SecurityAction {\n"
            "        // 1. فحص هل تم تفعيل وضع الطوارئ لتجاوز الـ SDK بسبب إنذارات كاذبة؟\n"
            "        if (remoteConfig.isSecurityKillSwitchActive()) {\n"
            "            telemetryLogger.logWarning(\"Security SDK bypassed via remote kill-switch\")\n"
            "            return SecurityAction.ALLOW\n"
            "        }\n"
            "\n"
            "        // 2. تسجيل الإشارات للتحليل دون إغلاق التطبيق فوراً:\n"
            "        telemetryLogger.logSignals(detectedSignals)\n"
            "\n"
            "        // 3. التدرج في اتخاذ القرار بناءً على مستوى الخطر:\n"
            "        return when {\n"
            "            detectedSignals.contains(\"FRIDA_HOOK_ACTIVE\") -> SecurityAction.BLOCK_SESSION\n"
            "            detectedSignals.contains(\"CUSTOM_ROM_SUSPECTED\") -> SecurityAction.STEP_UP_AUTH\n"
            "            securitySdkScore > remoteConfig.getRiskThreshold() -> SecurityAction.RESTRICT_PAYMENT\n"
            "            else -> SecurityAction.ALLOW\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Manage security SDK false positives by implementing a graduated, risk-based response ladder rather than binary app termination. Use remote feature flags as emergency kill-switches to toggle aggressive rules, enforce step-up authentication instead of outright bans, and monitor false positive metrics continuously in production.",
        "best_answer": (
            "Balancing application availability with security enforcement requires a risk-scoring architecture rather than hardcoded binary kill-switches:\n\n"
            "1. **The False Positive Dilemma**: Third-party RASP SDKs rely on heuristics like checking for test keys or custom build tags. Across fragmented Android OEM ecosystems (e.g. customized budget devices in emerging markets), legitimate vendor ROMs trigger false detections, causing widespread user lockouts.\n\n"
            "2. **Graduated Response Ladder**:\n"
            "   - **Informational**: Low-confidence anomalies (e.g. unknown device build) trigger client telemetry logging without disrupting user UX.\n   - **Step-Up Verification**: Suspicious environments (e.g. unlocked bootloader) require stepped-up authentication (e.g., SMS OTP, passkey verification, or email confirmation).\n   - **Scoped Feature Restriction**: Moderate risks restrict sensitive operations (e.g., initiating high-value transfers) while leaving non-sensitive areas (viewing transaction history, support chat) fully operational.\n   - **Session Termination**: Reserved exclusively for high-confidence active tampering (e.g. Frida memory hooks detected during transaction signing).\n\n"
            "3. **Dynamic Remote Governance**: Wrap security SDK evaluation inside server-driven feature flags (e.g., Firebase Remote Config). If an SDK update causes false-positive lockouts, ops can remotely dial back detection sensitivity in minutes without waiting for Play Store updates."
        ),
        "deep_answer": (
            "From an operational reliability perspective, senior architects treat security SDKs as untrusted third-party dependencies requiring observability SLAs:\n\n"
            "1. **False Positive Telemetry & Alerting**: Track the 'Security Block Rate' metric in real-time dashboards. If blocks spike above a statistical baseline (e.g., jumping from 0.05% to 2.0% post-app update), automated alerts fire immediately to investigate OEM-specific clusters.\n\n"
            "2. **Silent Shadow-Mode Deployment**: When evaluating or upgrading a security SDK, deploy it first in 'Observation / Shadow Mode' for 2–4 weeks. Log what the SDK *would* have blocked without executing the block action, allowing the team to measure actual false-positive rates across millions of production devices before enabling enforcement.\n\n"
            "3. **Customer Support Recovery Channels**: Provide clear, non-technical error codes (e.g. `ERR-SEC-402`) in the UI when restrictions occur, enabling tier-1 customer support agents to look up backend risk logs and grant temporary device exemptions if legitimate customers are affected."
        ),
        "follow_ups": [
            {
                "question": "What is Shadow Mode in security SDK rollout?",
                "answer": "Running the security SDK purely to log telemetry and flagged risk scores without executing any blocking actions, verifying false-positive rates before hard enforcement."
            },
            {
                "question": "Why should security error dialogs avoid exposing internal detection details to users?",
                "answer": "Detailed error messages (e.g. 'su binary found in /system/xbin') guide attackers on exactly which file or hook triggered detection, simplifying evasion."
            }
        ]
    }
]


def update_sec_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in SEC_25_32:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions SEC-25 to SEC-32. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_sec_data()
