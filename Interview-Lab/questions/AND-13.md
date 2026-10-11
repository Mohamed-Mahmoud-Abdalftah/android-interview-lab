---
id: "AND-13"
question: "How do you handle runtime permissions and denial/permanent denial?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 43
editorial_status: "reviewed"
---

# AND-13

## Original interview question

How do you handle runtime permissions and denial/permanent denial?

## What the interviewer evaluates

- Request only a capability required for a user-initiated feature, at the moment of use.
- Handle grant, ordinary denial, repeated denial, revocation, and Settings return without trapping the user.
- Avoid treating `shouldShowRequestPermissionRationale()` as a universal permanent-denial oracle.

## Explanation in Arabic

قبل ما تطلب permission اسأل لو في API زي Photo Picker يغني عنها. لو لازم، اطلبها وقت ما المستخدم يبدأ الميزة، واشرح السبب بوضوح، وافحص الـgrant كل مرة قبل الاستخدام لأن المستخدم ممكن يسحبها من Settings. لو رفض، خلي باقي التطبيق شغال وقدم fallback مناسب. لو النظام ما بقاش يعرض dialog بعد رفض متكرر أو “don't ask again”، ما تعملش loop طلبات؛ وضّح إن الميزة محتاجة الإذن وقدّم مسار Settings باختيار المستخدم. `shouldShowRequestPermissionRationale()` وحدها مش دليل قاطع على permanent denial: ممكن ترجع false قبل أول طلب أو حسب سلوك النظام/الإصدار.

## Why it matters and how it works

Dangerous permissions need runtime grant on supported Android versions and can be revoked. The Activity Result `RequestPermission` contract gives a lifecycle-aware result; the app must still check permission at use time and handle the denied path. Rationale helps explain why a specific feature needs access; it is not a coercive gate. If the system stops showing the prompt after repeated denial, the app cannot grant itself access. Platform permission rules vary by API level and permission category, so code should follow current guidance for camera, location, media, notifications, and background location separately.

## Worked example

A nearby-store feature first checks coarse location permission. If granted, it loads stores; if denied, it offers manual city selection. Its Activity registers `RequestPermission()` unconditionally at creation, launches only after the user taps “Near me,” and handles false by showing the manual path. The permission check repeats when returning from Settings. This design example omits full Activity wiring; do not infer that `shouldShowRequestPermissionRationale()==false` uniquely means permanent denial.

## Trade-offs and decision criteria

Asking at onboarding is easy for code but often lacks user context and increases denial; just-in-time requests explain value. Precise location can improve results but coarse location may be sufficient and less intrusive. A system picker can avoid broad media access, but may not meet bulk background processing requirements. Settings navigation should be optional and explained; denying the feature must not make unrelated app functions unusable.

## Failure modes

An app asks repeatedly after every denial, causing a hostile loop. Another assumes permission remains granted forever and crashes after revocation. Treating false rationale as a permanent-denial flag on first launch misclassifies users. Requesting background location alongside foreground location can violate platform flow and confuse users. Test first request, one denial, repeated denial, Settings grant/revoke, and API-version differences on real devices.

## Production perspective

For a delivery app, keep address search usable manually and request location only when the user selects GPS assistance. Record aggregate permission funnel events without storing coordinates unnecessarily. A feature gate checks current grant before accessing location and handles `SecurityException` as defense in depth. The release test matrix covers target SDK and supported API levels, revocation while backgrounded, and the return path from Settings.

## Interview answer — short

“I ask for a dangerous permission only when a user needs the feature, explain why, handle denial with a usable fallback, and recheck at use time because grants can be revoked. After repeated denial I stop prompting in a loop and offer an optional Settings path.”

## Interview answer — structured

“I first see whether a scoped API avoids permission altogether. If not, I register a lifecycle-aware permission launcher, check current grant, show a contextual rationale when appropriate, and request only after a user action. Grant enters the feature; denial gets a non-blocking fallback. I do not assume shouldShowRequestPermissionRationale false proves permanent denial, because it has other states. If the system no longer presents a dialog, I explain an optional Settings route and check again on return. A false rationale result is ambiguous: it can occur before a first request as well as after a system policy suppresses prompts. I therefore track the user journey, offer a fallback and only suggest Settings when the app cannot request again. Permissions can be revoked later, so every use has a current check and safe error path.”
## Interview answer — deep senior

“Permission design is a product and platform contract. I minimize capability first, for example preferring a system picker to broad media permission when the use case allows it. A runtime request is made in context, via a lifecycle-aware launcher registered consistently, and the app remains useful on denial. Each access checks current grant and handles revocation races. I distinguish first request, rationale, repeated denial and Settings return without inferring permanent denial from a single boolean. I test across supported Android versions because permission categories evolve, and measure feature success without logging sensitive location data. Permission design begins with avoiding a permission when a scoped platform API can meet the need. For location, I might request coarse access only when the user taps Near me, while manual city selection remains available. I register the Activity Result launcher consistently, check grant at the point of use, and explain the benefit without trapping the user in repeated prompts. `shouldShowRequestPermissionRationale()` is a UI hint, not a universal permanent-denial oracle. Android permission categories and target SDK behavior change, so I test initial request, one and repeated denial, Settings return, revocation and background transitions across supported API levels. I avoid logging coordinates merely to measure the funnel.”
## Deep-dive talking points

Discuss permission minimization, rationale state ambiguity, repeated denial, revocation, Activity Result registration, coarse versus fine location, settings return, and API-version test coverage.

## Follow-up questions

- [AND-14](../and-14/): Why register the launcher every creation? **Answer:** pending results must be delivered correctly after Activity or process recreation.
- [SEC-01](../sec-01/): Is a runtime grant backend authorization? **Answer:** no; it only allows platform resource access under the Android permission model.
- [AND-18](../and-18/): What if the grant is revoked while backgrounded? **Answer:** recheck before use and handle denial or `SecurityException` on return.

## Self-check rubric

Name a permission-free alternative; describe a just-in-time request; handle first and repeated denial; explain rationale ambiguity; and test revocation and Settings return.

## References and reviewed-on date

- [Request runtime permissions](https://developer.android.com/training/permissions/requesting) — request timing, rationale, denial, and revocation.
- [Get a result from an activity](https://developer.android.com/training/basics/intents/result) — lifecycle-aware launcher registration.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The nearby-store flow is illustrative and was not Android-compiled.
