int soc;

int open_port(const char *portName);
int send_frame(int soc, struct can_frame *frame);
canid_t read_port(int soc);



