package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class ViewSessionTest {
    @Test
    fun noRendererBeforeAttach() {
        assertFalse(ViewSession().show("hello"))
    }

    @Test
    fun attachedRendererReceivesValue() {
        val seen = mutableListOf<String>()
        val session = ViewSession()
        session.attach { seen.add(it) }
        assertTrue(session.show("A"))
        assertEquals(listOf("A"), seen)
    }

    @Test
    fun detachedRendererDoesNotReceiveLaterValue() {
        val seen = mutableListOf<String>()
        val session = ViewSession()
        session.attach { seen.add(it) }
        session.detach()
        assertFalse(session.show("late"))
        assertEquals(emptyList<String>(), seen)
    }

    @Test
    fun aNewViewCanAttachAfterOldViewIsDetached() {
        val old = mutableListOf<String>()
        val current = mutableListOf<String>()
        val session = ViewSession()
        session.attach { old.add(it) }
        session.detach()
        session.attach { current.add(it) }
        assertTrue(session.show("new"))
        assertEquals(emptyList<String>(), old)
        assertEquals(listOf("new"), current)
    }
}
