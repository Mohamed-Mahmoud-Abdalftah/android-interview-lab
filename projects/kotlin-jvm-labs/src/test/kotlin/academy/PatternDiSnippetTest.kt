package academy

import interviewlab.pat_07.OrderTotal
import interviewlab.pat_07.PromotionPolicy
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class PatternDiSnippetTest {
    @Test
    fun injectedPolicyChangesCalculationWithoutChangingConsumer() {
        val tenPercent = object : PromotionPolicy {
            override fun discountCents(subtotal: Int) = subtotal / 10
        }
        assertEquals(900, OrderTotal(tenPercent).dueCents(1000))
    }

    @Test
    fun invalidPolicyAndInputAreRejected() {
        val tooMuch = object : PromotionPolicy {
            override fun discountCents(subtotal: Int) = subtotal + 1
        }
        assertThrows(IllegalArgumentException::class.java) { OrderTotal(tooMuch).dueCents(100) }
        assertThrows(IllegalArgumentException::class.java) { OrderTotal(tooMuch).dueCents(-1) }
    }
}
