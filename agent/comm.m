/**
 * DSPloit Agent — Communication implementation.
 * File-based protocol: PC writes commands, agent reads and responds.
 */

#import <Foundation/Foundation.h>
#include "comm.h"
#include <stdarg.h>

static char cmd_buffer[MAX_CMD_LEN];
static char result_buffer[MAX_RESULT_LEN];

int comm_init(void) {
    // Clear any stale files
    [@"" writeToFile:@CMD_FILE atomically:YES
        encoding:NSUTF8StringEncoding error:nil];
    [@"" writeToFile:@RESULT_FILE atomically:YES
        encoding:NSUTF8StringEncoding error:nil];
    
    comm_log("Agent communication initialized");
    return 0;
}

void comm_send(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    vsnprintf(result_buffer, MAX_RESULT_LEN, fmt, args);
    va_end(args);
    
    NSString *result = [NSString stringWithUTF8String:result_buffer];
    [result writeToFile:@RESULT_FILE atomically:YES
        encoding:NSUTF8StringEncoding error:nil];
}

void comm_log(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    char log_buf[2048];
    vsnprintf(log_buf, sizeof(log_buf), fmt, args);
    va_end(args);
    
    NSString *logPath = @LOG_FILE;
    NSString *existing = [NSString stringWithContentsOfFile:logPath
        encoding:NSUTF8StringEncoding error:nil] ?: @"";
    NSString *entry = [NSString stringWithFormat:@"%@\n",
        [NSString stringWithUTF8String:log_buf]];
    NSString *updated = [existing stringByAppendingString:entry];
    [updated writeToFile:logPath atomically:YES
        encoding:NSUTF8StringEncoding error:nil];
}

char *comm_receive(void) {
    NSString *content = [NSString stringWithContentsOfFile:@CMD_FILE
        encoding:NSUTF8StringEncoding error:nil];
    
    if (content && content.length > 0) {
        strncpy(cmd_buffer, content.UTF8String, MAX_CMD_LEN - 1);
        cmd_buffer[MAX_CMD_LEN - 1] = '\0';
        return cmd_buffer;
    }
    return NULL;
}

void comm_clear_cmd(void) {
    [@"" writeToFile:@CMD_FILE atomically:YES
        encoding:NSUTF8StringEncoding error:nil];
}
