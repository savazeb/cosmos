#include <mqueue.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/select.h>
#include <termios.h>
#include <stropts.h>
#include <cstdio>


#define QNAME "/motorPowerQueue"

#define MAX_POWER 100
#define MIN_POWER -100

int clamp(int val){
    if (val > MAX_POWER)
         return MAX_POWER;
    else if (val < MIN_POWER)
        return MIN_POWER;
    return val;
}

int _kbhit() {
    static bool initialized = false;

    if (! initialized) {
            // Use termios to turn off line buffering
            struct termios term;
            tcgetattr(STDIN_FILENO, &term);
            term.c_lflag &= ~ICANON;
            tcsetattr(STDIN_FILENO, TCSANOW, &term);
            setbuf(stdin, NULL);
            initialized = true;
    }

    int bytesWaiting;
    ioctl(STDIN_FILENO, FIONREAD, &bytesWaiting);
    return bytesWaiting;
}


int main(){
	int x_power = 0, y_power = 0, turn_power = 0;
	int ret;
	char str[100];
	char *buff;
	mqd_t q;

	struct mq_attr attr;
	attr.mq_flags = 0;
	attr.mq_maxmsg = 10;
	attr.mq_msgsize = 1024;
	attr.mq_curmsgs = 0;

	mode_t omask;
	omask = umask(0);
	q = mq_open(QNAME, (O_WRONLY | O_CREAT), 0777, &attr);
	umask(omask);

	if ( q == -1 ){
		printf("[ERROR]%d: %s\n", errno, strerror(errno));
		return 1;
	}
	while(1){
        
        while(_kbhit()){
            switch(getc(stdin)){
                case 'w':y_power+=10;break;
                case 's':y_power-=10;break;
                case 'd':x_power+=10;break;
                case 'a':x_power-=10;break;
                case 'l':turn_power+=10;break;
                case 'j':turn_power-=10;break;
            }

            /* pass clamp function */
            y_power = clamp(y_power);
            x_power = clamp(x_power);
            turn_power = clamp(turn_power);

            sprintf(str ,"%d,%d,%d", x_power, y_power, turn_power);
            buff = (char *)calloc(strlen(str) + 1, sizeof(char));
            strcpy( buff, str );
            printf("%s\n", buff);

            ret = mq_send( q, buff , strlen(buff) , 0);
            if ( ret == -1	) {
                printf("[ERROR]%d: %s\n", errno, strerror(errno));
                return 1;
            }
            free(buff);
        }
        sleep(1);
	}
}