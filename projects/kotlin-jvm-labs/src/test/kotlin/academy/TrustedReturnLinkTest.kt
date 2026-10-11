package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class TrustedReturnLinkTest {
    @Test fun acceptsExactHttpsOriginPathAndAllowedFields() {
        assertEquals(
            PaymentReturn("order_42", ReturnStatus.SUCCESS),
            parseTrustedPaymentReturn("https://pay.example.com/payment/return?orderId=order_42&status=success"),
        )
    }

    @Test fun queryOrderDoesNotChangeMeaning() {
        assertEquals(
            PaymentReturn("A-9", ReturnStatus.CANCELLED),
            parseTrustedPaymentReturn("https://pay.example.com/payment/return?status=cancelled&orderId=A-9"),
        )
    }

    @Test fun rejectsLookalikeHostsAndUntrustedSchemes() {
        assertNull(parseTrustedPaymentReturn("https://pay.example.com.attacker.test/payment/return?orderId=A&status=success"))
        assertNull(parseTrustedPaymentReturn("http://pay.example.com/payment/return?orderId=A&status=success"))
    }

    @Test fun rejectsAuthorityTricksPortsFragmentsAndWrongPaths() {
        assertNull(parseTrustedPaymentReturn("https://pay.example.com@attacker.test/payment/return?orderId=A&status=success"))
        assertNull(parseTrustedPaymentReturn("https://pay.example.com:444/payment/return?orderId=A&status=success"))
        assertNull(parseTrustedPaymentReturn("https://pay.example.com/payment/return/extra?orderId=A&status=success"))
        assertNull(parseTrustedPaymentReturn("https://pay.example.com/payment/return?orderId=A&status=success#ignored"))
    }

    @Test fun rejectsDuplicateUnknownOrMalformedQueryFields() {
        assertNull(parseTrustedPaymentReturn("https://pay.example.com/payment/return?orderId=A&orderId=B&status=success"))
        assertNull(parseTrustedPaymentReturn("https://pay.example.com/payment/return?orderId=A&status=success&admin=true"))
        assertNull(parseTrustedPaymentReturn("https://pay.example.com/payment/return?orderId=A%2FB&status=success"))
    }

    @Test fun rejectsMissingInvalidAndOversizedValues() {
        assertNull(parseTrustedPaymentReturn("https://pay.example.com/payment/return?orderId=A"))
        assertNull(parseTrustedPaymentReturn("https://pay.example.com/payment/return?orderId=A&status=approved"))
        assertNull(parseTrustedPaymentReturn("https://pay.example.com/payment/return?orderId=${"x".repeat(65)}&status=success"))
    }
}
