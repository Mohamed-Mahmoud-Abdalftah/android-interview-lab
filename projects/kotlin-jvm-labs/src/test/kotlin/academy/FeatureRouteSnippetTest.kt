package academy

import interviewlab.mod_09.CatalogActions
import interviewlab.mod_09.CheckoutRoute
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class FeatureRouteSnippetTest {
    @Test
    fun catalogEmitsIdOnlyRoute() {
        val routes = mutableListOf<CheckoutRoute>()
        CatalogActions(routes::add).onBuy("p-42")
        assertEquals(listOf(CheckoutRoute("p-42")), routes)
    }

    @Test
    fun blankIdDoesNotNavigate() {
        val routes = mutableListOf<CheckoutRoute>()
        assertThrows(IllegalArgumentException::class.java) { CatalogActions(routes::add).onBuy(" ") }
        assertEquals(emptyList<CheckoutRoute>(), routes)
    }
}
