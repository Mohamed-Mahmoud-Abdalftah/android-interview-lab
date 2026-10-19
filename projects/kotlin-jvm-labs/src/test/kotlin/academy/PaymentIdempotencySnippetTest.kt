package academy

import interviewlab.pay_02.PaymentGateway
import interviewlab.pay_02.PaymentIntent
import interviewlab.pay_02.SubmitResult
import interviewlab.pay_02.resolvePayment
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals

class PaymentIdempotencySnippetTest {
    @Test
    fun `unknown submission looks up the same operation`() = runTest {
        val intent = PaymentIntent("payment-17", 50000)
        val submitted = mutableListOf<PaymentIntent>()
        val lookedUp = mutableListOf<String>()
        val gateway = object : PaymentGateway {
            override suspend fun submit(intent: PaymentIntent): SubmitResult {
                submitted += intent
                return SubmitResult.Unknown
            }

            override suspend fun lookup(operationId: String): SubmitResult {
                lookedUp += operationId
                return SubmitResult.Final(approved = true)
            }
        }

        assertEquals(SubmitResult.Final(approved = true), resolvePayment(intent, gateway))
        assertEquals(listOf(intent), submitted)
        assertEquals(listOf(intent.operationId), lookedUp)
    }

    @Test
    fun `known submission does not perform a redundant lookup`() = runTest {
        var lookups = 0
        val gateway = object : PaymentGateway {
            override suspend fun submit(intent: PaymentIntent) = SubmitResult.Final(approved = false)
            override suspend fun lookup(operationId: String): SubmitResult {
                lookups++
                return SubmitResult.Unknown
            }
        }

        assertEquals(SubmitResult.Final(approved = false), resolvePayment(PaymentIntent("payment-18", 20000), gateway))
        assertEquals(0, lookups)
    }
}
