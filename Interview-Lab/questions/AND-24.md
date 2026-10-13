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

Validate untrusted deep links by verifying the scheme and host, strictly whitelisting allowed path patterns, sanitizing all query parameters to prevent injection or path traversal, and enforcing an authentication gateway before navigating to protected screens.

## Interview answer — structured

Deep links are inherently untrusted external input that must undergo rigorous security validation before driving navigation:

1. **Scheme & Host Whitelisting**: Verify that incoming URIs strictly match authorized domains. Prefer verified Android App Links (`https://`) backed by `assetlinks.json` over custom schemes (`myapp://`), which any malicious app can register and hijack.

2. **Strict Path Routing**: Route exclusively against a hardcoded whitelist of allowed destination paths. Never use dynamic reflection or generic string concatenation to instantiate activities from deep link path segments.

3. **Query Parameter Sanitization**: Validate types and bounds on all parameters (e.g., verifying `id` matches expected alphanumeric UUID formats) to prevent SQL injection or path traversal attacks.

4. **Authentication and Authorization Gate**: Never assume an authenticated session when processing deep links. If a deep link targets an authenticated screen (like Account Settings or Checkout), the navigation handler must verify active credentials. If unauthenticated, redirect to the Login flow, caching the target route to resume upon successful authentication.

## Interview answer — deep senior

From an application security standpoint, special care must be taken with **Embedded WebViews** opened via deep links. If a deep link accepts a parameter like `myapp://webview?url=https://...`, an attacker can craft a link pointing to a phishing website (`https://evil-phishing.com`). If the internal WebView has JavaScript interfaces enabled (`addJavascriptInterface`), the external website can execute code within the app's context.

To secure WebView deep links: 1. Strictly enforce domain whitelisting on all target URLs. 2. Never pass arbitrary query parameters directly into database queries or IPC intents without strict parsing. 3. Ensure the receiving Activity validates incoming extras before forwarding them to internal exported components.

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
