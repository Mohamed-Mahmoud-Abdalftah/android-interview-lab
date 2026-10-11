---
id: "SEC-16"
question: "Why might CharArray be preferable to String for passwords, and what are its limitations?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 313
editorial_status: "reviewed"
---

# SEC-16

## Original interview question

Why might CharArray be preferable to String for passwords, and what are its limitations?

## What the interviewer evaluates

- Why immutable String cannot be wiped deliberately.
- Practical limitations of CharArray, copies and Android UI/runtime paths.

## Explanation in Arabic

`String` immutable؛ لو password اتخزن فيها مش قادر تمسح نفس memory buffer بإرادتك، والـGC توقيته مش مضمون. `CharArray` تسمح `fill('\u0000')` بعد الاستخدام، فبتقلل مدة وجود نسخة معينة. لكن keyboard، `EditText`، copies، JNI وnetwork library ممكن يعملوا نسخ تانية؛ ما ينفعش نقول إن `CharArray` ضمان لمسح كلمة السر من كل memory.

## Why it matters and how it works

A mutable array gives control over one allocation. The caller must avoid converting it to String and must wipe it in a `finally` block after the consumer finishes. The runtime may copy values during input, encoding or TLS transfer, and GC can move objects, so exact erasure is not guaranteed.

## Worked example

Illustrative Kotlin scope: `val password: CharArray = readPassword(); try { authenticate(password) } finally { password.fill('\u0000') }`. This assumes `authenticate` consumes synchronously and does not retain or copy the array; a real Android UI input pipeline needs separate inspection.

## Trade-offs and decision criteria

CharArray reduces one memory-residence window but makes APIs less convenient. If an authentication SDK only accepts String, converting may be unavoidable; minimize lifetime and never persist or log it. Avoid inventing a fragile custom input widget solely to promise perfect erasure.

## Failure modes

Wiping the array before an asynchronous coroutine finishes corrupts the request; wiping only on success leaves failure paths. Use clear ownership/lifetime and a `finally` block after actual consumption, and test cancellation behavior.

## Production perspective

A finance login flow sends the password over validated TLS, never stores it after sign-in, disables sensitive logs and clears editable fields when appropriate. Security review documents residual copies in UI/framework libraries rather than asserting complete memory sanitization.

## Interview answer — short

“CharArray lets me overwrite one password buffer; String does not. It is a useful lifetime reduction, not a guarantee that Android or libraries made no other copies.”

## Interview answer — structured

“A Java/Kotlin String is immutable, so the app cannot reliably wipe its characters after use. A CharArray can be overwritten in finally once the authentication call has consumed it. I avoid creating String copies and never log or persist the password. But input widgets, encoders, libraries and the runtime may copy it, so I describe this as exposure reduction rather than complete erasure. I also handle cancellation and asynchronous ownership correctly. The array must stay owned until the authentication consumer has finished, including asynchronous work; wiping it too early corrupts the request. I use a `finally` block for the buffer I control, avoid unnecessary String conversion and recognize that input widgets or libraries may already have copies. The main objective is shorter exposure, not perfect erasure.”
## Interview answer — deep senior

“I would trace the password’s entire lifetime: keyboard and input widget, validation, encoding, network request and cleanup. CharArray only gives deterministic overwrite of one buffer, and an async function must not retain it after the caller wipes it. I would design a synchronous consumption boundary or explicit owned copy with cleanup, use TLS, avoid telemetry and persistence, and rely on server-side password verification controls. On a rooted device, a hook may capture the value at input or transmission regardless of local wiping, so this is defense in depth. I would trace a password from keyboard entry through UI validation, encoding, network client and cleanup. A mutable CharArray gives the app a way to overwrite that particular allocation, unlike an immutable String, but it cannot erase copies inside Android input components, TLS buffers or JNI. If an API accepts only String, I minimize its lifetime and ensure it never enters persistent state or telemetry. The timing of cleanup matters: a coroutine that still references the array must not observe it wiped midway, and cancellation/error paths still need cleanup once consumption ends. On a rooted device, hooking at entry or send can reveal the value despite local hygiene. The backend uses appropriate password verification and rate limiting; the app does not claim deterministic memory sanitization.”
## Deep-dive talking points

Explain immutable String copies versus wipeable mutable buffers, then identify JVM copies, keyboard/IME paths and libraries that defeat perfect zeroization.

## Follow-up questions

- [SEC-17](../sec-17/): Does wiping one array clear all copies? **Answer:** no, trace every transform and library boundary.
- [SEC-15](../sec-15/): What is a more common production leak? **Answer:** logs or crash/analytics SDKs.

## Self-check rubric

Can I explain immutability, wiping one buffer, asynchronous ownership and residual copies without promising perfect erasure?

## References and reviewed-on date

- [OWASP MASVS storage](https://mas.owasp.org/MASVS/controls/MASVS-STORAGE-1/) — sensitive data minimization.
- [Android sensitive data guidance](https://developer.android.com/privacy-and-security/security-best-practices) — handling sensitive information.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
