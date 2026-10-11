---
id: "SEC-31"
question: "A team puts a private API key in BuildConfig from local.properties. Why is this not sufficient?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "C"
phase: 3
priority: "P1"
order: 328
editorial_status: "reviewed"
---

# SEC-31

## Original interview question

A team puts a private API key in BuildConfig from local.properties. Why is this not sufficient?

## What the interviewer evaluates

- BuildConfig/local.properties extraction path.
- Incident response and server-side privilege design.

## Explanation in Arabic

`local.properties` يحمي private key من commit بالصدفة؛ لكن لما Gradle ينسخه إلى `BuildConfig` يبقى constant في APK. أي مستخدم يقدر يستخرجها بالـdecompile أو يراقب call اللي بتستخدمها. لو key بتدي صلاحية private API أو charge، اتعامل معها كـleaked: rotate، audit، وانقل العملية لـbackend.

## Why it matters and how it works

BuildConfig values are compiled into the distributed client. R8 name changes and JNI relocation cannot create a server-controlled secret. Provider package/signature restrictions and quotas may help for public mobile identifiers, but private operations require server custody and authorization.

## Worked example

A team stores `ACQUIRER_PRIVATE_KEY` in local.properties and writes it to BuildConfigField. The remediation is to revoke/rotate the key, inspect provider activity, remove it from APK artifacts, and have the backend create scoped payment intents after validating user and order state.

## Trade-offs and decision criteria

Keeping config out of Git remains useful hygiene. A backend proxy costs latency and maintenance but is the proper trust boundary for privileged keys. Public SDK keys can stay in APK only under the provider’s documented restrictions.

## Failure modes

Rotating only the local.properties file leaves already released APKs with the old key. Removing the source line without revoking the provider credential leaves the incident active. Inspect all release versions and use provider-side revocation.

## Production perspective

CI scans source and packaged artifacts, while secret-management controls restrict backend access. Backend logs key identifiers and operation IDs rather than raw credentials.

## Interview answer — short

“local.properties is build hygiene, not runtime secrecy. BuildConfig ships the value in the APK. I rotate any exposed private key and move privileged API calls to a backend that authorizes them.”

## Interview answer — structured

“Gradle reads local.properties during the build; once the value becomes a BuildConfig constant, every installed APK carries it. Decompilation or runtime instrumentation can recover it, regardless of R8. If it is a private payment key, I treat it as compromised, rotate and audit it, then call the provider only from the backend. The mobile app sends a scoped request that the backend verifies against user identity, order price and state. The mechanics matter. BuildConfig values are compiled into the distributed client. R8 name changes and JNI relocation cannot create a server-controlled secret. Provider package/signature restrictions and quotas may help for public mobile identifiers, but private operations require server custody and authorization. The choice has a trade-off. Keeping config out of Git remains useful hygiene. A backend proxy costs latency and maintenance but is the proper trust boundary for privileged keys. Public SDK keys can stay in APK only under the provider’s documented restrictions.”

## Interview answer — deep senior

“I separate prevention and remediation. For prevention, private provider credentials never enter mobile build inputs; CI scans artifacts as well as Git. For remediation, I revoke the distributed key at the provider, inspect abuse, roll backend credentials and release an app without it. Server endpoints enforce least privilege, rate limits, idempotency and audit trails. If a key is intentionally public for a mobile SDK, I apply documented package/signing restrictions and quotas, but I still assume extraction and do not grant financial authority through it. Consider a concrete case. A team stores `ACQUIRER_PRIVATE_KEY` in local.properties and writes it to BuildConfigField. The remediation is to revoke/rotate the key, inspect provider activity, remove it from APK artifacts, and have the backend create scoped payment intents after validating user and order state. A failure case illustrates the risk. Rotating only the local.properties file leaves already released APKs with the old key. Removing the source line without revoking the provider credential leaves the incident active. Inspect all release versions and use provider-side revocation. In production, the response is concrete. CI scans source and packaged artifacts, while secret-management controls restrict backend access. Backend logs key identifiers and operation IDs rather than raw credentials.”

## Deep-dive talking points

Prompt for APK artifact inspection, provider rotation, backend authority and distinction between public identifier and private key.

## Follow-up questions

- [SEC-04](../sec-04/): What did local.properties protect? **Answer:** source-control hygiene only.
- [SEC-05](../sec-05/): Can JNI or R8 fix it? **Answer:** no; the client must use the value.

## Self-check rubric

Can I trace the secret into APK, describe full incident response and redesign provider access?

## References and reviewed-on date

- [Android build configuration](https://developer.android.com/build/gradle-tips) — build-time constants.
- [OWASP MASVS resilience](https://mas.owasp.org/MASVS/controls/MASVS-RESILIENCE-1/) — reverse-engineering limits.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
