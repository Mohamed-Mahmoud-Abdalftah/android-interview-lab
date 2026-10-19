package academy

import interviewlab.mod_11.CheckoutAccess
import interviewlab.mod_11.FixedSession
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class MultiModuleDiSnippetTest {
    @Test
    fun consumerUsesInjectedSessionContract() {
        assertTrue(CheckoutAccess(FixedSession("u-1")).canCheckout())
        assertFalse(CheckoutAccess(FixedSession(null)).canCheckout())
    }
}
