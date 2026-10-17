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

## Concept and technical explanation

The foundational law of mobile security architecture states: Never trust the client. On a client endpoint under attacker control, any client-side business logic, price calculations, entitlement checks, or root detections can be trivially neutralized by modifying Smali bytecode or hooking runtime methods with Frida. The backend must operate under zero-trust assumptions, treating all incoming requests as potentially forged. The backend reconstructs state by accepting only minimal operational intents (such as productId and quantity), fetching canonical prices and discounts directly from trusted database tables, validating transaction nonces and timestamps to defeat replay attacks, and enforcing strict state machine transitions. Client app authenticity is validated via server-to-server attestation through Play Integrity API.

## Practical walkthrough (English)

Server-side transaction reconstruction and anti-tamper verification architecture:
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
```

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

The backend must never trust the client, operating under the rule that any client-side check can be reversed or patched. The server must reconstruct all business state, computing authoritative prices, discounts, and eligibility directly from its trusted databases. Every transaction requires cryptographic nonces to prevent replays, paired with server-verified Play Integrity attestation.

## Interview answer — structured

When an attacker decompiles and modifies an APK, every client-side barrier including input validation, pricing calculations, entitlement checks, and root detection routines can be eliminated with a few bytecode edits.
Consequently, our backend architecture operates under an absolute zero-trust policy toward incoming mobile payloads.
The mobile application is treated as a remote presentation layer that only submits user intent, never authoritative state.
For example, in a checkout flow, the app transmits solely product identifiers and quantities.
The server queries its database to retrieve authentic prices, applies active discounts, computes taxes, and calculates the total payable amount.
To prevent replay attacks where an attacker captures and repeats a legitimate request, the server issues cryptographically random nonces and enforces single-use idempotency keys.
Furthermore, the backend validates client integrity out-of-band by requiring signed attestation tokens from Google Play Integrity API, verifying application signing signatures and licensing directly with Google servers.

## Interview answer — deep senior

The core law of distributed systems security is that client-side logic provides user convenience, while server-side logic provides system security.
On an endpoint under adversary control, decompilers like JADX and tools like APKTool allow modifying Smali bytecode to invert boolean checks or bypass local validation.
Our defense strategy centers on server-side state reconstruction and transaction invariants.
The backend never accepts computed financial figures, account privileges, or validation flags from mobile requests.
When processing transactions, the backend validates state machine transitions in the database, verifying that an account has sufficient balance and appropriate status before advancing order state.
To defeat automated tampering and botnets, we integrate Google Play Integrity API through server-to-server verification.
The mobile client requests a one-time cryptographic nonce from the backend, bound to the user id and transaction hash.
The client retrieves a signed integrity verdict from Google Play Services and sends it to our server.
Our backend decrypts and verifies the token, checking that appRecognitionVerdict matches our registered package and SHA-256 certificate digest, and verifying that deviceRecognitionVerdict confirms genuine Android hardware.
If any parameter deviates, the backend rejects the transaction, records the anomaly in our fraud prevention telemetry, and flags the associated user account for administrative review. We also enforce strict API schema validation on the gateway, immediately dropping payloads that submit unexpected properties or tampered client headers.

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
