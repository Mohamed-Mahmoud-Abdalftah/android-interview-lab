package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class NoteRowTest {
    @Test fun sameIdMeansSameLogicalRowDespiteContentChange() {
        assertTrue(sameRow(NoteRow("n-1", "old"), NoteRow("n-1", "new")))
    }

    @Test fun differentIdsAreDifferentRowsEvenWithEqualContent() {
        assertFalse(sameRow(NoteRow("n-1", "same"), NoteRow("n-2", "same")))
    }

    @Test fun contentComparisonDetectsVisibleChange() {
        assertFalse(sameRowContent(NoteRow("n-1", "old"), NoteRow("n-1", "new")))
        assertTrue(sameRowContent(NoteRow("n-1", "same"), NoteRow("n-1", "same")))
    }

    @Test fun snapshotDoesNotTrackLaterMutationOfSourceList() {
        val source = mutableListOf(NoteRow("n-1", "first"))
        val snapshot = snapshotRows(source)
        source[0] = NoteRow("n-1", "changed")
        source += NoteRow("n-2", "second")
        assertEquals(listOf(NoteRow("n-1", "first")), snapshot)
    }
}
