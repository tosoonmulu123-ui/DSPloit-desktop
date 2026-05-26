# DSPloit PC

**Desktop controller for DSPloit jailbreak tool.**

Same exploit. Same capabilities. Controlled from PC with panic-safe logging.

## What is this?

DSPloit PC is a direct port of the DSPloit iOS jailbreak app to a PC-based tool. Instead of running the UI on the iPhone, you control everything from your computer via USB.

**Key advantage:** Every exploit step is logged to PC *before* execution. If the device panics, logs survive — you know exactly which step caused the crash.

## Requirements

- Python 3.10+
- PySide6 (Qt GUI)
- pymobiledevice3 (USB communication)
- iPhone connected via USB (trusted/paired)
- Pre-compiled agent binary (or macOS + Xcode to build)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## Architecture

```
PC (Python + Qt)  ←→  USB  ←→  iPhone (Agent binary)
     │                              │
     ├── GUI                        ├── darksword (kernel exploit)
     ├── Research Console           ├── post-exploitation
     ├── Panic-safe Logger          ├── command handler
     └── Device Manager             └── log reporter
```

## Features

- 🏠 One-click jailbreak (same 7-step chain as iOS app)
- 🔬 Research Console — step-by-step execution with panic-safe logging
- 🧠 Kernel Memory Inspector — read/write/dump kernel memory from PC
- ⚗️ Experiments — predefined AMFI bypass experiments
- 📁 File Manager — browse device filesystem
- 📦 Package Manager — install .deb packages
- 💻 SSH Terminal — root shell access
- 📋 Live Logs — real-time device + exploit logs

## Building Agent

The agent binary requires macOS with Xcode:

```bash
./scripts/build_agent.sh arm64e
```

## Building Standalone App

```bash
python compile.py
```

## Source

All exploit code from: https://github.com/tosoonmulu123-ui/DSPloit

---

*Created by Royan | 2026*
