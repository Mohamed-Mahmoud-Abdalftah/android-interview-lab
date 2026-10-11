---
id: "PAY-14"
question: "A release-only native dependency fails on some hardware ABIs. What is your investigation and safe rollout plan?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "C"
phase: 5
priority: "P2"
order: 484
editorial_status: "reviewed"
---

# PAY-14

## Original interview question

A release-only native dependency fails on some hardware ABIs. What is your investigation and safe rollout plan?

## What the interviewer evaluates

- ABI packaging, native load versus runtime faults and staged release.
- Safe rollback without interrupting financial state reconciliation.

## Explanation in Arabic

Release-only native SDK failure ممكن يكون missing `.so` لـABI معيّن، R8/JNI name issue، ABI split packaging، أو firmware/hardware incompatibility. نبدأ بـcrash signature وdevice/ABI matrix، نعيد المشكلة على minified release build، نفحص APK/AAB outputs والـvendor compatibility. Rollout تدريجي مع kill switch للعمليات الجديدة، لكن pending payments لازم تكمل reconciliation.

## Why it matters and how it works

Android loads ABI-matched native libraries; packaging filters and App Bundle splits affect delivery. R8 can also break reflected/JNI entry points. A safe investigation compares debug and release artifacts, library dependencies, vendor SDK version and device firmware.

## Worked example

If `UnsatisfiedLinkError` appears only on `arm64-v8a` terminals, inspect the generated APK split for `libvendor.so` and transitive native dependencies, reproduce on affected hardware with the exact release variant, and retrace stacks. Halt new authorization on affected cohort while preserving read/status/reversal recovery.

## Trade-offs and decision criteria

Pinning SDK version or disabling a new feature may restore availability, but payment terminal certification may constrain changes. Global rollback can strand in-flight state if old schema cannot read it; migrations must be compatible.

## Failure modes

Treating all native crashes as R8 issues wastes time. Disabling payment code abruptly while unknown operations remain can lose reconciliation. Separate initiation gate from recovery path and test rollback with real pending rows.

## Production perspective

Canary by ABI/device/firmware, monitor crash-free sessions and unknown-payment backlog, then widen rollout only after hardware smoke tests. Preserve mapping and native symbols for exact builds under restricted access.

## Interview answer — short

“I reproduce with the release variant, inspect delivered ABI libraries and JNI/R8 rules, and canary by device. I can stop new payments, but I keep pending status/reversal reconciliation running during rollback.”

## Interview answer — structured

“I first segment crashes by ABI, model, firmware and app version. I reproduce using the shipped minified APK or split, check native library packaging and dependencies, then inspect JNI/reflection rules and vendor compatibility. A safe rollout gates new authorizations on affected devices while allowing existing unknown transactions and reversals to reconcile. I canary fixes on real hardware and keep schema/SDK rollback compatibility. The mechanics matter. Android loads ABI-matched native libraries; packaging filters and App Bundle splits affect delivery. R8 can also break reflected/JNI entry points. A safe investigation compares debug and release artifacts, library dependencies, vendor SDK version and device firmware. The choice has a trade-off. Pinning SDK version or disabling a new feature may restore availability, but payment terminal certification may constrain changes. Global rollback can strand in-flight state if old schema cannot read it; migrations must be compatible.”

## Interview answer — deep senior

“I distinguish load-time `UnsatisfiedLinkError`, JNI symbol mismatch and a runtime native crash, because each has different evidence. I inspect the AAB-generated split for every supported ABI, native dependencies, R8 mapping and symbol files, and reproduce under production signing/minification where possible. The rollout plan preserves financial obligations: a remote gate stops new transactions but never disables status lookup or reversal workers. I test rollback against persisted pending rows and provider state, then canary by hardware cohort and monitor both crash rate and reconciliation backlog before expansion. Consider a concrete case. If `UnsatisfiedLinkError` appears only on `arm64-v8a` terminals, inspect the generated APK split for `libvendor.so` and transitive native dependencies, reproduce on affected hardware with the exact release variant, and retrace stacks. Halt new authorization on affected cohort while preserving read/status/reversal recovery. A failure case illustrates the risk. Treating all native crashes as R8 issues wastes time. Disabling payment code abruptly while unknown operations remain can lose reconciliation. Separate initiation gate from recovery path and test rollback with real pending rows. In production, the response is concrete. Canary by ABI/device/firmware, monitor crash-free sessions and unknown-payment backlog, then widen rollout only after hardware smoke tests. Preserve mapping and native symbols for exact builds under restricted access.”

## Deep-dive talking points

Prompt for error classification, ABI split inspection, exact release variant, cohort canary and recovery-path continuity.

## Follow-up questions

- [SEC-09](../sec-09/): Could R8 cause release-only failure? **Answer:** yes, if dynamic names need keep rules.
- [PAY-12](../pay-12/): Why retain recovery on rollback? **Answer:** in-flight issuer approvals still need reconciliation.

## Self-check rubric

Can I separate load/JNI/runtime faults and preserve recovery while blocking new transactions?

## References and reviewed-on date

- [Android app ABI management](https://developer.android.com/ndk/guides/abis) — native ABI packaging.
- [R8 shrink guide](https://developer.android.com/build/shrink-code) — release optimization behavior.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
