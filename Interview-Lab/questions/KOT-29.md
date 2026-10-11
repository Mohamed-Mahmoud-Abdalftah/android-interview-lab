---
id: "KOT-29"
question: "Does storing sensitive values in native code prevent reverse engineering?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "C"
phase: 1
priority: "P1"
order: 29
editorial_status: "reviewed"
---

# KOT-29

## Original interview question

Does storing sensitive values in native code prevent reverse engineering?

## What the interviewer evaluates

Reject native-code secrecy claims and explain threat model, server authority, Keystore and minimization.

## Explanation in Arabic

لا. Native `.so` بتتوزع جوّه APK/AAB delivery، والمهاجم يقدر يفك الحزمة ويحلّل binary أو يراقب runtime/JNI calls. إخفاء string في C++ أو obfuscation يزوّد مجهود التحليل بس ما يمنعش استخراج secret موجود عند العميل. لو secret ثابت لكل المستخدمين وموجود في التطبيق، اعتبره exposed وصمّم backend يحفظه. لو token خاص بالمستخدم، قلّل عمره وصلاحياته، خزّنه حسب threat model باستخدام Android Keystore-backed key management، وقدّم revocation؛ Keystore تحمي key material بدرجات حسب الجهاز لكن ما تمنعش جهاز مخترق من استخدام التطبيق نفسه. صلاحيات الدفع والauthorization لازم تتأكد على server.

## Why it matters and how it works

The client device is under an attacker’s control in the threat model. Packaging a secret in native code changes reverse-engineering effort, not the trust boundary. Security depends on server-side authority and limiting value of compromised client material.

## Worked example

Conceptual architecture, no “secret-hiding” code: app obtains a short-lived user token from an authenticated server session; server holds the provider API key and calls the provider; app sends only permitted requests. For local key material, use Android Keystore APIs with recovery and invalidation design, never a hardcoded C++ string.

## Trade-offs and decision criteria

Native code may be justified for C++ libraries or measured compute work, not as a key vault. Keystore can improve local key protection but adds backup, invalidation, and device-capability constraints. Short-lived tokens and server checks reduce impact; they do not make a hostile client trustworthy.

## Failure modes

A payment provider secret is compiled into `libpayments.so`; extraction allows attackers to call provider APIs. Rotate the exposed key, move calls server-side, enforce server authorization and monitor abuse. Obfuscating the symbol is only defense-in-depth, not remediation.

## Production perspective

A fintech app keeps payment signing credentials on the server. The Android client uses a scoped session token, TLS, Keystore-backed local protection where appropriate, and server-issued one-time payment intents. Abuse detection and token revocation handle compromise.

## Interview answer — short

No. Native code shipped in the app can be reverse engineered or observed at runtime. I keep shared secrets and payment authority on the server, use scoped short-lived client tokens, and use Keystore only for appropriate device-local key protection.

## Interview answer — structured

Moving a literal from Kotlin to C++ changes its location, not its exposure: the `.so` is delivered to the attacker-controlled device. Static analysis and runtime hooking can recover the value or observe its use. I would move provider secrets to a backend, issue limited client credentials, and enforce authorization server-side. Android Keystore helps protect generated local keys under device guarantees, but does not turn a client into a trusted server. A reverse engineer can inspect the `.so` or observe the key when the app uses it. If the app needs a client token, I limit its scope and lifetime and provide revocation. The server still checks every privileged operation.

## Interview answer — deep senior

I would first classify the secret. A shared provider API key must never be in the APK, regardless of Kotlin, JNI, R8, or string encryption, because the app must eventually reconstruct it. User-specific tokens may be stored locally, but should be scoped, short-lived, revocable, and protected according to the threat model. Keystore makes key extraction harder on supported devices; a compromised runtime may still invoke allowed operations. For payment decisions I use server-side authorization, idempotency, monitoring, and rotation plans. Native code is an implementation choice, not a security boundary. I assume the device can be inspected and instrumented by its owner. A native library is packaged with the app and must reconstruct an embedded secret to use it, so static or dynamic analysis can recover it. Obfuscation may raise effort but cannot create a trustworthy boundary. I classify secrets: shared API keys and payment signing credentials belong on a server; user-scoped tokens can be held on device only with limited scope, expiry, revocation, and threat-model-appropriate storage. I would rotate a leaked embedded key, remove it from future clients, and monitor abuse. Native code remains appropriate for computation or library reuse, not as a substitute for backend authorization. I would also plan recovery after suspected exposure: rotate shared credentials, invalidate affected sessions where necessary, and monitor anomalous provider calls. Hiding a string in native code does not address those operational controls, while a backend can enforce them centrally.

## Deep-dive talking points

Discuss static versus dynamic analysis, APK extraction, native hooking, Keystore limits, token scope, key rotation and backend authority.

## Follow-up questions

- [KOT-24](../kot-24/): What is JNI useful for? **Answer:** native library reuse or justified computation, not durable secret concealment.
- [SEC-11](../sec-11/): What can Keystore protect? **Answer:** device-local key material and permitted operations, subject to device and runtime threat limits.

## Self-check rubric

Explain why C++ cannot hide an embedded key, propose a server design, and state one Keystore limitation.

## References and reviewed-on date

- [Android hardcoded cryptographic secrets](https://developer.android.com/privacy-and-security/risks/hardcoded-cryptographic-secrets) — embedded secrets are recoverable.
- [Android Keystore](https://developer.android.com/privacy-and-security/keystore) — key protection boundaries.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
