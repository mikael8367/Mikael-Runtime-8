package com.mikael.runtimecheck;

import java.io.File;
import java.io.FileOutputStream;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.jar.JarFile;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * Small Java 8 smoke test for a candidate runtime.
 * It does not prove Minecraft/Forge/OptiFine compatibility.
 */
public final class RuntimeSmokeTest {
    private static int passed;
    private static int failed;

    private RuntimeSmokeTest() {}

    private static void check(String name, CheckedTest test) {
        try {
            test.run();
            passed++;
            System.out.println("[PASS] " + name);
        } catch (Throwable error) {
            failed++;
            System.out.println("[FAIL] " + name + " -> " + error);
            error.printStackTrace(System.out);
        }
    }

    private interface CheckedTest {
        void run() throws Exception;
    }

    public static void main(String[] args) throws Exception {
        System.out.println("Mikael Runtime 8 - Android Java smoke test");
        System.out.println("java.version=" + System.getProperty("java.version"));
        System.out.println("java.vm.name=" + System.getProperty("java.vm.name"));
        System.out.println("java.vm.version=" + System.getProperty("java.vm.version"));
        System.out.println("os.name=" + System.getProperty("os.name"));
        System.out.println("os.arch=" + System.getProperty("os.arch"));
        System.out.println("java.library.path=" + System.getProperty("java.library.path"));
        System.out.println("java.class.path=" + System.getProperty("java.class.path"));

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
                Method method = type.getMethod("length");
                Object result = method.invoke("mikael");
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
        check("Heap allocation and garbage collection", new CheckedTest() {
            public void run() {
                byte[][] blocks = new byte[128][];
                for (int i = 0; i < blocks.length; i++) blocks[i] = new byte[8192];
                long before = Runtime.getRuntime().totalMemory();
                System.gc();
                if (before <= 0 || Runtime.getRuntime().maxMemory() <= 0) {
                    throw new AssertionError("Invalid heap metrics");
                }
            }
        });
        check("File I/O and UTF-8", new CheckedTest() {
            public void run() throws Exception {
                File file = File.createTempFile("mikael-runtime-", ".txt");
                try {
                    byte[] expected = "Mikael Runtime 8 — teste".getBytes(StandardCharsets.UTF_8);
                    Files.write(file.toPath(), expected);
                    byte[] actual = Files.readAllBytes(file.toPath());
                    if (!java.util.Arrays.equals(expected, actual)) {
                        throw new AssertionError("File content mismatch");
                    }
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
                        if (jar.getEntry("probe.txt") == null) {
                            throw new AssertionError("JAR entry missing");
                        }
                    } finally {
                        jar.close();
                    }
                } finally {
                    if (file.exists() && !file.delete()) file.deleteOnExit();
                }
            }
        });

        optionalClass("net.minecraft.launchwrapper.Launch", "LaunchWrapper");
        optionalClass("net.minecraftforge.fml.common.Loader", "Forge Loader");
        optionalClass("net.minecraft.client.Minecraft", "Minecraft client");

        System.out.println("RESULT: passed=" + passed + " failed=" + failed);
        if (failed != 0) System.exit(1);
    }

    private static void optionalClass(final String className, final String label) {
        check(label + " classpath visibility (optional)", new CheckedTest() {
            public void run() throws Exception {
                try {
                    Class.forName(className, false, Thread.currentThread().getContextClassLoader());
                    System.out.println("  Found " + className);
                } catch (ClassNotFoundException absent) {
                    System.out.println("  Not on this test process classpath: " + className);
                }
            }
        });
    }
}
