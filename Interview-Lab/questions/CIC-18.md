---
id: "CIC-18"
question: "A malicious pull request tries to access signing secrets. How do you prevent leakage?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "C"
phase: 4
priority: "P2"
order: 437
editorial_status: "reviewed"
---

# CIC-18

## Original interview question

A malicious pull request tries to access signing secrets. How do you prevent leakage?

## What the interviewer evaluates

- Malicious PR code in build scripts/tests and privileged workflow contexts.
- Separation of untrusted validation from signing/release.

## Explanation in Arabic

PR خبيث ممكن يضيف Gradle task أو test يقرأ environment secrets ويبعتها لخارج CI. إخفاء secret في logs مش كفاية. شغّل fork/unreviewed PRs في job بدون signing keys أو Play token وبـread-only permissions؛ privileged release job يشتغل فقط من protected branch/artifact بعد review، وما ينفذش PR head code بسياق secrets.

### Practical walkthrough in Egyptian Arabic

Manifest merge يجمّع declarations من app والـlibraries والـflavors؛ debug manifest ممكن يخفي provider ناقص في release. في CI ابْنِ release variant وافحص merged manifest النهائي، وتحقق `authorities` المطلوبة، `exported` وpermissions وplaceholder values. شغّل release smoke test يحاول الوصول للـprovider، لأن وجود declaration وحده لا يثبت URI behavior. احتفظ بالmerge report عشان تقدر تعرف أي dependency أو source set غيّر العقد.

## Why it matters and how it works

CI executes repository code, including build scripts and plugins, so PR jobs are code execution by an untrusted author. `pull_request_target`-style privileged contexts are dangerous if they check out untrusted commits. Artifact promotion must validate provenance rather than trusting attacker-produced files.

## Worked example

An attacker changes `build.gradle.kts` to POST `$PLAY_TOKEN`. In safe CI, PR job has no token and outbound restrictions where feasible. After merge/review, a separate release job retrieves scoped credentials and signs a known commit’s artifact.

## Trade-offs and decision criteria

Isolated workflows add complexity and may delay external contributions, but protect signing authority. Dependency verification and pinned actions reduce supply-chain exposure; they do not replace PR-secret isolation.

## Failure modes

A workflow uses a privileged token and then checks out `github.event.pull_request.head.sha`; malicious Gradle runs with secrets. Remove secret from that context, restrict permissions and rotate any exposed credential.

## Production perspective

Security review covers workflows, actions, Gradle plugins and artifact handoff. Audit release-trigger permissions and credential use, and alert on unexpected Play uploads.

## Interview answer — short

“I treat PR build code as untrusted. It gets no signing or Play secrets; privileged release jobs run only reviewed protected commits and verify artifact provenance.”

## Interview answer — structured

“A malicious PR can alter Gradle scripts or tests to read and exfiltrate CI secrets. Masking in logs does not stop an HTTP POST. I split PR validation from release signing, set read-only permissions for untrusted jobs and never run PR-head code inside a privileged workflow. After protected merge, a separate job uses scoped credentials to sign and publish a traceable artifact. I also pin dependencies/actions and rotate credentials if exposure is suspected. ”

## Interview answer — deep senior

“I test the shipped manifest, not the manifest source file I happened to edit. Android Gradle Plugin merges declarations from the app, dependencies, product flavors and build type, so a debug-only provider can disappear in release or a placeholder can resolve to the wrong authority. CI builds the production release variant, inspects its merged manifest or packaged artifact, and asserts the exact authority, exported status and permissions expected for the provider. I also run a smoke test that resolves a content URI under the release-like package name and verifies allowed and denied callers as appropriate. The static assertion catches omissions early; the runtime test checks that routing and access work. I store the manifest-merger report to explain which source contributed a value. The trade-off is an extra artifact-level check, but it is cheap compared with shipping a broken share or SDK initialization path. I fail the release if a new unexpected exported component appears.”

## How to answer in the interview

- **Why:** source manifests differ from shipped merge.
- **How:** inspect release merged manifest and smoke URI.
- **Trade-off:** static speed versus runtime proof.
- **Failure case:** placeholder resolves to wrong authority.
- **Production solution:** gate exact authority, permissions and export state.

## Deep-dive talking points

Prompt for build script exfiltration, privileged context danger, artifact provenance and credential rotation.

## Follow-up questions

- [CIC-09](../cic-09/): Why is masking insufficient? **Answer:** malicious code can send secret to network.
- [CIC-08](../cic-08/): What checks run on PR? **Answer:** fast validation without release credentials.

## Self-check rubric

Explain fork-PR secret isolation, workflow permission minimization and avoiding privileged pull_request_target checkout of attacker code. Show a safe path for artifact validation before signing.

## References and reviewed-on date

- [Play App Signing](https://developer.android.com/studio/publish/app-signing) — signing roles.
- [Gradle dependency verification](https://docs.gradle.org/current/userguide/dependency_verification.html) — supply-chain integrity.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
