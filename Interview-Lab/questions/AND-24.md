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

## Concept and technical explanation

Deep links and universal App Links bridge external web pages, emails, and third-party messaging apps into an application's internal navigation stack. Because incoming URIs and Intent extras originate outside the application's security boundary, they must be treated as completely untrusted input. Malicious actors frequently exploit unvalidated deep links to execute path traversal attacks, trigger arbitrary internal screen navigation (bypassing authentication or payment gates), manipulate query parameters, or abuse open redirectors to phish credentials.
Securing deep link navigation requires a comprehensive validation pipeline across multiple architectural checkpoints. First, apps should prioritize verified Android App Links (https scheme) configured with Digital Asset Links (.well-known/assetlinks.json) over custom URI schemes (myapp://), which lack domain verification and can be hijacked by malicious third-party apps on the same device. Second, the incoming URI must be rigorously parsed against an explicit allowlist of supported schemes, hosts, and paths. Third, all query parameters must undergo strict type validation and regex sanitization to block path traversal sequences (such as ../). Fourth, incoming routes targeting protected resources must be gated behind an authentication and authorization layer, ensuring that unauthenticated users are intercepted and redirected to a login flow before accessing sensitive destinations.

## Practical walkthrough (English)

Implementing a secure, layered deep link validation gateway before dispatching navigation:

```kotlin
class DeepLinkHandler {
    fun parseAndValidate(uri: Uri?, session: UserSession): NavigationTarget? {
        if (uri == null) return null

        // 1. Enforce strict Scheme and Host allowlist:
        if (uri.scheme != "https" || uri.host != "app.mycompany.com") {
            return null
        }

        // 2. Validate Path and sanitize parameters:
        val segments = uri.pathSegments
        return when {
            segments.size == 2 && segments[0] == "product" -> {
                val productId = segments[1]
                // Ensure ID is alphanumeric, preventing injection or traversal:
                if (productId.matches(Regex("^[a-zA-Z0-9_-]{1,32}$"))) {
                    NavigationTarget.ProductDetails(productId)
                } else null
            }

            segments.size == 1 && segments[0] == "checkout" -> {
                // 3. Authorization check before navigation:
                if (session.isAuthenticated) {
                    NavigationTarget.Checkout
                } else {
                    NavigationTarget.Login(returnTarget = NavigationTarget.Checkout)
                }
            }

            else -> null // Reject unrecognized paths
        }
    }
}
```

Failure scenario: A deep link handler accepts myapp://webview?url=... without domain validation. An attacker sends a malicious SMS containing myapp://webview?url=https://phishing-login.com. When tapped, the app opens the internal WebView displaying the attacker's phishing site within the trusted application frame, tricking the user into revealing sensitive banking credentials.

## Explanation in Arabic

فحص وتأمين الروابط العميقة غير الموثوقة (Untrusted Deep Links) قبل التنقل هو أحد أهم اختبارات الأمان في تطبيقات أندرويد لمنع ثغرات الـ Phishing والـ Injection:

1. ما هي المخاطر الأمنية في الـ Deep Links غير الموثوقة؟
   - الـ Deep Link يمكن أن يأتي من رابط ويب خبيث، رسالة SMS تصيد احتيالي، أو تطبيق خبيث على هاتف المستخدم.
   - **تجاوز المصادقة (Auth Bypass):** رابط يفتح `myapp://checkout/confirm?orderId=123` ويقوم بالشراء بدون التحقق من تسجيل دخول المستخدم.
   - **هجمات الـ Path Traversal و Parameter Tampering:** التلاعب بالـ URL Parameters لتغيير حساب المستلم أو سرقة بيانات.
   - **الـ Open Redirect:** رابط خبيث يوجه الـ WebView الداخلي لفتح موقع خارجي مزيف وسرقة بيانات الدفع.

2. ما هي إجراءات التحقق الإلزامية (The 4-Step Validation Pipeline)؟
   - **1. التحقق من المخطط والنطاق (Scheme & Host Validation):** التأكد من أن الرابط يطابق الـ Host الشرعي، وتفضيل Android App Links الموثقة (`https://example.com`).
   - **2. فحص مسار الوجهة (Path Whitelisting):** مطابقة الـ Path مع قائمة بيضاء صارمة للمسارات المسموح بها في التطبيق.
   - **3. فحص وتطهير المعاملات (Parameter Sanitization):** التحقق من صحة المعرفات (مثل التأكد من أن `orderId` رقم صالح ولا يحتوي على أكواد حقن).
   - **4. فحص جلسة المستخدم (Authentication Gate):** التحقق من أن المستخدم مسجل للدخول قبل فتح الشاشات الحساسة؛ وإذا لم يكن مسجلاً، توجيهه لصفحة الدخول أولاً.

## Practical walkthrough

تنفيذ معالج Deep Link آمن في الكود:
```kotlin
class DeepLinkHandler {
    fun parseAndValidate(uri: Uri?, session: UserSession): NavigationTarget? {
        if (uri == null) return null
        
        // 1. التحقق من الـ Host:
        if (uri.host != "app.mycompany.com") return null
        
        // 2. مطابقة المسارات مع القائمة البيضاء:
        return when (uri.path) {
            "/product" -> {
                val id = uri.getQueryParameter("id")
                // 3. التحقق من المعامل:
                if (!id.isNullOrBlank() && id.all { it.isLetterOrDigit() }) {
                    NavigationTarget.ProductDetails(id)
                } else null
            }
            "/profile" -> {
                // 4. بوابة المصادقة الحساسة:
                if (session.isLoggedIn) NavigationTarget.Profile else NavigationTarget.Login(redirectTo = "profile")
            }
            else -> null // رفض أي مسار غير معتمد
        }
    }
}
```

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

## Trade-offs and decision criteria

Allowlisting exact hosts/routes is restrictive but audit-friendly; accepting flexible redirects increases ambiguity and attack surface. Verified App Links reduce hijacking risk for owned web domains, but custom schemes remain claimable by other apps. A signed one-time link can prove a server-issued token if the backend validates its expiry and audience, yet sensitive actions should still enforce session, CSRF/replay protection as applicable, and server-side authorization.

## Failure modes

Checking `contains("example.com")` accepts `example.com.attacker.test`. Trusting an `accountId` query parameter can expose another user's data if the backend does not check ownership. Forwarding an embedded Intent may invoke a privileged internal component. Loading an arbitrary link into a WebView can expose cookies or bridge APIs. Test malformed encoding, extra/multiple parameters, lookalike hosts, expired sessions, and logged-out navigation. Log a sanitized rejection reason, not the full token-bearing URI.

## Production perspective

Define a typed link contract per destination, validate it at one ingress boundary, and pass only validated route arguments internally. Recheck auth after process recreation or account switch. The backend enforces receipt ownership on every fetch. Test `adb am start` cases and App Link verification for supported Android versions, plus a matrix of malicious URLs in unit tests. Track rejected-route rates without storing raw private links.

## Interview answer — short

Treat every external deep link as untrusted input. Validate scheme and host against strict allowlists, and prefer verified Android App Links with Digital Asset Links over custom schemes to prevent intent hijacking. Sanitize all path parameters to prevent injection or directory traversal, and route sensitive destinations through an authentication gate to enforce active session verification.

## Interview answer — structured

Every incoming deep link originates outside the application boundary and must be treated as untrusted user input. We prioritize verified Android App Links using HTTPS and Digital Asset Links over custom URI schemes, preventing rogue applications installed on the device from intercepting our traffic via intent filter collisions.

The deep link ingress must pass through a centralized validation gateway before invoking navigation. The router matches incoming URIs against a strict allowlist of recognized schemes, domain hosts, and path patterns, instantly dropping unknown or malformed URIs.

In production, path and query parameters require rigorous sanitization. We parse parameters into strongly typed domain models, enforcing alphanumeric regex constraints to prevent SQL injection, cross-site scripting in WebViews, and directory traversal sequences like ../.

Access to sensitive destinations like account settings or checkout must be gated behind authentication guards. If an incoming link targets a protected screen while the user session is expired or unauthenticated, the router halts navigation, redirects to the login gateway, and caches the validated destination to resume navigation post-authentication.


## Interview answer — deep senior

From a security engineering perspective, deep link vulnerabilities are among the most exploited vectors on mobile platforms. Custom URI schemes like myapp:// offer zero cryptographic ownership; any application on the device can declare an identical scheme in its manifest, leading to Intent Ambiguity dialogs or silent traffic hijacking. To establish verifiable identity, enterprise applications implement Android App Links, where the operating system's PackageManager verifies domain ownership during app installation by fetching assetlinks.json from the HTTPS domain and matching the SHA-256 fingerprint of the APK's release signing key.
Within the application, deep link handling must adhere to strict defensiveness against Open Redirects and Confused Deputy attacks. A notorious vulnerability pattern occurs when an exported activity takes a url query parameter and loads it directly into an internal WebView that has JavaScript and file access enabled. An external link loading a file URI can exfiltrate local SQLite databases. Our routing engine enforces that all WebView URLs match an explicit domain allowlist with strict subdomain validation.
Furthermore, navigation routing must never couple directly to raw framework Intent objects or Uri strings. In modern Jetpack Compose or Fragment architectures, the ingress Activity parses the raw URI, validates the structure, and maps it into a type-safe navigation destination using Kotlinx Serialization.
Finally, session state verification must occur in the Domain layer, not merely in UI navigation guards. If a deep link opens an order route, the UI destination must not assume user ownership of that order. When the repository fetches the resource, the backend API must validate that the authenticated bearer token owns the requested record, returning an HTTP 403 Forbidden if an attacker attempts horizontal privilege escalation by guessing sequential order identifiers.

## How to answer in the interview

- **Why:** An external URI crosses into privileged in-app navigation.
- **How:** Parse exact scheme, host, route shape, encoding, and expected parameters.
- **Trade-offs:** Reject unknown forms explicitly; keep route IDs opaque and bounded.
- **Failure cases:** Mention host-suffix bypass, encoded path tricks, and treating App Links as authorization.
- **Production solution:** Authenticate and server-authorize the receipt before rendering it.

## Deep-dive talking points

Distinguish App Link verification from payload trust; explain exact host matching, encoded path ambiguities, typed routes, account switching, backend object authorization, and avoiding unsafe nested Intents or WebView targets.

## Follow-up questions

- **Interviewer:** "Why are custom URI schemes like `myapp://` considered insecure?"
  **Answer:** "Because Android does not verify ownership of custom URI schemes. Multiple apps can register `myapp://` in their manifests, allowing a rogue app to intercept user clicks and steal sensitive parameters (like OAuth tokens)."

- **Interviewer:** "How do Android App Links fix that vulnerability?"
  **Answer:** "Android App Links use HTTPS domain verification via Digital Asset Links (`.well-known/assetlinks.json`) on your website. Android verifies that your app's signing certificate matches the website's asset links before allowing it to open automatically without user prompts."

- **Interviewer:** "What is Open Redirect vulnerability in mobile apps?"
  **Answer:** "An Open Redirect occurs when an app accepts an unvalidated target URL parameter in a deep link and redirects its internal navigation or WebView to that URL, exposing users to phishing attacks."

## Self-check rubric

Give exact scheme/host/path/parameter checks; explain why App Links are not authorization; route an unauthenticated user safely; name two malicious inputs; and place the final access check on the backend.

## References and reviewed-on date

- [Unsafe use of deep links](https://developer.android.com/privacy-and-security/risks/unsafe-use-of-deeplinks) — validation and authorization risks.
- [About Android App Links](https://developer.android.com/training/app-links/about) — verified-domain routing boundary.

Technically reviewed against primary documentation on 2026-10-13.
