plugins {
    kotlin("jvm") version "2.4.20"
    application
}

kotlin { jvmToolchain(17) }
application { mainClass.set("academy.MainKt") }

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.11.0")
    testImplementation(kotlin("reflect"))
    testImplementation(kotlin("test"))
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
val labSnippetIds = listOf("COR-01", "COR-02", "COR-09", "FLO-06", "PAY-02", "TST-04", "TST-05", "TST-09", "TST-10", "TST-19", "TST-20", "DSA-01", "DSA-07", "DSA-08", "DSA-11", "DSA-15", "ARC-01", "ARC-04", "ARC-25") +
    (1..28).map { "KOT-%02d".format(it) } + listOf("KOT-30") +
    listOf("DI-01", "PAT-07", "SOL-07", "MOD-09", "MOD-11", "SYS-10", "FLO-01", "FLO-02", "FLO-03", "FLO-05", "FLO-07", "FLO-10", "FLO-11", "FLO-12", "FLO-13", "FLO-14", "FLO-15", "FLO-16", "FLO-17", "FLO-18", "FLO-19", "FLO-20", "FLO-21", "FLO-24", "FLO-27", "FLO-29", "FLO-30", "FLO-32")
val labSnippetBank = projectDir.resolve("../../Interview-Lab/questions")
val generateLabSnippets by tasks.registering {
    inputs.files(labSnippetIds.map { labSnippetBank.resolve("$it.md") })
    outputs.dir(labSnippetOutput)
    doLast {
        val output = labSnippetOutput.get().asFile
        output.mkdirs()
        for (id in labSnippetIds) {
            val markdown = labSnippetBank.resolve("$id.md").readText()
            val snippet = Regex("## Worked example[\\s\\S]*?```kotlin\\n([\\s\\S]*?)```").find(markdown)?.groupValues?.get(1)
                ?: Regex("```kotlin\\n([\\s\\S]*?)```").find(markdown)?.groupValues?.get(1)
                ?: error("Missing Kotlin example in $id")
            output.resolve("${id.replace('-', '_')}.kt").writeText(
                "package interviewlab.${id.replace('-', '_').lowercase()}\n\n$snippet"
            )
        }
    }
}
sourceSets.test { kotlin.srcDir(labSnippetOutput) }
tasks.named("compileTestKotlin") { dependsOn(generateLabSnippets) }
