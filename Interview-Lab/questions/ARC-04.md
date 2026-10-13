---
id: "ARC-04"
question: "What is the Repository pattern? What is a UseCase?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 149
editorial_status: "reviewed"
---

# ARC-04

## Original interview question

What is the Repository pattern? What is a UseCase?

## What the interviewer evaluates

Define repository as data abstraction/source coordination and use case as business action, without mandatory pass-through classes.

## Explanation in Arabic

Repository interface أو class بتقدّم app data وتخفي هل جت من Room أو network أو cache، وكمان تحدد refresh/conflict/source-of-truth policy. UseCase بيمثل فعل business محدد زي `PlaceOrder` أو `ObserveEligibleOffers`، وممكن يجمع أكتر من repository أو يطبق rule. مش كل repository method محتاجة UseCase wrapper؛ لو الـViewModel بس بيقرأ products من repo بسيط، wrapper فارغ يزوّد ملفات من غير فائدة. Repository ما يسرّبش DTOs للـUI، وUseCase ما يتحوّلش لمكان لكل logic بلا ownership.

## Practical walkthrough

Repository يمثل data contract مثل `observeOrders()` مع سياسة cache/server، وUseCase يمثل action أو policy مثل `SubmitOrder` أو `GetEligibleOffers`. مش كل DAO يحتاج repository wrapper فارغ، ومش كل getter يحتاج UseCase. لو payment retry له قواعد، ضعه في use case/domain، بينما request mapping والstatus endpoint في repository. اجعل الاختبار يثبت القرار والأثر.

## Why it matters and how it works

Data repositories are entry points to data and may coordinate multiple sources. Use cases are optional units of domain behavior in Android guidance, useful for reuse and complex logic. Boundaries should expose domain results and clearly state freshness, errors, and cancellation.

## Worked example

Conceptual design: `OrdersRepository.observeOrder(id): Flow<Order>` reads Room as source of truth while refresh writes server updates. `PlaceOrderUseCase(repo, limits)` validates amount, sends a request key, and returns `Accepted`, `Rejected`, or `PendingVerification`. The ViewModel maps those outcomes into screen state.

A small JVM contract shows the split: the use case owns input policy; the repository owns persistence/transport behind its interface. This does not prove the actual HTTP or Room adapter, which needs integration tests.

```kotlin
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

data class OrderDraft(val sku: String, val quantity: Int)
data class Receipt(val id: String)
interface OrderRepository { fun submit(draft: OrderDraft): Receipt }

class SubmitOrder(private val repository: OrderRepository) {
    fun invoke(draft: OrderDraft): Receipt {
        require(draft.sku.isNotBlank() && draft.quantity > 0)
        return repository.submit(draft)
    }
}

class SubmitOrderExampleTest {
    @Test fun validatesBeforeRepositoryCall() {
        var calls = 0
        val repository = object : OrderRepository {
            override fun submit(draft: OrderDraft): Receipt {
                calls++
                return Receipt("order-1")
            }
        }
        val submit = SubmitOrder(repository)
        assertThrows(IllegalArgumentException::class.java) {
            submit.invoke(OrderDraft("sku", 0))
        }
        assertEquals(0, calls)
        assertEquals(Receipt("order-1"), submit.invoke(OrderDraft("sku", 1)))
        assertEquals(1, calls)
    }
}
```

## Trade-offs and decision criteria

A repository can contain data-centric business rules such as merge policy. A use case adds value when it coordinates or centralizes application behavior. Avoid many one-line use cases in a small app; conversely avoid a huge repository that owns unrelated workflows.

## Failure modes

A repository exposing `Call<OrderDto>` forces UI to know Retrofit, dispatching, and server schema. Another failure is treating a use case as a durable job owner; process-death recovery requires persisted state and scheduling, not just a class name.

## Production perspective

An offline-first feed repository exposes database-backed Flow and refreshes from network. A “bookmark article” use case is worthwhile if the same rule spans feed, details, and notifications. Tests separate data merge behavior from policy.

## Interview answer — short

A Repository abstracts and coordinates data sources, including source-of-truth rules. A UseCase represents a business action or reusable rule above that data. The domain layer is optional; I add use cases when they clarify real behavior.

## Interview answer — structured

I use a repository to define how the app obtains and updates data, not simply as a DAO wrapper. It can combine Room, network, and cache and expose a stable model. A use case expresses something the product does, such as placing an order or computing eligibility, often by calling one or more repositories. Android guidance treats use cases as optional. If one merely forwards a single repository call, I may skip it until complexity or reuse appears. A practical signal that a use case earns its place is a rule used by checkout, profile, and notifications or an operation coordinating several repositories. If it is only `operator fun invoke() = repository.get()`, I ask what boundary or behavior it actually adds.

## Interview answer — deep senior

The separation becomes valuable when data consistency and business policy evolve independently. A repository decides whether local storage is the source of truth, how remote refresh is applied, and what failures are surfaced. A use case can validate rules, coordinate repositories, and return a domain outcome that is not tied to transport details. I keep cancellation and error semantics explicit and do not pretend a use case alone survives process death. For a tiny app I may call a repository from a ViewModel; for a multi-feature payment workflow I likely want a use case with focused tests. I review the direction of dependencies and model types, because a beautifully named repository that returns Retrofit DTOs still leaks its boundary. For an offline-first feed, repository consistency is substantial work: choose local truth, refresh, map, and preserve cached data on failure. A use case above it might calculate what the user may do with those articles, but should not reimplement refresh logic. I test the repository against races and stale data, and the use case against policy inputs. If the operation must survive process death, persisted work and scheduling sit outside a screen coroutine.

## How to answer in the interview

- **Why:** data access and business decision differ.
- **How:** define repository contract and use case policy.
- **Trade-off:** extra layers versus meaningful separation.
- **Failure case:** pass-through classes hide responsibility.
- **Production solution:** test policy and real adapter separately.

## Deep-dive talking points

Compare repository data ownership with use-case action semantics; explain offline source of truth, multi-repository coordination, cancellation and process-death limits.

## Follow-up questions

- [ARC-10](../arc-10/): Who decides source of truth? **Answer:** the data layer/repository contract and implementation.
- [ARC-13](../arc-13/): When is a use case optional? **Answer:** when no meaningful reuse or complex policy warrants it.

## Self-check rubric

Describe a repository that actually coordinates sources, one use case that adds business value, and one pass-through use case you would omit.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository responsibilities.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — use cases and optionality.

Technically reviewed against the linked official Android architecture guidance on 2026-10-11. Conceptual flows and snippets are not device-tested.
