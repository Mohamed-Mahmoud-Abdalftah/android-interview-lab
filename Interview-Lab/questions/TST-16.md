---
id: "TST-16"
question: "What should be unit-tested versus verified with an emulator/device?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 411
editorial_status: "reviewed"
---

# TST-16

## Original interview question

What should be unit-tested versus verified with an emulator/device?

## What the interviewer evaluates

- JVM versus platform fidelity boundary.
- Emulator/device matrix driven by OS and hardware risks.

## Explanation in Arabic

اختار test layer حسب الشيء المراد إثباته. Rounding، validation وstate reducer من غير Android APIs تُختبر سريعًا على JVM مع edge cases. Room migration، permissions، process recreation وCompose semantics تحتاج emulator أو جهاز لأن contract متعلق بالـplatform.

## Practical walkthrough

POS reader disconnect أو camera timing يحتاج hardware/provider sandbox؛ fake callback تثبت state machine في التطبيق فقط. Emulator لا يمثل كل firmware أو OEM behavior، وجهاز واحد لا يغطي كل API levels. اكتب في التقرير claim دقيقة: “unit test يثبت قرار Unknown”، وليس “اختبرنا terminal” لو ما شغلناش terminal. رتّب matrix بالمخاطر: flows حرجة لها integration/device coverage، بينما logic بسيط لا يحتاج suite بطيئة لكل حالة.

## Why it matters and how it works

JVM tests execute without Android runtime and cannot prove manifest, Binder, file backup or device UI behavior. I record which devices and SDK versions were actually covered. Some local Robolectric-style tests approximate framework behavior but are not a substitute for hardware or OS-specific validation.

## Worked example

Test a payment amount rounding function on JVM; test Room migration on emulator; test POS reader disconnect on actual terminal hardware with provider sandbox. A fake terminal callback test covers app state logic but not firmware timing.

## Trade-offs and decision criteria

Device tests cost time and infrastructure; prioritize platform-sensitive risks. JVM-only coverage is fast but can provide false assurance about security, process death and SDK behavior.

## Failure modes

A mocked permission manager test passes while the manifest lacks a permission. A simulated NFC SDK test passes while one ABI cannot load its `.so`. Use release-like device smoke tests for those boundaries.

## Production perspective

Build a supported API/device/ABI matrix. Run fast JVM PR checks, targeted emulator suites, and hardware release gates for payment-critical flows. Record which claims were device-verified.

## Interview answer — short

“JVM tests cover deterministic Kotlin logic. Emulator/device tests cover Android framework behavior, and real hardware is needed for vendor SDK and physical peripheral risks.”

## Interview answer — structured

“I choose the environment based on what could fail. A use case or algorithm runs in JVM tests; permissions, lifecycle, Room migration and Compose UI need Android execution. Emulators cover API levels and screen sizes efficiently, while a POS SDK and reader disconnect require actual terminal hardware. I state which devices, OS versions and provider versions were actually exercised, because a mock cannot certify the hardware.”

## Interview answer — deep senior

“I choose the cheapest environment that can observe the contract. Pure fee rounding, ID validation and reducers belong in JVM unit tests with exhaustive edge cases. When the claim depends on Android framework behavior—Room migrations, permissions, Activity recreation, Compose semantics or manifest packaging—I run a targeted emulator or device test. Hardware and provider timing need another boundary: a fake POS callback can prove that my state machine enters Unknown after a disconnect, but it cannot certify the terminal firmware or payment provider protocol. I keep a small hardware and sandbox suite for release-critical paths, and state exactly which devices, API levels and provider versions were exercised. An emulator is valuable but cannot represent every OEM implementation; a physical device is not universal proof either. I separate app-policy tests from platform and external-system verification in the release report. That avoids both extremes: making every simple rule wait for a device, and declaring a payment integration safe because a mocked callback passed on the JVM.”

## How to answer in the interview

- **Why:** a fake proves app policy but cannot emulate firmware or Android exactly.
- **How:** allocate rounding to JVM, lifecycle/Room to device and POS timing to hardware.
- **Trade-off:** speed and coverage versus cost of realistic environments.
- **Failure case:** a mocked disconnect is called terminal certification.
- **Production solution:** explicit device/provider coverage in release evidence.

## Deep-dive talking points

Prompt for JVM boundary, emulator API matrix, real hardware, release variant and claim scope.

## Follow-up questions

- [TST-11](../tst-11/): Why real Room? **Answer:** SQL and migration semantics depend on Android/SQLite.
- [TST-17](../tst-17/): What needs a device benchmark? **Answer:** frame/startup performance in realistic runtime.

## Self-check rubric

Place pure rounding/policy on JVM, Room or permission behavior on emulator, and reader disconnect timing on real hardware. Explain why a fake callback cannot certify firmware or platform integration.

## References and reviewed-on date

- [Android test fundamentals](https://developer.android.com/training/testing/fundamentals) — local versus instrumented tests.
- [Android device testing](https://developer.android.com/training/testing) — test environment guidance.

Technically reviewed against the cited primary documentation on 2026-10-12; automated technical review only, not human review.
