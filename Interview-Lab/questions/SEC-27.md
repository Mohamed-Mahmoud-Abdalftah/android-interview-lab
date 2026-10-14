---
id: "SEC-27"
question: "An attacker modifies an APK and bypasses client-only checks. How should the backend defend itself?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "C"
phase: 3
priority: "P1"
order: 324
editorial_status: "reviewed"
---

# SEC-27

## Original interview question

An attacker modifies an APK and bypasses client-only checks. How should the backend defend itself?

## What the interviewer evaluates

- A repackaged APK can forge all client-only decisions.
- Backend reconstruction of identity, price, state and replay protection.

## Explanation in Arabic

مهاجم قام بتعديل الـ APK وتجاوز جميع الفحوصات الأمنية المحلية (Client-Side Checks). كيف يجب على الـ Backend حماية نفسه؟

1. وهم الأمان من جانب العميل (The Fallacy of Client-Only Validation):
   - أي فحص محلي يتم داخل كود أندرويد (مثل فحص الأسعار، فحص الرصيد، فحص الكوبونات، أو فحص الـ Root) يمكن لمهاجم تجاوزه بسهولة بتعديل سطر Smali واحد أو استخدام Frida.
   - **القاعدة الذهبية في هندسة الأمان**: **Never Trust the Client** (لا تثق في العميل أبداً؛ العميل هو بيئة معادية ومخترقة افتراضياً).

2. كيف يدافع الـ Backend عن نفسه بشكل قطعي؟
   - **إعادة حساب كل العمليات المنطقية على السيرفر**: السيرفر لا يستقبل "السعر النهائي" من التطبيق! يستقبل فقط معرّف المنتج (`productId`) والكمية، ويقوم السيرفر بجلب السعر من قاعدة البيانات وحساب الخصم والضرائب بنفسه.
   - **التحقق من توقيع التطبيق وسلامته عبر Play Integrity API**: يرسل السيرفر Nonce عشوائي، ويطلب من التطبيق شهادة Play Integrity. السيرفر يتحقق من Google أن الطلب قادم من APK أصلي موقع بشهادة الإنتاج ولم يتم التلاعب بملف الـ DEX.
   - **فحص الصلاحيات والـ RBAC على السيرفر**: كل API Endpoint تفحص هل الـ User ID المستخرج من الـ Token المصادق عليه يملك صلاحية الوصول لهذا المورد أم لا.
   - **كشف الشذوذ السلوكي (Behavioral Anomaly Detection)**: مراقبة سرعة الطلبات (Rate Limiting)، وفحص الموقع الجغرافي المستحيل (Impossible Travel)، وحظر الحسابات التي ترسل طلبات غير متناسقة.

## Practical walkthrough

المقارنة بين API معيب يثق في العميل و API مؤمن يفرض سلطة السيرفر المطلقة:
```kotlin
// ❌ تصميم كارثي: السيرفر يثق في حسابات العميل ومدخلاته الحساسة:
// إذا عدل المهاجم الكود وجعل totalAmount = 0.01$، السيرفر سيقبل العملية!
data class InsecureCheckoutRequest(
    val productId: String,
    val totalAmount: Double, // ثغرة: العميل يحدد المبلغ!
    val isDiscountApplied: Boolean // ثغرة: العميل يحدد الخصم!
)

// ✅ المعمارية الاحترافية: السيرفر هو مصدر الحقيقة الأوحد ولا يثق في العميل:
data class SecureCheckoutRequest(
    val productId: String,
    val quantity: Int,
    val promoCode: String?,
    val clientNonce: String
)

// منطق السيرفر (Backend Logic):
// 1. استخراج userId من الـ Cryptographically Verified JWT Token
// 2. جلب سعر المنتج الحقيقي من الـ Database
// 3. التحقق من صلاحية الكوبون ومطابقته للشروط في السيرفر
// 4. فحص الـ Nonce لمنع هجمات التكرار (Replay Attacks)
// 5. التحقق من شهادة Play Integrity المرفقة في هيدر الطلب
```

## Why it matters and how it works

Client input is untrusted regardless of app signing or obfuscation. The backend validates authenticated principal, authorization for resource, canonical pricing, legal state transition and replay/idempotency contract inside a transaction. Provider callbacks are verified via their documented mechanism and reconciled against server records.

## Worked example

A patched checkout sends `{itemId, amountMinor: 1, approved: true}`. The server reads product price and pending order from its database, rejects amount mismatch, creates one operation ID and calls the provider under an idempotency contract. It marks approved only after an authoritative provider result.

## Trade-offs and decision criteria

Recomputing business state server-side costs backend complexity but is necessary for financial authority. Integrity checks may add fraud signals and friction; their absence should follow a documented tiered policy rather than make forged values acceptable.

## Failure modes

Relying on a local signature or native SDK Boolean for charge approval permits tampering. Racing two identical requests can also create duplicates if server-side uniqueness is not atomic. Test modified APK requests and concurrent retries.

## Production perspective

Backend tests include changed amount, foreign order ID, stale state, duplicate operation and provider callback replay. Audit logs use opaque IDs; fraud monitoring flags inconsistent device signals without storing sensitive payloads.

## Interview answer — short

The backend must enforce a Zero-Trust architecture: never trust client-calculated prices, roles, or checks. Recalculate business invariants entirely on the server, validate Google-signed Play Integrity attestation tokens bound to server nonces, enforce strict rate limiting, and use cryptographic transaction signing.

## Interview answer — structured

When an attacker tampers with an APK to bypass client validations, backend security controls form the true line of defense.

First, with Server Authoritative Business Logic, Next, clients submit intentions (e.g. `productId`, `quantity`), never outcomes (e.g. `price`, `discountedTotal`). The server looks up product costs in authoritative databases, computes taxes and discounts, and initiates charges based solely on its own calculations.
**Cryptographic Attestation Verification**. The backend validates the Google Play Integrity token provided with critical requests. The server verifies Google's cryptographic signature, checking that `appRecognitionVerdict` equals `PLAY_RECOGNIZED` and the signing certificate SHA-256 matches the official release keystore. Modified/repackaged APKs will return `UNRECOGNIZED_VERSION`.
**Idempotency & Replay Protection**. Critical requests require a server-issued one-time cryptographically random nonce or UUID idempotency key stored in Redis with short TTL. Replayed requests are rejected.
**Strict Server-Side Authorization (RBAC/ABAC)**. Finally, every request verifies that the authenticated user identity extracted from the verified session token has explicit permission to access the target entity ID (preventing IDOR vulnerabilities).


## Interview answer — deep senior

From an enterprise fraud and threat modeling perspective, backend defenses incorporate multi-signal behavioral analytics.

First, with Behavioral Fraud Scoring, even if an attacker successfully patches an APK and mimics API payloads, machine learning fraud engines analyze request velocity, header entropy, TLS client fingerprinting (JA3/JA4 signatures), and impossible geographic travel intervals to score transaction risk. Next, with Step-Up Authentication Challenges, when risk signals indicate an anomalous client environment, the backend refuses to execute the requested action directly. Instead, it challenges the client with step-up verification (e.g., FIDO2 / Passkey biometric challenge or out-of-band push notification to a trusted secondary device).
Finally, with Tarpitting and Honeypots, backend APIs can embed decoy parameters or obscure endpoints. Modified clients invoking hidden deprecated endpoints expose automated tampering tools, triggering silent shadow-banning without alerting the attacker.


## How to answer in the interview

- **Why:** all client fields and checks can be forged.
- **How:** recompute canonical amount and allowed state server-side before payment.
- **Trade-off:** server validation adds reads and coordination.
- **Failure case:** trusting approved=true or a client price.
- **Production solution:** transactional idempotency plus provider reconciliation.

## Deep-dive talking points

Prompt for canonical server price, authorization, atomic uniqueness, provider confirmation and tampered-client tests.

## Follow-up questions

- **Interviewer:** "What is an IDOR vulnerability and how does server-side auth prevent it?"
  **Answer:** "Insecure Direct Object Reference occurs when a client changes an ID parameter (e.g., /account/123 -> /account/124); server-side auth validates that the token's user owns that specific ID."

- **Interviewer:** "What is TLS JA3 fingerprinting?"
  **Answer:** "It analyzes the client's TLS ClientHello packet (ciphers, extensions, curves) to identify the underlying HTTP client library, detecting automated python/curl bots masquerading as official Android apps."

## Self-check rubric

Can I reject a forged amount/status and describe duplicate-request protection?

## References and reviewed-on date

- [Play Integrity overview](https://developer.android.com/google/play/integrity/overview) — server-side decisions.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — one provider’s retry contract.

Technically reviewed against primary documentation on 2026-10-13.
