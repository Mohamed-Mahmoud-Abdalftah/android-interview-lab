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

“The sandbox starts with an app UID, private storage, and Binder caller identity. Manifest permissions describe requested capabilities, while dangerous permissions require runtime consent. I prefer scoped APIs such as a system picker, check permission again before use, and handle revocation. Exported components and URI grants intentionally cross the sandbox and need review. A platform permission is not backend authorization.”

## Interview answer — deep senior

“I model the sandbox as a default isolation layer rather than a universal trust guarantee. The framework can enforce access to camera or location, but exported activities, providers, PendingIntents, and shared files add new attack surfaces. I audit the merged manifest and third-party SDK permissions, test denial/revocation paths, and apply least privilege. Rooted devices can weaken local assumptions. The backend independently authenticates the user and checks ownership for every sensitive operation; a client permission or local flag never grants financial authority.”

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

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
