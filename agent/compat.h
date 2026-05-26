//
//  compat.h — Agent-mode compatibility layer
//  DSPloit PC Agent
//
//  Overrides iOS-specific macros/functions for headless agent mode.
//  When AGENT_MODE is defined, UIKit/SwiftUI calls become no-ops
//  and logging goes through comm.h instead of NSLog.
//

#ifndef compat_h
#define compat_h

#import "darksword.h"
#import "offsets.h"
#import "utils.h"

// In agent mode, we don't have UIDevice — stub the version check macro
#ifdef AGENT_MODE

#import <Foundation/Foundation.h>

// Replace UIDevice systemVersion check with NSProcessInfo
#define SYSTEM_VERSION_GREATER_THAN_OR_EQUAL_TO(v) \
    ([[NSProcessInfo processInfo].operatingSystemVersionString compare:v options:NSNumericSearch] != NSOrderedAscending)

// Stub UIKit types that may be referenced
#define UINotificationFeedbackGenerator void
#define UIDevice void

#else

// Original iOS version — uses UIDevice
#define SYSTEM_VERSION_GREATER_THAN_OR_EQUAL_TO(v) \
    ([[[UIDevice currentDevice] systemVersion] compare:v options:NSNumericSearch] != NSOrderedAscending)

#endif /* AGENT_MODE */

#endif /* compat_h */
