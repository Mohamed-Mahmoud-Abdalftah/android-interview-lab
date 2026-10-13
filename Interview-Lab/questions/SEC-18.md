---
id: "SEC-18"
question: "How do you validate exported components, deep links, and PendingIntents?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 315
editorial_status: "reviewed"
---

# SEC-18

## Original interview question

How do you validate exported components, deep links, and PendingIntents?

## What the interviewer evaluates

- Exported component identity, URI/deep-link validation and PendingIntent mutability.
- Distinguishing input parsing from business authorization.

## Explanation in Arabic

`exported` component مدخل من apps تانية؛ لازم نراجع manifest النهائي، permissions المطلوبة، caller identity والـURI اللي داخلة. Deep link مش دليل إن المستخدم مخوّل؛ ممكن attacker يفتح URL مزيف بparameters. `PendingIntent` لو mutable من غير داعي ممكن يتغيّر محتواه. كل incoming data تتحقق، والـbackend يقرر ownership.

## Practical walkthrough

Deep link زي `bank://transfer?amount=100` يقدر أي app يفتحه، فلا تثق في amount أو `approved=true` من الـIntent. أعد جلب operation من backend وتحقق من user والـstate. `PendingIntent` mutable ممكن تتعدّل fields لو مش محتاج ده؛ استخدم immutable/explicit target حسب الحالة. بالنسبة لـprovider، راجع exported والـURI grants والصلاحيات في merged manifest.

## Why it matters and how it works

Android resolves intents to exported activities/services/receivers/providers according to manifest filters. Deep links can carry attacker-controlled inputs. A PendingIntent delegates the creating app’s identity to another holder, so explicit targets and `FLAG_IMMUTABLE` are preferred unless mutation is required. Validate URI scheme/host/path and business state separately.

## Worked example

Android example: a notification opens an explicit app activity with an opaque operation ID. `PaymentReturnActivity` is the application's component; it re-fetches the authenticated user's status from the backend and never trusts an `approved` extra or deep-link amount.

```kotlin
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.Uri

fun paymentReturnIntent(context: Context, operationId: String): PendingIntent {
    val intent = Intent(context, PaymentReturnActivity::class.java)
        .putExtra("operationId", operationId)
        .setData(Uri.Builder().scheme("app").authority("payment-return")
            .appendPath(operationId).build()) // distinct PendingIntent identity
    return PendingIntent.getActivity(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_ONE_SHOT,
    )
}
// PaymentReturnActivity is an application type; it must validate and fetch status.
```

## Trade-offs and decision criteria

Exporting is necessary for legitimate entry points, but each adds an external surface. App Links can improve domain association but do not eliminate malicious parameter values or backend authorization. Mutable PendingIntents are justified only for specific fill-in flows.

## Failure modes

An exported receiver accepts an intent extra `admin=true` and invokes a privileged action. Another app can send that intent. Require a protected entry point and server permission check; fuzz malformed URIs and unexpected extras.

## Production perspective

CI inspects merged manifests for unintended exports, tests hostile intents and deep links, and reviews PendingIntent flags across supported Android versions. Financial state is fetched from the backend using session identity and operation ID.

## Interview answer — short

“I treat exported components, deep links and PendingIntents as cross-app boundaries. I validate inputs, restrict exposure, use immutable explicit PendingIntents by default, and verify financial state server-side.”

## Interview answer — structured

“An exported Android component can receive data from another app. I inventory each entry in the merged manifest, limit permissions and validate every URI, extra and content URI. A deep link can navigate the user but cannot prove payment approval. PendingIntents carry the creator’s privileges, so I make them explicit and immutable unless a documented fill-in field is required. The backend checks authenticated ownership for any sensitive operation. Deep links can carry attacker-controlled inputs.”

## Interview answer — deep senior

“My review combines static manifest inspection and adversarial tests. I try direct intents, malformed links, unexpected MIME types, traversal-like paths and URI grants. For PendingIntents I inspect mutability and whether the target is explicit, because a holder may act with our identity. App Links help route trusted domains but request parameters remain untrusted. I bind any payment callback to a locally known operation and query authoritative server state; even a valid link cannot set approved status. I also review SDK-added components in the merged manifest. A payment-return activity receives `myapp://checkout/result?operationId=...`. Another app can send that intent.  I would test the same entry point from an untrusted app with missing, oversized and conflicting extras, then replay a PendingIntent if the action is intended to be one-shot. For deep links, a valid-looking operation ID is only a lookup key; the server must check that the current user owns it. For providers, I would inspect URI grants and query parameters as carefully as activity intents, because the manifest export is only the first gate.”

## How to answer in the interview

- **Why:** exported entry points accept attacker-controlled data.
- **How:** parse links defensively, validate server state, and constrain PendingIntent mutability and targets.
- **Trade-off:** stricter exports can limit intended integrations.
- **Failure case:** deep link amount becomes authorization.
- **Production solution:** malicious-intent tests and manifest/URI grant audit.

## Deep-dive talking points

Prompt for manifest export audit, caller identity, URI parsing, explicit immutable PendingIntents, and server-side payment verification.

## Follow-up questions

- [SEC-01](../sec-01/): Why does export matter to sandboxing? **Answer:** it intentionally opens a cross-UID entry point.
- [PAY-08](../pay-08/): Can a return link prove payment success? **Answer:** no; query authoritative status.

## Self-check rubric

Can I test a hostile intent, explain PendingIntent delegation, and reject deep-link parameters as authorization?

## References and reviewed-on date

- [Android exported component guidance](https://developer.android.com/privacy-and-security/risks/android-exported) — component exposure.
- [PendingIntent security](https://developer.android.com/privacy-and-security/risks/pending-intent) — mutability risk.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
