package academy

import interviewlab.kot_02.CartStateHolder
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals

class ValVarSnapshotTest {
    @Test
    fun `new cart state does not mutate an earlier list snapshot`() {
        val cart = CartStateHolder()
        cart.add("phone")
        val first = cart.items

        cart.add("case")

        assertEquals(listOf("phone"), first)
        assertEquals(listOf("phone", "case"), cart.items)
    }
}
