package academy

import interviewlab.sol_14.CheckEligibility
import interviewlab.sol_14.Eligibility
import interviewlab.sol_14.EligibilitySource
import interviewlab.sol_14.NetworkEligibilitySource
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class HiltDipBoundarySnippetTest {
    @Test
    fun policyCanUseFakeWithoutTransportTypes() = runBlocking {
        val fake = object : EligibilitySource {
            override suspend fun status(customerId: String) =
                Eligibility(customerId == "approved", null)
        }
        assertEquals(Eligibility(true, null), CheckEligibility(fake).forCustomer("approved"))
    }

    @Test
    fun adapterMapsTransportResultToDomainValue() = runBlocking {
        val adapter = NetworkEligibilitySource { id ->
            if (id == "blocked") false to "policy hold" else true to null
        }
        assertEquals(
            Eligibility(false, "policy hold"),
            CheckEligibility(adapter).forCustomer("blocked")
        )
    }
}
