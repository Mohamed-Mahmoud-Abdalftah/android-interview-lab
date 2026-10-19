package academy

import interviewlab.sys_10.UploadEvent
import interviewlab.sys_10.UploadState
import interviewlab.sys_10.reduce
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class StateMachineSnippetTest {
    @Test
    fun staleResultCannotOverwriteNewRequest() {
        val newState = reduce(UploadState.Sending("new"), UploadEvent.Succeeded("old", "r-1"))
        assertEquals(UploadState.Sending("new"), newState)
    }

    @Test
    fun matchingResultCompletesAndDuplicateStartDoesNotReopen() {
        val completed = reduce(UploadState.Sending("new"), UploadEvent.Succeeded("new", "r-2"))
        assertEquals(UploadState.Complete("r-2"), completed)
        assertEquals(completed, reduce(completed, UploadEvent.Start("again")))
    }
}
