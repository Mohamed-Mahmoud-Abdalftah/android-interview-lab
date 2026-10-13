---
id: "SEC-01"
question: "What is the Android application sandbox and permission model?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 298
editorial_status: "reviewed"
---

# SEC-01

## Original interview question

What is the Android application sandbox and permission model?

## What the interviewer evaluates

- Linux UID isolation, app-private files, Binder identity, and permission gates.
- The limits of permissions when the user, device, or another exported surface is hostile.

## Explanation in Arabic

كل app غالبًا ليه Linux UID مستقل؛ الـsandbox بيعزل ملفاتها وعملياتها عن apps تانية. الوصول للكاميرا أو الموقع بيمرّ من permission model ومن system service، وبعض الصلاحيات لازم موافقة runtime. العزل مش معناه إن كل بيانات جوّه app آمنة لو الجهاز rooted، ولا إن exported component آمن تلقائيًا. الـbackend يظل صاحب قرار authorization.

## Practical walkthrough

مثال: شاشة رفع إيصال تستخدم Photo Picker بدل طلب صلاحية قراءة كل الصور. ده يقلل مساحة الوصول، لكن الـURI اللي رجع من picker لازم تتعامل معاه على إنه input غير موثوق وتتحقق من الحجم والنوع قبل الرفع. ولو عندك `ContentProvider` exported، الـsandbox مش هيمنع app تانية من استدعائه؛ لازم تصاريح وauthorization على كل مسار.

## Why it matters and how it works

Android assigns an app identity and enforces file/process isolation through the kernel and framework. A manifest declaration states a requested capability; dangerous permissions also need runtime grant on supported versions. A system service checks the caller identity. Content providers, intents, URI grants, and shared storage create deliberate crossings of that boundary.

## Worked example

A photo upload flow requests only media access needed by its implementation, or uses the system photo picker when appropriate. It checks permission at use time and handles denial or later revocation. A private database stays in internal app storage; an exported provider needs its own authorization. This is a design example, not a tested program.

## Trade-offs and decision criteria

Least privilege reduces blast radius and review burden. Runtime prompts add friction, so prefer scoped platform pickers when possible. Permissions grant access to platform resources; they do not prove a user is allowed to read a server account.

## Failure modes

An app checks permission once during onboarding, then assumes it remains granted forever. Revocation can cause failure later. Recheck before use and handle denial. A mistakenly exported provider can leak data even though the database file itself is sandboxed.

## Production perspective

For a fintech app, keep customer data in app-private storage, request only necessary permissions, audit manifest exports and SDK permissions, and enforce account ownership on every backend request. Test denied and revoked permissions plus malicious intents.

## Interview answer — short

“Android gives each app an isolated identity and gates sensitive platform APIs with permissions. I request the minimum permission at the moment of need, handle denial and revocation, and still validate every cross-app and server boundary.”

## Interview answer — structured

“Android gives each app a UID and private storage, while permissions gate access to platform capabilities. I prefer scoped APIs such as Photo Picker, request dangerous permissions only when needed, and handle denial or revocation. The boundary changes when I export a component or grant a URI, so I inspect the merged manifest and test untrusted intents. A permission to use the camera does not authorize a transfer or another customer's data; the backend checks account ownership separately.”

## Interview answer — deep senior

“I start by identifying the boundary. The Android UID and framework permission checks protect private files and platform capabilities, but an exported component or URI grant deliberately crosses that boundary. For a receipt upload I would prefer Photo Picker, validate the selected content, and handle a revoked grant. I would inspect the merged manifest, including SDK-added exports, and test malformed intents. None of that authorizes a financial action: the backend still checks the signed-in user and ownership of the requested record. On a rooted device I assume local isolation can be weakened, so I keep the client’s authority narrow. For verification, I would revoke media access after selection, attempt an exported-provider read from another app, and send a deep link with an unexpected account ID. Those tests show whether the client handles platform grants safely; a separate API test proves the server rejects cross-account access. I would document the exact supported Android versions because permission and picker behavior can differ, while keeping the backend invariant constant.”

## How to answer in the interview

- **Why:** sandbox boundaries reduce accidental cross-app access.
- **How:** trace UID, permission check, URI grant, and exported component.
- **Trade-off:** a scoped picker reduces access but adds URI handling.
- **Failure case:** an exported provider leaks private rows.
- **Production solution:** audit merged manifest and enforce server ownership on every request.

## Deep-dive talking points

Trace one cross-UID data path through a provider or URI grant; distinguish platform permission checks from account authorization at the backend.

## Follow-up questions

- [SEC-18](../sec-18/): Why inspect an exported provider? **Answer:** it is an explicit cross-UID entry point; enforce caller and URI authorization.
- [SEC-23](../sec-23/): Does app-private storage solve backup exposure? **Answer:** no; backup and device-transfer policy are separate.

## Self-check rubric

Can I explain UID isolation, runtime permission denial, a cross-app entry point, least privilege, and why backend authorization remains separate?

## References and reviewed-on date

- [Android app sandbox](https://source.android.com/docs/security/app-sandbox) — UID-based isolation.
- [Android permissions overview](https://developer.android.com/guide/topics/permissions/overview) — declarations and runtime access.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
