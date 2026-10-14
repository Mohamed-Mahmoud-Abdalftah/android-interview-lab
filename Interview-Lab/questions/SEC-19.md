---
id: "SEC-19"
question: "How do you secure WebView, JavaScript bridges, and file/content URIs?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 316
editorial_status: "reviewed"
---

# SEC-19

## Original interview question

How do you secure WebView, JavaScript bridges, and file/content URIs?

## What the interviewer evaluates

- WebView origin/content controls and JavaScript bridge exposure.
- File/content URI handling and external URL navigation.

## Explanation in Arabic

كيف تقوم بتأمين الـ WebView، جسور الـ JavaScript، والوصول إلى ملفات النظام و الـ Content URIs؟

1. مخاطر الـ WebView في أندرويد:
   - الـ WebView هو متصفح كامل مدمج داخل تطبيقك. إذا سمحت له بتحميل محتوى غير موثوق، فإن أي ثغرة Cross-Site Scripting (XSS) في صفحة الويب تتحول مباشرة إلى ثغرة اختراق لتطبيق أندرويد نفسه!

2. تأمين جسر الـ JavaScript (@JavascriptInterface):
   - ربط كود Kotlin بـ JavaScript عبر `addJavascriptInterface` يسمح لكود الويب باستدعاء دوال native.
   - **قاعدة صارمة**: لا تقم بحقن الـ JS Interface أبداً في صفحات غير موثوقة. يجب التحقق من الدومين ومسار الصفحة (`origin`) في كود الـ WebView قبل تفعيل أو تنفيذ أي دالة في الجسر.

3. إغلاق منافذ الوصول للملفات المحلية (Local File Access):
   - بشكل افتراضي في الإصدارات الحديثة، ولكن يجب تأكيده برمجياً:
     * `settings.allowFileAccess = false`: يمنع تحميل ملفات التطبيق المحلية عبر `file://`.
     * `settings.allowContentAccess = false`: يمنع الوصول إلى الـ Content Providers.
     * يمنع هجمات سرقة ملفات الـ SharedPreferences وقواعد البيانات عبر كود HTML خبيث.

4. التحميل الآمن للأصول المحلية عبر `WebViewAssetLoader`:
   - بدلاً من تحميل الملفات عبر بروتوكول `file:///android_asset/` غير الآمن، استخدم مكتبة AndroidX `WebViewAssetLoader` التي تقوم بتحميل الأصول المحلية تحت بروتوكول افتراضي آمن (`https://appassets.androidplatform.net/`)، مما يحافظ على تطبيق سياسة Same-Origin Policy ويمنع تسريب البيانات.

5. التعامل الصارم مع أخطاء شهادات الـ SSL:
   - **ممنوع نهائياً**: استدعاء `handler.proceed()` داخل دالة `onReceivedSslError`. هذا يسمح بهجمات Man-in-the-Middle (MITM). يجب دائماً استدعاء `handler.cancel()`.

## Practical walkthrough

تكوين WebView آمن للإنتاج مع إغلاق منافذ الملفات واستخدام WebViewAssetLoader والتحقق من الـ SSL:
```kotlin
class SecureWebActivity : ComponentActivity() {
    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        webView = WebView(this)
        setContentView(webView)
        configureSecureSettings(webView)
    }

    private fun configureSecureSettings(view: WebView) {
        view.settings.apply {
            // 1. تقييد الوصول للملفات والـ Content URIs:
            allowFileAccess = false
            allowContentAccess = false
            javaScriptEnabled = true // تفعيل فقط عند الحاجة القصوى
            
            // تعطيل مشاركة الموقع والتخزين غير الضروري
            setGeolocationEnabled(false)
            databaseEnabled = false
        }

        // 2. استخدام AssetLoader الآمن لتحميل الملفات المحلية كـ HTTPS مجازي:
        val assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        view.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {
                return assetLoader.shouldInterceptRequest(request.url)
            }

            override fun onReceivedSslError(view: WebView, handler: SslErrorHandler, error: SslError) {
                // ❌ لا تقم أبداً باستدعاء handler.proceed()!
                // ✅ إلغاء الطلب فوراً لحماية المستخدم من هجمات MITM:
                handler.cancel()
            }
        }
    }
}
```

## Why it matters and how it works

JavaScript interfaces can be invoked by frames loaded into the WebView, so origin assumptions must be explicit. WebView settings and navigation callbacks govern JavaScript, mixed content, file access and URL transitions. `WebViewAssetLoader` provides a safer way to serve bundled assets over an HTTPS-like origin.

## Worked example

Android example for a controlled, read-only receipt origin. This screen has no JavaScript bridge and no need for file/content access. A feature needing JavaScript must be reviewed separately for origin and message validation.

```kotlin
import android.net.Uri
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient

fun configureReceipt(webView: WebView) {
    webView.settings.javaScriptEnabled = false
    webView.settings.allowFileAccess = false
    webView.settings.allowContentAccess = false
    webView.webViewClient = object : WebViewClient() {
        private fun blocked(uri: Uri): Boolean =
            uri.scheme != "https" || uri.host != "receipts.example.com"

        override fun shouldOverrideUrlLoading(
            view: WebView, request: WebResourceRequest,
        ): Boolean = blocked(request.url)

        @Suppress("DEPRECATION")
        override fun shouldOverrideUrlLoading(view: WebView, url: String): Boolean =
            blocked(Uri.parse(url)) // older Android versions
    }
    webView.loadUrl("https://receipts.example.com/")
}
```

Returning `true` blocks navigation outside the allowed origin; production code also needs a policy for redirects, external links and embedded subresources.

## Trade-offs and decision criteria

A WebView can speed integration of hosted checkout, but its JS bridge and navigation enlarge attack surface. Native screens avoid some browser risks; hosted checkout may reduce direct card-data handling if the provider’s documented flow is followed.

## Failure modes

Loading a user-supplied URL then exposing a bridge allows injected content to invoke native methods. A permissive file URL setting can expose local resources. Validate origin, restrict settings and test redirects, iframes and compromised content.

## Production perspective

Security tests enumerate loaded domains, redirects, bridge methods and URI grants. A payment success page is treated as presentation; backend state determines completion. Release configs disable WebView debugging where appropriate.

## Interview answer — short

Secure WebViews by disabling allowFileAccess and allowContentAccess, loading local bundled content safely via AndroidX WebViewAssetLoader under a virtual HTTPS origin, canceling onReceivedSslError unconditionally, and strictly restricting addJavascriptInterface to audited, whitelisted internal origins.

## Interview answer — structured

Hardening Android WebView requires mitigating data exfiltration, local file access, and bridge exploitation.

First, with Disable File & Content Scheme Access, Next, explicitly disable `settings.allowFileAccess = false` and `settings.allowContentAccess = false`. This blocks attackers from using malicious scripts or iframe tags to read private app files (`file:///data/data/<package>/...`) or query internal ContentProviders.
**Use AndroidX WebViewAssetLoader**. Traditional `file:///android_asset/` URLs violate modern web security models and cross-origin boundaries. `WebViewAssetLoader` intercepts requests and serves local assets via a virtual domain (`https://appassets.androidplatform.net/assets/`), enforcing the standard Same-Origin Policy and secure HTTPS context.
**Lock Down JavaScript Interfaces**. Only expose `@JavascriptInterface` methods to pages loaded from strictly whitelisted, first-party HTTPS origins verified inside `shouldOverrideUrlLoading` or `onPageStarted`.
**Unconditional SSL Error Rejection**. Finally, in `WebViewClient.onReceivedSslError()`, always call `handler.cancel()`. Never call `handler.proceed()`, as doing so completely bypasses TLS validation and exposes users to Man-in-the-Middle attacks.


## Interview answer — deep senior

From an advanced security engineering perspective, WebViews represent a hybrid execution environment requiring strict boundaries.

First, with Safe Browsing Integration, in Android 8.0+ (API 27), verify that Google Safe Browsing is enabled in WebView (`settings.safeBrowsingEnabled = true`). Implement `onSafeBrowsingHit()` to handle malicious phishing URLs identified by Google before page rendering begins. Next, with Mitigating Universal Cross-Site Scripting (UXSS), for sensitive hybrid applications, enable multi-process WebView mode (default on Android 8+) and restrict JavaScript execution permissions dynamically. Avoid exposing native payment or authentication tokens through JavaScript bridge callback return values; instead, bridge only transient action triggers while executing actual cryptographic token transfers over native secure channels.
Finally, with Content Security Policy (CSP), ensure server responses loaded into WebViews include strict HTTP Content Security Policy headers (`default-src 'self'`), mitigating inline script injections and preventing unauthorized external script loading.


## How to answer in the interview

- **Why:** WebView bridges and URIs cross trust boundaries.
- **How:** allowlist origins, minimize JavaScript exposure, disable unnecessary file access, and validate content reads.
- **Trade-off:** strict loading rules can constrain third-party content.
- **Failure case:** untrusted page invokes a privileged bridge.
- **Production solution:** isolated WebView design and hostile-content tests.

## Deep-dive talking points

Prompt for frame origin, bridge API surface, file/content URI policy, redirects, and authoritative checkout status.

## Follow-up questions

- **Interviewer:** "Why is addJavascriptInterface dangerous on Android versions prior to API 17?"
  **Answer:** "On Android < 4.2, reflection could be used by injected JavaScript to access getClass().forName() on Java objects and execute arbitrary Linux shell commands."

- **Interviewer:** "What is the security risk of enabling setAllowUniversalAccessFromFileURLs(true)?"
  **Answer:** "It permits scripts running in a local file context to make cross-origin requests to arbitrary web origins, completely dismantling Same-Origin Policy."

## Self-check rubric

Can I outline origin allowlisting, bridge minimization, URI restrictions and server confirmation?

## References and reviewed-on date

- [WebView native bridge risks](https://developer.android.com/privacy-and-security/risks/insecure-webview-native-bridges) — interface exposure.
- [WebViewAssetLoader](https://developer.android.com/reference/androidx/webkit/WebViewAssetLoader) — local content loading.

Technically reviewed against primary documentation on 2026-10-13.
