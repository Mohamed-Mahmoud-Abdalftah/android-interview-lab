---
id: "SYS-07"
question: "Design a notification system with deep links."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 336
editorial_status: "reviewed"
---

# SYS-07

## Original interview question

Design a notification system with deep links.

## What the interviewer evaluates

Design notification delivery with server authority, deep links and security validation.

## Explanation in Arabic

Notifications تبدأ من server event له stable ID وrecipient، ثم push يوقظ التطبيق إن أمكن؛ push مش durable database ولا ضمان ترتيب/وصول. عند tap، PendingIntent/deep link تفتح destination وتتحقق من auth، account وresource permissions من backend. لو app كانت مقتولة أو المستخدم logged out، نعيد بناء state من repository ونوجّه لـlogin ثم الهدف إذا مصرح. قناة notification وأذونتها حسب Android version.

## Why it matters and how it works

Use notification payload as a hint/identifier, not trusted authorization or secret data. Persist user-visible inbox/history server-side if delivery matters. Android 13+ notification runtime permission affects display; channel configuration affects user control. Deep links must validate URI/arguments and avoid open redirects.

## Worked example

Conceptual deep-link contract; actual NavHost and PendingIntent flags must be configured per target SDK.

```kotlin
data class NotificationTarget(val eventId: String, val resourceId: String)
interface NotificationRouter {
    suspend fun resolve(target: NotificationTarget, session: Session): Route
}
// Resolve by authenticated server lookup; never trust a push payload
// as proof that the resource belongs to the current account.
```

## Trade-offs and decision criteria

Push is low latency and battery-efficient, but can be delayed, dropped or disabled; server inbox plus sync gives recoverability. Deep links improve UX but broaden attack surface. Notification content should minimize sensitive data on lock screen.

## Failure modes

Trusting a resource ID from a forged link can expose another user’s item. A notification tapped after logout can navigate to stale private content. Duplicate push can display twice without event IDs. Permission denial means no visible notification even though server event exists.

## Production perspective

A messaging app stores messages on backend, sends push with opaque event ID, deduplicates local display and on tap fetches authorized conversation state. After login it resumes destination; tests cover cold start, old app version, disabled notifications and malicious URI.

## Interview answer — short

“Push is a hint, not durable truth. I use stable event IDs, server-backed inbox state and a validated deep link that rechecks session and resource authorization on cold start. I handle notification permission and duplicate delivery.”

## Interview answer — structured

“I define notification delivery separately from navigation. The backend owns an event and sends a push containing a minimal opaque ID. Android may delay or drop push, so important content is available from a server inbox or sync endpoint. On tap, the app parses a validated deep link, restores session if needed and fetches the resource under current authorization. It does not trust the push payload as access control. I deduplicate events, configure channels and runtime notification permission where required, and test cold start and logout. Push is low latency and battery-efficient, but can be delayed, dropped or disabled; server inbox plus sync gives recoverability. Deep links improve UX but broaden attack surface. Notification content should minimize sensitive data on lock screen.”

## Interview answer — deep senior

“The system has several failure windows: push never arrives, arrives twice, user taps after account switch, app process is dead, or the resource is deleted. I make the server event store authoritative and push only a wake/display hint with a stable ID. The app uses an explicit PendingIntent and allowlisted route, validates arguments and checks backend authorization after login before rendering. I avoid putting secrets in notification text or extras, respect user channel/permission controls, and support in-app inbox recovery. Metrics distinguish server event creation, push provider acceptance, app receipt, display and open; none alone proves the user saw it. Tests cover forged deep links, duplicate push, cold start, process death and version skew. Use notification payload as a hint/identifier, not trusted authorization or secret data. Persist user-visible inbox/history server-side if delivery matters. Android 13+ notification runtime permission affects display; channel configuration affects user control. Deep links must validate URI/arguments and avoid open redirects. Trusting a resource ID from a forged link can expose another user’s item. A notification tapped after logout can navigate to stale private content. Duplicate push can display twice without event IDs. Permission denial means no visible notification even though server event exists. A messaging app stores messages on backend, sends push with opaque event ID, deduplicates local display and on tap fetches authorized conversation state.”

## Deep-dive talking points

Trace event creation to authorized destination and list delivery/visibility limits.

## Follow-up questions

- [SYS-18](../sys-18/): What if old app sees new payload? **Answer:** version the event contract and tolerate unknown fields/routes.
- [SYS-03](../sys-03/): What after logout? **Answer:** restore session and re-authorize target before display.

## Self-check rubric

Can I distinguish push from durable truth, validate deep links and handle duplicate/cold-start paths?

## References and reviewed-on date

- [Android notifications](https://developer.android.com/develop/ui/views/notifications) — channels and permission.
- [Android deep links](https://developer.android.com/training/app-links/deep-linking) — routing/security.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
