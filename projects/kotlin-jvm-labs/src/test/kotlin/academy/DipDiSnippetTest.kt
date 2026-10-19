package academy

import interviewlab.sol_07.CheckoutFeePolicy
import interviewlab.sol_07.FeeQuote
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class DipDiSnippetTest {
    @Test
    fun policyAcceptsDeterministicFeeQuote() {
        val quote = object : FeeQuote {
            override fun feeCents(orderCents: Int) = orderCents / 20
        }
        assertEquals(105, CheckoutFeePolicy(quote).totalCents(100))
    }

    @Test
    fun policyRejectsInvalidInputAndOverflow() {
        val negative = object : FeeQuote {
            override fun feeCents(orderCents: Int) = -1
        }
        assertThrows(IllegalArgumentException::class.java) { CheckoutFeePolicy(negative).totalCents(100) }
        assertThrows(IllegalArgumentException::class.java) { CheckoutFeePolicy(negative).totalCents(-1) }
        val one = object : FeeQuote {
            override fun feeCents(orderCents: Int) = 1
        }
        assertThrows(ArithmeticException::class.java) { CheckoutFeePolicy(one).totalCents(Int.MAX_VALUE) }
    }
}
