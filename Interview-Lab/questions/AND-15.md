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

## Concept and technical explanation

Modern Android application architecture spans four evolutionary navigation paradigms, each representing distinct memory boundaries, lifecycle complexities, and routing models:

1. Multi-Activity Navigation:
The historical Android paradigm where every distinct screen is encapsulated in an independent, manifest-declared Activity. Activities represent heavyweight OS-level windows managed directly by the platform ActivityTaskManagerService and the Linux low-memory killer. Transitions incur substantial IPC overhead, window-swapping latency, and isolated memory heaps. State sharing requires Parcelable Intent extras, making intra-app communication clunky and slow.

2. Single-Activity with Fragment Navigation:
Introduced to mitigate multi-activity overhead, this paradigm hosts multiple modular UI sub-trees (Fragments) within a single container Activity using the Jetpack Navigation Component. Destinations share a single Window and process heap, significantly accelerating transition performance. However, it introduces the notorious dual-lifecycle dilemma: a Fragment's object instance outlives its view tree when pushed to the backstack, creating pervasive ViewBinding and observer memory leak hazards.

3. Jetpack Compose Navigation:
The modern declarative paradigm where destinations are pure Composable functions hosted within a single NavHost. It completely eliminates FragmentManager overhead and view lifecycle bifurcation. In modern Navigation Compose (2.8+), destinations are declared type-safely using `@Serializable` Kotlin objects or data classes backed by Kotlinx Serialization, eliminating untyped route strings. Each backstack entry (`NavBackStackEntry`) acts as a dedicated LifecycleOwner, ViewModelStoreOwner, and SavedStateRegistryOwner, providing clean, scoped memory boundaries.

4. Deep Links and Android App Links:
External routing entry points that direct users into specific application destinations from web links, notifications, or third-party applications. Standard deep links rely on custom URI schemes (`myapp://product/42`), while verified Android App Links use standard HTTPS URLs (`https://example.com/product/42`) cryptographically verified against a domain Digital Asset Links JSON file, opening the application directly without an OS chooser dialog while synthesizing proper hierarchical backstacks.

## Practical walkthrough (English)

Implementing modern Type-Safe Jetpack Compose Navigation with verified Deep Link routing:
```kotlin
// 1. Declare type-safe routes using Kotlinx Serialization
@Serializable
data object HomeRoute

@Serializable
data class ProductDetailRoute(val productId: String)

// 2. Configure NavHost with type-safe destinations and deep links
@Composable
fun AppNavGraph(navController: NavHostController) {
    NavHost(navController = navController, startDestination = HomeRoute) {
        composable<HomeRoute> {
            HomeScreen(onProductClick = { id ->
                navController.navigate(ProductDetailRoute(productId = id))
            })
        }

        composable<ProductDetailRoute>(
            deepLinks = listOf(
                navDeepLink<ProductDetailRoute>(
                    basePath = "https://shop.example.com/products"
                )
            )
        ) { backStackEntry ->
            // Route parameters are extracted with 100% compile-time type safety
            val route: ProductDetailRoute = backStackEntry.toRoute()
            ProductDetailScreen(productId = route.productId)
        }
    }
}
```
Failure scenario:
If an application opening from a deep link does not synthesize a hierarchical backstack (e.g., using NavDeepLinkBuilder), pressing the system Back button closes the application immediately instead of navigating to the parent catalog screen, breaking standard platform navigation expectations.

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

Multi-Activity navigation relies on heavyweight OS windows; Fragment navigation uses modular sub-trees within one Activity but introduces dual-lifecycle complexity; Compose Navigation uses lightweight, type-safe declarative Composable destinations scoped to NavBackStackEntry; and Deep Links provide verified external HTTPS entry routes with synthesized backstacks.

## Interview answer — structured

Android navigation has evolved across four distinct paradigms, progressing from heavy system window boundaries toward lightweight, declarative destination graphs.

The traditional Multi-Activity approach encapsulates each screen in a distinct Activity. While offering rigid OS-level isolation, it introduces heavy IPC transitions and complex Intent data sharing. The Single-Activity with Fragment model improved rendering speed by swapping views inside one window, but introduced the infamous dual-lifecycle mismatch between Fragment instances and view hierarchies.

Jetpack Compose Navigation represents the modern standard. By mapping routes directly to Composable functions, it abolishes FragmentManager complexity. With modern Navigation Compose, routes are declared type-safely via Kotlinx Serialization, while each NavBackStackEntry provides an isolated scope for ViewModels and saved state.

In production, Deep Links and verified Android App Links serve as external gateways. Using Digital Asset Links for cryptographic domain ownership verification, App Links allow web URLs to bypass app-chooser dialogs, launching users directly into target screens while seamlessly synthesizing a natural hierarchical backstack.


## Interview answer — deep senior

At the operating system, WindowManager, and SurfaceFlinger level, the architectural divide between Multi-Activity and Single-Activity architectures is profound. In a Multi-Activity setup, every Activity maintains its own PhoneWindow, SurfaceControl hierarchy, and dedicated render thread pipelines. Transitioning between activities requires ActivityTaskManagerService to execute an inter-process transition, taking snapshots and swapping hardware display surfaces through the system compositor, which consumes substantial GPU and memory bandwidth.

Transitioning to a Single-Activity architecture collapses this overhead: the entire application shares a single Surface, Window, and view tree root. However, the Fragment-based implementation introduced massive framework baggage. FragmentManager manages its own internal backstack transaction engine, BackStackRecord lists, and view lifecycle transitions, where onDestroyView() destroys the layout while keeping the Fragment instance alive, causing widespread memory leaks when view bindings are not manually nulled.

Jetpack Compose Navigation eliminates this entire abstraction layer. A Composable destination is not a component; it is an emitting node within the Compose runtime node graph. Navigation Compose manages a stack of NavBackStackEntry objects. Each entry implements LifecycleOwner, ViewModelStoreOwner, and SavedStateRegistryOwner. This guarantees that when a Composable destination is popped from the navigation backstack, its scoped ViewModelStore is cleared, triggering onCleared() and freeing memory without FragmentManager gymnastics.

For external ingress, verified Android App Links rely on the system Package Manager verifying the domain's /.well-known/assetlinks.json file during installation. When verified with android:autoVerify="true", the OS routes the HTTPS intent directly to the app without prompting the user. Production navigation architectures intercept these intents via NavDeepLinkBuilder, synthesizing the entire synthetic parent backstack so that pressing Back navigates the user logically upward toward the root screen rather than exiting the application.

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
