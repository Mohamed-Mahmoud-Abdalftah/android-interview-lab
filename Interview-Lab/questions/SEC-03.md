---
id: "SEC-03"
question: "Compare cryptographic keys, access tokens, refresh tokens, API keys, and passwords."
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 300
editorial_status: "reviewed"
---

# SEC-03

## Original interview question

Compare cryptographic keys, access tokens, refresh tokens, API keys, and passwords.

## What the interviewer evaluates

- Purpose, lifetime, exposure and rotation of five credential types.
- Why a bearer token is not a cryptographic key and an APK API key is not a secret.

## Explanation in Arabic

مقارنة شاملة بين 5 أنواع من بيانات الاعتماد الحساسة في Android:
المفاتيح التشفيرية، و Access Tokens، و Refresh Tokens، و API Keys، وكلمات المرور:

1. Cryptographic Keys (المفاتيح التشفيرية - مثل AES / RSA / ECC):
   - **طبيعتها**: أرقام باينري عشوائية تُستخدم للعمليات الرياضية (تشفير، فك تشفير، توقيع رقمي HMAC أو RSA).
   - **مكان حفظها**: حصرياً داخل `AndroidKeyStore` المدعوم عتادياً.
   - **فترة البقاء**: طويلة جداً (أشهر أو سنوات) حتى إعادة تثبيت التطبيق أو إبطالها.

2. Access Tokens (توكنز الوصول المؤقتة - مثل JWT Bearer Tokens):
   - **طبيعتها**: تصريح دخول قصير المدى يحمله العميل في كل طلب شبكة (`Authorization: Bearer <token>`).
   - **مكان حفظها**: في الذاكرة (RAM) أو في تخزين مشفر بمفتاح Keystore (Encrypted DataStore).
   - **فترة البقاء**: قصيرة جداً (15 دقيقة إلى ساعة واحدة) لتقليل ضرر التسريب.

3. Refresh Tokens (توكنز التجديد طويلة المدى):
   - **طبيعتها**: بيانات اعتماد سرية تُستخدم فقط لاستدعاء سيرفر المصادقة لإصدار Access Token جديد.
   - **مكان حفظها**: مخزن مشفر عالي الحماية (Android Keystore + Encrypted Storage).
   - **فترة البقاء**: طويلة (أيام أو أسابيع)، ويتم تجديدها مع كل استخدام (Refresh Token Rotation).

4. API Keys (مفاتيح واجهات الطرف الثالث - مثل Google Maps API Key):
   - **طبيعتها**: معرفات عامة للمشروع (Public Identifiers) لتتبع الاستهلاك وإصدار الفواتير لدى Google أو Firebase.
   - **تحذير خطير**: **ليست أسراراً (Not Secrets)**! أي مفتاح مدمج في ملف الـ APK يمكن استخراجه في 3 ثوانٍ بواسطة `apktool`! يجب تقييدها عبر لوحة تحكم Google Cloud بقيود الحزمة وبصمة التوقيع (Package Name + SHA-1 Restriction).

5. Passwords / PINs (كلمات المرور والرموز السرية للمستخدم):
   - **طبيعتها**: بيانات اعتماد يدخلها المستخدم لإثبات هويته.
   - **قاعدة ذهبية**: لا تحفظ كلمات المرور كـ Plaintext في التخزين المحلي أبداً! استبدلها بـ Session Tokens فور تسجيل الدخول، ومسح الـ CharArray من الذاكرة فوراً.

## Practical walkthrough

جدول المقارنة المعمارية بين أنواع بيانات الاعتماد الخمسة في Android:
```text
┌────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬─────────────────────────┐
│ نوع الاعتماد       │ الغرض المعماري       │ فترة الحياة (TTL)    │ مكان التخزين الآمن   │ الإجراء عند التسريب     │
├────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Cryptographic Key  │ تشفير وتوقيع رقمي    │ دائمة (حتى الإلغاء)  │ Android Keystore (HW)│ إبطال وإعادة توليد محلي │
│ Access Token       │ مصادقة طلبات الشبكة  │ قصيرة (15-60 دقيقة)  │ Encrypted DataStore  │ انتهاء الصلاحية التلقائي│
│ Refresh Token      │ تجديد Access Token   │ متوسطة (14-30 يوماً) │ Encrypted DataStore  │ إبطال الجلسة في السيرفر │
│ API Key (APK)      │ تتبع الاستهلاك والفوترة│ دائمة                │ BuildConfig/Manifest │ قيود SHA-1 + PackageName│
│ Password / PIN     │ إثبات هوية المستخدم  │ عابرة في الذاكرة     │ لا تُخزن أبداً محلياً│ تغيير كلمة المرور فوراً │
└────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴─────────────────────────┘
```

## Why it matters and how it works

Each credential has a distinct issuer, verifier, scope and revocation path. Passwords are verified server-side with an appropriate salted password-hashing scheme. Access/refresh tokens are issued and checked by the identity backend. Cryptographic keys may be generated in Android Keystore. A public mobile API key can identify a project but needs server restrictions and quotas.

## Worked example

In a checkout app, the backend authenticates the user and issues scoped access/refresh credentials. The app stores only what it needs; the refresh token is replaceable through sign-in and never enters logs. The payment-provider private key remains on the server. A bundled map-service identifier is restricted by provider controls, not treated as confidential.

## Trade-offs and decision criteria

Short access-token lifetimes limit exposure but increase refresh traffic. Refresh-token rotation improves revocation visibility but requires race handling. Keystore protects a local encryption key; it does not turn a bearer token into proof of device integrity.

## Failure modes

Putting a provider secret in BuildConfig ships it in the APK. Recording Authorization headers leaks bearer tokens. Reusing one symmetric key for unrelated purposes complicates rotation. Keep private provider operations behind a backend and use per-credential lifecycle rules.

## Production perspective

Document a credential inventory: owner, storage location, scope, lifetime, rotation, incident response. Build a redaction policy and server revocation endpoint. Test expired tokens, refresh races and logout across devices.

## Interview answer — short

Cryptographic keys perform local crypto inside Keystore. Access tokens authenticate API requests with short lifespans (15-60m). Refresh tokens obtain new access tokens and require rotation and secure storage. APK API keys are public client identifiers (not secrets) secured via Google Cloud SHA-1 restrictions. Passwords authenticate users and must never be stored locally.

## Interview answer — structured

A senior engineer establishes strict threat models and retention boundaries across these five distinct credential types.

First, with Cryptographic Keys (AES/RSA/ECC), mathematical keys used to encrypt data or sign tokens. Protected exclusively inside hardware-backed `AndroidKeyStore`. They never leave secure hardware and cannot be inspected over the network. Next, with Access Tokens (JWT / Bearer Tokens), ephemeral proofs of authorization granted to an authenticated client. They have short lifespans (15 to 60 minutes) to minimize damage if intercepted in memory. Kept in memory or encrypted persistent storage.
Additionally, with Refresh Tokens, long-lived credentials (days to months) used solely to issue fresh access tokens. Held in encrypted storage and rotated on every use (Refresh Token Rotation). Revocable server-side. With API Keys (Embedded in APK), client identifiers (Google Maps, Mixpanel, Firebase). **These are never secrets**. Anyone who downloads the APK can decompile it and read the string. They must be protected on the cloud provider side via IP, Package Name, and SHA-1 signing certificate restrictions.
Finally, with Passwords / PINs, user-provided secrets used to establish identity. Never store raw passwords on the device. Transmit over TLS to exchange for session tokens, wiping password buffers from RAM immediately.


## Interview answer — deep senior

The Architectural Fallacy of 'Hiding' Third-Party Backend Secrets in an APK:

Teams frequently ask: 'Where should I store our Stripe Secret Key or OpenAI Private API Key in our Android app? In NDK C++? Obfuscated with XOR? In local.properties?'

**The Senior Answer: Nowhere in the APK!**
A distributed Android APK is entirely in the hands of the client (attacker). No amount of ProGuard, NDK C++ compilation, or XOR encoding will prevent an attacker with Frida, Ghidra, or Wireshark from extracting the private key. Private API keys must reside **exclusively on your backend server**. The Android client authenticates to your backend with a user session token, and your backend proxies requests to Stripe or OpenAI using the private key.


## How to answer in the interview

- **Why:** calling everything a secret hides its authority.
- **How:** classify each by issuer, storage, scope, expiry, rotation, and revocation.
- **Trade-off:** shorter sessions improve exposure limits but add refresh traffic.
- **Failure case:** shipping a privileged provider key in an APK.
- **Production solution:** server-own private keys and rotate/revoke sessions explicitly.

## Deep-dive talking points

Classify each credential by issuer, holder, scope, revocation and lifetime; explain why an APK API key is not equivalent to a backend private key.

## Follow-up questions

- **Interviewer:** "Why is an APK API key like Google Maps safe to ship in an APK?"
  **Answer:** "Because Google Maps verifies requests by checking the client's HTTP Referer or Android Package Name and SHA-1 certificate fingerprint against the Google Cloud Console allowlist."

- **Interviewer:** "What is the difference between an Access Token and an API Key?"
  **Answer:** "An API key identifies the client application or project; an Access token identifies a specific authenticated user session with specific scopes."

## Self-check rubric

Can I name issuer, verifier, lifetime, storage, and revocation for each of the five credential types?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key operations.
- [OWASP MASVS authentication](https://mas.owasp.org/MASVS/controls/MASVS-AUTH-1/) — authentication controls.

Technically reviewed against primary documentation on 2026-10-13.
