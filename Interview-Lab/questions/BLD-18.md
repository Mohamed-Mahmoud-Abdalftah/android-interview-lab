---
id: "BLD-18"
question: "A release manifest merge drops a required ContentProvider authority. What CI check would catch it?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "C"
phase: 4
priority: "P1"
order: 392
editorial_status: "reviewed"
---

# BLD-18

## Original interview question

A release manifest merge drops a required ContentProvider authority. What CI check would catch it?

## What the interviewer evaluates

- Inspect final merged manifest for the exact release variant.
- Assert provider name/authority/exported/grant behavior as needed.
- Test packaged artifact or startup integration, not only source XML.

## Explanation in Arabic

CI تبني `prodRelease` وتفحص merged manifest الناتجة بعد كل source sets وAAR manifests و`tools:` merge rules؛ assert على `provider android:name` و`android:authorities` المتوقعة (مع applicationId suffix)، وربما `exported`, permissions وgrantUri حسب contract. مجرد فحص `src/main/AndroidManifest.xml` لا يكفي؛ release source set أو library قد تغير/تحذف العقدة. استخدم manifest merger report لتفسير من غيّرها، ثم APK/AAB-derived manifest أو instrumented smoke test يؤكد ما شُحن. لا تحل المشكلة بإضافة authority ثابتة قد تصطدم بين flavors.

## Why it matters and how it works

AGP merges manifests by source-set/library priority and explicit tools markers. The final application has one merged manifest; a provider can be replaced, removed or have an authority placeholder resolved differently for a variant. A CI assertion on that output catches a silent release-only configuration regression before upload. A runtime test can additionally verify provider resolution and URI access semantics.

## Worked example

A file-sharing SDK expects `com.acme.app.files` authority. `src/release` contains `tools:node="remove"` for a similarly named provider, so `prodDebug` works but `prodRelease` loses it. A CI script parses the final merged manifest and fails unless the named provider has `${applicationId}.files` resolved to the expected string; a release startup/share test queries the URI path.

## Trade-offs and decision criteria

Static manifest assertions are fast and deterministic but do not prove provider code works. An emulator release test costs time but covers runtime registration and permissions. Avoid brittle grep over source XML; parse the merged/package manifest for the exact variant and assert meaningful attributes.

## Failure modes

CI tests only debug manifest. A placeholder remains unresolved in an assertion against source text. A provider exists but authority is wrong for the flavor. `exported` or grant flags differ, causing security or URI failures. Merger markers in an AAR affect downstream app unexpectedly.

## Production perspective

Check required manifest contracts per published variant, store merger reports on failures, and run a focused minified release integration test for high-risk providers. Review merged manifest diffs during SDK and flavor changes.

## Interview answer — short

“CI should parse the final merged manifest of the shipped release variant and assert the provider's resolved authority and required attributes, then smoke-test the packaged flow.”

## Interview answer — structured

“I build the exact release flavor, not debug, and inspect AGP's merged manifest output. A test asserts provider class, resolved authority and relevant exported/permission or URI-grant attributes. On failure I attach the manifest merger report to show which source set or AAR changed it. For a critical file-sharing provider I also launch or query a packaged release artifact on an emulator, because presence in XML does not prove runtime behavior.”

## Interview answer — deep senior

“The check belongs after manifest merging for the artifact we intend to publish. AGP merges `main`, flavor, build-type and library manifests with priority and `tools:` rules, so a source file can look correct while the final `prodRelease` manifest has no provider or a different authority. I add a CI task that parses the merged manifest or final packaged manifest and asserts the exact provider class and resolved `applicationId`-specific authority. Depending on the contract I also assert exported state, permissions and URI grant settings, because a present provider with wrong access rules can still break or expose data. I store the merger decision report as a diagnostic artifact when the assertion fails. Then a focused release-variant integration test exercises the URI path on an emulator. I avoid a raw grep of `src/main` and avoid a fixed authority that collides across flavors or test installs. The check is small, deterministic and tied to the variant, while the device test verifies behavior that static XML cannot.”

## Deep-dive talking points

Discuss merge priority, placeholders, `tools:` markers, parsed assertions, packaged artifact and runtime URI test.

## Follow-up questions

- Why is `src/main` inspection insufficient? **Answer:** flavor, build type and libraries can override/remove entries during merge.
- What report helps explain a changed provider? **Answer:** AGP's manifest merger decision report for that variant.
- Does a manifest assertion prove provider functionality? **Answer:** no; add a focused runtime test for critical behavior.

## Self-check rubric

Name final variant, assert provider attributes, attach merge report, and verify runtime path.

## References and reviewed-on date

- [Manage manifest files](https://developer.android.com/build/manage-manifests) — merge rules and reports.
- [Configure build variants](https://developer.android.com/build/build-variants) — source-set priority.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Authority values are illustrative.
A release manifest merge drops a required ContentProvider authority. What CI check would catch it?
