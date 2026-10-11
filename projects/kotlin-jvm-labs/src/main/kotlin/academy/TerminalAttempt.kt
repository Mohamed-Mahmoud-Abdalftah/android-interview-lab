package academy

sealed interface TerminalState {
    data object Idle : TerminalState
    data class AwaitingTap(val attemptId: String, val amountMinor: Long) : TerminalState
    data class Authorizing(val attemptId: String, val amountMinor: Long) : TerminalState
    data class Approved(val attemptId: String, val amountMinor: Long, val receiptId: String) : TerminalState
    data class Declined(val attemptId: String, val amountMinor: Long, val reason: String) : TerminalState
    data class Unknown(val attemptId: String, val amountMinor: Long, val reason: String) : TerminalState
}

sealed interface TerminalEvent {
    data class Start(val attemptId: String, val amountMinor: Long) : TerminalEvent
    data class CardRead(val attemptId: String, val opaqueToken: String) : TerminalEvent
    data class Approved(val attemptId: String, val receiptId: String) : TerminalEvent
    data class Declined(val attemptId: String, val reason: String) : TerminalEvent
    data class TransportLost(val attemptId: String) : TerminalEvent
}

fun reduceTerminal(state: TerminalState, event: TerminalEvent): TerminalState = when (event) {
    is TerminalEvent.Start -> when (state) {
        is TerminalState.AwaitingTap, is TerminalState.Authorizing -> state
        else -> {
            require(event.attemptId.isNotBlank())
            require(event.amountMinor > 0)
            TerminalState.AwaitingTap(event.attemptId, event.amountMinor)
        }
    }
    is TerminalEvent.CardRead -> when (state) {
        is TerminalState.AwaitingTap -> if (event.attemptId == state.attemptId && event.opaqueToken.isNotBlank()) {
            TerminalState.Authorizing(state.attemptId, state.amountMinor)
        } else state
        else -> state
    }
    is TerminalEvent.Approved -> when (state) {
        is TerminalState.Authorizing -> if (event.attemptId == state.attemptId && event.receiptId.isNotBlank()) {
            TerminalState.Approved(state.attemptId, state.amountMinor, event.receiptId)
        } else state
        else -> state
    }
    is TerminalEvent.Declined -> when (state) {
        is TerminalState.Authorizing -> if (event.attemptId == state.attemptId && event.reason.isNotBlank()) {
            TerminalState.Declined(state.attemptId, state.amountMinor, event.reason)
        } else state
        else -> state
    }
    is TerminalEvent.TransportLost -> when (state) {
        is TerminalState.Authorizing -> if (event.attemptId == state.attemptId) {
            TerminalState.Unknown(state.attemptId, state.amountMinor, "transport_lost")
        } else state
        else -> state
    }
}
