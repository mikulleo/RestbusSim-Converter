#include "socketCan.h" 

int s;
struct sockaddr_can addr;
struct ifreq ifr;

int open_port(const char *portName)
{
  if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) 
  {
		perror("Error when creating a socket");
		return(1);
	}
  
  strcpy(ifr.ifr_name,portName);
  fcntl(s, F_SETFL, O_NONBLOCK);
  
  if (ioctl(s, SIOCGIFINDEX, &ifr) == -1) 
  {
    perror(portName);
		return(1);
	}
  
  addr.can_family = AF_CAN;
  addr.can_ifindex = ifr.ifr_ifindex;
  
  if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) 
  {
		perror("Bind error");
		return(1);
	}

  return s;
}

int * read_port(int soc)
{
  struct can_frame frame;
  ssize_t recvbytes;
    
  recvbytes = read(soc, &frame, sizeof(struct can_frame));
  
  if (recvbytes < 0) 
  {
    perror("Error during reading socket");
    exit(1);
  }

    if (recvbytes < sizeof(struct can_frame)) 
    {
      fprintf(stderr, "Error: incomplete CAN frame\n");
      exit(1);
    }
    
   //printf("rcv: %#010x\n",frame.data[7]);
   int *returnData = malloc(8);
   int i;
   for (i = 0; i < sizeof(8); i++) {
		returnData[i] = frame.data[i];
   }
   return returnData; 
}

int send_frame(int soc, const struct can_frame *frame)
{
  ssize_t sentbytes;  
  
  sentbytes = write(soc, frame, sizeof(struct can_frame));
  if (sentbytes < 0)
  {
    perror("Error when sending a frame");
    return(1);
  }
  printf("sent: %#010x\n",frame->data[6]);
  return sentbytes;  
}
