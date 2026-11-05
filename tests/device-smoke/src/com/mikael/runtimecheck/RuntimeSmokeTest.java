package com.mikael.runtimecheck;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.jar.JarFile;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/** Device-side smoke test. This diagnoses the JVM used to launch this JAR. */
public final class RuntimeSmokeTest {
    private static final StringBuilder REPORT = new StringBuilder();
    private static int passed;
    private static int failed;
    private static int info;

    private RuntimeSmokeTest() {}

    private static void log(String line) {
        REPORT.append(line).append('\n');
        System.out.println(line);
    }

    private static void check(String name, CheckedTest test) {
        try {
            test.run();
            passed++;
            log("[PASS] " + name);
        } catch (Throwable error) {
            failed++;
            log("[FAIL] " + name + " -> " + error);
            for (StackTraceElement frame : error.getStackTrace()) {
                log("    at " + frame);
            }
        }
    }

    private interface CheckedTest {
        void run() throws Exception;
    }

    private static void property(String name) {
        log(name + "=" + System.getProperty(name, "<not reported>"));
    }

    private static void optionalClass(final String className, final String label) {
        try {
            Class.forName(className, false, Thread.currentThread().getContextClassLoader());
            info++;
            log("[INFO] " + label + " found: " + className);
        } catch (ClassNotFoundException absent) {
            info++;
            log("[INFO] " + label + " not on diagnostic classpath (not a failure): " + className);
        } catch (Throwable error) {
            failed++;
            log("[FAIL] " + label + " class lookup -> " + error);
        }
    }

    private static File saveReport() {
        String fileName = "MikaelRuntime8-device-report.txt";
        File primary = new File(System.getProperty("user.dir", "."), fileName);
        try {
            Files.write(primary.toPath(), REPORT.toString().getBytes(StandardCharsets.UTF_8));
            return primary;
        } catch (Throwable first) {
            File fallback = new File(System.getProperty("java.io.tmpdir", "."), fileName);
            try {
                Files.write(fallback.toPath(), REPORT.toString().getBytes(StandardCharsets.UTF_8));
                return fallback;
            } catch (Throwable second) {
                System.out.println("[WARN] Could not save report: " + first + " / " + second);
                return null;
            }
        }
    }

    public static void main(String[] args) {
        log("Mikael Runtime 8 - Android Java diagnostic");
        log("==========================================");
        property("java.version");
        property("java.specification.version");
        property("java.vm.name");
        property("java.vm.version");
        property("java.vendor");
        property("os.name");
        property("os.version");
        property("os.arch");
        property("sun.arch.data.model");
        property("file.encoding");
        property("java.home");
        property("java.io.tmpdir");
        property("user.dir");
        property("java.library.path");
        property("java.class.path");
        log("availableProcessors=" + Runtime.getRuntime().availableProcessors());
        log("maxMemoryBytes=" + Runtime.getRuntime().maxMemory());
        log("totalMemoryBytes=" + Runtime.getRuntime().totalMemory());
        log("");

        check("Java 8 runtime", new CheckedTest() {
            public void run() {
                String version = System.getProperty("java.specification.version");
                if (!"1.8".equals(version) && !"8".equals(version)) {
                    throw new AssertionError("Expected Java 8, got " + version);
                }
            }
        });
        check("ARM64 architecture", new CheckedTest() {
            public void run() {
                String arch = System.getProperty("os.arch", "").toLowerCase();
                if (!(arch.contains("aarch64") || arch.contains("arm64"))) {
                    throw new AssertionError("Expected ARM64, got " + arch);
                }
            }
        });
        check("Class loading and reflection", new CheckedTest() {
            public void run() throws Exception {
                Class<?> type = Class.forName("java.lang.String");
                Object result = type.getMethod("length").invoke("mikael");
                if (!Integer.valueOf(6).equals(result)) {
                    throw new AssertionError("Unexpected reflection result: " + result);
                }
            }
        });
        check("Threads and synchronization", new CheckedTest() {
            public void run() throws Exception {
                final int count = 8;
                final AtomicInteger total = new AtomicInteger();
                final CountDownLatch done = new CountDownLatch(count);
                for (int i = 0; i < count; i++) {
                    new Thread(new Runnable() {
                        public void run() {
                            try {
                                for (int n = 0; n < 10000; n++) total.incrementAndGet();
                            } finally {
                                done.countDown();
                            }
                        }
                    }, "runtime-smoke-" + i).start();
                }
                done.await();
                if (total.get() != count * 10000) {
                    throw new AssertionError("Lost updates: " + total.get());
                }
            }
        });
        check("Heap allocation and GC metrics", new CheckedTest() {
            public void run() {
                byte[][] blocks = new byte[128][];
                for (int i = 0; i < blocks.length; i++) blocks[i] = new byte[8192];
                long before = Runtime.getRuntime().totalMemory();
                System.gc();
                if (before <= 0 || Runtime.getRuntime().maxMemory() <= 0) {
                    throw new AssertionError("Invalid heap metrics");
                }
                log("  heapAfterGcBytes=" + Runtime.getRuntime().totalMemory());
            }
        });
        check("File I/O and UTF-8", new CheckedTest() {
            public void run() throws Exception {
                File file = File.createTempFile("mikael-runtime-", ".txt");
                try {
                    byte[] expected = "Mikael Runtime 8 — teste".getBytes(StandardCharsets.UTF_8);
                    Files.write(file.toPath(), expected);
                    byte[] actual = Files.readAllBytes(file.toPath());
                    if (!Arrays.equals(expected, actual)) throw new AssertionError("File content mismatch");
                } finally {
                    if (file.exists() && !file.delete()) file.deleteOnExit();
                }
            }
        });
        check("ZIP/JAR read and write", new CheckedTest() {
            public void run() throws Exception {
                File file = File.createTempFile("mikael-runtime-", ".jar");
                try {
                    ZipOutputStream out = new ZipOutputStream(new FileOutputStream(file));
                    try {
                        out.putNextEntry(new ZipEntry("probe.txt"));
                        out.write("ok".getBytes(StandardCharsets.UTF_8));
                        out.closeEntry();
                    } finally {
                        out.close();
                    }
                    JarFile jar = new JarFile(file);
                    try {
                        if (jar.getEntry("probe.txt") == null) throw new AssertionError("JAR entry missing");
                    } finally {
                        jar.close();
                    }
                } finally {
                    if (file.exists() && !file.delete()) file.deleteOnExit();
                }
            }
        });
        check("Temporary directory writable", new CheckedTest() {
            public void run() throws Exception {
                File dir = new File(System.getProperty("java.io.tmpdir", "."));
                if (!dir.isDirectory() || !dir.canWrite()) {
                    throw new AssertionError("Temporary directory is not writable: " + dir);
                }
            }
        });

        optionalClass("net.minecraft.launchwrapper.Launch", "LaunchWrapper");
        optionalClass("net.minecraftforge.fml.common.Loader", "Forge Loader");
        optionalClass("net.minecraft.client.Minecraft", "Minecraft client");

        log("");
        log("RESULT: passed=" + passed + " failed=" + failed + " info=" + info);
        File report = saveReport();
        if (report != null) System.out.println("REPORT_FILE=" + report.getAbsolutePath());
        System.out.println("Send the complete report file or copy the complete output for analysis.");
        if (failed != 0) System.exit(1);
    }
}
