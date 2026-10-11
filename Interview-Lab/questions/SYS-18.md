---
id: "SYS-18"
question: "How do you support version skew between older apps and newer backend contracts?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 347
editorial_status: "reviewed"
---

# SYS-18

## Original interview question

How do you support version skew between older apps and newer backend contracts?

## What the interviewer evaluates

Handle older APKs against newer backend contracts with versioned compatibility.

## Explanation in Arabic

مستخدم Android ممكن يفضل على APK قديمة شهور؛ backend لازم تعرف version skew. نفضّل additive JSON/API changes، default values وfeature negotiation، ونحافظ على endpoints/schema قديمة لفترة معلنة. لو change breaking نستخدم versioned route أو minimum-supported-version response واضح، لكن ما نمسحش قدرة user offline على قراءة data. Contract tests تغطي أقدم نسخة مدعومة.

## Why it matters and how it works

Old clients may not know new enum values or required fields; robust parsing and explicit unknown states help. Backend rollout should precede client use of new fields, then remove old behavior only after telemetry confirms migration. Security fixes may require forced upgrade with careful user/data policy.

## Worked example

Conceptual API response parsing strategy; actual serializer configuration is library-specific.

```kotlin
sealed interface ServerMode {
    data object Standard : ServerMode
    data object NewCheckout : ServerMode
    data class Unknown(val wireValue: String) : ServerMode
}
// Preserve unknown values safely; do not assume old APK can execute new protocol.
```

## Trade-offs and decision criteria

Backward compatibility increases backend maintenance cost but avoids breaking offline/slow-updating users. Forced upgrade simplifies support only when justified and may strand users without network or store access. Versioned contracts require deprecation policy.

## Failure modes

A server that changes a field from optional string to required nested object can crash old clients. A new enum value may hit exhaustive `when` parsing. Removing an endpoint before old app usage drops creates widespread 404/401 confusion.

## Production perspective

A bank deploys additive transaction-status fields first, updates Android parser with Unknown handling, stages new UI and tracks old-version traffic. A critical security protocol change uses an explicit supported-version gate and migration/help path.

## Interview answer — short

“I assume old APKs coexist with new backend. I use additive or versioned contracts, unknown-field handling, contract tests for supported versions and measured deprecation. Breaking security changes use an explicit upgrade policy.”

## Interview answer — structured

“Mobile clients cannot all update at once. I deploy backend changes in a backward-compatible way, make new fields optional for old clients, and use versioned endpoints or capability negotiation for a truly different protocol. The app parser handles unknown enum values safely. CI runs contract tests against the oldest supported APK/API model, and telemetry shows when old traffic is low enough to retire a path. If an upgrade is mandatory for security, the backend returns a clear minimum-version response and preserves user data through the transition. Versioned contracts require deprecation policy.”

## Interview answer — deep senior

“I plan an expand-migrate-contract sequence. First the backend accepts both old and new request shapes and emits additive responses. Then new clients roll out gradually with feature capability and schema/version handling. Only after usage data and policy thresholds allow do we remove the old contract. I test unknown fields/enum variants, auth refresh and deep links on old clients, and I maintain a compatibility matrix for DB versions as well. A forced upgrade may be necessary for a severe security flaw, but it must explain the user path and avoid destroying offline drafts. Version skew is an operational reality, not an edge case.”

## Deep-dive talking points

Draw old/new app by old/new server matrix and a deprecation timeline.

## Follow-up questions

- [SYS-13](../sys-13/): What about local DB? **Answer:** test migration from shipped schemas alongside backend compatibility.
- [SYS-08](../sys-08/): Can flags replace API versioning? **Answer:** no, old clients may not understand new protocol.

## Self-check rubric

Can I support old clients, parse unknowns and plan safe contract removal?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — robust persistent model boundaries.
- [Android modularization guide](https://developer.android.com/topic/modularization) — stable API boundaries.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
