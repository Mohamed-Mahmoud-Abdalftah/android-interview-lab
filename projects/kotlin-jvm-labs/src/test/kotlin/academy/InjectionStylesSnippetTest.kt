package academy

import interviewlab.di_02.ManualGraph
import interviewlab.di_02.OpenOrderCount
import interviewlab.di_02.OrdersRepository
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class InjectionStylesSnippetTest {
    @Test
    fun manualGraphAndDirectConstructorUseTheSameExplicitContract() {
        val fake = object : OrdersRepository {
            override fun countOpen() = 3
        }
        assertEquals(3, OpenOrderCount(fake).load())
        assertEquals(3, ManualGraph(fake).openOrderCount().load())
    }
}
