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

`MockWebServer` أو equivalent يخلينا نرسل responses محددة: 401، 429، 500، malformed JSON، delay أو connection drop، ونفحص request headers/body. ده يختبر Retrofit/OkHttp adapter وretry mapping من غير backend حي. لكنه لا يثبت server idempotency أو provider approval؛ محتاج contract/integration منفصل.

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

“I design HTTP tests around failure timing: before connection, after request write, after server commit before response, and partial response. The client cannot distinguish all of these, so its policy must be safe under ambiguity. MockWebServer catches interceptor mistakes such as automatic retry with a fresh key, tests auth refresh and `Retry-After` interpretation, and lets me inspect redacted requests. It does not simulate server atomicity or issuer decisions, so I run integration tests against a controlled backend and test the provider’s actual idempotency window.”

## Deep-dive talking points

Prompt for transport timing, real interceptor path, stable ID, status mapping and backend contract gap.

## Follow-up questions

- [TST-10](../tst-10/): How test backoff? **Answer:** combine scripted failures with virtual scheduler at policy layer.
- [TST-20](../tst-20/): Who proves no duplicate charge? **Answer:** backend/provider contract under lost response.

## Self-check rubric

Can you explain the mechanism, reproduce the example, justify the trade-off, identify the failure case, and answer both follow-ups for this question?

## References and reviewed-on date

- [OkHttp MockWebServer](https://github.com/square/okhttp/blob/master/README.md) — OkHttp official project documentation.
- [Android network testing](https://developer.android.com/training/testing) — integration test guidance.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
