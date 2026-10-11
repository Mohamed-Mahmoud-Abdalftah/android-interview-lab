package academy

data class EditorUiState(
    val draftTitle: String = "",
    val isSaving: Boolean = false,
    val message: String? = null,
    val requestId: Int = 0,
)

sealed interface EditorEvent {
    data class TitleChanged(val value: String) : EditorEvent
    data object SaveTapped : EditorEvent
    data class SaveSucceeded(val requestId: Int) : EditorEvent
    data class SaveFailed(val requestId: Int) : EditorEvent
    data object MessageDismissed : EditorEvent
}

/** Pure presentation transition; persistence and asynchronous ownership live elsewhere. */
fun reduceEditor(state: EditorUiState, event: EditorEvent): EditorUiState = when (event) {
    is EditorEvent.TitleChanged -> state.copy(draftTitle = event.value, isSaving = false, message = null)
    EditorEvent.SaveTapped -> when {
        state.isSaving -> state
        state.draftTitle.isBlank() -> state.copy(message = "Title required")
        else -> state.copy(isSaving = true, message = null, requestId = state.requestId + 1)
    }
    is EditorEvent.SaveSucceeded -> if (state.isSaving && event.requestId == state.requestId) state.copy(isSaving = false, message = "Saved") else state
    is EditorEvent.SaveFailed -> if (state.isSaving && event.requestId == state.requestId) state.copy(isSaving = false, message = "Save failed") else state
    EditorEvent.MessageDismissed -> state.copy(message = null)
}
