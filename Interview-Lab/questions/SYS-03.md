---
id: "SYS-03"
question: "Design login, session management, and secure token refresh."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 332
editorial_status: "reviewed"
---

# SYS-03

## Original interview question

Design login, session management, and secure token refresh.

## What the interviewer evaluates

Design secure login/session lifecycle and race-safe token refresh.

## Explanation in Arabic

نبدأ من backend auth contract: access token قصير العمر، refresh policy، revocation، session generation وdevice risk. Android تخزن أقل قدر لازم في storage مناسب مع backup/threat model؛ APK أو Keystore مش server secret vault. Interceptor يضيف token، refresh coordinator يعمل single-flight عند 401 مع recheck بعد lock. logout يمسح local session ويمنع response متأخرة من إحياءها، والسيرفر يلغيها حسب العقد.

## Why it matters and how it works

Session state is a state machine: signed out, authenticating, active, refreshing, expired. Token refresh is per session and must handle concurrent 401s, network failure, permanent rejection and logout race. UI derives destination from session state. Sensitive endpoints need TLS; do not log credentials.

## Worked example

Conceptual Kotlin state model; real credential storage and backend revocation are product-specific.

```kotlin
sealed interface SessionState {
    data object SignedOut : SessionState
    data class Active(val generation: Long) : SessionState
    data class Refreshing(val generation: Long) : SessionState
    data object Expired : SessionState
}
// A refresh result commits only if generation is still current.
```

## Trade-offs and decision criteria

Bearer tokens simplify API calls but theft gives access until expiry/revocation; short lifetimes increase refresh pressure. A session-scoped coordinator adds complexity but prevents rotation races. Biometric unlock protects local UX but is not backend authentication by itself.

## Failure modes

Two concurrent refreshes can invalidate each other. A late refresh after logout can restore old credentials. Saving refresh token in backup without key policy can leak or become unreadable. An embedded client secret is extractable from APK.

## Production perspective

A finance app uses backend-bound session IDs, TLS, short-lived access token, controlled refresh, generation-aware logout and server revocation. Tests force simultaneous 401s and process restart; telemetry excludes secrets and monitors refresh failures.

## Interview answer — short

“I model session state explicitly, store credentials under a threat model, serialize refresh per session and use a generation check to prevent late results after logout. Backend remains authority for revocation; the app never embeds a trusted secret.”

## Interview answer — structured

“Login is more than saving a token. I define backend-issued access/refresh credentials, expiration and revocation behavior, then expose an explicit session state to UI. Requests attach access tokens at the network boundary. Concurrent 401s use one refresh coordinator that rechecks current token under a lock and saves the pair atomically. Logout clears local state, cancels session-owned work and increments a generation so a late refresh cannot resurrect the session. I avoid logging tokens and do not treat Keystore or an APK resource as a substitute for server trust. Bearer tokens simplify API calls but theft gives access until expiry/revocation; short lifetimes increase refresh pressure. A session-scoped coordinator adds complexity but prevents rotation races. Biometric unlock protects local UX but is not backend authentication by itself.”

## Interview answer — deep senior

“I would draw the full session state machine and its races. The backend authenticates and revokes; Android holds only what it needs, with storage and backup choices based on threat model. Access tokens are attached to protected calls; a bounded single-flight refresh handles simultaneous 401s. A transient offline refresh failure is different from permanent invalid credentials, so I do not falsely log the user out. A generation counter guards logout/account switch against late network responses. Navigation derives from current session state, while stale caches and pending work are partitioned by account. I test process death, token rotation, clock skew, concurrent refresh, logout during refresh and server revocation, and I redact credentials from all telemetry. Session state is a state machine: signed out, authenticating, active, refreshing, expired. Token refresh is per session and must handle concurrent 401s, network failure, permanent rejection and logout race. UI derives destination from session state. Sensitive endpoints need TLS; do not log credentials. Two concurrent refreshes can invalidate each other. A late refresh after logout can restore old credentials. Saving refresh token in backup without key policy can leak or become unreadable. An embedded client secret is extractable from APK. A finance app uses backend-bound session IDs, TLS, short-lived access token, controlled refresh, generation-aware logout and server revocation.”

## Deep-dive talking points

Trace simultaneous 401s, transient failure, permanent revocation and logout race.

## Follow-up questions

- [DAT-19](../dat-19/): How serialize refresh? **Answer:** shared single-flight with recheck and generation-safe commit.
- [SYS-10](../sys-10/): Why explicit states? **Answer:** to prevent illegal transitions such as Active after logout.

## Self-check rubric

Can I protect credentials, define backend authority and test refresh/logout races?

## References and reviewed-on date

- [Android security configuration](https://developer.android.com/privacy-and-security/security-config) — TLS trust.
- [Android architecture guide](https://developer.android.com/topic/architecture) — SSOT/state ownership.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
