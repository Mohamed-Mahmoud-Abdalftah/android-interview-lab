#!/usr/bin/env python3
"""Generator for SEC-09 through SEC-16 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "sec.json"

SEC_09_16 = [
    {
        "id": "SEC-09",
        "arabic_explanation": (
            "ما هو الـ Obfuscation (التشويش البرمجي) عبر R8/ProGuard، وما هي حدوده الحقيقية التي يجب على كل Senior فهمها؟\n\n"
            "1. كيف يعمل الـ Obfuscation في أندرويد؟\n"
            "   - أداة R8 (التي حلت محل ProGuard) تقوم بثلاث مهام رئيسية: **Shrinking** (حذف الكود والموارد غير المستخدمة)، **Optimization** (دمج الدوال وInlining)، و**Obfuscation** (إعادة تسمية الكلاسات والدوال والمتغيرات إلى أسماء مبهمة وقصيرة مثل `a`, `b`, `c`).\n"
            "   - الهدف الأساسي هو جعل الكود المُفكك (Decompiled Bytecode عبر أدوات مثل JADX) صعب القراءة والفهم على المهاجمين، وتقليص حجم الـ DEX النهائي.\n\n"
            "2. ما الذي لا يستطيع R8 إخفاؤه؟ (The Hard Limitations):\n"
            "   - **النصوص الصريحة (Hardcoded Strings)**: أسماء الـ API Endpoints، مفاتيح التشفير، الـ Shared Preferences keys، ومسارات الـ URLs تظل واضحة تماماً بنصها الأصلي (Plaintext) داخل ملف الـ DEX! يمكن استخراجها بأمر واحد: `strings classes.dex | grep api`.\n"
            "   - **استدعاءات الـ Android Framework و SDKs المشهورة**: استدعاءات مثل `Retrofit`, `OkHttpClient`, `RoomDatabase`, أو `Cipher.getInstance()` لا يتم تشويش أسمائها لأنها مكتبات عامة. المهاجم يستطيع تتبع مسار البيانات بسهولة من نقطة إرسال الطلب في الشبكة إلى نقطة حفظها في قاعدة البيانات.\n"
            "   - **هيكل التدفق المنطقي (Control Flow)**: رغم تغير أسماء الدوال، فإن المنطق البرمجي (Conditional checks, loops, business logic) يظل قابلاً للتحليل العكسي (Reverse Engineering).\n\n"
            "3. القاعدة الذهبية:\n"
            "   - الـ Obfuscation هو **Security through Obscurity**؛ هو يرفع تكلفة ووقت الهندسة العكسية ولكنه **ليس تشفيراً ولا يمنع الاختراق** أبداً."
        ),
        "practical_walkthrough": (
            "إعداد قواعد R8 وتجنب كسر Reflection والتحذير من تخزين الأسرار داخل الكود:\n"
            "```kotlin\n"
            "// ❌ كارثة أمنية: الاعتماد على Obfuscation لحماية Secret Key أو API Key في الكود:\n"
            "class ApiConfig {\n"
            "    companion object {\n"
            "        // حتى لو R8 شوش اسم الكلاس إلى a.b، النص \"sk_live_99887766\" سيظل نصاً صريحاً في الـ DEX!\n"
            "        const val STRIPE_SECRET_KEY = \"sk_live_99887766554433221100\"\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ المعمارية السليمة: إخفاء المسارات وحماية نماذج البيانات مع تصدير mapping.txt:\n"
            "// في ملف proguard-rules.pro:\n"
            "// 1. تشويش أسماء الكلاسات والدوال دون كسر نماذج السيريالايزيشن:\n"
            "-keepattributes *Annotation*,Signature,InnerClasses,EnclosingMethod\n"
            "\n"
            "// 2. حماية كلاسات الـ DTO المعتمدة على Reflection / Moshi / Kotlinx Serialization:\n"
            "@Keep\n"
            "data class PaymentResponse(\n"
            "    val transactionId: String,\n"
            "    val status: String\n"
            ")\n"
            "\n"
            "// 3. حذف استدعاءات الـ Logging تماماً أثناء عملية الـ Optimization:\n"
            "-assumenosideeffects class android.util.Log {\n"
            "    public static boolean isLoggable(java.lang.String, int);\n"
            "    public static int v(...);\n"
            "    public static int d(...);\n"
            "    public static int i(...);\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Obfuscation via R8 renames classes, fields, and methods to meaningless symbols to increase the cognitive cost of reverse engineering and reduce DEX size. However, it is security through obscurity: hardcoded strings, framework API calls, and logic flow remain fully exposed in decompiled bytecode. It slows attackers down, but does not secure secrets.",
        "best_answer": (
            "Obfuscation transforms compiled DEX bytecode into structurally equivalent code that is difficult for human analysts and automated decompilers to decipher:\n\n"
            "1. **What R8 Obfuscation Does**: It mangles human-readable identifiers into short non-descriptive names (`a`, `b.c()`), inlines short methods, and removes unused metadata. This shrinks application footprint and disrupts automated decompilation signatures.\n\n"
            "2. **Critical Limitations**: \n"
            "   - **String Literals Are Not Encrypted**: Strings like base URLs, cryptographic algorithms, or accidentally embedded API tokens reside in plain ASCII/UTF-8 within the DEX string pool. Running `strings classes.dex` reveals them instantly.\n"
            "   - **External Framework APIs Remain Identifiable**: Calls to standard Android or third-party classes (`Cipher.getInstance`, `Retrofit`, `SharedPreferences`) cannot be renamed because they bind to external runtimes. Attackers simply trace data flow into these known API sinks.\n"
            "   - **Control Flow Preserved**: Tools like JADX and Ghidra reconstruct control flow graphs accurately regardless of class names.\n\n"
            "Obfuscation raises the effort barrier for casual tampering, but any secret baked into client bytecode is compromised by definition."
        ),
        "deep_answer": (
            "From an application hardening perspective, senior engineers differentiate between basic identifier renaming, control flow flattening, and actual cryptographic security:\n\n"
            "1. **Renaming vs. Advanced Protection**: Standard R8 only performs symbol renaming, dead code elimination, and method inlining. Advanced commercial tools (e.g. DexGuard) add control flow flattening (inserting synthetic branches and opaque predicates), string encryption, and native code hiding. However, even encrypted strings must be decrypted in memory at runtime, leaving them vulnerable to dynamic memory inspection.\n\n"
            "2. **Production Deobfuscation Management**: Obfuscation complicates production crash triage. CI/CD must archive and upload the cryptographic `mapping.txt` matching the exact build version code to crash reporting services (Firebase Crashlytics, Sentry) to deobfuscate stack traces.\n\n"
            "3. **Architectural Posture**: We treat the mobile client as a completely hostile environment. Obfuscation is applied as a baseline hygiene measure alongside R8 optimizations, but zero architectural trust relies on it. Confidential business logic, key management, and authorization policies belong exclusively on the backend."
        ),
        "follow_ups": [
            {
                "question": "What happens if you accidentally keep `@Keep` on too many classes?",
                "answer": "You bloat DEX size, prevent R8 optimizations like dead code elimination and inlining, and make those parts of the codebase trivial to read in decompiled APKs."
            },
            {
                "question": "How do you deobfuscate a production crash trace locally if Crashlytics fails to map it?",
                "answer": "Using the `retrace` CLI tool bundled with Android command-line tools: `retrace mapping.txt obfuscated_trace.txt`."
            }
        ]
    },
    {
        "id": "SEC-10",
        "arabic_explanation": (
            "ما هي الهندسة العكسية (Reverse Engineering) لتطبيقات أندرويد؟ وما الذي يغيره وجود Root، الـ Hooking، والـ Dynamic Instrumentation؟\n\n"
            "1. كيف تتم الهندسة العكسية عملياً؟\n"
            "   - **Static Analysis (التحليل الساكن)**: تفكيك الـ APK بواسطة أدوات مثل `apktool` لاستخراج ملفات الموارد و`smali` bytecode، أو استخدام `JADX-GUI` لإعادة بناء كود Java/Kotlin شبه كامل وقراءة منطق التطبيق بدون تشغيله.\n"
            "   - **Dynamic Analysis (التحليل الديناميكي)**: تشغيل التطبيق في بيئة مراقبة واعتراض اتصالات الشبكة عبر بروكسي (Burp Suite, Charles) وقراءة استدعاءات الدوال أثناء تنفيذها في الذاكرة.\n\n"
            "2. ما الذي يغيره الـ Root؟\n"
            "   - يلغي حواجز أمان نظام Linux (UID Isolation) بالكامل. يصبح للمهاجم صلاحيات `root` (UID 0)، مما يمكنه من:\n"
            "     * قراءة وتعديل ملفات الـ Sandbox الداخلية (`/data/data/<package>/`).\n"
            "     * تفريغ ذاكرة الرام الخاصة بالتطبيق (`/proc/<pid>/mem`).\n"
            "     * تنصيب شهادات CA مزيفة في مخزن شهادات النظام الموثوقة (System Trust Store) لتجاوز قيود فحص الشهادات.\n\n"
            "3. ما هو الـ Hooking والـ Dynamic Instrumentation (Frida / Xposed)؟\n"
            "   - أدوات مثل **Frida** تحقن JavaScript engine داخل عملية التطبيق قيد التشغيل وتعدل مؤشرات الدوال في الذاكرة (Memory Hooking).\n"
            "   - يمكن للمهاجم عبر سطرين كود Frida تغيير نتيجة أي دالة أمنية في التطبيق! مثل جعل دالة `isRooted()` أو `checkBiometric()` تعيد `true` دائماً، أو تعطيل الـ SSL Pinning في لحظة استدعائه."
        ),
        "practical_walkthrough": (
            "فهم كيف يعطل المهاجم فحص الـ Root عبر Frida وكيف نصمم دفاعات متعددة الطبقات (Defense in Depth):\n"
            "```kotlin\n"
            "// ❌ فحص أمني هش يسهل تجاوزه بسطر كود Frida واحد:\n"
            "class WeakSecurityCheck {\n"
            "    // المهاجم يستخدم Frida: Java.use('com.example.WeakSecurityCheck').isDeviceSecure.implementation = function() { return true; };\n"
            "    fun isDeviceSecure(): Boolean {\n"
            "        return !isRooted() && !isEmulator()\n"
            "    }\n"
            "}\n"
            "\n"
            "// ✅ معمارية أمنية صلبة: الدفاع في العمق وتفويض قرار الثقة للسيرفر (Zero Trust Client):\n"
            "class ResilientSecurityManager(\n"
            "    private val playIntegrityRepository: PlayIntegrityRepository,\n"
            "    private val backendAuthApi: BackendAuthApi\n"
            ") {\n"
            "    // 1. الفحوصات المحلية لا تتخذ قرارات حاسمة بمفردها؛ فقط تُرسل إشارات مؤشرات خطر (Risk Signals)\n"
            "    fun collectLocalTelemetry(): SecurityTelemetry {\n"
            "        return SecurityTelemetry(\n"
            "            hasSuBinary = checkSuFiles(),\n"
            "            testKeysDetected = Build.TAGS?.contains(\"test-keys\") == true,\n"
            "            fridaPortOpen = checkFridaDefaultPort()\n"
            "        )\n"
            "    }\n"
            "\n"
            "    // 2. التحقق الحقيقي يتم عبر شهادة موقعة عتادياً ومفحوصة على السيرفر:\n"
            "    suspend fun verifyAndAuthorizeSession(nonce: String): AuthorizationResult {\n"
            "        // الحصول على Integrity Token مشفر وموقع رقمياً من Google Play Servers\n"
            "        val integrityToken = playIntegrityRepository.requestToken(nonce)\n"
            "        \n"
            "        // إرسال الـ Token للسيرفر لفك تشفيره والتحقق من سلامة الباكدج والتوقيع وعتاد الهاتف\n"
            "        return backendAuthApi.verifyAppIntegrity(integrityToken)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Reverse engineering involves inspecting static bytecode via tools like JADX and dynamic behavior at runtime. Root access breaks Linux UID isolation, giving attackers raw file and memory access. Dynamic instrumentation frameworks like Frida inject code into the running process to hook methods, alter return values, and bypass local security checks in real time.",
        "best_answer": (
            "Reverse engineering in Android spans static analysis, dynamic analysis, and runtime manipulation:\n\n"
            "1. **Static Analysis & Tooling**: Attackers disassemble APKs using `apktool` into Smali intermediate representation, or use `JADX` to decompile classes into Java. They can patch code (e.g. flipping boolean checks in Smali), reassemble the APK with `apktool b`, and re-sign it with a debug key.\n\n"
            "2. **Impact of Root Access**: Root (UID 0) removes Linux discretionary access controls. The attacker gains unrestricted read/write access to app-private storage (`/data/data/<package>/`), can dump heap memory, attach gdb/lldb debuggers, and push user-installed CA certificates into the system trust store.\n\n"
            "3. **Hooking and Dynamic Instrumentation (Frida/Xposed)**: Frameworks like Frida inject a JavaScript engine into the target process by attaching via `ptrace` or native library loading. They rewrite function entry points in memory (VMT hooking / inline hooks). An attacker can intercept parameters, read decrypted data passing through crypto APIs, and force methods like `verifyCertificate()` or `isRooted()` to return success without modifying the on-disk APK.\n\n"
            "Consequently, client-side tampering detections are merely speed bumps; backend verification is mandatory."
        ),
        "deep_answer": (
            "When analyzing threat vectors involving root and instrumentation, senior engineers model the attack lifecycle under the assumption that client execution cannot be fully trusted:\n\n"
            "1. **Anti-Tampering & RASP Limitations**: Runtime Application Self-Protection (RASP) mechanisms detect `su` binaries, test-keys, Frida listener ports (e.g. 27042), or `/proc/self/maps` memory modifications. While useful against automated script kiddies, an experienced reverse engineer running custom Frida builds with renamed native symbols and kernel-level Magisk hide modules (e.g., Zygisk/Shamiko) bypasses all client-only heuristics.\n\n"
            "2. **Hardware & Cryptographic Attestation**: To combat runtime hooking, we leverage hardware-backed attestation via the Play Integrity API and hardware-backed Keystore keys (`KeyGenParameterSpec` with user authentication or attestation challenge). An attacker hooking client methods cannot forge Google's cryptographic server signature on an integrity verdict.\n\n"
            "3. **Zero-Trust Backend Architecture**: The backend treats all incoming payloads as untrusted input. It enforces short token lifetimes, strict replay protection via nonces, behavioral anomaly detection, and cryptographic signing of critical business transactions."
        ),
        "follow_ups": [
            {
                "question": "Can Frida hook native C/C++ libraries loaded via JNI?",
                "answer": "Yes, Frida can intercept functions in ELF `.so` libraries using `Interceptor.attach(Module.findExportByName('libnative.so', 'func'), ...)` and inspect register values."
            },
            {
                "question": "How does Magisk/Zygisk hide root from detection libraries?",
                "answer": "It hooks Zygote process creation to unmount root-related filesystems and filter out root files from mount namespaces for targeted package names before the app process forks."
            }
        ]
    },
    {
        "id": "SEC-11",
        "arabic_explanation": (
            "كيف تقوم بتنفيذ تشفير مدعوم عتادياً بالـ Keystore لتخزين أسرار التطبيق الصغيرة (App Secrets) بشكل آمن؟\n\n"
            "1. ما هي خوارزمية التشفير القياسية الموصى بها؟\n"
            "   - **AES/GCM/NoPadding (Galois/Counter Mode)**: هي خوارزمية تشفير متماثل توفر **Authenticated Encryption with Associated Data (AEAD)**. هذا يعني أنها لا تكتفي بتشفير البيانات (Confidentiality) فقط، بل تولد أيضاً **Authentication Tag** يحمي من أي تلاعب أو تعديل في النص المشفر (Integrity & Authenticity).\n   - في حال حاول المهاجم تعديل حتى بايت واحد في البيانات المشفرة، تفشل عملية فك التشفير برمي استثناء `AEADBadTagException` فوراً.\n\n"
            "2. دور الـ Android Keystore:\n"
            "   - يُولد مفتاح AES-256 داخل الـ Keystore ولا يخرج منه أبداً (`PURPOSE_ENCRYPT or PURPOSE_DECRYPT`).\n   - التطبيق يستخدم اسم المفتاح (Alias) فقط لتوجيه أوامر التشفير وفك التشفير للنظام.\n\n"
            "3. إدارة متجه البدء (Initialization Vector - IV):\n"
            "   - تتطلب خوارزمية GCM متجه بدء (IV) فريداً تماماً لكل عملية تشفير (عادة 12 بايت).\n   - **قاعدة حرجة**: لا تقم أبداً بإعادة استخدام نفس الـ IV مع نفس المفتاح، لأن ذلك يدمر أمان خوارزمية GCM بالكامل!\n   - يُترك لـ `Cipher.init(Cipher.ENCRYPT_MODE, secretKey)` توليد IV عشوائي جديد تلقائياً في كل مرة، ويتم حفظ هذا الـ IV بجانب النص المشفر (مثلاً بدمجهما معاً في نفس المصفوفة) لأن الـ IV ليس سراً."
        ),
        "practical_walkthrough": (
            "تطبيق احترافي لتشفير وفك تشفير البيانات الصغيرة باستخدام Android Keystore و AES-256-GCM:\n"
            "```kotlin\n"
            "class KeystoreSecretStorage {\n"
            "    private val KEY_ALIAS = \"app_auth_secret_v1\"\n"
            "    private val ANDROID_KEYSTORE = \"AndroidKeyStore\"\n"
            "    private val TRANSFORMATION = \"AES/GCM/NoPadding\"\n"
            "    private val GCM_TAG_LENGTH_BITS = 128\n"
            "    private val IV_SIZE_BYTES = 12\n"
            "\n"
            "    private fun getOrCreateKey(): SecretKey {\n"
            "        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }\n"
            "        if (keyStore.containsAlias(KEY_ALIAS)) {\n"
            "            return (keyStore.getEntry(KEY_ALIAS, null) as KeyStore.SecretKeyEntry).secretKey\n"
            "        }\n"
            "        val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE)\n"
            "        val spec = KeyGenParameterSpec.Builder(KEY_ALIAS, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)\n"
            "            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)\n"
            "            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)\n"
            "            .setKeySize(256)\n"
            "            .setRandomizedEncryptionRequired(true) // يجبر النظام على رفض IV مكرر\n"
            "            .build()\n"
            "        keyGen.init(spec)\n"
            "        return keyGen.generateKey()\n"
            "    }\n"
            "\n"
            "    fun encrypt(plaintext: ByteArray): ByteArray {\n"
            "        val cipher = Cipher.getInstance(TRANSFORMATION)\n"
            "        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())\n"
            "        val iv = cipher.iv // 12-byte IV تم توليده عشوائياً بواسطة الـ Cipher\n"
            "        val ciphertextWithTag = cipher.doFinal(plaintext)\n"
            "        \n"
            "        // دمج الـ IV مع النص المشفر في مصفوفة واحدة: [12 bytes IV] + [Ciphertext + Tag]\n"
            "        return ByteBuffer.allocate(iv.size + ciphertextWithTag.size)\n"
            "            .put(iv)\n"
            "            .put(ciphertextWithTag)\n"
            "            .array()\n"
            "    }\n"
            "\n"
            "    fun decrypt(encryptedPayload: ByteArray): ByteArray {\n"
            "        val buffer = ByteBuffer.wrap(encryptedPayload)\n"
            "        val iv = ByteArray(IV_SIZE_BYTES).also { buffer.get(it) }\n"
            "        val ciphertextWithTag = ByteArray(buffer.remaining()).also { buffer.get(it) }\n"
            "\n"
            "        val cipher = Cipher.getInstance(TRANSFORMATION)\n"
            "        val spec = GCMParameterSpec(GCM_TAG_LENGTH_BITS, iv)\n"
            "        cipher.init(Cipher.DECRYPT_MODE, getOrCreateKey(), spec)\n"
            "        return cipher.doFinal(ciphertextWithTag)\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "To encrypt small secrets, generate an AES-256 key inside Android Keystore configured for AES/GCM/NoPadding. Let the Cipher generate a fresh 12-byte IV on each encryption, store the IV prepended to the ciphertext, and decrypt using a GCMParameterSpec with 128-bit authentication tag. GCM ensures both confidentiality and tamper detection.",
        "best_answer": (
            "Encrypting small secrets securely on Android requires Keystore-managed hardware isolation and authenticated encryption:\n\n"
            "1. **Key Generation in Keystore**: Generate a 256-bit AES key inside `AndroidKeyStore` using `KeyGenParameterSpec` configured with `PURPOSE_ENCRYPT or PURPOSE_DECRYPT`, `BLOCK_MODE_GCM`, `ENCRYPTION_PADDING_NONE`, and `setRandomizedEncryptionRequired(true)`. The key material never leaves hardware.\n\n"
            "2. **Authenticated Encryption (AES-GCM)**: GCM is an AEAD (Authenticated Encryption with Associated Data) mode. In addition to encrypting data, it appends a 128-bit authentication tag. If an attacker modifies even a single byte of ciphertext in storage, `cipher.doFinal()` throws `AEADBadTagException`, preventing bit-flipping attacks.\n\n"
            "3. **IV Management**: GCM requires a unique Initialization Vector (IV)—typically 12 bytes—for every encryption under the same key. Reusing an IV with GCM destroys cryptographic security. Always let `cipher.init(Cipher.ENCRYPT_MODE, key)` generate the random IV via the system's secure RNG, and prepend the IV to the stored ciphertext.\n\n"
            "4. **Decryption**: Extract the first 12 bytes as IV, initialize `Cipher.DECRYPT_MODE` with `GCMParameterSpec(128, iv)`, and decrypt the remaining bytes."
        ),
        "deep_answer": (
            "From an architectural standpoint, implementing Keystore-backed encryption requires considering concurrency, performance, and key resilience:\n\n"
            "1. **Keystore IPC Bottlenecks**: Android Keystore operations involve IPC to the `keystored` daemon and hardware TEE/StrongBox calls. These calls are CPU-intensive and blocking. Encryption and decryption routines must never execute on the Main Thread; dispatch them to a dedicated background Coroutine dispatcher (`Dispatchers.IO` or `Dispatchers.Default`).\n\n"
            "2. **Handling Corrupted Entries**: In production across diverse OEM implementations, Keystore operations occasionally throw `KeyStoreException` or `UnrecoverableKeyException` due to hardware glitches or OS upgrades. Resilient architectures catch these exceptions, clear the corrupted alias, purge stale encrypted tokens from storage, and gracefully prompt the user to re-authenticate.\n\n"
            "3. **Size Constraints**: Keystore AES-GCM is designed for small payloads (tokens, encryption keys, PII strings). For large files or databases, use an **Envelope Encryption** pattern: generate a random data key in memory, encrypt the file using standard AES-CTR/CBC, and use Keystore only to encrypt that data key."
        ),
        "follow_ups": [
            {
                "question": "Why should you never use AES/ECB/PKCS5Padding?",
                "answer": "ECB mode encrypts identical plaintext blocks into identical ciphertext blocks, revealing patterns and structure, and lacks an authentication tag against tampering."
            },
            {
                "question": "What happens if you supply your own hardcoded IV to AES/GCM?",
                "answer": "If `setRandomizedEncryptionRequired(true)` is set, Keystore throws an exception; if bypassed, reusing the same IV completely breaks GCM security and exposes key details."
            }
        ]
    },
    {
        "id": "SEC-12",
        "arabic_explanation": (
            "ما هي حقيقة مكتبة `EncryptedSharedPreferences` ومكتبة `security-crypto`، ولماذا تم إيقافها (Deprecated) وما هي البدائل الحديثة؟\n\n"
            "1. ما كانت فكرة `EncryptedSharedPreferences`؟\n"
            "   - كانت جزءاً من مكتبة `androidx.security:security-crypto` وتعتمد على مكتبة Google Tink لتشفير مفاتيح وقيم الـ SharedPreferences تلقائياً، بحيث يتم تشفير المفاتيح باستخدام خوارزمية SIV-AES ويتم تشفير القيم باستخدام AES-GCM، مع حفظ مفتاح رئيسي (MasterKey) في الـ Android Keystore.\n\n"
            "2. لماذا أصبحت كابوساً برمجياً وتم اعتبارها Deprecated؟\n"
            "   - **معدل انهيارات كارثي في الإنتاج (High Crash Rates)**: مكتبة Tink كانت تعتمد على حفظ Keyset مشفر داخل ملف xml. على العديد من أجهزة سامسونج وشاومي وعند حدوث تحديثات للنظام (OTA) أو استعادة نسخ احتياطي، كان الـ Keystore يفقد المفتاح أو يتلف ملف الـ Keyset، مما يسبب انهيارات غير قابلة للإصلاح مثل `SecurityException`, `DeadObjectException`, `CleartextKeysetException`, و`GeneralSecurityException`.\n   - **أداء ضعيف وتجميد للـ UI**: كانت تقرأ وتفك تشفير الـ Keyset بالكامل وتستدعي الـ Keystore عبر IPC عند تهيئة التطبيق، مما يسبب Jank أو ANR إذا تمت تهيئتها على الـ Main Thread.\n   - **توقف التطوير الرسمي (Maintenance Mode)**: جوجل توقفت عن صيانة وتحديث المكتبة لفترة طويلة وأعلنت إيقافها لاحقاً لعدم استقرارها الهندسي.\n\n"
            "3. ما هي البدائل المعتمدة في بيئات الإنتاج الحديثة؟\n"
            "   - **Android Jetpack DataStore (مع تشفير مخصص)**: استخدام DataStore مع مُشفّر مخصص (Custom Serializer) يعتمد مباشرة على Android Keystore الخام.\n   - **SQLCipher مع Room Database**: لتخزين البيانات المنظمة الحساسة بقاعدة بيانات مشفرة بالكامل.\n   - **التشفير المباشر عبر Keystore AES-GCM**: تشفير التوكنز فقط يدوياً قبل حفظها في DataStore أو تخزينها."
        ),
        "practical_walkthrough": (
            "بديل حديث ومستقر: استخدام Jetpack Preferences DataStore مع تشفير القيم عبر Keystore الخام بدون الاعتماد على المكتبة التالفة:\n"
            "```kotlin\n"
            "// ❌ النمط القديم المليء بالمشاكل والانهيارات:\n"
            "// val sharedPrefs = EncryptedSharedPreferences.create(context, \"secrets\", masterKey, ...)\n"
            "// يسبب أعطالاً مفاجئة في أجهزة الإنتاج: KeyPermanentlyInvalidatedException أو Keystore crashes!\n"
            "\n"
            "// ✅ المعمارية الحديثة: DataStore مع تشفير التوكنز عبر Android Keystore مباشرة وبشكل آمن:\n"
            "class SecureTokenStorage(\n"
            "    private val dataStore: DataStore<Preferences>,\n"
            "    private val cryptoManager: KeystoreSecretStorage // كلاس Keystore AES-GCM موثوق ومفحوص\n"
            ") {\n"
            "    private val TOKEN_KEY = stringPreferencesKey(\"encrypted_auth_token\")\n"
            "\n"
            "    suspend fun saveAuthToken(token: String) {\n"
            "        val encryptedBytes = cryptoManager.encrypt(token.toByteArray(Charsets.UTF_8))\n"
            "        val base64Ciphertext = Base64.encodeToString(encryptedBytes, Base64.NO_WRAP)\n"
            "        \n"
            "        dataStore.edit { preferences ->\n"
            "            preferences[TOKEN_KEY] = base64Ciphertext\n"
            "        }\n"
            "    }\n"
            "\n"
            "    fun getAuthToken(): Flow<String?> = dataStore.data.map { preferences ->\n"
            "        val base64Ciphertext = preferences[TOKEN_KEY] ?: return@map null\n"
            "        try {\n"
            "            val encryptedBytes = Base64.decode(base64Ciphertext, Base64.NO_WRAP)\n"
            "            val decryptedBytes = cryptoManager.decrypt(encryptedBytes)\n"
            "            String(decryptedBytes, Charsets.UTF_8)\n"
            "        } catch (e: Exception) {\n"
            "            // إذا تلف المفتاح أو تم مسحه، التعامل بمرونة وحذف التوكن التالف بدون انهيار التطبيق\n"
            "            null\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "EncryptedSharedPreferences was deprecated due to high production crash rates caused by Keystore state corruption, DeadObjectExceptions across OEM updates, and Tink keyset deserialization failures. Modern production systems replace it with Jetpack DataStore combined with raw Android Keystore AES-GCM encryption, or SQLCipher for structured datasets.",
        "best_answer": (
            "`EncryptedSharedPreferences` (part of Jetpack `androidx.security:security-crypto`) provided out-of-the-box key and value encryption wrapping Google Tink and Android Keystore. However, it proved unreliable in production:\n\n"
            "1. **Root Causes of Deprecation**:\n"
            "   - **Keyset Corruption & Crashes**: Tink stored an encrypted keyset in private XML files. Across OEM Android updates, backup restores, or Keystore daemon crashes, the hardware master key would become unrecoverable, throwing unrecoverable `SecurityException`, `DeadObjectException`, or `CleartextKeysetException` during app startup.\n"
            "   - **Main-Thread Blocking**: Initializing `EncryptedSharedPreferences` performed blocking Keystore IPC and keyset decryption, triggering frame drops and ANRs.\n"
            "   - **Unmaintained Status**: Google ceased active development, leaving reported bugs unresolved.\n\n"
            "2. **Modern Production Alternatives**:\n"
            "   - **Jetpack DataStore + Custom Keystore Encryption**: Persist encrypted byte buffers or Base64 payloads into Jetpack DataStore asynchronously using Coroutines, backed by a clean, self-contained raw Keystore AES-GCM implementation.\n"
            "   - **SQLCipher / Room**: For structured relational data requiring at-rest encryption."
        ),
        "deep_answer": (
            "Senior engineers evaluating Android storage security avoid black-box abstraction libraries that hide Keystore lifecycle hazards:\n\n"
            "1. **State Inconsistency Post-Reboot/Restore**: When a user restores from Google Auto Backup or when OEM Keystore daemons desynchronize after a major OS update, the keyset file remains on disk while the hardware Keystore alias has vanished. `EncryptedSharedPreferences` crashes permanently because it cannot decrypt the keyset and lacks an automatic reset fallback.\n\n"
            "2. **Resilient Replacement Architecture**: In our production stack, we decouple persistence from encryption:\n"
            "   - We maintain a dedicated `CryptoEngine` executing on `Dispatchers.Default` using raw `AndroidKeyStore`.\n"
            "   - When decryption fails due to key invalidation or hardware faults, we catch the cryptographic error, proactively wipe the corrupted storage entry, and fire a re-authentication event to navigate the user to login.\n"
            "   - This graceful degradation guarantees that security failures never cascade into unrecoverable app startup crashes."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between SIV and GCM in Tink's implementation?",
                "answer": "SIV (Synthetic IV) is deterministic authenticated encryption used for SharedPreferences keys so identical lookup keys produce identical ciphertexts for querying, while GCM is randomized for values."
            },
            {
                "question": "Why is Jetpack DataStore structurally safer than SharedPreferences for encrypted payloads?",
                "answer": "DataStore is fully asynchronous, runs on Coroutine dispatchers off the UI thread, supports transactional data migration, and handles error recovery through explicit Catch operators."
            }
        ]
    },
    {
        "id": "SEC-13",
        "arabic_explanation": (
            "كيف تتعامل مع إبطال المفاتيح (Key Invalidation)، تدوير المفاتيح (Key Rotation)، النسخ الاحتياطي (Auto Backup)، وإعادة التثبيت (Reinstall)؟\n\n"
            "1. إبطال المفاتيح (Key Invalidation) عبر البصمة:\n"
            "   - عند إنشاء مفتاح في Keystore مع خاصية `setInvalidatedByBiometricEnrollment(true)`، فإن إضافة أو حذف أي بصمة جديدة على مستوى الهاتف يقوم **بإبطال المفتاح عتادياً وبشكل نهائي**!\n   - أي محاولة استخدام لاحقة للمفتاح سترمي `KeyPermanentlyInvalidatedException`. هذا يحمي التطبيق البنكي إذا قام شخص يعرف رمز قفل الشاشة بتسجيل بصمة إصبعه على هاتف الضحية.\n\n"
            "2. تدوير المفاتيح (Key Rotation):\n"
            "   - يجب أن تدعم المعمارية إصدارات متعددة للمفاتيح (`secret_key_v1`, `secret_key_v2`).\n   - عند تدوير المفتاح، يتم إنشاء المفتاح الجديد، وقراءة البيانات القديمة وفك تشفيرها بالمفتاح القديم، ثم إعادة تشفيرها بالمفتاح الجديد، وحذف المفتاح القديم.\n\n"
            "3. خطر النسخ الاحتياطي التلقائي (Auto Backup Hazard):\n"
            "   - ميزة Android Auto Backup (`allowBackup=\"true\"`) تقوم برفع ملفات التطبيق الداخلية إلى Google Drive.\n   - **الكارثة**: ملفات البيانات المشفرة يتم رفعها، ولكن **مفاتيح Android Keystore لا تغادر الشريحة العتادية للهاتف أبداً**!\n   - عندما يشتري المستخدم هاتفاً جديداً ويسترجع النسخة الاحتياطية، توجد الملفات المشفرة ولكن المفتاح العتادي غير موجود، فتفشل عملية فك التشفير برمي `KeyNotFoundException` أو انهيار التطبيق!\n   - **الحل**: استثناء الملفات المشفرة عبر `backup_rules.xml` أو تعطيل النسخ الاحتياطي كلياً للتطبيقات الحساسة (`android:allowBackup=\"false\"`)."
        ),
        "practical_walkthrough": (
            "معالجة إبطال المفاتيح برمجياً واستثناء الملفات المشفرة من الـ Auto Backup:\n"
            "```kotlin\n"
            "// 1. التعامل مع استثناء إبطال المفتاح العتادي KeyPermanentlyInvalidatedException:\n"
            "class BiometricCryptoRepository(\n"
            "    private val keyStore: KeyStore,\n"
            "    private val sessionManager: SessionManager\n"
            ") {\n"
            "    fun getEncryptCipher(keyAlias: String): Cipher? {\n"
            "        return try {\n"
            "            val secretKey = keyStore.getKey(keyAlias, null) as SecretKey\n"
            "            Cipher.getInstance(\"AES/GCM/NoPadding\").apply {\n"
            "                init(Cipher.ENCRYPT_MODE, secretKey)\n"
            "            }\n"
            "        } catch (e: KeyPermanentlyInvalidatedException) {\n"
            "            // تم تسجيل بصمة جديدة على الجهاز! المفتاح أُبطل عتادياً لحماية الحساب\n"
            "            keyStore.deleteEntry(keyAlias)\n"
            "            sessionManager.forceLogoutDueToBiometricChange()\n"
            "            null\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "```xml\n"
            "<!-- 2. منع رفع الملفات المشفرة في Android Auto Backup داخل res/xml/backup_rules.xml -->\n"
            "<data-extraction-rules>\n"
            "    <cloud-backup>\n"
            "        <!-- استثناء مجلد الداتابيز وقيم التوكنز المشفرة لأن المفاتيح العتادية لن تنتقل للجهاز الجديد -->\n"
            "        <exclude path=\"datastore/secure_tokens.preferences_pb\" />\n"
            "        <exclude domain=\"database\" path=\"encrypted_app_db\" />\n"
            "    </cloud-backup>\n"
            "</data-extraction-rules>\n"
            "```"
        ),
        "quick_answer": "Biometric Keystore keys are permanently invalidated via KeyPermanentlyInvalidatedException when new biometrics are enrolled. In backup scenarios, hardware Keystore keys never migrate between devices; therefore, encrypted files must be excluded via backup_rules.xml to avoid decryption crashes upon reinstall. Key rotation requires versioned aliases and background re-encryption.",
        "best_answer": (
            "Managing the cryptographic key lifecycle across OS events requires planning for three distinct operational hazards:\n\n"
            "1. **Biometric Key Invalidation**: When keys are generated with `setInvalidatedByBiometricEnrollment(true)`, the hardware invalidates the key if the device user adds, removes, or modifies biometric enrollments. Future cryptographic operations throw `KeyPermanentlyInvalidatedException`. Production code must catch this specific exception, purge local biometric credentials, and route the user to re-authenticate with primary credentials (password/OTP).\n\n"
            "2. **The Auto Backup / Reinstall Pitfall**: Android Cloud Auto Backup transfers private app files to Google Drive, but Keystore hardware keys are physically locked to the device's TEE/SE and are never exported. When restored on a new device, encrypted files exist without the decryption key, causing permanent decryption failure. Apps must exclude encrypted databases and DataStore files in `backup_rules.xml` or disable `android:allowBackup=\"false\"`.\n\n"
            "3. **Key Rotation**: Production key rotation uses versioned aliases (e.g., `key_alias_v2`). The app reads data encrypted with `v1`, decrypts it, generates `v2` in Keystore, re-encrypts the payload, updates an encrypted metadata pointer, and securely destroys `v1`."
        ),
        "deep_answer": (
            "From an enterprise security posture, handling key invalidation and restore states is a critical architectural requirement:\n\n"
            "1. **Device Reinstall Lifecycle**: When an app is uninstalled and reinstalled on the same physical device, Keystore keys are permanently wiped by the Android OS package manager. Any residual orphaned data (e.g., stored on external scoped storage or synced back from cloud backups) cannot be decrypted. The app must detect a fresh install lifecycle, re-initialize its cryptographic Keystore keysets, and request a fresh session token from the backend.\n\n"
            "2. **Zero-Downtime Key Rotation Strategy**: For server-synced local data, client key rotation should be triggered via backend-driven feature flags or rotation metadata headers. When the server signals a key rollover, a background WorkManager job performs atomic read-decrypt-reencrypt operations on local stores in chunks, preventing blocking operations during critical user flows.\n\n"
            "3. **Defensive Exception Handling**: Never treat `KeyStoreException` as a generic runtime failure. Differentiate between `UserNotAuthenticatedException` (biometric prompt required), `KeyPermanentlyInvalidatedException` (credential enrollment changed), and hardware communication errors (`KeyStoreConnectException`), taking deterministic recovery actions for each."
        ),
        "follow_ups": [
            {
                "question": "What happens if a user disables their screen lock (PIN/Password) on a device with biometric keys?",
                "answer": "All Keystore keys requiring device credentials or user authentication are instantly destroyed and wiped by the Android Keymaster daemon."
            },
            {
                "question": "Why does setting android:allowBackup=\"false\" help fintech applications?",
                "answer": "It blocks adb backup extraction (`adb backup`) and Google Drive cloud backups, preventing local database extraction on developer-enabled devices."
            }
        ]
    },
    {
        "id": "SEC-14",
        "arabic_explanation": (
            "أين وكيف يجب تخزين الـ Access Tokens والـ Refresh Tokens، وكيف يتم إلغاؤها (Revocation) من جهة السيرفر والتطبيق؟\n\n"
            "1. استراتيجية تخزين الـ Tokens على الهاتف:\n"
            "   - **Access Token (قصير العمر - Short-Lived: 5 إلى 15 دقيقة)**: يُفضل الاحتفاظ به في **ذاكرة الـ RAM فقط** (داخل Singleton أو Repository في الذاكرة) أثناء تشغيل التطبيق. لا داعي لحفظه على القرص إذا كان قصير العمر، أو يُحفظ مشفراً في Keystore/DataStore إذا أردنا تجنب طلب توكن جديد عند إعادة فتح التطبيق.\n   - **Refresh Token (طويل العمر - Long-Lived: أيام أو أسابيع)**: **يُمنع منعاً باتاً تخزينه كنص صريح (Plaintext)**. يجب تخزينه مشفراً باستخدام مفتاح عتادي داخل Android Keystore مدمج مع Jetpack DataStore.\n\n"
            "2. آلية الـ Token Rotation والـ Revocation في السيرفر:\n"
            "   - **Refresh Token Rotation (RTR)**: في كل مرة يستخدم فيها العميل الـ Refresh Token للحصول على Access Token جديد، يقوم السيرفر بإنشاء Refresh Token جديد وإلغاء القديم فوراً.\n   - **كشف سرقة التوكن (Token Theft Detection)**: إذا حاول مهاجم استخدام Refresh Token قديم تم تدويره مسبقاً، يدرك السيرفر فوراً أن هناك سرقة حدثت، فيقوم بإلغاء عائلة التوكنز بالكامل (Family Revocation) وقطع جميع الجلسات فوراً.\n\n"
            "3. آلية التجديد التلقائي عبر OkHttp Authenticator:\n"
            "   - لا يتم فحص صلاحية التوكن يدوياً في كل Request. بل نعتمد على `okhttp3.Authenticator` الذي يتم استدعاؤه تلقائياً فقط عند رجوع استجابة `HTTP 401 Unauthorized` من السيرفر، ليقوم بتجميد الطلبات وتجديد التوكن وإعادة المحاولة بسلاسة."
        ),
        "practical_walkthrough": (
            "تنفيذ تجديد التوكن بسلاسة وأمان باستخدام OkHttp Authenticator و Mutex لمنع Race Conditions:\n"
            "```kotlin\n"
            "class TokenAuthenticator(\n"
            "    private val tokenStorage: SecureTokenStorage,\n"
            "    private val authService: AuthService\n"
            ") : Authenticator {\n"
            "    private val refreshMutex = Mutex()\n"
            "\n"
            "    override fun authenticate(route: Route?, response: Response): Request? {\n"
            "        // 1. منع المحاولات المتكررة اللانهائية إذا فشل الـ Refresh أصلاً:\n"
            "        if (responseCount(response) >= 3) return null\n"
            "\n"
            "        val currentAccessToken = runBlocking { tokenStorage.getAccessToken() }\n"
            "        \n"
            "        // 2. فحص ما إذا كان طلب آخر قد قام بتجديد التوكن بالفعل أثناء انتظار هذا الطلب:\n"
            "        val requestToken = response.request.header(\"Authorization\")?.removePrefix(\"Bearer \")\n"
            "        if (requestToken != currentAccessToken && currentAccessToken != null) {\n"
            "            // تم تجديد التوكن بالفعل؛ إعادة إرسال الطلب بالتوكن الجديد فوراً:\n"
            "            return response.request.newBuilder()\n"
            "                .header(\"Authorization\", \"Bearer $currentAccessToken\")\n"
            "                .build()\n"
            "        }\n"
            "\n"
            "        // 3. تجديد التوكن بشكل متزامن وحصري عبر Mutex:\n"
            "        return runBlocking {\n"
            "            refreshMutex.withLock {\n"
            "                val latestToken = tokenStorage.getAccessToken()\n"
            "                if (latestToken != requestToken && latestToken != null) {\n"
            "                    return@withLock response.request.newBuilder()\n"
            "                        .header(\"Authorization\", \"Bearer $latestToken\")\n"
            "                        .build()\n"
            "                }\n"
            "\n"
            "                val refreshToken = tokenStorage.getRefreshToken() ?: return@withLock null\n"
            "                val newTokensResult = authService.refreshTokens(refreshToken)\n"
            "                \n"
            "                if (newTokensResult.isSuccessful) {\n"
            "                    val newTokens = newTokensResult.body()!!\n"
            "                    tokenStorage.saveTokens(newTokens.accessToken, newTokens.refreshToken)\n"
            "                    response.request.newBuilder()\n"
            "                        .header(\"Authorization\", \"Bearer ${newTokens.accessToken}\")\n"
            "                        .build()\n"
            "                } else {\n"
            "                    // تم رفض الـ Refresh Token على السيرفر؛ إبطال الجلسة وتوجيه المستخدم لتسجيل الدخول\n"
            "                    tokenStorage.clearTokens()\n"
            "                    null\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "    private fun responseCount(response: Response): Int = generateSequence(response) { it.priorResponse }.count()\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Store short-lived access tokens in memory or encrypted storage, and long-lived refresh tokens strictly in Keystore-backed encrypted DataStore. Revocation must occur server-side by blacklisting session IDs in Redis. Use OkHttp's Authenticator with a Mutex to seamlessly refresh tokens upon 401 responses and handle token rotation.",
        "best_answer": (
            "Token architecture follows a tiered security approach balancing user experience against attack windows:\n\n"
            "1. **Storage Topology**:\n"
            "   - **Access Token**: Short validity (5–15 minutes). Can reside in an in-memory repository during active process lifecycle, supplemented with Keystore-backed encrypted persistence to survive process death without forced re-logins.\n"
            "   - **Refresh Token**: Longer validity (7–30 days). Must never be stored in plain SharedPreferences. It must be encrypted using Android Keystore AES-GCM and stored in Jetpack DataStore.\n\n"
            "2. **Server-Side Revocation**:\n"
            "   - Mobile logout must invoke a backend `/logout` or `/revoke` endpoint. The server marks the session/refresh token family revoked in a distributed cache (e.g. Redis).\n   - Client-side token deletion alone is insufficient because a compromised token remains valid on the server until expiry.\n\n"
            "3. **Refresh Token Rotation (RTR)**:\n"
            "   - Every refresh request invalidates the previous refresh token and issues a new pair. If an invalidated refresh token is ever reused, the server detects token compromise and immediately revokes all tokens issued to that user session."
        ),
        "deep_answer": (
            "In high-traffic distributed mobile apps, token refreshing introduces significant concurrency and failure handling challenges:\n\n"
            "1. **Handling Thundering Herds on 401**: When multiple parallel API calls fail simultaneously with `401 Unauthorized`, an uncoordinated authenticator triggers parallel refresh calls. The first call succeeds and rotates the refresh token; the subsequent calls submit an already-invalidated refresh token, causing the backend to falsely assume token theft and revoke the session! We prevent this by serializing refresh execution using a Coroutines `Mutex` inside `okhttp3.Authenticator`.\n\n"
            "2. **Re-entrant 401 Loop Protection**: `Authenticator.authenticate()` must track `response.priorResponse` count. If the refresh request itself fails or if three consecutive retries return 401, return `null` to terminate the loop, wipe stored tokens, and dispatch an unauthenticated session event to navigate to the Login screen.\n\n"
            "3. **Token Binding & Attestation**: In high-assurance fintech apps, refresh tokens are cryptographically bound to a client-generated Keystore EC keypair (DPoP - Demonstrating Proof-of-Possession). Even if an attacker intercepts the refresh token via TLS proxy, they cannot replay it without signing the request using the device's non-exportable private key."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between an OkHttp Interceptor and an Authenticator for auth tokens?",
                "answer": "An Interceptor attaches the current token to outgoing requests; an Authenticator is triggered only when the server returns 401 Unauthorized, specifically designed for token refresh."
            },
            {
                "question": "Why should JWTs not store sensitive PII in their payload?",
                "answer": "JWT payloads are Base64Url-encoded, not encrypted; anyone intercepting or inspecting the token in memory can decode and read the claims instantly."
            }
        ]
    },
    {
        "id": "SEC-15",
        "arabic_explanation": (
            "كيف تمنع تسريب الـ Tokens والبيانات الحساسة عبر الـ Logs، لقطات الشاشة (Screenshots)، تقارير الأعطال (Crash Reports)، وأدوات الـ Analytics؟\n\n"
            "1. منع التسريب عبر الـ Logs (Logcat):\n"
            "   - **قاعدة صارمة**: لا تطبع الـ Tokens أو كلمات المرور أو أرقام البطاقات في الـ Logcat أبداً.\n   - في بيئة الـ Release، يجب تجريد استدعاءات `Log.d` و `Log.v` بالكامل عبر R8 (`-assumenosideeffects`).\n   - يجب تخصيص `HttpLoggingInterceptor` في OkHttp بحيث يُستثنى هيدر `Authorization` والـ Cookies من الطباعة (`redactHeader(\"Authorization\")`).\n\n"
            "2. منع التسريب عبر لقطات الشاشة وقائمة الـ Recent Apps:\n"
            "   - نظام أندرويد يأخذ لقطة شاشة تلقائية لواجهة التطبيق عند الضغط على زر Home أو فتح الـ App Switcher ويحفظها في ملفات النظام المؤقتة!\n   - **الحل**: تفعيل `WindowManager.LayoutParams.FLAG_SECURE` على مستوى الـ Activity الحساسة. هذا يمنع تسجيل الشاشة، يمنع أخذ Screenshots، ويعرض شاشة سوداء أو فارغة في قائمة الـ Recent Apps.\n\n"
            "3. منع التسريب عبر تقارير الأعطال (Crashlytics / Sentry):\n"
            "   - عند حدوث Crash، قد يرسل SDK التقارير معلومات الـ State أو الشبكة. يجب فحص وتطهير (Sanitize) الـ Custom Keys وسجلات الأحداث عبر `beforeSend` Callback لحذف أي PII أو Bearer tokens.\n\n"
            "4. منع التسريب عبر الـ Analytics:\n"
            "   - يُمنع إرسال مدخلات المستخدم الصريحة أو مسارات الـ URLs الكاملة التي تحتوي على query parameters بها tokens إلى أدوات مثل Firebase Analytics أو Mixpanel."
        ),
        "practical_walkthrough": (
            "تطبيق شامل لمنع تسريب البيانات الحساسة عبر الطبقات الأربع (Logs, Screen, Crashes, Network):\n"
            "```kotlin\n"
            "// 1. تأمين الشاشة ضد Screenshots والـ Recent Apps Switcher في Compose / Activity:\n"
            "class SecurePaymentActivity : ComponentActivity() {\n"
            "    override fun onCreate(savedInstanceState: Bundle?) {\n"
            "        super.onCreate(savedInstanceState)\n"
            "        // يمنع تصوير الشاشة ويحمي واجهة التطبيق في قائمة المهام الأخيرة:\n"
            "        window.setFlags(\n"
            "            WindowManager.LayoutParams.FLAG_SECURE,\n"
            "            WindowManager.LayoutParams.FLAG_SECURE\n"
            "        )\n"
            "        setContent { PaymentScreen() }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. تطهير هيدرز الشبكة ومنع تسريب الـ Tokens في Logcat:\n"
            "fun createSecureLoggingInterceptor(): HttpLoggingInterceptor {\n"
            "    return HttpLoggingInterceptor().apply {\n"
            "        level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.HEADERS else HttpLoggingInterceptor.Level.NONE\n"
            "        // إخفاء قيمة هيدر التفويض حتى في الـ Debug:\n"
            "        redactHeader(\"Authorization\")\n"
            "        redactHeader(\"Cookie\")\n"
            "        redactHeader(\"X-Api-Key\")\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. تطهير تقارير Crashlytics قبل إرسالها:\n"
            "class SecureCrashReporter {\n"
            "    fun recordHandledException(throwable: Throwable) {\n"
            "        // التحقق من خلو رسالة الخطأ من أي Bearer tokens قبل رفعها:\n"
            "        val sanitizedMessage = throwable.message?.replace(Regex(\"Bearer\\\\s+[A-Za-z0-9\\\\-_.]+\"), \"Bearer [REDACTED]\")\n"
            "        FirebaseCrashlytics.getInstance().recordException(Exception(sanitizedMessage, throwable.cause))\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Prevent leaks by masking Authorization headers via OkHttp's redactHeader, stripping Log calls in release builds with R8, setting FLAG_SECURE on sensitive Activities to block screenshots and recents snapshots, and sanitizing Crashlytics breadcrumbs and analytics events to strip PII and tokens before dispatch.",
        "best_answer": (
            "Data leakage occurs across four primary observation surfaces, each requiring deliberate architectural defenses:\n\n"
            "1. **Logcat & Network Logs**: \n"
            "   - Configure OkHttp's `HttpLoggingInterceptor` using `redactHeader(\"Authorization\")` and `redactHeader(\"Cookie\")` to prevent printing tokens.\n   - In release builds, use R8 rules (`-assumenosideeffects`) to strip `Log.d` and `Log.v` bytecodes entirely.\n\n"
            "2. **Screen Capture & App Switcher (Task Snapshots)**:\n"
            "   - When users background an app, Android saves a screenshot to disk for the multitasking overview. Applying `window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)` prevents screenshots, screen recording, and blacks out the task thumbnail in the recent apps switcher.\n\n"
            "3. **Crash Reporting (Crashlytics/Sentry)**:\n"
            "   - Scrub custom keys, breadcrumbs, and exception messages using filtering hooks (`beforeSend`). Network exception messages frequently contain full URLs with sensitive query parameters or authorization failure dumps.\n\n"
            "4. **Analytics Pipelines**:\n"
            "   - Enforce strict event data schemas. Never forward free-form user inputs, search queries with sensitive data, or complete server URLs to analytics tools."
        ),
        "deep_answer": (
            "From an operational compliance perspective (e.g. PCI-DSS, GDPR, HIPAA), unintentional token leakage is treated as a major security incident:\n\n"
            "1. **Dynamic FLAG_SECURE Management**: In modern Jetpack Compose applications, `FLAG_SECURE` can be dynamically toggled using a `DisposableEffect` based on whether the currently visible composable displays sensitive data (e.g., credit card entry or seed phrases), rather than blindly applying it across the entire application which impairs legitimate UX like support screenshots.\n\n"
            "2. **Memory Dumps & System Bug Reports**: When users trigger an Android bug report (`adb bugreport` or system developer settings), the OS dumps system log buffers and memory summaries. If tokens were printed to Logcat or stored in static string variables, they are bundled into plaintext bug report archives that users often share unencrypted over email or bug trackers.\n\n"
            "3. **Automated CI Linting**: Integrate static analysis linters (e.g., custom Android Lint rules or Semgrep) in CI to fail PR builds if developers log sensitive parameter names (`token`, `password`, `pan`, `cvv`) or attach raw network responses to analytics events."
        ),
        "follow_ups": [
            {
                "question": "Does FLAG_SECURE protect against root users capturing the screen via frame buffer reads?",
                "answer": "No; root users can read `/dev/graphics/fb0` or use SurfaceFlinger shell commands with root privileges to dump raw display hardware buffers."
            },
            {
                "question": "Can OkHttp body logs leak JSON payloads containing passwords?",
                "answer": "Yes; if Level.BODY is enabled, request bodies are printed in plaintext. In production, logging should be set to Level.NONE or use custom redact interceptors."
            }
        ]
    },
    {
        "id": "SEC-16",
        "arabic_explanation": (
            "لماذا يُفضل استخدام `CharArray` على `String` لحفظ كلمات المرور في الذاكرة، وما هي الحدود الواقعية لهذا النهج في أندرويد وKotlin؟\n\n"
            "1. مشكلة كائن الـ `String` في الذاكرة (Immutability & String Pool):\n"
            "   - كائنات `String` في Java و Kotlin **غير قابلة للتعديل (Immutable)**.\n   - بمجرد إنشاء كلمة المرور كـ `String`، تُحفظ مصفوفة البايتات في الـ Heap، ولا يمكن تعديلها أو مسحها برمجياً.\n   - تظل كلمة المرور موجودة في الـ RAM حتى يقرر الـ Garbage Collector (GC) تشغيل دورة تنظيف وحذفها، وهذا وقت غير محدد قد يستغرق دقائق أو ساعات!\n   - إذا أخذ مهاجم تفريغ للذاكرة (Heap Dump عبر `am dumpheap`) أثناء وجود التطبيق في الخلفية، سيجد كلمة المرور بنصها الصريح في الذاكرة!\n\n"
            "2. ميزة استخدام `CharArray`:\n"
            "   - كائن `CharArray` هو **مصفوفة قابلة للتعديل (Mutable)**.\n   - بمجرد استخدام كلمة المرور (مثلاً تشفيرها أو استخدامها لحساب Hash)، يمكن للمطور مسحها فوراً بملء المصفوفة بأصفار:\n     `Arrays.fill(passwordChars, '\u0000')`.\n   - هذا يقلص نافذة بقاء كلمة المرور في الذاكرة (Memory Exposure Window) إلى أجزاء من الثانية بدلاً من دقائق.\n\n"
            "3. الحدود الواقعية في أندرويد و Kotlin (The Pragmatic Reality):\n"
            "   - **مكونات الـ UI في أندرويد**: دالة `EditText.getText()` تعيد `Editable` (وهو `CharSequence`)، ولكن في Jetpack Compose دوال `TextField` أو `BasicTextField` تأخذ `String` أو `TextFieldValue` كـ State! هذا يعني أن الـ String تم إنشاؤه بالفعل بواسطة الـ Framework قبل أن يصل لكودك!\n   - **مكتبات الشبكة (Retrofit / Moshi / JSON)**: تحويل البيانات إلى JSON و إرسالها عبر HTTP يعتمد داخلياً على كائنات `String`.\n   - **الخلاصة**: استخدام `CharArray` مفيد جداً في الخوارزميات المشفرة المحلية (Crypto layers, PBKDF2)، لكن تحقيقه بنسبة 100% عبر طبقة الـ UI والشبكة يتطلب مكونات مخصصة معقدة."
        ),
        "practical_walkthrough": (
            "المقارنة بين تخزين الـ Password كـ String ومسحه يدوياً كـ CharArray:\n"
            "```kotlin\n"
            "// ❌ تخزين كلمة المرور في String: تظل في الذاكرة لفترة غير محددة:\n"
            "class InsecurePasswordHolder {\n"
            "    // الـ String غير قابل للتعديل؛ لا يمكنك إزالته من الـ Heap وسيكشفه أي Heap Dump:\n"
            "    var userPassword: String = \"SuperSecretP@ssword123\"\n"
            "}\n"
            "\n"
            "// ✅ استخدام CharArray ومسحه فور الانتهاء من العمليات الحسابية:\n"
            "class SecurePasswordProcessor {\n"
            "    fun hashAndZeroize(password: CharArray, salt: ByteArray): ByteArray {\n"
            "        return try {\n"
            "            val spec = PBEKeySpec(password, salt, 100_000, 256)\n"
            "            val factory = SecretKeyFactory.getInstance(\"PBKDF2WithHmacSHA256\")\n"
            "            factory.generateSecret(spec).encoded\n"
            "        } finally {\n"
            "            // مسح محتوى المصفوفة بأصفار فوراً لتقليص نافذة البقاء في الـ RAM:\n"
            "            password.fill('\u0000')\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "CharArray is preferred over String because Strings are immutable and persist unpredictably in the JVM heap until GC runs. With CharArray, developers can immediately overwrite the memory with zeroes after use via Arrays.fill. However, Android UI frameworks and JSON serializers often create intermediate Strings anyway, limiting practical coverage.",
        "best_answer": (
            "The security rationale for choosing `CharArray` over `String` centers on memory residence time and deterministic cleanup:\n\n"
            "1. **String Immutability Hazard**: Strings in the JVM are immutable and cached in heap memory or the string pool. Developers cannot mutate their underlying character arrays. They linger in heap memory until non-deterministic garbage collection cleans them up, leaving them vulnerable to heap dumps (`am dumpheap`), memory inspection on rooted devices, or swapped flash storage pages.\n\n"
            "2. **Zeroization with CharArray**: A `CharArray` is a mutable primitive array. Once the credential is used (e.g. passed to PBKDF2 key derivation), developers can immediately wipe the data in a `finally` block using `passwordChars.fill('\\u0000')` or `Arrays.fill(chars, '0')`. This reduces memory exposure from minutes to milliseconds.\n\n"
            "3. **Practical Android Limitations**: In real-world Android apps, achieving end-to-end zeroization is difficult. Jetpack Compose `TextField` manages state using immutable `String` instances. Similarly, Retrofit, OkHttp, and JSON serializers convert payloads to `String`. Unless custom zero-allocation text inputs and raw socket streaming are used, intermediate strings are created at framework boundaries."
        ),
        "deep_answer": (
            "From an advanced security engineering viewpoint, zeroizing sensitive buffers in managed JVM runtimes requires understanding ART garbage collection and native interactions:\n\n"
            "1. **ART Moving GC & Compaction**: The Android Runtime (ART) uses moving collectors (Concurrent Copying GC). When objects are relocated in memory, stale copies of the old memory block may remain unzeroed in free memory pages until overwritten. Overwriting a `CharArray` cleans the active instance, but cannot guarantee that previous relocated copies are wiped.\n\n"
            "2. **Native Memory Zeroization (JNI/C++)**: In high-assurance environments, passwords entered via custom virtual keyboards are passed directly into native C/C++ memory (`malloc`) via JNI, where `explicit_bzero()` or `SecureZeroMemory()` ensures that compiler optimizations do not elide the zeroing operations.\n\n"
            "3. **Architectural Recommendation**: Focus cryptographic hygiene where it matters most: inside key derivation factories (`PBEKeySpec`), cryptographic token generation, and biometric cipher wrappers, while acknowledging UI framework constraints."
        ),
        "follow_ups": [
            {
                "question": "Can the compiler optimize away Arrays.fill(chars, '\\u0000') if the array is not read again?",
                "answer": "In JIT-compiled C/C++ this is a known risk (dead store elimination), but in standard JVM bytecode execution, `Arrays.fill` calls are executed unless aggressive escape analysis proves the object unreachable."
            },
            {
                "question": "What is the benefit of using ByteBuffer.allocateDirect() for crypto buffers?",
                "answer": "Direct byte buffers reside in native off-heap memory, bypassing JVM garbage collection and allowing direct zeroization without ART object relocation."
            }
        ]
    }
]


def update_sec_data() -> None:
    data = []
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_map = {item["id"]: item for item in data}
    for item in SEC_09_16:
        existing_map[item["id"]] = item

    updated = [existing_map[k] for k in sorted(existing_map.keys())]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions SEC-09 to SEC-16. Total questions: {len(updated)}")


if __name__ == "__main__":
    update_sec_data()
