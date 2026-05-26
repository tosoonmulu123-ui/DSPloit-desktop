# DSPloit PC — Project Plan

## Port DSPloit dari iOS App ke PC/Laptop-Based Tool

**Version**: 2.0  
**Author**: Royan  
**Date**: 2026-05-26  
**Status**: Planning  
**Repository**: Baru (terpisah dari DSPloit iOS)

---

## 1. Konsep

**DSPloit PC = DSPloit iOS yang sama persis, tapi dijalankan dan dikontrol dari PC.**

Bukan gabungan project lain. Bukan tool baru. Ini adalah **port langsung** dari DSPloit app-based ke PC-based, dengan satu keuntungan utama: **real-time logging yang panic-safe**.

### Apa yang SAMA:
- Kernel exploit (darksword) — sama persis
- Post-exploitation (sbx, vfs, vnode, RemoteCall) — sama persis
- Jailbreak chain (7 steps) — sama persis
- Multi-exploit selector — sama persis
- KRW persistence — sama persis
- Offset resolution (XPF) — sama persis
- Semua fitur: SSH, packages, tweaks, file manager — sama persis

### Apa yang BERUBAH:
- UI bukan di iPhone, tapi di PC (Python + Qt)
- Control bukan tap tombol di device, tapi klik di PC
- Log tidak hilang saat panic — tersimpan di PC
- Bisa step-by-step execution untuk research
- Bisa inspect kernel memory dari PC

### Apa yang TIDAK di-port:
- `AMFIExperimentView.swift` — tetap di repo iOS, tidak di-port ke PC

---

## 2. Mengapa Pindah ke PC?

```
PROBLEM (App-Based):
  Experiment jalan → device panic → SEMUA LOG HILANG → blind

SOLUTION (PC-Based):
  Experiment jalan → setiap step di-log ke PC → device panic → 
  LOG TETAP ADA → tahu persis step mana yang panic
```

Ini bukan soal "chance lebih besar" — ini soal **visibility**:
- Setiap panic = data (bukan misteri)
- Bisa binary search exact instruction yang trigger PPL
- 10x faster iteration untuk research AMFI bypass
- Akhirnya bisa mencapai 100% FULL JAILBREAK ACCESS SYSTEM

---

## 3. Arsitektur

```
┌──────────────────────────────────────────────────────────────┐
│                     DSPloit PC (Python + Qt)                    │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐  │
│  │   GUI   │  │  USB     │  │  Exploit  │  │  Research  │  │
│  │(PySide6)│  │(usbmuxd) │  │  Engine   │  │  Console   │  │
│  └────┬────┘  └────┬─────┘  └─────┬─────┘  └─────┬──────┘  │
│       │             │              │               │          │
│  ┌────┴─────────────┴──────────────┴───────────────┴─────┐   │
│  │                   Core Engine                          │   │
│  │                                                        │   │
│  │  DeviceManager    — detect + pair iPhone via USB       │   │
│  │  ExploitEngine    — deploy + trigger + monitor         │   │
│  │  ResearchConsole  — step-by-step with panic-safe log   │   │
│  │  SessionManager   — SSH tunnel after jailbreak         │   │
│  │  PayloadManager   — build + deploy arm64 payload       │   │
│  └────────────────────────────────────────────────────────┘   │
│                            │ USB                               │
│                            ▼                                   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                  iPhone (Target)                         │   │
│  │                                                         │   │
│  │  [DSPloit Agent] — arm64 binary on device               │   │
│  │  ├── darksword.m (kernel exploit)                       │   │
│  │  ├── pe/ (sbx, vfs, vnode, apfs, RemoteCall)            │   │
│  │  ├── offsets (XPF + hardcoded)                          │   │
│  │  ├── persistence_v2                                     │   │
│  │  ├── TweakLoader                                        │   │
│  │  ├── log_reporter (send logs to PC via USB)             │   │
│  │  └── command_handler (receive commands from PC)         │   │
│  │                                                         │   │
│  │  [After Jailbreak]                                      │   │
│  │  ├── /var/jb/ bootstrap                                 │   │
│  │  ├── dropbear SSH                                       │   │
│  │  ├── dpkg                                               │   │
│  │  └── tweakloader.dylib                                  │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Mapping: DSPloit iOS → DSPloit PC

### On-Device Code (tetap Objective-C/Swift → compile arm64)

| DSPloit iOS | → DSPloit PC Agent | Status |
|-------------|-------------------|--------|
| `lara/kexploit/darksword.m` | `agent/darksword.m` | Sama persis |
| `lara/kexploit/darksword.h` | `agent/darksword.h` | Sama persis |
| `lara/kexploit/offsets.m` | `agent/offsets.m` | Sama persis |
| `lara/kexploit/offsets.h` | `agent/offsets.h` | Sama persis |
| `lara/kexploit/offsets_xpf.m` | `agent/offsets_xpf.m` | Sama persis |
| `lara/kexploit/utils.m` | `agent/utils.m` | Sama persis |
| `lara/kexploit/persistence.m` | `agent/persistence.m` | Sama persis |
| `lara/kexploit/persistence_v2.m` | `agent/persistence_v2.m` | Sama persis |
| `lara/kexploit/kcache_sym.m` | `agent/kcache_sym.m` | Sama persis |
| `lara/kexploit/kcache_analyze.m` | `agent/kcache_analyze.m` | Sama persis |
| `lara/kexploit/TrustCacheInjector.m` | `agent/TrustCacheInjector.m` | Sama persis |
| `lara/kexploit/TweakLoaderDylib.m` | `agent/TweakLoaderDylib.m` | Sama persis |
| `lara/kexploit/pe/sbx.m` | `agent/pe/sbx.m` | Sama persis |
| `lara/kexploit/pe/vfs.m` | `agent/pe/vfs.m` | Sama persis |
| `lara/kexploit/pe/vnode.m` | `agent/pe/vnode.m` | Sama persis |
| `lara/kexploit/pe/apfs.m` | `agent/pe/apfs.m` | Sama persis |
| `lara/kexploit/pe/rc.m` | `agent/pe/rc.m` | Sama persis |
| `lara/kexploit/TaskRop/RemoteCall.m` | `agent/TaskRop/RemoteCall.m` | Sama persis |
| `lara/kexploit/TaskRop/exc.m` | `agent/TaskRop/exc.m` | Sama persis |
| `lara/kexploit/TaskRop/pac.m` | `agent/TaskRop/pac.m` | Sama persis |
| `lara/kexploit/TaskRop/thread.m` | `agent/TaskRop/thread.m` | Sama persis |
| `lara/kexploit/TaskRop/vm.m` | `agent/TaskRop/vm.m` | Sama persis |
| `lara/kexploit/exploits/*` | `agent/exploits/*` | Sama persis |

### Control Logic (port Swift → Python)

| DSPloit iOS (Swift) | → DSPloit PC (Python) | Notes |
|--------------------|----------------------|-------|
| `JailbreakEngine.swift` | `src/core/exploit_engine.py` | Logic sama, bahasa beda |
| `dspmgr.swift` | `src/core/device_state.py` | State management |
| `RootExecutor.swift` | `src/core/root_executor.py` | Remote command execution |
| `SSHManager.swift` | `src/post_exploit/ssh_manager.py` | SSH deploy + manage |
| `DebInstaller.swift` | `src/post_exploit/deb_installer.py` | .deb parsing + install |
| `DpkgStatus.swift` | `src/post_exploit/dpkg_status.py` | Package tracking |
| `TweakLoader.swift` | `src/post_exploit/tweak_loader.py` | Tweak deployment |
| `AppRegistrar.swift` | `src/post_exploit/app_registrar.py` | App registration |
| `IOKitFuzzer.swift` | `src/research/iokit_fuzzer.py` | IOKit probing |
| `KernelcacheManager.swift` | `src/exploit/kernelcache_mgr.py` | Kcache download + parse |
| `IconThemeManager.swift` | `src/post_exploit/icon_theme.py` | Icon theming |

### Views (port SwiftUI → PySide6)

| DSPloit iOS (SwiftUI) | → DSPloit PC (Qt) | Notes |
|----------------------|-------------------|-------|
| `ContentView.swift` (Tab 1) | `src/gui/pages/home_page.py` | Jailbreak button + status |
| `RootDashboardView.swift` (Tab 2) | `src/gui/pages/tools_page.py` | Tool launcher |
| `RootFileManagerView.swift` | `src/gui/pages/files_page.py` | File browser |
| `PackageManagerView.swift` | `src/gui/pages/packages_page.py` | Package manager |
| `DaemonDisableView.swift` | `src/gui/pages/daemons_page.py` | Daemon control |
| `MobileBankingView.swift` | `src/gui/pages/banking_page.py` | JB detection hide |
| `DeviceCompatibilityView.swift` | `src/gui/pages/compat_page.py` | Device compat info |
| `ExperimentsView.swift` | `src/gui/pages/experiments_page.py` | Experiment runner |
| — (BARU) | `src/gui/pages/research_page.py` | Step-by-step console |
| — (BARU) | `src/gui/pages/memory_page.py` | Kernel memory inspector |
| `AMFIExperimentView.swift` | **TIDAK DI-PORT** | Tetap di repo iOS |

---

## 5. On-Device Agent

### Apa itu Agent?

Agent = semua code exploit DSPloit yang sekarang ada di .app, di-compile jadi **satu standalone binary** tanpa UI. Binary ini:
- Menerima command dari PC via USB
- Execute command (kread, kwrite, exploit, spawn, dll)
- Kirim result + log balik ke PC
- Tunggu command berikutnya

### Agent vs App

| | DSPloit App (sekarang) | DSPloit Agent (PC-based) |
|---|---|---|
| UI | SwiftUI di device | Tidak ada (headless) |
| Control | User tap tombol | PC kirim command |
| Logging | Dalam app (hilang saat panic) | Stream ke PC (panic-safe) |
| Execution | Semua step sekaligus | Step-by-step (PC kontrol) |
| Binary type | .app bundle | Standalone Mach-O |
| Code | Sama persis | Sama persis + command handler |

### Agent Architecture

```c
// agent/main.m — entry point

int main(int argc, char *argv[]) {
    // 1. Setup communication channel (file-based or socket)
    comm_init();
    
    // 2. Report ready
    comm_send("READY");
    
    // 3. Command loop
    while (1) {
        char *cmd = comm_receive();  // Block until PC sends command
        
        if (strcmp(cmd, "EXPLOIT_RUN") == 0) {
            comm_send("LOG:Starting darksword...");
            int ret = ds_run();
            comm_send("RESULT:%d", ret);
            
        } else if (strncmp(cmd, "KREAD64:", 8) == 0) {
            uint64_t addr = parse_hex(cmd + 8);
            comm_send("LOG:kread64(0x%llx)", addr);
            uint64_t val = ds_kread64(addr);
            comm_send("RESULT:0x%llx", val);
            
        } else if (strncmp(cmd, "KWRITE64:", 9) == 0) {
            // parse addr:value
            comm_send("LOG:kwrite64(0x%llx, 0x%llx)", addr, val);
            ds_kwrite64(addr, val);
            comm_send("RESULT:OK");
            
        } else if (strcmp(cmd, "FULL_CHAIN") == 0) {
            // Run full 7-step jailbreak chain
            // But log EVERY step to PC before executing
            run_full_chain_with_logging();
        }
        // ... more commands
    }
}
```

### Communication (PC ↔ Agent)

```
Method: File-based via AFC (Apple File Conduit)

PC writes command to:  /var/tmp/.dsploit_cmd
Agent reads command, executes, writes result to: /var/tmp/.dsploit_result
Agent writes logs to: /var/tmp/.dsploit_log (append)
PC polls result + log files

Fallback: After jailbreak, switch to SSH (faster, bidirectional)
```

---

## 6. Research Console (Fitur Baru — tidak ada di iOS version)

```python
# Dari PC — step-by-step exploit dengan logging setiap langkah

class ResearchConsole:
    """Execute exploit steps one-by-one with panic-safe logging."""
    
    def step(self, name: str, command: str) -> StepResult:
        """
        1. Log step name + command ke file PC (FLUSH)
        2. Send command ke device agent
        3. Wait for result (or timeout = panic)
        4. Log result ke file PC (FLUSH)
        5. Return result
        """
        
    def run_experiment(self, experiment: Experiment) -> ExperimentResult:
        """Run all steps of an experiment with full logging."""
        
    def panic_report(self) -> str:
        """After panic: show last successful step + the step that caused it."""
```

### Contoh Session

```
DSPloit PC Research Console
═══════════════════════════════════════════════════
Device: iPhone XR (A12) • iOS 18.2
Exploit: darksword (ready)
═══════════════════════════════════════════════════

[1/7] Running darksword exploit...
  → KRW achieved ✅ (kernel_base = 0xfffffff007004000 + 0x1234000)

[2/7] Sandbox escape...
  → sbx_escape() = 0 ✅

[3/7] RemoteCall to SpringBoard...
  → RC connected, pid = 312 ✅

[4/7] Root verification...
  → getuid() = 0 ✅

[5/7] Bootstrap...
  → /var/jb/ created ✅

[6/7] AMFI disable...
  → 10 flags zeroed ✅
  → cs_enforcement_disable = 1 ✅

[7/7] AMFI bypass research...
  → Step 7a: Find amfid proc... pid=847 ✅
  → Step 7b: Connect RC to amfid... ✅
  → Step 7c: dlsym MISValidateSignature... addr=0x1a2b3c4d ✅
  → Step 7d: Read original bytes... 0xD503201F ✅
  → Step 7e: mprotect RWX... ret=0 ✅
  → Step 7f: Write patch bytes...
  
  ⚠️ DEVICE DISCONNECTED (panic)
  
  PANIC REPORT:
  ├── Last success: Step 7e (mprotect returned 0)
  ├── Panic step: Step 7f (write to 0x1a2b3c4d)
  ├── Conclusion: mprotect succeeded but write still blocked
  └── Next: Try vm_remap approach instead of direct write
  
  Log saved: logs/2026-05-26_12-01-03_amfid_patch.txt
```

---

## 7. Direktori Project (Repository Baru)

```
dsploit-desktop/
│
├── main.py                         # Entry point
├── requirements.txt                # Python dependencies
├── compile.py                      # PyInstaller build
├── README.md
├── LICENSE
│
├── src/
│   ├── gui/                        # PySide6 GUI
│   │   ├── main_window.py
│   │   ├── theme.py
│   │   └── pages/
│   │       ├── home_page.py        # Device + jailbreak button
│   │       ├── research_page.py    # Step-by-step console (BARU)
│   │       ├── memory_page.py      # Kernel memory inspector (BARU)
│   │       ├── experiments_page.py # Experiment runner
│   │       ├── tools_page.py       # Root tools launcher
│   │       ├── files_page.py       # File manager
│   │       ├── packages_page.py    # Package manager
│   │       ├── daemons_page.py     # Daemon control
│   │       ├── banking_page.py     # JB detection hide
│   │       ├── ssh_page.py         # SSH terminal
│   │       ├── settings_page.py
│   │       └── logs_page.py        # Real-time logs
│   │
│   ├── core/                       # Core (port dari Swift)
│   │   ├── device_manager.py       # ← dspmgr.swift (device state)
│   │   ├── exploit_engine.py       # ← JailbreakEngine.swift
│   │   ├── root_executor.py        # ← RootExecutor.swift
│   │   ├── research_console.py     # BARU — step-by-step
│   │   ├── panic_analyzer.py       # BARU — analyze panics
│   │   └── session_manager.py      # SSH tunnel management
│   │
│   ├── usb/                        # USB communication
│   │   ├── device_link.py          # pymobiledevice3 wrapper
│   │   ├── afc_client.py           # File read/write via AFC
│   │   ├── syslog_relay.py         # Real-time syslog
│   │   ├── crash_reader.py         # Read panic logs after reboot
│   │   └── agent_comm.py           # PC ↔ Agent protocol
│   │
│   ├── exploit/                    # Exploit management
│   │   ├── payload_builder.py      # Build agent for target
│   │   ├── deployer.py             # Deploy agent to device
│   │   ├── trigger.py              # Trigger agent execution
│   │   ├── monitor.py              # Monitor exploit progress
│   │   └── offset_resolver.py      # ← offsets_xpf logic
│   │
│   ├── research/                   # Research system (BARU)
│   │   ├── experiment_base.py
│   │   ├── step_executor.py
│   │   ├── memory_inspector.py
│   │   ├── proc_inspector.py
│   │   └── experiments/
│   │       ├── exp_amfid_kill_race.py
│   │       ├── exp_amfid_rc_patch.py
│   │       ├── exp_amfid_mprotect.py
│   │       ├── exp_cryptex_race.py
│   │       └── exp_custom.py
│   │
│   ├── post_exploit/               # Post-JB (port dari Swift)
│   │   ├── ssh_manager.py          # ← SSHManager.swift
│   │   ├── deb_installer.py        # ← DebInstaller.swift
│   │   ├── dpkg_status.py          # ← DpkgStatus.swift
│   │   ├── tweak_loader.py         # ← TweakLoader.swift
│   │   ├── app_registrar.py        # ← AppRegistrar.swift
│   │   ├── file_manager.py
│   │   ├── daemon_manager.py
│   │   └── icon_theme.py           # ← IconThemeManager.swift
│   │
│   └── utils/
│       ├── logger.py               # Panic-safe logging
│       ├── config.py
│       ├── device_db.py
│       └── ios_version.py
│
├── agent/                          # On-device binary source
│   │                               # (= DSPloit iOS kexploit code)
│   ├── Makefile                    # Compile → arm64 binary
│   ├── main.m                      # Agent entry + command loop
│   ├── comm.m                      # Communication with PC
│   ├── comm.h
│   ├── darksword.m                 # ← SAMA dari DSPloit iOS
│   ├── darksword.h
│   ├── offsets.m
│   ├── offsets.h
│   ├── offsets_xpf.m
│   ├── offsets_xpf.h
│   ├── utils.m
│   ├── utils.h
│   ├── persistence.m
│   ├── persistence_v2.m
│   ├── kcache_sym.m
│   ├── kcache_analyze.m
│   ├── compat.h
│   ├── TrustCacheInjector.m
│   ├── TweakLoaderDylib.m
│   ├── pe/
│   │   ├── sbx.m
│   │   ├── vfs.m
│   │   ├── vnode.m
│   │   ├── apfs.m
│   │   └── rc.m
│   ├── TaskRop/
│   │   ├── RemoteCall.m
│   │   ├── RemoteCall.h
│   │   ├── exc.m
│   │   ├── pac.m
│   │   ├── thread.m
│   │   └── vm.m
│   ├── exploits/
│   │   ├── exploit_selector.m
│   │   ├── jpeg_uaf.m
│   │   ├── sepkeystore_uaf.m
│   │   └── aks_close_uaf.m
│   └── headers/
│       ├── fileport.h
│       ├── libgrabkernel2.h
│       └── xpf.h
│
├── payloads/                       # Pre-compiled binaries
│   ├── dsploit_agent_arm64e        # Compiled agent
│   ├── bootstrap.tar.xz
│   ├── dropbear_arm64e
│   └── dpkg_arm64e
│
├── logs/                           # Experiment logs (panic-safe)
│   └── .gitkeep
│
└── scripts/
    ├── build_agent.sh              # Compile agent (needs macOS)
    ├── build_windows.bat
    ├── build_macos.sh
    └── build_linux.sh
```

---

## 8. Development Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Repo setup + scaffold
- [ ] pymobiledevice3 device detection
- [ ] Basic Qt GUI (device info + log viewer)
- [ ] AFC file read/write
- [ ] Syslog relay (device → PC real-time)

### Phase 2: Agent Deploy (Week 3-4)
- [ ] Compile agent binary (copy DSPloit kexploit code + add command handler)
- [ ] Deploy agent to device via AFC
- [ ] Trigger agent execution
- [ ] PC ↔ Agent communication working
- [ ] Basic commands: PING, KREAD64, KWRITE64

### Phase 3: Research Console (Week 5-6)
- [ ] Step-by-step executor
- [ ] Panic-safe logger
- [ ] Memory inspector
- [ ] Experiment system
- [ ] Panic analyzer
- [ ] Port all experiments from iOS

### Phase 4: Full Exploit Chain (Week 7-8)
- [ ] EXPLOIT_RUN command (full darksword)
- [ ] FULL_CHAIN command (7-step jailbreak)
- [ ] Progress reporting to PC
- [ ] SSH auto-deploy after jailbreak
- [ ] USB SSH tunnel

### Phase 5: AMFI Research (Week 9-10)
- [ ] Run all AMFI experiments with proper logging
- [ ] Iterate based on panic data
- [ ] Find working bypass
- [ ] Integrate into main chain

### Phase 6: Full Tool (Week 11-12)
- [ ] Package manager from PC
- [ ] File manager from PC
- [ ] Tweak installer from PC
- [ ] One-click jailbreak mode
- [ ] PyInstaller builds
- [ ] Documentation

---

## 9. Kesimpulan

DSPloit PC = **exact same exploit + capabilities** as DSPloit iOS app, tapi:
- Dikontrol dari PC (bukan dari device)
- Log tersimpan di PC (panic-safe)
- Bisa step-by-step (untuk research)
- Mempercepat pencarian 100% FULL JAILBREAK ACCESS SYSTEM

**Agent binary** = semua code ObjC dari `lara/kexploit/` di-compile jadi satu binary headless yang menerima command dari PC.

**Python app** = semua logic Swift dari `lara/classes/` di-port ke Python + tambahan research console.

---

---

## 10. Source Reference Repository

**PENTING**: Semua code exploit dan post-exploitation di-ambil dari repo ini:

```
Repository: https://github.com/tosoonmulu123-ui/DSPloit
Branch: main
```

### File yang di-copy langsung ke Agent (JANGAN modifikasi logic):

```
FROM: https://github.com/tosoonmulu123-ui/DSPloit/tree/main/lara/kexploit/
TO:   dsploit-desktop/agent/

Mapping:
  lara/kexploit/darksword.m          → agent/darksword.m
  lara/kexploit/darksword.h          → agent/darksword.h
  lara/kexploit/offsets.m            → agent/offsets.m
  lara/kexploit/offsets.h            → agent/offsets.h
  lara/kexploit/offsets_xpf.m        → agent/offsets_xpf.m
  lara/kexploit/offsets_xpf.h        → agent/offsets_xpf.h
  lara/kexploit/utils.m              → agent/utils.m
  lara/kexploit/utils.h              → agent/utils.h
  lara/kexploit/compat.h             → agent/compat.h
  lara/kexploit/persistence.m        → agent/persistence.m
  lara/kexploit/persistence.h        → agent/persistence.h
  lara/kexploit/persistence_v2.m     → agent/persistence_v2.m
  lara/kexploit/persistence_v2.h     → agent/persistence_v2.h
  lara/kexploit/kcache_sym.m         → agent/kcache_sym.m
  lara/kexploit/kcache_sym.h         → agent/kcache_sym.h
  lara/kexploit/kcache_analyze.m     → agent/kcache_analyze.m
  lara/kexploit/kcache_analyze.h     → agent/kcache_analyze.h
  lara/kexploit/TrustCacheInjector.m → agent/TrustCacheInjector.m
  lara/kexploit/TrustCacheInjector.h → agent/TrustCacheInjector.h
  lara/kexploit/TweakLoaderDylib.m   → agent/TweakLoaderDylib.m
  lara/kexploit/pe/sbx.m            → agent/pe/sbx.m
  lara/kexploit/pe/sbx.h            → agent/pe/sbx.h
  lara/kexploit/pe/vfs.m            → agent/pe/vfs.m
  lara/kexploit/pe/vfs.h            → agent/pe/vfs.h
  lara/kexploit/pe/vnode.m          → agent/pe/vnode.m
  lara/kexploit/pe/vnode.h          → agent/pe/vnode.h
  lara/kexploit/pe/apfs.m           → agent/pe/apfs.m
  lara/kexploit/pe/apfs.h           → agent/pe/apfs.h
  lara/kexploit/pe/rc.m             → agent/pe/rc.m
  lara/kexploit/pe/rc.h             → agent/pe/rc.h
  lara/kexploit/pe/xpaci.h          → agent/pe/xpaci.h
  lara/kexploit/TaskRop/RemoteCall.m → agent/TaskRop/RemoteCall.m
  lara/kexploit/TaskRop/RemoteCall.h → agent/TaskRop/RemoteCall.h
  lara/kexploit/TaskRop/exc.m       → agent/TaskRop/exc.m
  lara/kexploit/TaskRop/exc.h       → agent/TaskRop/exc.h
  lara/kexploit/TaskRop/pac.m       → agent/TaskRop/pac.m
  lara/kexploit/TaskRop/pac.h       → agent/TaskRop/pac.h
  lara/kexploit/TaskRop/thread.m    → agent/TaskRop/thread.m
  lara/kexploit/TaskRop/thread.h    → agent/TaskRop/thread.h
  lara/kexploit/TaskRop/vm.m        → agent/TaskRop/vm.m
  lara/kexploit/TaskRop/vm.h        → agent/TaskRop/vm.h
  lara/kexploit/TaskRop/privateapi.h → agent/TaskRop/privateapi.h
  lara/kexploit/TaskRop/findcachedataoff.m → agent/TaskRop/findcachedataoff.m
  lara/kexploit/exploits/exploit_selector.m → agent/exploits/exploit_selector.m
  lara/kexploit/exploits/exploit_selector.h → agent/exploits/exploit_selector.h
  lara/kexploit/exploits/jpeg_uaf.m  → agent/exploits/jpeg_uaf.m
  lara/kexploit/exploits/jpeg_uaf.h  → agent/exploits/jpeg_uaf.h
  lara/kexploit/exploits/sepkeystore_uaf.m → agent/exploits/sepkeystore_uaf.m
  lara/kexploit/exploits/sepkeystore_uaf.h → agent/exploits/sepkeystore_uaf.h
  lara/kexploit/exploits/aks_close_uaf.m → agent/exploits/aks_close_uaf.m
  lara/kexploit/exploits/aks_close_uaf.h → agent/exploits/aks_close_uaf.h
  lara/headers/fileport.h            → agent/headers/fileport.h
  lara/headers/libgrabkernel2.h      → agent/headers/libgrabkernel2.h
  lara/headers/xpf.h                 → agent/headers/xpf.h
  lara/headers/IconServices.h        → agent/headers/IconServices.h
```

### Swift files yang logic-nya di-port ke Python:

```
FROM: https://github.com/tosoonmulu123-ui/DSPloit/tree/main/lara/classes/
TO:   dsploit-desktop/src/ (Python port)

Reference files (baca logic, port ke Python):
  lara/classes/JailbreakEngine.swift   → src/core/exploit_engine.py
  lara/classes/dspmgr.swift            → src/core/device_state.py
  lara/classes/RootExecutor.swift      → src/core/root_executor.py
  lara/classes/SSHManager.swift        → src/post_exploit/ssh_manager.py
  lara/classes/DebInstaller.swift      → src/post_exploit/deb_installer.py
  lara/classes/DpkgStatus.swift        → src/post_exploit/dpkg_status.py
  lara/classes/TweakLoader.swift       → src/post_exploit/tweak_loader.py
  lara/classes/AppRegistrar.swift      → src/post_exploit/app_registrar.py
  lara/classes/IOKitFuzzer.swift       → src/research/iokit_fuzzer.py
  lara/classes/KernelcacheManager.swift → src/exploit/kernelcache_mgr.py
  lara/classes/IconThemeManager.swift  → src/post_exploit/icon_theme.py
  lara/classes/IconThemeGalleryManager.swift → src/post_exploit/icon_gallery.py
  lara/classes/Logger.swift            → src/utils/logger.py
  lara/funcs/DeviceCompat.swift        → src/utils/device_db.py
  lara/funcs/fetchkcache.swift         → src/exploit/kernelcache_mgr.py
  lara/funcs/helpers.swift             → src/utils/helpers.py
  lara/funcs/isdebugged.swift          → src/utils/device_db.py
  lara/funcs/isunsupported.swift       → src/utils/device_db.py
```

### File yang TIDAK di-port (tetap di repo iOS saja):

```
SKIP — jangan port ke PC:
  lara/views/root/AMFIExperimentView.swift  ← tetap di repo iOS
```

### Experiment file (port logic ke Python):

```
FROM: https://github.com/tosoonmulu123-ui/DSPloit/tree/main/lara/experiments/
TO:   dsploit-desktop/src/research/experiments/

  lara/experiments/exp_amfid_patch.swift → src/research/experiments/exp_amfid_rc_patch.py
```

### Config & Build files (referensi):

```
Referensi build:
  lara/Info.plist                     → referensi entitlements
  Config/lara.entitlements            → referensi entitlements untuk agent
  .github/workflows/build.yml         → referensi CI setup
  scripts/build_ipa.sh                → referensi build flow
```

---

## 11. Aturan untuk Next Session

1. **JANGAN modifikasi logic exploit** — copy as-is dari repo DSPloit iOS
2. **Agent = headless version** dari DSPloit app — tambah command handler, hapus UI
3. **Python = control layer** — port LOGIC dari Swift, bukan translate line-by-line
4. **Selalu refer ke repo** `https://github.com/tosoonmulu123-ui/DSPloit` untuk source of truth
5. **Jangan buat fitur baru** yang tidak ada di DSPloit iOS (kecuali research console)
6. **AMFIExperimentView.swift SKIP** — tidak di-port

---

*DSPloit PC — Same power. Better visibility. Faster research.*  
*Source: https://github.com/tosoonmulu123-ui/DSPloit*  
*Created by Royan | 2026-05-26*
