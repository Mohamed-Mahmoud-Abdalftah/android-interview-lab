---
id: "SOL-15"
question: "How would you split a large interface with mostly unused methods?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 186
editorial_status: "reviewed"
---

# SOL-15

## Original interview question

How would you split a large interface with mostly unused methods?

## What the interviewer evaluates

Split a fat interface by consumer capabilities while preserving migration compatibility and behavior.

## Explanation in Arabic

ابدأ بـcall-site matrix: كل client بيستخدم methods إيه؟ جمع methods اللي لها نفس consumer contract في `SessionReader`, `ProfileEditor`, `ExportRunner` بدل giant `AccountService`. ممكن implementation واحدة تنفّذ interfaces كلها، لكن clients تعتمد على أصغر capability. اعمل adapters مؤقتة للمهاجرة، غيّر callers تدريجيًا، واختبر contract لكل capability. ما تقسمش حسب method واحدة لكل interface تلقائيًا؛ المجموعة المتماسكة أفضل. راجع scopes/security: UI لا تحتاج token-refresh method لو هي بس تعرض اسم المستخدم.

## Why it matters and how it works

ISP reduces client coupling to unrelated methods. A capability map guides the split; one implementation can satisfy several views. Migration should preserve behavior while narrowing public dependencies.

## Worked example

Conceptual Kotlin:
```kotlin
interface SessionReader { fun observeUserId(): kotlinx.coroutines.flow.Flow<String?> }
interface SignOut { suspend fun signOut() }
class AccountMenu(private val signOut: SignOut)
```
The menu cannot accidentally call token-refresh internals just because they share an implementation.

## Practical walkthrough

لو interface اسمها `AccountOperations` فيها 20 method، ابدأ بجدول callers: `AccountMenu` تستعمل signOut، profile header تستعمل observeUserId، وخدمة sync تستعمل refreshToken. استخرج roles حسب الاستعمال الحقيقي: `SignOut` و`SessionReader` مثلاً. implementation واحدة ممكن تدعمهم كلهم. انقل caller واحد في كل مرة، وشغّل tests بدل big-bang refactor. ما تخليش كل method interface مستقلة؛ العمليات اللي بتتغير مع بعض وبتستخدم مع بعض ممكن تفضل مجموعة. الفشل المعتاد إن fake في test يضطر ينفذ 19 method فارغين.

## Trade-offs and decision criteria

Many tiny interfaces cost wiring and navigation. Choose cohesive capability groups. For a private one-consumer class, a concrete API may be simpler; ISP becomes important when consumers use disjoint subsets or modules rebuild together.

## Failure modes

A fake for a read-only widget stubs `deleteAccount()` and `chargeCard()` with unimplemented throwing stubs because the interface is wide; production code may accidentally call those methods. Split surface and test only promised behavior.

## Production perspective

A large app gradually migrates account features to session-read, profile-edit and sign-out contracts. Security review verifies that payment and token operations are not exposed through a general UI dependency.

## Interview answer — short

I map consumers to the methods they use, then split a large interface into cohesive capabilities. One implementation may implement several; callers depend only on their needed view. I migrate gradually and test behavior.

## Interview answer — structured

A large interface with many unused methods forces every client and fake to know too much. I list call sites and group operations by meaningful capabilities, such as reading session state versus signing out. Then I introduce narrow contracts, let the current implementation implement them, and migrate one client at a time. I do not make one interface per method unless that truly matches a consumer boundary. Contract tests and build checks verify that behavior and dependencies improve. During migration, I can let the old implementation implement the new interfaces and change callers one feature at a time. That avoids a synchronized rewrite of every module.

## Interview answer — deep senior

I would first measure the problem: which modules recompile for unrelated changes, which fakes have empty or throwing methods, and which clients import sensitive capabilities they never need. A call-site matrix usually reveals clusters. I define small but cohesive interfaces for those clusters and keep one underlying implementation if its state ownership remains coherent. During migration I can use an adapter so existing callers remain functional, then remove the fat contract when no longer used. I test each capability’s behavior and lifecycle, especially session logout or token refresh races. Over-segregation creates its own navigation and binding cost, so I stop where client coupling is meaningfully reduced. ISP is about what a client must see, not a fixed method count. I would start with a client-method matrix and change history, not arbitrary splitting. If account menu uses only sign-out and a header only observes user ID, expose those as role contracts; one class may implement both. Migrate callers gradually so the public API change is reviewable. A warning sign is a test fake with many unused methods or production implementations throwing for operations they cannot support. The trade-off is more small types, so I group operations that belong to a stable client workflow rather than one interface per method. After migration, I would remove the broad contract and verify that client modules no longer import unrelated token or account-management APIs.

## How to answer in the interview

- **Why:** Show client-method matrix.
- **How:** extract role interfaces.
- **Trade-offs:** note type count.
- **Failure cases:** cite empty fake methods.
- **Production solutions:** finish with staged migration and dependency checks..

## Deep-dive talking points

Construct a consumer-method matrix, capability split, migration adapter and contract tests.

## Follow-up questions

- [SOL-05](../sol-05/): What does ISP require? **Answer:** clients do not depend on unused capabilities.
- [SOL-08](../sol-08/): Does splitting an interface also split implementation? **Answer:** not necessarily; one implementation can expose multiple narrow views.

## Self-check rubric

Group six methods into two or three client capabilities and explain migration without empty stubs.

## References and reviewed-on date

- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — interface segregation.
- [Android modularization guide](https://developer.android.com/topic/modularization) — client module boundaries.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
