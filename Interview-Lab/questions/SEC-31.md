---
id: "SEC-31"
question: "A team puts a private API key in BuildConfig from local.properties. Why is this not sufficient?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "C"
phase: 3
priority: "P1"
order: 328
editorial_status: "reviewed"
---

# SEC-31

## Original interview question

A team puts a private API key in BuildConfig from local.properties. Why is this not sufficient?

## What the interviewer evaluates

- BuildConfig/local.properties extraction path.
- Incident response and server-side privilege design.

## Explanation in Arabic

فريق برمجي يضع مفتاح الـ API الخاص (Private API Key) في ملف `local.properties` ويقرأه داخل `BuildConfig`. لماذا يُعد هذا غير كافٍ وثغرة أمنية فادحة؟

1. ما الذي يفعله `local.properties` وما الذي لا يفعله؟
   - وضع المفتاح في `local.properties` يمنع رفعه إلى مستودع الـ Git (GitHub/GitLab) إذا كان الملف مستثنى في `.gitignore`. هذا إجراء تنظيمي جيد لحماية الـ Git History فقط.
   - **لكن**: عند قراءة المفتاح وتمريره إلى `buildConfigField`, يقوم Gradle بتوليد كلاس جافا اسمه `BuildConfig.java` يحتوي على سطر صريح:
     `public static final String STRIPE_SECRET = "sk_live_1234567890";`.

2. كيف يتم استخراج هذا المفتاح من الـ APK في 5 ثوانٍ؟
   - عند تجميع الـ APK، يُترجم كلاس `BuildConfig` إلى Dalvik Bytecode داخل `classes.dex`.
   - يستطيع أي شخص تنزيل الـ APK من المتجر وتنفيذ أمر سطر واحد في الـ Terminal:
     `strings classes.dex | grep sk_live`
     أو فتح الـ APK في `JADX-GUI` وقراءة المفتاح بنصه الصريح فوراً!

3. الفرق بين المفاتيح العامة (Public Keys) والمفاتيح الخاصة (Private Secrets):
   - **المفاتيح العامة (Allowed on Client)**: مفاتيح مثل Google Maps API Key أو Firebase Public Key. هذه المفاتيح مخصصة لتعريف التطبيق ومحمية من جهة Google Console بقيود الباكدج والبصمة الرقمية (Package Name + SHA-1 Restriction).
   - **المفاتيح الخاصة (Strictly Forbidden on Client)**: مفاتيح مثل OpenAI Secret Key, Stripe Secret Key, AWS S3 Master Credentials. هذه المفاتيح **ممنوع تماماً وضعها في أي تطبيق موبايل**! يجب أن تظل حصرياً على خادم الـ Backend (BFF - Backend for Frontend)، ويقوم الموبايل بالاتصال بالسيرفر الخاص بك والسيرفر هو من يتصل بتلك الخدمات.

## Practical walkthrough

المقارنة بين الطريقة الساذجة المكشوفة في الـ APK والمعمارية الصحيحة باستخدام Backend for Frontend:
```groovy
// ❌ ثغرة أمنية فادحة في build.gradle: توليد المفتاح الخاص في كود الـ APK:
android {
    defaultConfig {
        // يتم تضمين هذا المفتاح كنص صريح في ملف DEX ويمكن استخراجه في ثوانٍ!
        buildConfigField "String", "OPENAI_SECRET_KEY", "\"sk-proj-998877665544332211\""
    }
}
```

```kotlin
// ✅ المعمارية الصحيحة: العميل لا يملك المفتاح السري، بل يتصل بـ Backend Proxy:
class AiAssistantRepository(
    private val companyBackendApi: CompanyBackendApi
) {
    suspend fun generateSummary(userPrompt: String): String {
        // التطبيق يرسل الطلب لسيرفر شركتك موثقاً بـ User Session Token:
        val response = companyBackendApi.requestAiSummary(
            prompt = userPrompt
        )
        // سيرفر شركتك (الـ Backend) هو من يحتفظ بـ OPENAI_SECRET_KEY في بيئة آمنة
        // ويتحقق من رصيد المستخدم وصلاحياته قبل استدعاء OpenAI API
        return response.summary
    }
}
```

## Why it matters and how it works

BuildConfig values are compiled into the distributed client. R8 name changes and JNI relocation cannot create a server-controlled secret. Provider package/signature restrictions and quotas may help for public mobile identifiers, but private operations require server custody and authorization.

## Worked example

A team stores `ACQUIRER_PRIVATE_KEY` in local.properties and writes it to BuildConfigField. The remediation is to revoke/rotate the key, inspect provider activity, remove it from APK artifacts, and have the backend create scoped payment intents after validating user and order state.

## Trade-offs and decision criteria

Keeping config out of Git remains useful hygiene. A backend proxy costs latency and maintenance but is the proper trust boundary for privileged keys. Public SDK keys can stay in APK only under the provider’s documented restrictions.

## Failure modes

Rotating only the local.properties file leaves already released APKs with the old key. Removing the source line without revoking the provider credential leaves the incident active. Inspect all release versions and use provider-side revocation.

## Production perspective

CI scans source and packaged artifacts, while secret-management controls restrict backend access. Backend logs key identifiers and operation IDs rather than raw credentials.

## Interview answer — short

Putting keys in local.properties keeps them out of git, but defining them in BuildConfig bakes them into classes.dex as plaintext strings. Anyone can extract them in seconds via JADX or strings CLI. Private secrets must never exist on mobile clients; they belong exclusively on an authoritative backend proxy.

## Interview answer — structured

Using `local.properties` with `BuildConfig` addresses version control hygiene, but offers zero cryptographic confidentiality against reverse engineering:

1. **Compilation into Plaintext DEX**: Gradle generates a Java constant in `BuildConfig.java` (`public static final String API_KEY = "...";`). During compilation, this string constant is placed directly into the `classes.dex` string pool. Anyone who downloads the APK can run `strings classes.dex` or inspect `BuildConfig` in JADX to extract the secret immediately.

2. **Public vs. Private API Keys**:
   - **Public Client Keys**: Identifiers like Google Maps keys or Firebase App IDs are designed to be public. They rely on server-side restrictions (e.g. Google Cloud package name + SHA-1 fingerprint whitelisting) rather than secrecy.
   - **Private Secrets**: Keys providing privileged administrative access, billing capabilities, or third-party paid API quotas (OpenAI, Stripe Secret, AWS IAM credentials) must **never** be packaged into a mobile application.

3. **Architectural Remedy (Backend-for-Frontend)**:
   - Deploy a backend proxy / BFF. The mobile client authenticates against your backend using short-lived user session tokens. Your backend holds the private API secret securely in environment variables or an enterprise secret manager and proxies requests to third-party providers.

## Interview answer — deep senior

From a threat modeling perspective, understanding client-side secret exposure reveals common misconceptions:

1. **The Native C/C++ Illusion**: Some teams attempt to bypass this by moving the string into a C++ JNI library (`libkeys.so`) or breaking the string into byte arrays combined with XOR masks. These are merely obfuscation speed bumps. An analyst running Frida or Ghidra can locate the assembly instructions and extract the recombined string from memory during execution in minutes.

2. **Credential Stuffing & Quota Exhaustion**: When third-party private secrets are leaked from an APK, attackers scrape them to make automated API requests on the developer's billing account or exfiltrate private database records, causing massive financial and reputational liability.

3. **Rule of Thumb for Mobile Architects**: Treat any code and asset shipped inside an APK as publicly published on the internet. If exposing a key compromises customer data, financial balances, or cloud infrastructure, that key must never be compiled into the mobile build.

## How to answer in the interview

- **Why:** compilation copies the credential into an attacker-owned binary.
- **How:** inspect build artifacts and runtime use, then classify the key's privilege.
- **Trade-off:** backend proxy adds an integration step.
- **Failure case:** leaked key can authorize calls outside user context.
- **Production solution:** revoke, investigate, rotate, and remove private credentials from mobile builds.

## Deep-dive talking points

Prompt for APK artifact inspection, provider rotation, backend authority and distinction between public identifier and private key.

## Follow-up questions

- **Interviewer:** "Why is Google Maps API key safe to keep in AndroidManifest.xml?"
  **Answer:** "Because Google Maps APIs restrict usage by verifying the calling app's package name and SHA-1 signing certificate fingerprint on Google servers."

- **Interviewer:** "Can R8 obfuscation hide BuildConfig strings?"
  **Answer:** "No; R8 renames class and variable identifiers, but literal string constants remain completely unencrypted in the DEX string pool."

## Self-check rubric

Can I trace the secret into APK, describe full incident response and redesign provider access?

## References and reviewed-on date

- [Android build configuration](https://developer.android.com/build/gradle-tips) — build-time constants.
- [OWASP MASVS resilience](https://mas.owasp.org/MASVS/controls/MASVS-RESILIENCE-1/) — reverse-engineering limits.

Technically reviewed against primary documentation on 2026-10-13.
