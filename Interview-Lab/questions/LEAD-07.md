---
id: "LEAD-07"
question: "How do you align mobile, backend, QA, and security teams on an API contract?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "B"
phase: 5
priority: "P2"
order: 462
editorial_status: "reviewed"
---

# LEAD-07

## Original interview question

How do you align mobile, backend, QA, and security teams on an API contract?

## What the interviewer evaluates

- Shared API contract across mobile/backend/QA/security.
- Error, retry, versioning and trust semantics before implementation.

## Explanation in Arabic

كيف تقوم بمواءمة وتنسيق العمل بين فرق الموبايل، والـ Backend، والـ QA، والأمان على عقد الـ API (API Contract) قبل كتابة الكود؟

1. معضلة التطوير التقليدي المنعزل (Siloed Development):
   - يكتب فريق الـ Backend الـ API على هواه بناءً على هيكل قاعدة البيانات (Data-centric).
   - بعد أسبوعين يتسلمه مهندس الموبايل ليكتشف أن الـ API يتطلب 5 استدعاءات متتالية لعرض شاشة واحدة، وأن حقول الـ Nullability غير واضحة، وأن استجابة الـ JSON ضخمة وتستهلك باقات المستخدمين!
   - النتيجة: إعادة كتابة الكود، وتأخر الإطلاق، وتبادل اللوم.

2. منهجية الـ API-First / Contract-Driven Development:
   - **1. الاجتماع المبكر لصياغة العقد (Contract Workshop)**: اجتماع مصغر يجمع مهندس الموبايل، ومهندس الـ Backend، وممثل الـ QA، ومهندس الأمان قبل كتابة سطر كود واحد.
   - **2. توثيق العقد بصيغة قياسية موحدة (OpenAPI / Swagger / Protocol Buffers)**:
     * تحديد أسماء الحقول بدقة، وأنواع البيانات، والـ Nullability الصريحة (هل الحقل قد يرجع `null`؟).
     * تحديد رموز الأخطاء (HTTP Status Codes) وهيكل كائن الخطأ الموحد (`ErrorCode`, `UserMessage`, `Retryable`).
   - **3. تصميم الـ API لتلبية تجربة المستخدم (UI-Driven API Design)**:
     * تطبيق نمط **Backend For Frontend (BFF)** أو نقاط نهاية مخصصة تجمع البيانات لشاشة الموبايل في طلب واحد لتقليل استهلاك البطارية والشبكة.
   - **4. فك ارتباط التطوير عبر الـ Mock Servers**:
     * بمجرد اعتماد ملف الـ OpenAPI، يقوم فريق الموبايل والـ QA بتوليد **Mock Server** (عبر Prism أو Postman أو MockWebServer).
     * يبدأ مهندس الموبايل في كتابة الواجهة واختبارها فوراً بالتوازي مع قيام الـ Backend ببناء الـ Services الحقيقية.

## Practical walkthrough

نموذج عقد API قياسي متفق عليه بصيغة OpenAPI ومخطط استجابة أخطاء موحد:
```yaml
# openapi-contract.yaml
paths:
  /v1/checkout/summary:
    get:
      summary: Retrieve checkout summary for mobile
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                required: [order_id, total_amount, currency, items]
                properties:
                  order_id: { type: string, example: "ord_9876" }
                  total_amount: { type: string, example: "149.99" } # String لتفادي مشاكل تقريب Float
                  discount_applied: { type: boolean }
                  promo_code: { type: string, nullable: true } # Nullable صريح لمنع NPE
        '422':
          description: Business validation error
          content:
            application/json:
              schema:
                type: object
                required: [error_code, message, is_retryable]
                properties:
                  error_code: { type: string, example: "ERR_INSUFFICIENT_STOCK" }
                  message: { type: string, example: "Item out of stock" }
                  is_retryable: { type: boolean, example: false }
```

## Why it matters and how it works

A written schema can validate shape but not all semantics. Consumer-driven examples or OpenAPI plus contract tests make breaking changes visible. Mixed mobile versions remain installed, so server should support old contracts through a defined sunset period.

## Worked example

Payment endpoint contract says POST with stable operationId and immutable amount, returns pending/approved/declined; timeout is unknown; GET by ID resolves status; duplicate same-key request returns prior status, changed payload is rejected. QA injects lost response and security checks that client amount is not trusted.

## Trade-offs and decision criteria

Detailed contracts take cross-team time but prevent expensive integration defects. Server flexibility helps old apps but increases maintenance; negotiate explicit version support and deprecation.

## Failure modes

Backend changes `pending` to `failed` and client treats it as decline, causing repeat payment. Contract tests catch enum change; a rollout plan supports both versions or uses additive fields.

## Production perspective

Hold joint review before implementation, publish schema and examples, run both consumer/provider contracts in CI, and monitor unknown/unrecognized response metrics after rollout.

## Interview answer — short

Align cross-functional teams using Contract-First API Design: co-author the specification (OpenAPI/Protobuf) collaboratively before implementation, explicitly defining nullability, error payload schemas, and pagination. Spin up mock servers from the contract so mobile, QA, and backend build and test concurrently without blocking.

## Interview answer — structured

Cross-functional API contract alignment requires adopting a Contract-First / API-First methodology:

1. **Collaborative Contract Co-Design**:
   - Convene a short alignment workshop with Mobile, Backend, QA, and Security leads. Design endpoints around mobile UI consumption patterns (minimizing roundtrips) rather than raw database relational schemas.

2. **Rigorous OpenAPI / Protobuf Specification**:
   - Formulate the contract using OpenAPI (Swagger) or Protocol Buffers. Explicitly codify:
     - **Nullability and Optionality**: Prevent Kotlin `NullPointerException` crashes by strictly documenting whether fields can be null.
     - **Numeric Precision**: Transmit monetary values as Strings or integer cents to avoid floating-point inaccuracies.
     - **Standardized Error Schemas**: Define a unified error envelope containing `error_code`, localized user message, and a boolean `is_retryable` flag.

3. **Parallel Execution via Contract Mocking**:
   - Export the verified spec into mock servers (MockWebServer, WireMock, or Prism). Mobile engineers develop and test against realistic mock payloads, and QA authors test matrices in parallel while backend engineers build database pipelines.

## Interview answer — deep senior

From an API governance and backward compatibility angle, contracts must enforce long-term survivability:

1. **The Asymmetry of Mobile Version Lifecycles**: A backend API can be updated in a single deployment, but legacy mobile app versions linger in production for years because users disable auto-updates. The contract must mandate **strict backward compatibility**: fields can be added, but existing fields must never be renamed, deleted, or have their types altered without incrementing the API path version (`/v2/`).

2. **Security & Data Minimization Auditing**: Security and compliance teams must audit the API contract against GDPR/CCPA regulations. Mobile payloads must never leak excessive PII or backend server details (e.g. leaking raw SQL stack traces in 500 error responses).

3. **Automated Contract Testing (Pact / Consumer-Driven Contracts)**: Modern engineering teams integrate Consumer-Driven Contract testing (such as Pact). Mobile test suites define contract expectations; if a backend engineer modifies a response field on a PR, the backend CI build breaks automatically before the breaking change reaches staging.

## How to answer in the interview

- **Why:** distributed failures cross team boundaries.
- **How:** agree on lost-response trace and ownership.
- **Trade-off:** upfront coordination versus incident ambiguity.
- **Failure case:** each team assumes another handles dedup.
- **Production solution:** versioned contract and joint failure tests.

## Deep-dive talking points

Prompt for semantic contract, mixed versions, lost response, ownership and contract tests.

## Follow-up questions

- **Interviewer:** "Why is backward compatibility far more critical for mobile APIs than web frontend APIs?"
  **Answer:** "Because users run old app versions indefinitely without updating, whereas web users receive the newest JavaScript bundle upon page refresh."

- **Interviewer:** "Why should monetary amounts never be transmitted as standard Float or Double in API JSON responses?"
  **Answer:** "Because binary floating-point representation causes precision loss and rounding errors; amounts should be passed as fixed strings or integer cents."

## Self-check rubric

Define request/response schema, errors, auth, idempotency and versioning with backend, QA and security; assign owners and prove agreement with a contract test.

## References and reviewed-on date

- [Android data-layer guide](https://developer.android.com/topic/architecture/data-layer) — repository/API boundaries.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — example retry semantics.

Technically reviewed against primary documentation on 2026-10-13.
