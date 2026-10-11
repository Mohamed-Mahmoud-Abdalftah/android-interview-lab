package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class EditorReducerTest {
    @Test fun blankTitleProducesVisibleValidationState() {
        val state = reduceEditor(EditorUiState(draftTitle = "  "), EditorEvent.SaveTapped)
        assertFalse(state.isSaving)
        assertEquals("Title required", state.message)
    }

    @Test fun validTitleMovesToPendingWithoutClaimingPersistence() {
        val state = reduceEditor(EditorUiState(draftTitle = "  Prep  "), EditorEvent.SaveTapped)
        assertTrue(state.isSaving)
        assertEquals(null, state.message)
        assertEquals("  Prep  ", state.draftTitle)
    }

    @Test fun completionBecomesStateAndCanBeAcknowledged() {
        val pending = EditorUiState("Prep", isSaving = true, requestId = 1)
        val complete = reduceEditor(pending, EditorEvent.SaveSucceeded(1))
        assertFalse(complete.isSaving)
        assertEquals("Saved", complete.message)
        assertEquals(null, reduceEditor(complete, EditorEvent.MessageDismissed).message)
    }

    @Test fun repeatedTapWhilePendingDoesNotCreateAnotherTransition() {
        val pending = EditorUiState("Prep", isSaving = true)
        assertEquals(pending, reduceEditor(pending, EditorEvent.SaveTapped))
    }

    @Test fun titleEditClearsOldMessageAndFailureIsVisible() {
        val changed = reduceEditor(EditorUiState("old", message = "Saved"), EditorEvent.TitleChanged("new"))
        assertEquals(null, changed.message)
        val failed = reduceEditor(changed.copy(isSaving = true, requestId = 2), EditorEvent.SaveFailed(2))
        assertFalse(failed.isSaving)
        assertEquals("Save failed", failed.message)
    }

    @Test fun oldCompletionCannotReportSuccessForNewerDraft() {
        val first = reduceEditor(EditorUiState("first"), EditorEvent.SaveTapped)
        val edited = reduceEditor(first, EditorEvent.TitleChanged("second"))
        val second = reduceEditor(edited, EditorEvent.SaveTapped)
        val stale = reduceEditor(second, EditorEvent.SaveSucceeded(first.requestId))
        assertEquals(second, stale)
        assertTrue(reduceEditor(stale, EditorEvent.SaveSucceeded(second.requestId)).message == "Saved")
    }
}
