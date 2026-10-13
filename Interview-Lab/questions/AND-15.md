---
id: "AND-15"
question: "Compare Activity, Fragment, Compose navigation, and deep links."
topic: "Android Fundamentals, Lifecycle & Context"
code: "AND"
group: "B"
phase: 1
priority: "P1"
order: 45
editorial_status: "reviewed"
---

# AND-15

## Original interview question

Compare Activity, Fragment, Compose navigation, and deep links.

## What the interviewer evaluates

- Separate platform component lifecycle from in-app destinations and external entry routes.
- Explain back stack, saved state, arguments, and process restoration across each choice.
- Recognize that a deep link must be validated and authorized regardless of UI toolkit.

## Explanation in Arabic

المقارنة الشاملة بين نماذج التنقل (Navigation Paradigms) في Android: Activity vs Fragment vs Compose Navigation vs Deep Links:

1. الـ Multi-Activity Navigation (النموذج الكلاسيكي القديم):
   - كل شاشة عبارة عن `Activity` منفصلة.
   - **العيوب:** استهلاك كبير لموارد النظام (كل Activity لها Window و Context منفصل)؛ انتقال بطيء مع وميض بين الشاشات؛ صعوبة مشاركة البيانات المعقدة؛ وعدم مرونة الـ Animations.

2. الـ Fragment-based Navigation (Single-Activity Architecture):
   - `MainActivity` واحدة تحتوي على `NavHostFragment` وشاشات عبارة عن `Fragments`.
   - **المميزات:** أسرع بكثير وأخف في الذاكرة؛ إمكانية مشاركة ViewModel على مستوى الـ Activity أو الـ Graph؛ ودعم كامل للـ Navigation Component XML.
   - **العيوب:** تعقيد دورة حياة الـ Fragment View وضرورة إدارة `viewLifecycleOwner` لتجنب الـ Leaks.

3. الـ Jetpack Compose Navigation (النموذج الحديث 100%):
   - التنقل بين دوال `@Composable` عادية تماماً (`NavHost(navController) { composable("route") }`).
   - **المميزات:** خفيف جداً بدون أي Fragment overhead؛ يزيل الـ ViewBinding leaks تماماً؛ وتكامل تام مع Type-Safe Navigation (Kotlin Serialization في Compose 2.8+).

4. الـ Deep Links (الروابط العميقة):
   - فتح شاشة معينة داخل التطبيق مباشرة من رابط خارجي (URL أو إشعار).
   - تتطلب بناء **Synthetic Backstack** سليم حتى إذا ضغط المستخدم زر 'Back' يعود للشاشة السابقة للتطبيق وليس للخروج من التطبيق فجأة.

## Practical walkthrough

كيف تطورت كتابة الـ Navigation حتى الـ Type-Safe Navigation الحديثة في Compose:
```kotlin
// مع Compose 2.8+ و Kotlinx Serialization:
@Serializable data class ProductDetailsRoute(val productId: String, val fromSearch: Boolean)

NavHost(navController = navController, startDestination = HomeRoute) {
    composable<HomeRoute> { HomeScreen(onProductClick = { id -> 
        navController.navigate(ProductDetailsRoute(id, true)) 
    }) }
    
    composable<ProductDetailsRoute> { backStackEntry ->
        val route: ProductDetailsRoute = backStackEntry.toRoute()
        ProductDetailsScreen(productId = route.productId)
    }
}
```
وداعاً للـ String URLs والأخطاء الإملائية؛ التنقل أصبح Type-Safe 100%.

## Why it matters and how it works

An Activity is a platform component with its own task semantics and lifecycle. A Fragment is hosted and managed by an Activity; its view can be destroyed independently of the Fragment. Compose Navigation models destinations as entries in an in-app back stack, with arguments and scoped state. A deep link is an address into a destination, potentially delivered at cold start with a new process. Each layer must cooperate on restoration: the system recreates components and saved state, while repositories reload durable business data.

## Worked example

A commerce app has one host Activity with Compose destinations for catalog, product, and cart. A verified HTTPS App Link opens `/product/42`; the Activity parses a stable product ID, Navigation creates the destination, and the ViewModel loads the product from a repository. If the user is unauthenticated for a private order route, navigation goes through sign-in and resumes only after authorization. This is an architecture sketch; exact navigation code depends on library version and existing app structure.

## Trade-offs and decision criteria

Multiple Activities can express platform tasks or separate surfaces, but cross-Activity state and transitions take more coordination. Fragments remain appropriate for existing View-based apps and some hosted integrations; observe their view lifecycle correctly. Navigation Compose keeps Compose destination behavior together but requires deliberate argument and state design. Deep links improve reachability while expanding the input surface; prefer stable IDs over serialized objects in URLs.

## Failure modes

Treating a Fragment's lifecycle as its view lifecycle leaks bindings. Passing a mutable object through a navigation route creates stale or oversized state. A deep link may arrive with no prior in-memory session and crash a destination that assumes earlier screens ran. Back-stack behavior can differ after an external launch. Test cold links, authenticated and unauthenticated cases, rotation, process recreation, and Up versus Back navigation.

## Production perspective

Define a route contract per destination, sanitize untrusted URI parameters, and reconstruct screen state from stable IDs. Keep authorization in a domain or data boundary, not only in navigation guards. Record link-routing failures without sensitive query data. Add UI tests for task entry from notification and browser as well as ordinary in-app movement.

## Interview answer — short

Multi-Activity navigation is heavy and deprecated; Fragment navigation (Single-Activity) is lightweight but has complex view lifecycles; Compose Navigation is modern, declarative, and type-safe with zero Fragment overhead; and Deep Links route external URLs directly to internal screens requiring synthetic backstacks.

## Interview answer — structured

Modern Android architecture has evolved through four navigation paradigms:

1. **Multi-Activity (Legacy)**: Each screen is an Activity. It incurs high memory overhead per window, creates clunky window transitions, and makes complex state sharing difficult. It is now reserved only for truly distinct app entry points (e.g., Auth vs Main App).

2. **Fragment Navigation (Single-Activity Architecture)**: A single Activity hosts a `NavHostFragment`. It improved transition fluidity and memory efficiency, enabling shared ViewModels. However, managing the dual lifecycle of Fragments and nulling ViewBindings added cognitive overhead.

3. **Jetpack Compose Navigation (Modern Standard)**: Pure declarative navigation between Composables via `NavHost` and `NavController`. It eliminates Fragment view boilerplate entirely. Starting with Navigation Compose 2.8+, it supports **Type-Safe Navigation** using Kotlinx Serialization classes instead of error-prone String route paths.

4. **Deep Links**: URL-based ingress allowing notifications, emails, or web links to route directly to internal destinations. They require proper synthetic backstack construction via `TaskStackBuilder` so pressing Back navigates up the logical app hierarchy rather than exiting to the launcher.

## Interview answer — deep senior

At the architectural boundary, Deep Links pose significant security and state-restoration challenges: When an external link opens `myapp://order/123`, the app must not assume that the user is authenticated. The navigation graph must implement a conditional gateway: if the user's session token is missing or expired, intercept the deep link, redirect to the Login route, and upon successful authentication, resume navigation to the intended target route.

Furthermore, for App Links (`https://example.com/order/123`), verifying Android App Links via Digital Asset Links (`.well-known/assetlinks.json`) is mandatory. Verified App Links open your app directly without displaying the ambiguous system disambiguation dialog, protecting users against phishing by imposter apps claiming custom schemes.

## How to answer in the interview

- **Why:** Navigation must preserve a predictable task and state across entry paths.
- **How:** Separate Activity host, UI destination, navigation graph, and external deep link.
- **Trade-offs:** Keep the existing View/Compose stack coherent and scope ViewModels by destination.
- **Failure cases:** Mention broken Back stack and treating a route ID as authorization.
- **Production solution:** Open an order link, authenticate, load authorized data, and test cold Back/Up.

## Deep-dive talking points

Discuss task stack versus NavHost stack, Fragment view lifecycle, deep-link trust boundaries, state restoration, and stable route arguments.

## Follow-up questions

- **Interviewer:** "How does `NavBackStackEntry` scope ViewModels in Compose Navigation?"
  **Answer:** "Each destination in the navigation backstack is a `ViewModelStoreOwner`. A ViewModel retrieved inside a composable using `viewModel()` is scoped to that specific `NavBackStackEntry` and is automatically cleared when popped from the backstack."

- **Interviewer:** "What is the difference between Deep Links and Android App Links?"
  **Answer:** "Deep Links use custom URI schemes (e.g., `myapp://`) and trigger a system chooser if multiple apps support them. Android App Links use verified HTTP/HTTPS domains backed by a server `assetlinks.json` file, opening your verified app directly without dialogs."

- **Interviewer:** "How do you share a ViewModel between two destinations in Compose Navigation?"
  **Answer:** "By retrieving the parent destination's `NavBackStackEntry` via `remember(backStackEntry) { navController.getBackStackEntry("parent_route") }` and passing it to the `viewModel(viewModelStoreOwner = parentEntry)` factory."

## Self-check rubric

Define all four layers; describe a cold deep-link launch, back stack and state restoration; give a security check and a Fragment view-lifecycle pitfall.

## References and reviewed-on date

- [Guide to app architecture](https://developer.android.com/topic/architecture) — UI, state, and data boundaries.
- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — Compose destinations and route arguments.
- [Create deep links](https://developer.android.com/training/app-links/deep-linking) — external navigation entry.

Technically reviewed against primary documentation on 2026-10-13.
