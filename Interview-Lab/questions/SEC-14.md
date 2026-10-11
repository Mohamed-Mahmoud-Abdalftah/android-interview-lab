---
id: "SEC-14"
question: "Where should access and refresh tokens be stored and how are they revoked?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 311
editorial_status: "reviewed"
---

# SEC-14

## Original interview question

Where should access and refresh tokens be stored and how are they revoked?

## What the interviewer evaluates

- Access/refresh token scope and storage minimization.
- Server revocation, rotation races and logout across process death.

## Explanation in Arabic

Access token قصير العمر غالبًا يتحفظ في memory لو ده مناسب لتجربة المستخدم؛ refresh token أكثر حساسية لأنه يطلع access tokens جديدة. لو لازم يبقى بعد process death، خليه في app-private storage مع حماية حسب threat model وbackup policy واضحة. Logout الحقيقي مش مسح المحلي بس: لازم server يبطل grant/session، والـapp يمسح copies ويوقف refresh jobs.

## Why it matters and how it works

Token validity is determined by the issuer, not by local encryption. A refresh endpoint should enforce rotation/reuse detection according to the server design. Concurrent 401 responses can race to refresh and invalidate one another; serialize refresh for one session and recheck the latest token before making a new request.

## Worked example

In an account app, an OkHttp authenticator delegates refresh to one session repository. That repository uses a mutex around the refresh state, persists a rotated refresh token before releasing waiting calls, and clears state after an authoritative invalid-grant response. The mutex is only process-local; server policy handles multi-device races.

## Trade-offs and decision criteria

In-memory access tokens reduce persistence exposure but require refresh after process death. Keystore-backed local storage raises extraction cost but adds key-loss behavior. Long-lived sessions improve convenience while increasing abuse window; use server revocation and device/session visibility.

## Failure modes

If logout only removes a DataStore value, a copied refresh token may still work. If `CancellationException` is swallowed in refresh logic, canceled requests may continue unexpectedly. Handle 401 storms, revoked grants and lost rotation responses without retry loops.

## Production perspective

Production logout coordinates local clearing, cancellation of pending authenticated work, backend revocation and redacted audit events. On offline logout, locally block further use and queue/retry revocation under an explicit server policy; do not claim remote revocation already succeeded.

## Interview answer — short

“Keep access tokens short-lived and minimize persistence; protect a necessary refresh token with an explicit recovery plan. Logout requires server-side revocation as well as local clearing, and refresh must be race-safe.”

## Interview answer — structured

“Access tokens authorize API calls and can often live in memory. A refresh token persists only if the product needs a durable session; then I use app-private storage, a threat-modelled protection layer and backup exclusions. The server owns expiry, rotation and revocation. I serialize local refresh for one session so parallel 401 responses do not rotate the token twice, and I distinguish a transient network failure from an authoritative invalid grant. Logout clears local state and requests server revocation. I would serialize refresh for one local session and compare a session generation before saving a rotated token. Otherwise parallel 401s or a late response after logout can resurrect credentials. The issuer controls revocation; encrypted local storage only reduces one exposure path. Offline logout should block local use while remote revocation is still pending.”
## Interview answer — deep senior

“I model session state as an issuer-controlled grant with replaceable local copies. A single-flight refresh path coordinates parallel requests, persists a successful rotated credential before waking waiters, and compares session generation so an old response cannot resurrect a logged-out session. Process death is handled by durable storage only for the refresh token when required; an unavailable Keystore key forces sign-in. If logout occurs offline, the UI and local requests are blocked immediately while server revocation remains pending and observable. Server expiry, token rotation/reuse policy and per-device session controls limit damage from a copied bearer token. In a production session repository I keep access credentials short-lived and avoid persistence where feasible. A refresh credential persists only if the product needs session continuity, in app-private storage with a key-loss and backup policy. Concurrent requests join one refresh operation; after a successful rotation, the new credential is committed before waiting calls resume. An authoritative invalid-grant response clears state, whereas a transient network failure does not prove revocation. Logout increments the local session generation, cancels pending authenticated work and asks the server to revoke the grant; stale refresh responses cannot overwrite that newer state. On a compromised device tokens may be observed at use time, so sensitive transactions still require backend ownership checks and, where justified, step-up authentication.”
## Deep-dive talking points

Trace login, refresh rotation, concurrent 401 handling, logout and server-side revocation; describe how a leaked refresh token is invalidated.

## Follow-up questions

- [SEC-13](../sec-13/): What if the encryption key is lost? **Answer:** clear the replaceable token and re-authenticate.
- [SEC-15](../sec-15/): Where else can tokens leak? **Answer:** headers in logs, analytics, crash reports and screenshots.

## Self-check rubric

Can I explain token lifetime, storage, single-flight refresh, offline logout and authoritative server revocation?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — local key protection.
- [OWASP MASVS authentication](https://mas.owasp.org/MASVS/controls/MASVS-AUTH-1/) — authentication and session controls.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
