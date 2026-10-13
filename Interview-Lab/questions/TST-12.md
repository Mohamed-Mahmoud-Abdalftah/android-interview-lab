---
id: "TST-12"
question: "How do you test HTTP failures with MockWebServer or equivalent?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 407
editorial_status: "reviewed"
---

# TST-12

## Original interview question

How do you test HTTP failures with MockWebServer or equivalent?

## What the interviewer evaluates

- Controlled HTTP errors, latency and disconnects.
- Distinguishing client mapping from server-side guarantees.

## Explanation in Arabic

`MockWebServer` أو test server مشابه تتيح ردود HTTP متحكم فيها: status، headers، body ناقص، delay، disconnect، وترتيب requests. اختبر request method/path/body/headers غير الحساسة، ثم state الذي يراه المستخدم. في payment، أخطر حالة server سجّل approval وبعدها الاتصال وقع قبل response؛ العميل لا يجوز يفترض Declined أو يولّد ID جديدة.

## Practical walkthrough

اختبر أن intent المحفوظة تظل Unknown وأن status lookup أو retry تستخدم نفس key، ثم افصل backend integration test لإثبات dedup. Fake ترجع timeout قبل تنفيذ server effect لا تمثل هذه الحالة. لا تطبع Authorization أو card data في سجلات الاختبار، واعزل server per test حتى لا تنتقل responses بين الاختبارات.

## Why it matters and how it works

A local scripted server receives actual HTTP requests from the client stack, so serialization, interceptors, auth and timeout handling are exercised. Test response bodies and transport failures separately; a timeout after request arrival leaves remote outcome unknown.

## Worked example

Enqueue a 200 response whose body is cut off after server recorded a payment operation. Assert the Android client keeps the same operation ID, reports Unknown and performs status lookup rather than creating a new charge. Also assert Authorization is absent from test logs.

## Trade-offs and decision criteria

Local servers are deterministic and fast but do not reproduce TLS, CDN, backend transactions or provider semantics unless configured. Use backend contract tests and staging drills for those gaps.

## Failure modes

A test mocks Retrofit interface directly and misses an interceptor that retries POST automatically. A MockWebServer test observes actual request count and idempotency header. Distinguish 4xx permanent errors from retryable 5xx under API contract.

## Production perspective

CI covers auth expiry, rate limit, malformed responses, lost body and slow network with a local server. Provider sandbox tests validate unknown-outcome handling across system boundaries.

## Interview answer — short

“MockWebServer scripts HTTP responses and records requests, so I can test parsing, headers, retries and disconnects. It cannot prove the remote server actually deduplicates a payment.”

## Interview answer — structured

“I exercise the real OkHttp/Retrofit client against a local server. I script status codes, malformed bodies, delays and socket failures, then assert request count, headers and mapped domain errors. A payment response lost after the request was sent must become Unknown and retain the original operation ID. Separately, backend contract and provider sandbox tests prove idempotency and reconciliation behavior. ”

## Interview answer — deep senior

“I script transport failures as distinct cases. An HTTP 500 response is not the same as a socket disconnect, a truncated body or a timeout after the server committed. With MockWebServer or an equivalent controlled server I inspect the actual method, path, headers and body the client sent, then assert the repository’s result and UI state. For a payment call I deliberately let the server record the operation and drop the reply. The client must retain its durable ID and immutable amount, show an Unknown or pending state, and query status or retry under the same idempotency contract. I also test malformed JSON, unauthorized responses, a retry budget, cancellation, and that sensitive headers are redacted from logs. I reset the server and dispatcher per test to avoid order-dependent failures. This is an Android-client HTTP integration test: it proves serialization and local recovery behavior. It cannot guarantee that a real backend or payment provider has atomic same-key deduplication; that needs backend concurrency and provider sandbox tests.”

## How to answer in the interview

- **Why:** timeout, truncated response and HTTP rejection imply different outcomes.
- **How:** script each server response and inspect emitted request identity.
- **Trade-off:** controlled HTTP integration versus real backend guarantee.
- **Failure case:** fake timeout occurs before a simulated server commit.
- **Production solution:** after-commit fault test plus backend concurrency verification.

## Deep-dive talking points

Prompt for transport timing, real interceptor path, stable ID, status mapping and backend contract gap.

## Follow-up questions

- [TST-10](../tst-10/): How test backoff? **Answer:** combine scripted failures with virtual scheduler at policy layer.
- [TST-20](../tst-20/): Who proves no duplicate charge? **Answer:** backend/provider contract under lost response.

## Self-check rubric

Script HTTP status, truncated body and disconnect cases; inspect the emitted request and resulting state. For a lost payment reply, prove the client keeps the operation ID and queries status; say what only the backend can prove.

## References and reviewed-on date

- [OkHttp MockWebServer](https://github.com/square/okhttp/blob/master/README.md) — OkHttp official project documentation.
- [Android network testing](https://developer.android.com/training/testing) — integration test guidance.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
