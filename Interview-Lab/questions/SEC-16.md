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

## Practical walkthrough

`CharArray` تسمح تمسح password بعد الاستخدام بـ`fill`, عكس `String` immutable. بس keyboard و`EditText` وencoder أو SDK ممكن يعملوا نسخ أخرى، فمسح array واحدة مش ضمان إزالة كل أثر من memory. استخدمها لو API يسمح، قلّل مدة الاحتفاظ، وما تحولهاش لـString لمجرد الراحة. السيرفر يعمل password hashing مناسب؛ الموبايل ما يخزنش كلمة المرور أصلًا.

## Why it matters and how it works

A mutable array gives control over one allocation. The caller must avoid converting it to String and must wipe it in a `finally` block after the consumer finishes. The runtime may copy values during input, encoding or TLS transfer, and GC can move objects, so exact erasure is not guaranteed.

## Worked example

Illustrative Kotlin scope. The caller gives up ownership of a `CharArray`; `authenticate` must consume it without retaining or converting it to `String`. Android UI widgets and network libraries may still make copies, so this is best-effort cleanup rather than guaranteed erasure.

```kotlin
suspend fun signIn(
    password: CharArray,
    authenticate: suspend (CharArray) -> Unit,
) {
    try {
        authenticate(password)
    } finally {
        password.fill('\u0000')
    }
}
```

## Trade-offs and decision criteria

CharArray reduces one memory-residence window but makes APIs less convenient. If an authentication SDK only accepts String, converting may be unavoidable; minimize lifetime and never persist or log it. Avoid inventing a fragile custom input widget solely to promise perfect erasure.

## Failure modes

Wiping the array before an asynchronous coroutine finishes corrupts the request; wiping only on success leaves failure paths. Use clear ownership/lifetime and a `finally` block after actual consumption, and test cancellation behavior.

## Production perspective

A finance login flow sends the password over validated TLS, never stores it after sign-in, disables sensitive logs and clears editable fields when appropriate. Security review documents residual copies in UI/framework libraries rather than asserting complete memory sanitization.

## Interview answer — short

“CharArray lets me overwrite one password buffer; String does not. It is a useful lifetime reduction, not a guarantee that Android or libraries made no other copies.”

## Interview answer — structured

“A `CharArray` can be overwritten in `finally` after the consumer finishes; an immutable `String` cannot be wiped in that way. I keep password handling in a narrow scope, avoid conversions and never persist or log it. This is best-effort exposure reduction because Android input widgets, encoders, libraries and the JVM may make copies. For an asynchronous SDK I make buffer ownership explicit so it is not cleared before consumption, and the server handles password verification with a dedicated salted password hash.”

## Interview answer — deep senior

“`CharArray` is useful because I can clear the array I own in a `finally` block; an immutable `String` cannot be wiped that way. I would keep the password in a narrow scope, pass it only to an API that consumes it promptly, and avoid converting it into `String`. I would not claim guaranteed zeroization: Android input widgets, encoders, libraries and the JVM may create copies outside that array. The larger control is to avoid storing the password at all and to keep it out of logs and crash data. Server-side password verification uses a dedicated salted password-hashing scheme. For an asynchronous authentication API, the buffer's owner must know when the consumer has finished; clearing it immediately after launching a request could corrupt the input while the SDK still reads it. Conversely, keeping it in a ViewModel field extends exposure. I would make the API contract explicit, test success, failure and cancellation cleanup, and document unavoidable framework copies. If the provider only accepts a String, I would state that limitation honestly and minimize its lifetime.”

## How to answer in the interview

- **Why:** mutable buffers permit explicit best-effort cleanup.
- **How:** keep a CharArray briefly and clear it in finally.
- **Trade-off:** platform inputs and libraries can make unmanaged copies.
- **Failure case:** converting to String negates the intended benefit.
- **Production solution:** avoid password persistence and choose APIs with controlled buffer handling.

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

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
