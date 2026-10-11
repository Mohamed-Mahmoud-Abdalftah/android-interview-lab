package academy

import java.net.URI

enum class ReturnStatus { SUCCESS, CANCELLED }

data class PaymentReturn(val orderId: String, val status: ReturnStatus)

/**
 * Parses one deliberately narrow web-return contract. Android intent and
 * domain verification still need platform and end-to-end tests.
 */
fun parseTrustedPaymentReturn(raw: String): PaymentReturn? {
    val uri = runCatching { URI(raw) }.getOrNull() ?: return null
    if (!uri.scheme.equals("https", ignoreCase = true)) return null
    if (!uri.host.equals("pay.example.com", ignoreCase = true)) return null
    if (uri.userInfo != null || uri.port != -1 || uri.fragment != null) return null
    if (uri.path != "/payment/return") return null

    val pieces = uri.rawQuery?.split('&') ?: return null
    if (pieces.size != 2) return null
    val fields = mutableMapOf<String, String>()
    for (piece in pieces) {
        val pair = piece.split('=', limit = 2)
        if (pair.size != 2 || pair[0] !in setOf("orderId", "status")) return null
        if (fields.put(pair[0], pair[1]) != null) return null
    }

    val orderId = fields["orderId"]?.takeIf { it.matches(Regex("[A-Za-z0-9_-]{1,64}")) } ?: return null
    val status = when (fields["status"]) {
        "success" -> ReturnStatus.SUCCESS
        "cancelled" -> ReturnStatus.CANCELLED
        else -> return null
    }
    return PaymentReturn(orderId, status)
}
