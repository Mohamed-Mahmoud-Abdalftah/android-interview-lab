plugins {
    kotlin("jvm") version "2.4.20"
    application
}

kotlin { jvmToolchain(17) }
application { mainClass.set("academy.MainKt") }

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.11.0")
    testImplementation(kotlin("reflect"))
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.11.0")
    testImplementation("app.cash.turbine:turbine:1.2.1")
    testImplementation(platform("org.junit:junit-bom:5.14.4"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
    testLogging { events("passed", "skipped", "failed") }
}

// Compile exact JVM Kotlin fences from reviewed Interview Lab records in isolated packages.
val labSnippetOutput = layout.buildDirectory.dir("generated/interview-lab-snippets")
val labSnippetIds = listOf("COR-01", "COR-02", "FLO-06", "PAY-02", "TST-09", "TST-19", "TST-20") +
    (1..28).map { "KOT-%02d".format(it) } + listOf("KOT-30")
val labSnippetBank = projectDir.resolve("../../Interview-Lab/questions")
val generateLabSnippets by tasks.registering {
    inputs.files(labSnippetIds.map { labSnippetBank.resolve("$it.md") })
    outputs.dir(labSnippetOutput)
    doLast {
        val output = labSnippetOutput.get().asFile
        output.mkdirs()
        for (id in labSnippetIds) {
            val markdown = labSnippetBank.resolve("$id.md").readText()
            val snippet = Regex("```kotlin\\n([\\s\\S]*?)```").find(markdown)?.groupValues?.get(1)
                ?: error("Missing Kotlin example in $id")
            output.resolve("${id.replace('-', '_')}.kt").writeText(
                "package interviewlab.${id.replace('-', '_').lowercase()}\n\n$snippet"
            )
        }
    }
}
sourceSets.test { kotlin.srcDir(labSnippetOutput) }
tasks.named("compileTestKotlin") { dependsOn(generateLabSnippets) }
