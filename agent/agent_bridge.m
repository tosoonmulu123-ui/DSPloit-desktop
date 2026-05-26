/**
 * agent_bridge.m — Bridge between C command handler and ObjC APIs.
 * Provides C-callable wrappers for RemoteCall and other ObjC interfaces.
 */

#import <Foundation/Foundation.h>
#include <dlfcn.h>
#include "darksword.h"
#include "offsets.h"
#include "utils.h"
#include "TaskRop/RemoteCall.h"
#include "comm.h"

static RemoteCall *g_springboard_rc = nil;

/**
 * Initialize RemoteCall to a named process.
 * Returns 0 on success, -1 on failure.
 */
int rc_init_process(const char *name) {
    NSString *procName = [NSString stringWithUTF8String:name];
    
    comm_log("RC: connecting to %s...", name);
    
    RemoteCall *rc = [[RemoteCall alloc] initWithProcess:procName useMigFilterBypass:NO];
    if (!rc || rc.pid == 0) {
        NSString *err = [RemoteCall lastInitError];
        comm_log("RC: init failed — %s", err ? err.UTF8String : "unknown");
        return -1;
    }
    
    comm_log("RC: connected to %s (pid=%d)", name, rc.pid);
    
    // Store SpringBoard RC globally
    if (strcmp(name, "SpringBoard") == 0) {
        g_springboard_rc = rc;
    }
    
    return 0;
}

/**
 * Get the global SpringBoard RemoteCall instance.
 */
RemoteCall *get_springboard_rc(void) {
    return g_springboard_rc;
}

/**
 * Destroy RemoteCall session.
 */
void rc_destroy(void) {
    if (g_springboard_rc) {
        [g_springboard_rc destroyRemoteCall];
        g_springboard_rc = nil;
    }
}

/**
 * Execute a remote function call on SpringBoard.
 * Simplified wrapper for agent use.
 */
uint64_t rc_call_func(const char *func_name, uint64_t arg0, uint64_t arg1,
                       uint64_t arg2, uint64_t arg3) {
    if (!g_springboard_rc) return 0;
    
    void *ptr = dlsym(RTLD_DEFAULT, func_name);
    if (!ptr) return 0;
    
    uint64_t args[] = {arg0, arg1, arg2, arg3};
    return [g_springboard_rc doRemoteCallStableWithTimeout:5
                                             functionName:(char *)func_name
                                          functionPointer:ptr
                                                     args:args
                                                 argCount:4];
}
