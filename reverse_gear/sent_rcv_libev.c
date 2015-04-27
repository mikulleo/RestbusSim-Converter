#include <ev.h>
#include "socketCan.h"
#include "socketCan.c"

ev_idle idle;                  // processing watcher
ev_io can_io;                  // I/O watcher   
ev_timer timer;				   // timer
 
struct ev_loop *loop;  
int s;

void delay(int milliseconds)
{
    long pause;
    clock_t now,then;

    pause = milliseconds*(CLOCKS_PER_SEC/1000);
    now = then = clock();
    while( (now-then) < pause )
        now = clock();
}

static void recvmsg_cb(EV_P_ ev_io *w, int revents)  // (revents, ...) parameters as in CAPL must be placed
{
  char *msg_name;

	printf("Receive callback ready\n");
	
	int *rcvData = read_port(s);
	printf("rcvData[2] = %#010x\n",rcvData[2]);
	if(rcvData) {
		free(rcvData);
	}
	//printf("ID: %#010x\n",rcv_id);

	if(rcvData[2] == 0x90) { printf("Reverse set in progress\n");	}
	else { printf("Reverse done\n"); };
		 
	// stop the I/O watcher, we received the event, but
	// are not yet ready to handle it.
	ev_io_stop(EV_A_ w);             // received event ---> stop the I/O watcher
}

static void sentmsg_cb(EV_P_ ev_timer *w, int revents)
{
	struct can_frame sentFrame;
	sentFrame.can_id = 0x000003DB;
	sentFrame.can_dlc = 8;
	// zpatecka 50800002460001A7
	sentFrame.data[0] = 0x50;
	sentFrame.data[1] = 0x80;
	sentFrame.data[2] = 0x00;
	sentFrame.data[3] = 0x02;
	sentFrame.data[4] = 0x46;
	sentFrame.data[5] = 0x00;
	sentFrame.data[6] = 0x01;
	sentFrame.data[7] = 0xA7;
  
	int sentbytes = send_frame(s,&sentFrame);
	printf("Message sent, bytes:%d\n",sentbytes);
			
	ev_timer_stop(loop, &timer);	// stop the timer
	ev_timer_set(&timer, 5, 0.);	// reset the timer
	ev_timer_start(loop, &timer);	// start the timer again
	
	delay(1000);					// delay the time
    ev_io_init(&can_io,recvmsg_cb,s,EV_READ);
    ev_io_start(loop,&can_io);
}

void reverse_set()
{
	ev_timer_init(&timer,sentmsg_cb,2,0);
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
