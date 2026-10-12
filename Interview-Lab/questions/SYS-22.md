---
id: "SYS-22"
question: "A feature flag accidentally enables a broken security-sensitive path. How do you contain the impact?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "C"
phase: 4
priority: "P1"
order: 351
editorial_status: "reviewed"
---

# SYS-22

## Original interview question

A feature flag accidentally enables a broken security-sensitive path. How do you contain the impact?

## What the interviewer evaluates

Contain accidental activation of broken security-sensitive feature flag.

## Explanation in Arabic

لو flag فتحت path أمنية مكسورة، نوقف server endpoint/authorization path فورًا؛ client flag وحدها لا تكفي لأن APK ممكن تكون offline أو tampered أو config cached. نجمّد rollout، نحدد cohorts/versions المتأثرة، نراجع logs من غير أسرار، ونصلح/نلغي sessions أو tokens حسب التهديد. العمليات الجارية تتحول لحالة Pending/reconciliation، ثم نعمل postmortem واختبارات regression.

## Why it matters and how it works

Incident sequence: server-side deny/kill, client disable, assess exposure and revoke credentials if needed, preserve evidence, notify according to policy, patch and staged re-enable. Use safe default and short TTL for future flags, but never let a flag grant backend privilege. Version skew means older clients need server enforcement.

## Worked example

Conceptual server/client guard, not actual authorization code; backend check is mandatory.

```kotlin
data class FeatureDecision(val enabledForUi: Boolean)
fun mayShowButton(config: FeatureDecision) = config.enabledForUi
// Backend independently authorizes every sensitive request;
// disabling the server route contains offline or modified clients.
```

## Trade-offs and decision criteria

A hard server block minimizes exposure but can interrupt valid in-flight users; provide clear error/Pending handling. Client disable improves UX but propagates slowly. Emergency app release is slower but may be needed for local data leak; choose containment by threat model.

## Failure modes

Only switching remote config to false leaves cached/offline clients on vulnerable path. Deleting logs prematurely loses incident evidence. Rotating credentials without coordinating workers can produce confusing retries. Re-enabling without regression tests repeats incident.

## Production perspective

A fintech team blocks a vulnerable transfer endpoint, halts rollout, identifies affected operation IDs, reconciles ledger, revokes exposed tokens if necessary and ships patched client. Metrics confirm requests are denied server-side before staged re-enable.

## Interview answer — short

“For a security-sensitive flag incident I enforce containment on the backend first, then disable client exposure, audit affected operations and credentials, reconcile in-flight state and stage a tested fix. A client flag is not an authorization boundary.”

## Interview answer — structured

“I assume the client flag can be stale or modified. I stop the sensitive server path or tighten authorization immediately, then turn off the client flag to improve UX. I identify affected versions/cohorts and operation IDs, preserve incident evidence, and decide whether token revocation or user notification is required. In-flight financial work remains Pending until reconciled rather than being labelled failed. After patch and regression tests, I re-enable gradually with guardrails. The long-term fix is safe defaults and backend enforcement independent of flags.”

## Interview answer — deep senior

“The first minutes are about containing server effects, because remote config cannot reach every offline APK and the client is not trusted. I apply a server-side deny rule or feature kill switch, stop new vulnerable operations and retain audit records. I then disable client UX, inspect impacted versions/cohorts and reconcile any transaction already accepted. Depending on exposure, I revoke sessions/keys and coordinate support/legal response. I do not erase Pending records or misclassify outcomes. Root cause may be unsafe default, stale config TTL, missing backend check or rollout guardrail failure; tests must reproduce it. Re-enable occurs only after backend authorization tests, patched client rollout and metrics show recovery. Deleting logs prematurely loses incident evidence. Re-enabling without regression tests repeats incident.”

## Deep-dive talking points

Trace offline/tampered client, backend deny and in-flight transaction reconciliation.

## Follow-up questions

- [SYS-08](../sys-08/): Why is client flag insufficient? **Answer:** cached or modified clients can still call backend.
- [SYS-17](../sys-17/): Which guardrails matter? **Answer:** security events plus business outcome/unknown metrics.

## Self-check rubric

Can I contain at server, preserve evidence and handle in-flight operations honestly?

## References and reviewed-on date

- [Android security guidance](https://developer.android.com/privacy-and-security/security-tips) — client-side security considerations.
- [Android architecture guide](https://developer.android.com/topic/architecture) — authority boundaries.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
