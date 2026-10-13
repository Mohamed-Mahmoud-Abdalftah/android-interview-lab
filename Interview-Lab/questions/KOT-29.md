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

## Practical walkthrough

لو provider key مكتوبة في `libpayments.so`، attacker يقدر يفتح APK، يعمل static analysis أو يراقب الـJNI call وقت الاستخدام. حتى لو string متشفّرة، التطبيق لازم يفكها ومعاه material الفك؛ فده إخفاء مش حماية جذرية. خطوة remediation: rotate المفتاح، انقل provider calls للbackend، خليه يفحص user authorization وlimits، وراقب abuse. لو عندك device-local key، Android Keystore ممكن تمنع extraction حسب الجهاز والkey properties، لكنها ما تمنعش مهاجم متحكم في runtime من طلب عمليات مسموحة. token client لازم تكون قصيرة العمر، محدودة scope، وقابلة للإبطال؛ لا تخزن raw card/PIN data.

## Trade-offs and decision criteria

Native code may be justified for C++ libraries or measured compute work, not as a key vault. Keystore can improve local key protection but adds backup, invalidation, and device-capability constraints. Short-lived tokens and server checks reduce impact; they do not make a hostile client trustworthy.

## Failure modes

A payment provider secret is compiled into `libpayments.so`; extraction allows attackers to call provider APIs. Rotate the exposed key, move calls server-side, enforce server authorization and monitor abuse. Obfuscating the symbol is only defense-in-depth, not remediation.

## Production perspective

A fintech app keeps payment signing credentials on the server. The Android client uses a scoped session token, TLS, Keystore-backed local protection where appropriate, and server-issued one-time payment intents. Abuse detection and token revocation handle compromise.

## Interview answer — short

No. A native library is shipped to the device and can be inspected or instrumented. Shared provider secrets belong on the server. I use scoped, short-lived client credentials and Keystore for appropriate local keys, while server authorization remains decisive.

## Interview answer — structured

Moving a literal from Kotlin to C++ changes the effort of extraction, not the trust boundary. The native library is delivered with the app, and its use can be observed at runtime even if the string is obfuscated. I classify the value: shared payment credentials must stay server-side, while a user-specific token can be short-lived, scoped, and revocable. Android Keystore may protect generated local key material under device guarantees but cannot make a compromised client authoritative. If a key was already embedded, I rotate it, move the provider call to the backend, monitor misuse, and verify each privileged action there. I never claim native code prevents reverse engineering.

## Interview answer — deep senior

I would first classify the secret. A shared provider API key must never be in the APK, regardless of Kotlin, JNI, R8, or string encryption, because the app must eventually reconstruct it. User-specific tokens may be stored locally, but should be scoped, short-lived, revocable, and protected according to the threat model. Keystore makes key extraction harder on supported devices; a compromised runtime may still invoke allowed operations. For payment decisions I use server-side authorization, idempotency, monitoring, and rotation plans. Native code is an implementation choice, not a security boundary.

If an existing APK already contains a provider key inside a `.so`, I treat it as compromised: rotate it, move the provider call to a backend, and monitor use of the old credential. Obfuscation or splitting a string across native functions may slow inspection but the client must reconstruct it to use it, and runtime instrumentation can observe that point. A device-local key generated in Android Keystore can reduce extractability under supported hardware and policy, yet a hostile runtime may still invoke permitted operations. Server authorization and scoped, revocable tokens limit damage; raw card or PIN data should never be used as client-side hiding material.

## How to answer in the interview

- **Why:** Evaluate realistic attack vectors and dispel the myth that native C/C++ code provides unbreakable secret storage.
- **How:** Recognize that any secret shipped inside an APK can be extracted via static analysis (strings, disassemblers) or dynamic memory inspection (Frida, debuggers).
- **Trade-offs:** Obfuscation and native storage increase reverse engineering effort but provide zero cryptographic confidentiality against determined attackers.
- **Failure cases:** Storing private encryption keys, database passwords, or master payment credentials in native `.so` libraries, leading to complete secret compromise.
- **Production solution:** Keep sensitive business logic and credentials on secure backend servers, use short-lived scoped tokens, and authenticate devices using Google Play Integrity.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
