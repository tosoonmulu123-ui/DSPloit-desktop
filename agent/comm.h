/**
 * DSPloit Agent — Communication with PC.
 * File-based protocol via AFC.
 */

#ifndef DSPLOIT_COMM_H
#define DSPLOIT_COMM_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define CMD_FILE    "/var/tmp/.dsploit_cmd"
#define RESULT_FILE "/var/tmp/.dsploit_result"
#define LOG_FILE    "/var/tmp/.dsploit_log"
#define MAX_CMD_LEN 4096
#define MAX_RESULT_LEN 8192

// Initialize communication
int comm_init(void);

// Send result back to PC
void comm_send(const char *fmt, ...);

// Send log message to PC
void comm_log(const char *fmt, ...);

// Receive command from PC (blocks until command available)
char *comm_receive(void);

// Clear command file after processing
void comm_clear_cmd(void);

#endif /* DSPLOIT_COMM_H */
