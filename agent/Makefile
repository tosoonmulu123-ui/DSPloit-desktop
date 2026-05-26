# DSPloit Agent — Makefile
# Compiles agent binary for arm64e (A12+)
# Requires: macOS, Xcode, ldid

ARCH ?= arm64e
SDK = iphoneos
MIN_IOS = 15.0
CC = xcrun -sdk $(SDK) clang
LDID = ldid

TARGET = dsploit_agent
OUTPUT_DIR = ../payloads

# Source files — same as DSPloit iOS kexploit + agent comm layer
SRCS = main.m comm.m agent_bridge.m \
       darksword.m offsets.m offsets_xpf.m utils.m \
       persistence.m persistence_v2.m \
       kcache_sym.m kcache_analyze.m \
       TrustCacheInjector.m TweakLoaderDylib.m \
       pe/sbx.m pe/vfs.m pe/vnode.m pe/apfs.m pe/rc.m \
       TaskRop/RemoteCall.m TaskRop/exc.m TaskRop/pac.m \
       TaskRop/thread.m TaskRop/vm.m TaskRop/findcachedataoff.m \
       exploits/exploit_selector.m exploits/jpeg_uaf.m \
       exploits/sepkeystore_uaf.m exploits/aks_close_uaf.m

CFLAGS = -arch $(ARCH) \
         -miphoneos-version-min=$(MIN_IOS) \
         -isysroot $(shell xcrun --sdk $(SDK) --show-sdk-path) \
         -I. -Iheaders -ITaskRop -Ipe -Iexploits \
         -fobjc-arc \
         -fmodules \
         -DAGENT_MODE=1 \
         -Wno-unused-variable \
         -Wno-unused-function \
         -Wno-deprecated-declarations \
         -Wno-incompatible-pointer-types \
         -Wno-nonportable-include-path

LDFLAGS = -arch $(ARCH) \
          -framework Foundation \
          -framework IOKit \
          -framework IOSurface \
          -framework CoreFoundation \
          -framework Security

ENTITLEMENTS = entitlements.plist

.PHONY: all clean

all: $(OUTPUT_DIR)/$(TARGET)_$(ARCH)

$(OUTPUT_DIR)/$(TARGET)_$(ARCH): $(SRCS)
	@mkdir -p $(OUTPUT_DIR)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(SRCS)
	$(LDID) -S$(ENTITLEMENTS) $@
	@echo "Built: $@"
	@echo "Size: $$(du -h $@ | cut -f1)"

clean:
	rm -f $(OUTPUT_DIR)/$(TARGET)_*
