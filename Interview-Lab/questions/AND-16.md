---
id: "AND-16"
question: "How do you protect exported Android components?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 46
editorial_status: "reviewed"
---

# AND-16

## Original interview question

How do you protect exported Android components?

## What the interviewer evaluates

- Audit the merged manifest and justify every cross-app entry point.
- Apply caller permissions and per-resource authorization instead of trusting intent filters.
- Validate untrusted Intent/URI payloads and avoid privilege-confused deputies.

## Explanation in Arabic

أي Activity أو Service أو Receiver أو Provider معمول له `android:exported="true"` يبقى مدخل من apps تانية. ابدأ من merged manifest، مش ملفك بس، لأن libraries ممكن تضيف components. اقفل اللي مش محتاج خروج بـ`exported=false`، واللي لازم يبقى متاح حدد له contract ضيق وصلاحيات مناسبة زي signature permission للتكامل الموثوق، مع فحص caller وdata حسب نوع component. الـintent filter مش حارس أمان: app تانية ممكن تبعت explicit Intent للمكون المصدّر. الـdeep link وكل extra بيانات غير موثوقة، والـbackend لازم يتحقق من ملكية أي resource أو عملية حساسة.

## Why it matters and how it works

`android:exported` controls whether other applications can launch a component. Manifest filters describe implicit routing, but an explicit Intent can target an exported class regardless of the filter. A component that already has privileged permissions can become a confused deputy if it performs sensitive work for an unchecked external caller. Providers additionally need URI permission and operation-level checks. Defense combines minimal exposure, explicit manifest declarations, permission protection, strict input parsing, authentication, and backend authorization where data is remote.

## Worked example

A receipt deep-link Activity is exported because browser links must open it. It accepts only `https://app.example.com/receipts/{opaqueId}`, rejects unknown query parameters, requires a signed-in session, and fetches receipt data from a backend that checks ownership. An internal `PaymentAdminService` has no external use and is `exported=false`. A partner integration that truly needs cross-app access may require a signature-protected permission and a documented request contract. These are architecture examples; test the actual merged manifest and target SDK.

## Trade-offs and decision criteria

`exported=false` is the safest default but cannot serve legitimate external integrations. Signature permissions restrict to apps signed with the trusted key, yet are unsuitable for arbitrary partners. Runtime caller verification can add granularity, but identity APIs vary by component and must be used correctly. Verified App Links reduce interception of owned web links, but do not authenticate the sender or authorize the requested data. A provider can grant one URI temporarily instead of exposing a whole database.

## Failure modes

A developer assumes a narrow intent filter prevents an explicit call; the exported Activity accepts an arbitrary account ID and reveals data. A receiver with app permissions performs a privileged action from any broadcast. A library merges an unexpected exported provider into release builds. A mutable PendingIntent can also delegate more authority than intended. Test direct explicit Intents, malformed deep links, URI grants, and third-party manifest changes; never rely only on UI navigation for access control.

## Production perspective

Security review inventories all exported components from the release merged manifest, records the reason for exposure, and tests each with a hostile caller. CI can flag newly exported components for review. The app parses external inputs into typed routes; a backend enforces account ownership. Monitor rejected requests by reason without logging token-bearing URLs, and repeat the audit after SDK updates.

## Interview answer — short

“I minimize exported components and explicitly set exported in the manifest. For required entry points, I enforce narrow permissions and input validation, then authenticate and authorize sensitive operations. An intent filter is routing, not an access-control boundary.”

## Interview answer — structured

“I inspect the merged manifest because dependencies can add components. Internal components stay non-exported. For a required public Activity or provider, I define exact actions, schemes, hosts, paths, extras, and allowed operations, and use permissions or URI grants where appropriate. External data is untrusted even if it matched an intent filter. I recheck account ownership at the backend and test direct explicit calls that bypass the expected UI flow.”

## Interview answer — deep senior

“I treat each exported component as an API surface. First I inventory the release merged manifest and remove unnecessary exposure. For legitimate integrations I define caller identity, permission level, URI scope and an input schema; signature permissions fit same-signer integrations, while a public App Link still needs strict route parsing. I assume an attacker can send an explicit Intent to an exported component regardless of its filter, so no privileged action depends on UI navigation having happened. Providers enforce per-URI access and backend resources enforce authenticated ownership. I test hostile callers, malformed URIs, stale sessions, library manifest changes, and PendingIntent delegation paths.”

## Deep-dive talking points

Discuss merged-manifest audit, explicit Intent bypass of filters, signature permissions, provider URI grants, verified link limits, confused-deputy behavior, and server-side ownership checks.

## Follow-up questions

- [AND-24](../and-24/): Does a verified App Link make its payload trusted? **Answer:** no; parse it and authorize the resource independently.
- [SEC-18](../sec-18/): Can an intent filter protect an exported service? **Answer:** no; use explicit exposure and permission/caller checks.
- [AND-10](../and-10/): Why is a mutable PendingIntent relevant? **Answer:** it can delegate fill-in authority to a holder and must be narrowly designed.

## Self-check rubric

Name the merged-manifest audit step; explain explicit Intent targeting; protect one public Activity and one provider; describe a confused deputy; and identify where backend authorization belongs.

## References and reviewed-on date

- [android:exported security guidance](https://developer.android.com/privacy-and-security/risks/android-exported) — exposure semantics.
- [Permission-based access control to exported components](https://developer.android.com/privacy-and-security/risks/access-control-to-exported-components) — privilege boundary.
- [Intents and intent filters](https://developer.android.com/guide/components/intents-filters) — routing versus explicit targeting.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The integration examples were not exercised on a device.
