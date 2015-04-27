#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <time.h>

int soc;

extern int open_port(const char *portName);
extern int send_frame(int soc, const struct can_frame *frame);
canid_t read_port(int soc);





