#include "socketCan.h" 





  if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) 



  
  
  
	    perror(portName);
	   return(1);
	}

  
  


	}








    perror("Error during reading socket");


  if (recvbytes < sizeof(struct can_frame)) 
      fprintf(stderr, "Error: incomplete CAN frame\n");

   }

   return frame.can_id;


int send_frame(int soc, const struct can_frame *frame)



    perror("Error when sending a frame");


  printf("sent: %#010x\n",frame->data[6]);
  return sentbytes;
