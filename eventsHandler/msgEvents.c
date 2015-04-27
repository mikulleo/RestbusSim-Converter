#include <ev.h>
#include "socketCan.h"
#include "socketCan.c"

ev_idle idle;                  // processing watcher
ev_io can_io;                  // I/O watcher   
ev_timer timer;				   // timer
 
struct ev_loop *loop;  
int s;

/* IDs from relevant DB of messages */
//  CTRL_LED = 497;
//  CTRL_Buttons = 499;
//  CTRL_NumPad = 501;
//  ECU_info = 1220;


const char * convert_hexToID(int hexID)
{
  const char *msg_name;
  switch(hexID) {
    case 0x273H: msg_name = "CTRL_LED"; return msg_name;
    case 0x1F3H: msg_name = "CTRL_Buttons"; return msg_name;
    case 0x1F1H: msg_name = "CTRL_NumPad"; return msg_name;
    case 0x4C4H: msg_name = "ECU_info"; return msg_name;
    default: msg_name = "undefined"; return msg_name;   
  }
}

static void recvmsg_cb(EV_P_ ev_io *w, int revents)  // (revents, ...) parameters as in CAPL must be placed
{
  char *msg_name;

	printf("Receive callback ready\n");
	
	int rcv_id = read_port(s);
	printf("ID: %#010x\n",rcv_id);
  
  msg_name = convert_hexToID(rcv_id);
  
/* Events */
switch(msg_name) {
case CTRL_Buttons: CTRL_Buttons_event(); break;
}
case CTRL_LED: CTRL_LED_event(); break;
}
/* inserted before here */

	if(rcvData[2] == 0x90) { printf("Reverse set in progress\n");	}
	else { printf("Reverse done\n"); };
		 
	// stop the I/O watcher, we received the event, but
	// are not yet ready to handle it.
	ev_io_stop(EV_A_ w);             // received event ---> stop the I/O watcher
}

static void timer_cb(EV_P_ ev_timer *w, int revents)
{
		
	ev_timer_stop(loop, &timer);	// stop the timer
	ev_timer_set(&timer, 5, 0.);	// reset the timer
	ev_timer_start(loop, &timer);	// start the timer again
	
	delay(1000);					// delay the time
    ev_io_init(&can_io,recvmsg_cb,s,EV_READ);
    ev_io_start(loop,&can_io);
}

void reverse_set()
{
	ev_timer_init(&timer,timer_cb,2,0);
    ev_timer_start(loop,&timer);    
}

int start_watcher() 
{
    //struct ev_loop *loop;
    loop = EV_DEFAULT;
    
    s = open_port("can0");
    printf("port: %d\n",s);
    
    reverse_set();
    
    ev_run(loop, 0);
   
	return 0;
}