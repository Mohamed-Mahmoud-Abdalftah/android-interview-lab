---
id: "SYS-08"
question: "Design a feature flags and staged rollout system."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 337
editorial_status: "reviewed"
---

# SYS-08

## Original interview question

Design a feature flags and staged rollout system.

## What the interviewer evaluates

Design feature flags and staged rollout with typed defaults, kill switches and server trust.

## Explanation in Arabic

Feature flag بتغيّر behavior من غير إصدار جديد، لكن لازم default آمن، ownership، expiry وserver-controlled targeting. التطبيق يحتفظ last-known config مع version/TTL ويقبل rollback، بس ما يعتمدش على flag client-side كصلاحية أمنية؛ backend يفرض authorization. rollout تدريجي حسب cohort مع metrics وkill switch، ونختبر flag on/off وold app contract.

## Practical walkthrough

لو flag فعّلت checkout جديد، خلي config لها version وexpiry وsafe default. أثناء عملية دفع بدأت بالنسخة القديمة، ثبّت القرار لنفس operation بدل ما refresh يغيّر flow في النص. rollout يكون على cohort صغيرة مع crash وunknown-payment metrics، وrollback سريع. Client flag تتحكم في العرض فقط؛ لو path فيها صلاحية مالية، backend يفحصها مستقلًا حتى لو APK cached أو tampered.

## Why it matters and how it works

Config fetch can fail or arrive late; choose bootstrap defaults and apply changes at safe state boundaries. A security-sensitive flag should fail closed where appropriate and be enforced server-side. Rollout should have cohort stickiness, audit trail and rapid disable path; stale cached flags need expiry semantics.

## Worked example

Conceptual typed flag contract; transport/storage are app-specific.

```kotlin
data class FlagSnapshot(
    val version: Long,
    val expiresAtEpochMs: Long,
    val newCheckoutUi: Boolean = false,
)
interface FlagRepository {
    suspend fun refresh(): FlagSnapshot
    fun current(): FlagSnapshot
}
// Backend authorization cannot depend on newCheckoutUi.
```

## Trade-offs and decision criteria

Flags reduce release coupling but add combinatorial states and stale-config risk. Remote kill switch is useful only if app can fetch it in time; a backend block is stronger for security-sensitive operations. Remove obsolete flags after rollout.

## Failure modes

A default-on sensitive path can expose users offline before config fetch. A flag that changes payment protocol mid-transaction can corrupt state unless pinned per operation. Cohort drift makes A/B results unreliable. Client flag can be modified on rooted device.

## Production perspective

A checkout feature rolls out to 1%, then 10%, with crash/ANR/payment error guardrails. Backend supports both protocols, operations pin their variant, and a server-side deny switch stops broken charges independent of client cache.

## Interview answer — short

“I use typed flags with safe defaults, stable cohorts, TTL, metrics and rollback. Security authority stays on the backend; client flags only shape UX. I pin critical workflows to a version so mid-flight updates do not change their rules.”

## Interview answer — structured

“A rollout system needs more than a Boolean fetch. I define a typed config schema, safe default and cache expiry, assign an owner and remove the flag after rollout. Targeting is stable per user/cohort, and metrics compare crash, latency and business errors before widening exposure. If remote config is unavailable, the app follows a documented fallback. A client-side flag never grants permission; the backend enforces security and can kill a broken path. I test both flag states and old app compatibility. Remove obsolete flags after rollout.”

## Interview answer — deep senior

“I treat flags as distributed configuration with version skew. A user can be offline with stale config, a refresh can arrive during payment, and old APKs may not understand a new field. I use typed defaults, schema versions, TTL and per-operation pinning for stateful workflows. Rollout cohorts remain sticky and are audited; guardrails include crash/ANR and conversion/payment integrity metrics, not just click rates. A kill switch in the client is helpful for recoverable UX, but a security-sensitive server path must be blockable server-side because the app can be offline, tampered with or slow to fetch. I test all meaningful combinations, disable rapidly on regression and delete stale flags to control complexity. Cohort drift makes A/B results unreliable. I would model configuration as a versioned snapshot with safe defaults and a TTL, then decide which decisions are pinned at operation start. A checkout already underway should not switch payment rules halfway because a refresh arrived. A staged rollout requires cohort stability, guardrail metrics and a named rollback owner. The server must enforce any sensitive eligibility independently, since a stale or modified APK can ignore a client flag. I would test offline launch with expired config, rollback during an operation and old-client parsing of new fields.”

## How to answer in the interview

- **Why:** flags are distributed, possibly stale configuration.
- **How:** use typed snapshots, stable cohorts, TTL, and per-operation pinning.
- **Trade-off:** rapid rollout adds policy and version-skew complexity.
- **Failure case:** mid-transaction flag flip or client-only security gate.
- **Production solution:** monitored canary, safe default, server authorization, and rollback owner.

## Deep-dive talking points

Trace offline default, mid-flight change, old app and server-side containment.

## Follow-up questions

- [SYS-22](../sys-22/): How contain broken security flag? **Answer:** server deny path plus staged rollback and incident response.
- [SYS-18](../sys-18/): How handle old apps? **Answer:** versioned tolerant contracts and backend compatibility window.

## Self-check rubric

Can I define safe default, guardrails, kill path and backend authorization?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — source of truth and state ownership.
- [Android app security](https://developer.android.com/privacy-and-security/security-tips) — client trust limits.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
