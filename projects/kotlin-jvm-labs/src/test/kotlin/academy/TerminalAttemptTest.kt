package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class TerminalAttemptTest {
    @Test fun positiveAmountStartsOneIdentifiedAttempt() {
        assertEquals(
            TerminalState.AwaitingTap("a-1", 1250),
            reduceTerminal(TerminalState.Idle, TerminalEvent.Start("a-1", 1250)),
        )
        assertThrows(IllegalArgumentException::class.java) {
            reduceTerminal(TerminalState.Idle, TerminalEvent.Start("a-1", 0))
        }
    }

    @Test fun matchingCardReadMovesToAuthorizationWithoutStoringCardData() {
        val state = reduceTerminal(TerminalState.AwaitingTap("a-1", 1250), TerminalEvent.CardRead("a-1", "opaque-token"))
        assertEquals(TerminalState.Authorizing("a-1", 1250), state)
    }

    @Test fun mismatchedOrBlankCardEventsDoNotAdvanceAttempt() {
        val waiting = TerminalState.AwaitingTap("a-2", 900)
        assertEquals(waiting, reduceTerminal(waiting, TerminalEvent.CardRead("old", "opaque-token")))
        assertEquals(waiting, reduceTerminal(waiting, TerminalEvent.CardRead("a-2", " ")))
    }

    @Test fun matchingAuthorizationProducesOneTerminalOutcome() {
        val authorizing = TerminalState.Authorizing("a-3", 500)
        val approved = reduceTerminal(authorizing, TerminalEvent.Approved("a-3", "receipt-7"))
        assertEquals(TerminalState.Approved("a-3", 500, "receipt-7"), approved)
        assertEquals(approved, reduceTerminal(approved, TerminalEvent.Declined("a-3", "late")))
    }

    @Test fun declineKeepsReasonWithoutClaimingApproval() {
        assertEquals(
            TerminalState.Declined("a-4", 750, "issuer_declined"),
            reduceTerminal(TerminalState.Authorizing("a-4", 750), TerminalEvent.Declined("a-4", "issuer_declined")),
        )
    }

    @Test fun lostTransportCreatesUnknownOutcomeInsteadOfAutomaticRetry() {
        assertEquals(
            TerminalState.Unknown("a-5", 1100, "transport_lost"),
            reduceTerminal(TerminalState.Authorizing("a-5", 1100), TerminalEvent.TransportLost("a-5")),
        )
    }

    @Test fun anotherStartCannotReplaceAnAttemptInProgress() {
        val active = TerminalState.Authorizing("a-6", 300)
        assertEquals(active, reduceTerminal(active, TerminalEvent.Start("a-7", 400)))
    }
}
