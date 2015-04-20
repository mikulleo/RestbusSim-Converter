#include <ev.h>
#include "socketCan.h"

ev_idle idle;                  // processing watcher
ev_io io;                      // I/O watcher                     

static void idle_cb(EV_P_ ev_idle *ev, int revents)
{
  int msg_id;  
    
  // read port for messages
  // actual processing
  msg_id = (int)read_port(soc);
  
  switch (msg_id) {       // better - relevant message name 
    case 0x101:           // better - e.g. msg_1
       // event_101(parameters)
       event_101();    
    case 0x102:           // better - e.g. msg_2
       // event_102(parameters)
        event_102();
    default:
      printf("Procedure for the message not found.\n");
  }
  
  // have to start the I/O watcher again, as
  // we have handled the event 
  ev_io_start(&io);     
}

static void msg_event_cb(EV_P_ ev_io *w, int revents, ...)  // parameters as in CAPL must be placed
{
  // stop the I/O watcher, we received the event, but
  // are not yet ready to handle it.
  ev_io_stop(EV_A_ ev);             // received event ---> stop the I/O watcher
  
  // start the idle watcher to handle the actual event
  // it will not be exectued as long as other watchers with default prioriry are receiving events
  ev_idle_start(EV_A_ &idle);
}

// void event_101(parameters)
void event_101()
{
  /*
      relevant CAPL code here
  */
}

// void event_101(parameters)
void event_102()
{
  /*
      relevant CAPL code here
  */
}

int main(int argc, char** argv) {
    open_port("can0");
    
    ev_idle_init(&idle, idle_cb);  // init processing watcher

    // io_events; register message events with specific procedures
    ev_io_init(&io,msg_event_cb,STDIN_FILENO,EV_READ);
    ev_io_start(&io);

}
