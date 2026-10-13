---
id: "AND-24"
question: "Your app receives an untrusted deep link. What validation should happen before navigation?"
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "C"
phase: 1
priority: "P1"
order: 54
editorial_status: "reviewed"
---

# AND-24

## Original interview question

Your app receives an untrusted deep link. What validation should happen before navigation?

## What the interviewer evaluates

- Treat every externally supplied URI and extra as untrusted input, even for a verified App Link.
- Validate route shape and identifiers, then recheck authentication and authorization at the destination/backend.
- Prevent unsafe intent redirection, WebView loading, and sensitive-action side effects from URL parameters.

## Explanation in Arabic

الـdeep link مدخل من خارج التطبيق، فلازم تفترض إن أي app أو صفحة ممكن تبعته أو تغيّر path وquery. اقبل `https` وhost محدد وpath بالشكل المتوقع؛ فكّ الـID وتأكد من نوعه وطوله، وارفض parameters الزيادة أو المكررة لو مش جزء من العقد. بعد كده افحص session، وخلي الـbackend يتحقق من حق المستخدم في قراءة الـresource؛ الـlink نفسه مش authorization. Verified App Links بتحسن ربط الدومين بالتطبيق، لكنها مش إثبات إن محتوى الرابط موثوق أو إن المستخدم مصرح له. ما تمررش nested Intent أو URL للـWebView بدون allowlist وفحص مستقل.

## Why it matters and how it works

An exported entry Activity receives an Intent containing a URI chosen outside the app. Manifest filters help the system route links, and verified App Links associate an HTTPS domain with the app, but input parsing and access control remain application duties. Parse exact scheme, normalized host, path segment count, ID format, allowed query keys, and fragments before creating a typed internal route. Navigation should resolve current authentication, then ask the backend for the resource under that user's credentials. No deep link may authorize a transfer, skip login, or change account context by itself.

## Worked example

Illustrative Android parser for a read-only receipt route; the surrounding app must implement sign-in gating and server authorization. The ID is an opaque lowercase UUID supplied by the backend. Rejecting all query and fragment data simplifies this route's contract.

```kotlin
import android.net.Uri

fun receiptIdFromLink(uri: Uri): String? {
    if (uri.scheme != "https" || uri.host != "app.example.com") return null
    if (uri.port != -1 || uri.encodedQuery != null || uri.encodedFragment != null) return null
    val parts = uri.pathSegments
    if (parts.size != 2 || parts[0] != "receipts") return null
    val id = parts[1]
    return id.takeIf {
        it.length == 36 && it.matches(
            Regex("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
        )
    }
}
```

The parser only creates a typed ID. Before showing a receipt, the destination requests it from the backend; `404`/`403` get deliberate UI states. Test encoded path separators and mixed-case hosts against the actual URI parser and routing contract.

## Practical walkthrough

deep link جاي من خارج app حتى لو verified App Link؛ verify link ownership بيحدد مين يستقبل URI، مش مين مسموح له يشوف receipt. parser لازم يحدد `https`، host مطابق بالكامل، path shape، encoded segments، طول/format ID، ورفض query/fragment غير المتوقعة؛ تجنب prefix host check زي `endsWith("example.com")` اللي قد يقبل نطاق ضار. بعد parsing اعمل sign-in gate وserver ownership check، ولا تنفّذ side effect حساس بمجرد فتح link. اختبر double encoding، encoded slash، null/blank، accounts مختلفة، cold start، process restore. خلّي bad link يروح safe route بدون crash.

## Trade-offs and decision criteria

Allowlisting exact hosts/routes is restrictive but audit-friendly; accepting flexible redirects increases ambiguity and attack surface. Verified App Links reduce hijacking risk for owned web domains, but custom schemes remain claimable by other apps. A signed one-time link can prove a server-issued token if the backend validates its expiry and audience, yet sensitive actions should still enforce session, CSRF/replay protection as applicable, and server-side authorization.

## Failure modes

Checking `contains("example.com")` accepts `example.com.attacker.test`. Trusting an `accountId` query parameter can expose another user's data if the backend does not check ownership. Forwarding an embedded Intent may invoke a privileged internal component. Loading an arbitrary link into a WebView can expose cookies or bridge APIs. Test malformed encoding, extra/multiple parameters, lookalike hosts, expired sessions, and logged-out navigation. Log a sanitized rejection reason, not the full token-bearing URI.

## Production perspective

Define a typed link contract per destination, validate it at one ingress boundary, and pass only validated route arguments internally. Recheck auth after process recreation or account switch. The backend enforces receipt ownership on every fetch. Test `adb am start` cases and App Link verification for supported Android versions, plus a matrix of malicious URLs in unit tests. Track rejected-route rates without storing raw private links.

## Interview answer — short

“I treat a deep link as untrusted input. I allowlist scheme, host, route, identifier, and parameters, then require authentication and backend authorization before showing data or doing anything sensitive. Verified App Links help routing, but do not make the URL's contents trusted.”

## Interview answer — structured

The exported Activity should parse the incoming URI into a typed route only after exact scheme and host checks, path-shape and ID validation, and rejection of unknown parameters. I do not pass arbitrary nested Intents or URLs into privileged components or WebViews. A receipt link then goes through login if necessary and a backend ownership check. I test malformed encodings, host lookalikes, account switching, and Android App Link verification. Verified App Links improve domain routing but do not validate every path or authorize the referenced account.

## Interview answer — deep senior

I separate three trust boundaries: OS routing, application parsing, and backend authorization. Domain verification reduces who can intercept an HTTPS link, but any sender can still construct a URL and the app can be launched through other paths. At ingress I enforce a typed, minimal route contract and reject malformed/extra data; downstream code receives only validated IDs. Session and account context come from trusted state, not URI parameters, and the backend checks object ownership. For sensitive actions I use a server-issued, expiring, replay-aware token or an explicit in-app confirmation as appropriate, and never trigger a transfer solely by opening a URL. I test adversarial URI encodings and process-restored navigation.

A receipt link is a route request, not a privilege. I require an exact HTTPS scheme and host, expected path segment count, bounded opaque ID format, and a deliberate policy for query and fragment data. Prefix or suffix host checks can accept attacker-controlled domains, and encoded slashes can change how a naive parser interprets the path. After parsing I gate sign-in and ask the backend whether the current account owns the receipt. The handler should fail to a safe destination, not crash or perform a write. I test cold launch, wrong accounts, double encoding, and process-restored navigation.

## How to answer in the interview

- **Why:** An external URI crosses into privileged in-app navigation.
- **How:** Parse exact scheme, host, route shape, encoding, and expected parameters.
- **Trade-offs:** Reject unknown forms explicitly; keep route IDs opaque and bounded.
- **Failure cases:** Mention host-suffix bypass, encoded path tricks, and treating App Links as authorization.
- **Production solution:** Authenticate and server-authorize the receipt before rendering it.

## Deep-dive talking points

Distinguish App Link verification from payload trust; explain exact host matching, encoded path ambiguities, typed routes, account switching, backend object authorization, and avoiding unsafe nested Intents or WebView targets.

## Follow-up questions

- [AND-16](../and-16/): Does `android:exported="false"` fit an external link Activity? **Answer:** no; an external entry point must be exported and protected by narrow routing and validation.
- [SEC-18](../sec-18/): Can a verified host authorize a receipt read? **Answer:** no; the backend must check the authenticated user's ownership.
- [AND-25](../and-25/): What happens after process recreation? **Answer:** revalidate route arguments and session state before restoring the destination.

## Self-check rubric

Give exact scheme/host/path/parameter checks; explain why App Links are not authorization; route an unauthenticated user safely; name two malicious inputs; and place the final access check on the backend.

## References and reviewed-on date

- [Unsafe use of deep links](https://developer.android.com/privacy-and-security/risks/unsafe-use-of-deeplinks) — validation and authorization risks.
- [About Android App Links](https://developer.android.com/training/app-links/about) — verified-domain routing boundary.

Technically reviewed against these primary sources on 2026-10-13 by editorial review. The parser is illustrative and has not been compiled against an Android SDK in this repository.
