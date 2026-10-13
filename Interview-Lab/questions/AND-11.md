---
id: "AND-11"
question: "What is the role of AndroidManifest.xml?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "A"
phase: 1
priority: "P1"
order: 41
editorial_status: "reviewed"
---

# AND-11

## Original interview question

What is the role of AndroidManifest.xml?

## What the interviewer evaluates

- Explain the manifest as the app's declaration to Android, build tools, and distribution rather than a runtime configuration store.
- Distinguish component declarations and intent filters from permissions, features, and application metadata.
- Inspect the *merged* manifest and explicit exported boundaries, especially when libraries contribute entries.

## Explanation in Arabic

ملف `AndroidManifest.xml` هو العقد اللي التطبيق بيعلن به نفسه للنظام: أسماء `Activity` و`Service` و`BroadcastReceiver` و`ContentProvider`، وإيه اللي ممكن يستقبله كل component، والصلاحيات والـfeatures المطلوبة. نظام البناء بيدمج manifest التطبيق مع ملفات المكتبات والـbuild variants، فالنسخة النهائية المدموجة هي اللي هتتعبأ داخل APK. وجود permission declaration لا يمنح runtime permission تلقائيًا. ووجود intent filter مع `android:exported` ممكن يفتح component لتطبيقات تانية، لذلك ده سطح أمني لازم يتراجع.

## Why it matters and how it works

Android can start an app component without a conventional `main()` function, so it needs declarations describing entry points and their attributes. The manifest declares package-level capabilities and restrictions; runtime state such as a logged-in user belongs elsewhere. During the Gradle build, manifest merger combines the app, variants, and libraries, with conflict rules and tools directives. Review the merged artifact when a dependency adds a provider or permission. The build namespace and final application ID have distinct Gradle roles; do not assume a source manifest `package` is the modern configuration point.

## Worked example

An exported deep-link Activity declares an `https` intent filter and `android:exported="true"`; its handler validates the URI and authenticates before showing account data. An internal settings Activity declares `android:exported="false"`. The build review inspects the merged manifest to catch a library-added provider and checks that every required permission has a corresponding user-facing runtime flow where Android requires one. This is an illustrative configuration review, not a complete manifest.

## Practical walkthrough

merged manifest هو العقد النهائي اللي Android يقرأه، مش ملف app module لوحده؛ library ممكن تضيف provider أو receiver. راجع `android:exported` لكل entry point، intent filters، permissions، foreground service types، App Links، وminimum/target SDK وتأثيرهم. مجرد declaration للـpermission مش معناها user وافق على runtime permission. في release review، شغّل manifest merger output وافتح components اللي SDKs أضافتها، وجرب invoke مباشر لها بIntent خارجي. بيانات session أو API key ما تتحطش في manifest metadata لأنها ضمن package القابل للفحص.

## Trade-offs and decision criteria

Explicit components and least privilege reduce unintended entry points. Intent filters enable external navigation but increase input validation obligations. A hardware `<uses-feature>` marked required can exclude devices from distribution; optional features need graceful fallback. Library manifest entries simplify integration, but the app owner still must audit the merged result.

## Failure modes

A missing declaration prevents a component from launching. An unintended exported component exposes internal operations. A permission added by an SDK may change privacy and distribution behavior. An overly strict required feature filters out supported devices. Diagnose with Android Studio's Merged Manifest view and build outputs, then test external entry points with adversarial intents.

## Production perspective

For a banking app, review the merged release manifest on each dependency update. Keep internal components non-exported, minimize permissions, verify App Links and exported handlers, and test cold starts from external intents after process death. A CI manifest diff can flag new permissions and exported components for security review.

## Interview answer — short

“The manifest declares the app's components, permissions, intent filters, features, and key metadata to Android and the build and distribution systems. I inspect the merged manifest because libraries and variants can change the shipped result.”

## Interview answer — structured

Android uses the manifest to discover and start components, and build tools merge declarations from the app, variants, and dependencies. It also lists requested permissions, device features, and application metadata. A permission declaration is not a runtime grant. I pay particular attention to `android:exported` and intent filters because they control external entry points. Before release I inspect the merged manifest, verify the permission and device-filter implications, and test exported handlers with untrusted input.

## Interview answer — deep senior

I treat the manifest as a shipped platform contract. Activities, services, receivers, and providers are declared there because Android can instantiate them directly. Intent filters and exported flags determine which external calls may reach them; those calls still need validation and authorization in code. Permissions and uses-feature declarations affect platform access and potentially Play device eligibility. Gradle merges source-set and dependency manifests, so reviewing only the source file misses the actual behavior. I inspect the merged release manifest after dependency changes, diff sensitive entries in CI, and test cold external launches and process restoration.

I inspect the merged release manifest because dependencies can contribute components, filters, and metadata that are absent from the app module’s source manifest. An exported Activity for a web link may be needed, but its URI and caller-controlled extras still require validation; an internal admin service should normally remain private. A manifest permission declaration also does not grant runtime permission, so the corresponding user flow must be tested. I would include a component inventory in release review and exercise entry points from a separate test app. Secrets do not belong in manifest metadata because packaged declarations are inspectable.

## How to answer in the interview

- **Why:** The manifest declares app entry points and platform capabilities.
- **How:** Describe the merged manifest, exports, filters, permissions, and service declarations.
- **Trade-offs:** Declare only components/capabilities needed by the feature.
- **Failure cases:** Explain a library-added exported provider or a permission declared but never requested.
- **Production solution:** Audit the release merged manifest and exercise external entry points.

## Deep-dive talking points

Discuss manifest merger, exported entry points, runtime grants, feature filtering, and validation after deep-link launch.

## Follow-up questions

- What does `android:exported` protect? **Answer:** it controls whether other apps can launch or bind a component; an exported handler still needs input validation and authorization.
- Why inspect the merged manifest? **Answer:** flavors, build types, and dependencies may add or override declarations in the final packaged app.
- Does `<uses-permission>` grant camera access? **Answer:** no; dangerous permissions also require the platform's runtime grant flow on relevant versions.

## Self-check rubric

Name the four component types, describe manifest merging, distinguish declaration from runtime grant, review an exported handler, and explain a device-feature consequence.

## References and reviewed-on date

- [App manifest overview](https://developer.android.com/guide/topics/manifest/manifest-intro) — required declarations and manifest purpose.
- [Manage manifests](https://developer.android.com/studio/build/manage-manifests) — merger and merged-manifest inspection.

Technically reviewed against these primary sources on 2026-10-13 by editorial review. The configuration example is illustrative.
