---
id: "SEC-21"
question: "What is Play Integrity API? What trust decisions must happen on the server?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 318
editorial_status: "reviewed"
---

# SEC-21

## Original interview question

What is Play Integrity API? What trust decisions must happen on the server?

## What the interviewer evaluates

- Play Integrity verdict as server-consumed risk signal, not client Boolean.
- Request binding, freshness, policy tiers and false positives.

## Explanation in Arabic

Play Integrity API بتدي signals عن app/device/account environment، لكنها مش تصريح دفع. الـapp تطلب token قريب من العملية الحساسة، والـbackend يفك ويتحقق من verdict ويربطه بالrequest hash أو nonce حسب النوع. الـserver يقرر policy تدريجية مع authentication والـtransaction rules. Root/hooking detections قابلة للتجاوز وفيها false positives.

## Practical walkthrough

قبل transfer كبير، app تطلب Play Integrity token مربوط بـrequest hash لحقول ثابتة زي operation ID والمبلغ والـbeneficiary. الـbackend يعيد حساب hash ويتحقق من verdict والتوقيت وهوية التطبيق، ثم يفحص session والحدود وحالة العملية. لو جهاز شرعي أخد verdict ضعيفة، مش لازم hard block آليًا؛ ممكن step-up أو limit حسب risk policy.

## Why it matters and how it works

The backend uses Google Play’s decode/verification flow and checks package identity, app recognition, request details and the action binding. Standard requests support requestHash; classic requests use nonce. Do not put sensitive raw data in these fields. Verdict categories and availability vary, so absent or adverse signals need documented handling.

## Worked example

Android/Kotlin request-binding illustration for a Play Integrity **standard** request. `TransferIntent` fields are validated and immutable; app and backend must use the exact same canonical serialization. Pass this digest as `requestHash`, then have the backend verify and decode the integrity token and recompute the hash before it applies transfer authorization.

```kotlin
import android.util.Base64
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.util.UUID

data class TransferIntent(
    val operationId: UUID,
    val amountMinor: Long,
    val currency: String,
    val beneficiaryId: UUID,
)

fun requestHash(intent: TransferIntent): String {
    require(intent.amountMinor > 0)
    require(intent.currency.matches(Regex("[A-Z]{3}")))
    val canonical = "${intent.operationId}|${intent.amountMinor}|" +
        "${intent.currency}|${intent.beneficiaryId}"
    val bytes = MessageDigest.getInstance("SHA-256")
        .digest(canonical.toByteArray(StandardCharsets.UTF_8))
    return Base64.encodeToString(bytes, Base64.NO_WRAP)
}
```

A hash binds fields but is not itself an authorization check; the server still validates session, operation state, amount and risk policy.

## Trade-offs and decision criteria

Integrity raises attack cost and supports fraud decisions but adds latency, quotas, platform dependency and exclusion risk. A high-friction deny policy may harm legitimate devices; tiered responses can preserve availability while limiting exposure.

## Failure modes

Checking the verdict only on-device lets an attacker patch the result. Reusing a token for another amount breaks request binding. A cached verdict can be proxied; request it near the protected action and validate server-side.

## Production perspective

Instrument acceptance/denial rates by app version and device cohort without collecting unnecessary identifiers. Review false-positive appeals, provide safe alternate verification, and test tampered request parameters.

## Interview answer — short

“Play Integrity supplies app and device signals. I bind the token to a sensitive request and verify it on the backend, where it informs a tiered risk decision alongside normal authentication and transaction checks.”

## Interview answer — structured

“I request a verdict near the protected action, bind it to the request with requestHash or nonce as appropriate, and send the token to my backend. The backend verifies and decodes it, checks app identity and matching request details, then applies a risk policy. It does not accept a client Boolean like `isSafe`. A compromised device can still be deceptive and verdicts can fail for legitimate users, so I monitor outcomes and retain server-side authorization.”

## Interview answer — deep senior

“For a payment decision, I would never let an integrity verdict stand alone. The server verifies package and signing recognition, time/request details and a digest of stable operation fields; it also validates the authenticated user, amount and idempotency identity. I choose a tiered policy: normal path, step-up authentication, limited capability or block according to risk, with support for false positives and outages. I test replay, parameter mutation and token unavailability, and avoid putting raw sensitive fields in the binding input. Signals improve confidence but cannot guarantee an unrooted or unhooked endpoint. I would bind the token to stable operation fields using a canonical digest and compare it on the backend after decoding the verdict through the supported server flow. The server also checks freshness, package/signing recognition and the authenticated user's permissions. A high-value transfer can require step-up when a signal is weak, while a low-risk balance view may continue. I would monitor false positives and never cache one verdict as permanent device trust.”

## How to answer in the interview

- **Why:** attestation adds signals, not user authorization.
- **How:** bind token to request details and verify verdict plus session server-side.
- **Trade-off:** strict enforcement can exclude legitimate devices.
- **Failure case:** trusting a client-decoded verdict or replayed token.
- **Production solution:** server risk tiers, nonce/hash binding, and outcome monitoring.

## Deep-dive talking points

Prompt for standard requestHash versus classic nonce, server decode, request binding, tiered policy and false-positive handling.

## Follow-up questions

- [SEC-29](../sec-29/): Does integrity stop Frida? **Answer:** it raises cost but cannot guarantee a clean client.
- [SEC-32](../sec-32/): What if false positives rise? **Answer:** use monitored, reversible risk tiers and appeals.

## Self-check rubric

Can I place token verification on the server and explain binding, normal authorization and adverse-verdict handling?

## References and reviewed-on date

- [Play Integrity overview](https://developer.android.com/google/play/integrity/overview) — signal and policy model.
- [Standard API request](https://developer.android.com/google/play/integrity/standard) — requestHash binding.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
