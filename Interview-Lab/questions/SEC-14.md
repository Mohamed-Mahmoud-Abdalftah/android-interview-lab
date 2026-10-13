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

## Practical walkthrough

لو access token مسروقة، قصر عمرها وscope يقلل الضرر، لكن لازم backend يقدر يبطل refresh token ويكتشف replay حسب session policy. خزّن access token في memory إن أمكن، وrefresh token محمية محليًا فقط لو persistence مطلوبة. عند logout امسح الاثنين محليًا واطلب revocation على السيرفر؛ مسح الهاتف وحده ما يبطل token موجودة عند مهاجم.

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

“I keep access tokens short-lived and preferably in memory, while protecting a refresh token only if persistent sessions are required. One session owner serializes refresh so concurrent 401 responses do not race token rotation. Logout clears local credentials and asks the backend to revoke the session; local deletion alone cannot invalidate a stolen bearer token. I also test invalid-grant, transient network errors and refresh replay so the UI does not confuse temporary failure with signed-out state.”

## Interview answer — deep senior

“I treat access and refresh tokens as bearer credentials with different lifetimes. The access token is short-lived and preferably memory-only; a persistent refresh token is protected locally only when the product needs session continuity. One session owner serializes refresh so concurrent 401 responses do not race token rotation. The backend maintains session identity, revocation and replay policy; clearing local state on logout is necessary but does not invalidate a stolen copy. I would keep tokens out of logs, test refresh failure and key loss, and require step-up for sensitive payments even with a valid access token. I would test two simultaneous requests receiving 401, a rotated refresh token arriving while logout begins, and a stolen refresh token replayed from another device. A process-local mutex prevents duplicate refresh attempts in one app process, but the server must own rotation and replay detection across devices. The UI should treat authoritative invalid-grant as signed out, while a temporary network failure should not accidentally erase a valid session.”

## How to answer in the interview

- **Why:** bearer tokens grant access wherever presented.
- **How:** minimize access-token life, protect refresh persistence, and rotate/revoke server-side.
- **Trade-off:** stronger session controls increase reauthentication and refresh traffic.
- **Failure case:** local deletion without server revocation leaves stolen credentials live.
- **Production solution:** session IDs, revocation policy, and replay monitoring.

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

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
