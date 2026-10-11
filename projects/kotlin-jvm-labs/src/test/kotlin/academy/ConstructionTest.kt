package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class ConstructionTest {
    @Test
    fun primaryConstructorInterleavesPropertiesAndInit() {
        val events = mutableListOf<String>()
        val record = ConstructionTimeline(" Ada ", events)

        assertEquals("ADA", record.label)
        assertEquals(listOf("property:Ada", "init", "label:ADA"), events)
    }

    @Test
    fun secondaryBodyRunsAfterPrimaryInitialization() {
        val events = mutableListOf<String>()
        val record = ConstructionTimeline(" Ada ", events, "member")

        assertEquals("ADA", record.label)
        assertEquals(listOf("property:Ada", "init", "label:ADA", "secondary:member"), events)
    }

    @Test
    fun validationStopsLaterInitializersAndSecondaryBody() {
        val events = mutableListOf<String>()

        assertThrows<IllegalArgumentException> {
            ConstructionTimeline("   ", events, "member")
        }
        assertEquals(listOf("property:", "init"), events)
    }

    @Test
    fun endpointFactoryRejectsAbsentAndBlankHosts() {
        assertNull(EndpointConfig.parse(null, 443))
        assertNull(EndpointConfig.parse("  ", 443))
    }

    @Test
    fun endpointFactoryRejectsInvalidPorts() {
        assertNull(EndpointConfig.parse("example.test", 0))
        assertNull(EndpointConfig.parse("example.test", 65536))
    }

    @Test
    fun endpointFactoryNormalizesBeforeConstruction() {
        val config = EndpointConfig.parse(" example.test ", 443)

        assertNotNull(config)
        assertEquals("example.test", config?.host)
        assertEquals("example.test:443", config?.authority())
    }
}
