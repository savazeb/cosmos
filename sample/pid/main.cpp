#include <iostream>
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
#include <unistd.h>
#include <sys/time.h>
#include <ctime>

#define QNAME "/keyQueue"

#define MAX_POWER 100
#define MIN_POWER 0
#define MAX_K 100
#define MIN_K 0

template <typename VAL>
VAL clamp(VAL val, VAL max, VAL min){
    if (val > max)
         return max;
    else if (val < min)
        return min;
    return val;
}

void display(int start, int min_power, int max_power, float kp, float ki, float kd){
    system("clear");
    char key_map[7][41] = {"----------------------------------------",
                           "                 [KEY]                  ",
                           "----------------------------------------",
                           "  start : h  pause : g                  ",
                           "        pmin:   pmax:   kp:   ki:    kd:",
                           "  {+}   e       d       o     l      .  ",
                           "  {-}   w       s       i     k      ,  "};

    for (uint8_t col = 0; col < 7; col++){
        for (uint8_t row =  0; row < 41; row++)
        {
            std::cout << key_map[col][row];
        }
        std::cout << "\n";
    }
    std::cout << "----------------------------------------\n";
    std::cout << "start : " << start << "\n";
    std::cout << "pmin  : " << min_power << "\n";
    std::cout << "pmax  : " << max_power << "\n";
    std::cout << "kp    : " << kp << "\n";
    std::cout << "ki    : " << ki << "\n";
    std::cout << "kd    : " << kd << "\n";
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
	float kp = 1, ki = 0, kd = 0;
    int min_power = 20, max_power = 40;
    int start = 0;
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
    struct timeval t_start, t_end;
    int dt = 10;
    int show = 1;
    gettimeofday(&t_start, 0);
	while(1){
        while(_kbhit()){
            switch(getc(stdin)){
                /* start key */
                case 'h':start = 1;break;
                case 'g':start = 0;break;
                /* power key */
                case 'e':min_power+=1;break;
                case 'w':min_power-=1;break;
                case 'd':max_power+=1;break;
                case 's':max_power-=1;break;
                /* pid key */ 
                case 'o':kp+=0.01;break;
                case 'i':kp-=0.01;break;
                case 'l':ki+=0.01;break;
                case 'k':ki-=0.01;break;
                case '.':kd+=0.01;break;
                case ',':kd-=0.01;break;
            }

            /* pass clamp function */
            max_power = clamp<int>(max_power, MAX_POWER, MIN_POWER);
            min_power = clamp<int>(min_power, MAX_POWER, MIN_POWER);
            
            kp = clamp<float>(kp, MAX_K, MIN_K);
            ki = clamp<float>(ki, MAX_K, MIN_K);
            kd = clamp<float>(kd, MAX_K, MIN_K);

            sprintf(str ,"%d,%d,%d,%.2f,%.2f,%.2f", start, min_power, max_power, kp, ki ,kd);
            buff = (char *)calloc(strlen(str) + 1, sizeof(char));
            strcpy( buff, str );

            ret = mq_send( q, buff , strlen(buff) , 0);
            if ( ret == -1	) {
                printf("[ERROR]%d: %s\n", errno, strerror(errno));
                return 1;
            }
            free(buff);
            gettimeofday(&t_start, 0);
            if(!show)
                show = !show;  
        }
        if (show){
            display(start, min_power, max_power, kp, ki ,kd);
            show = !show;
        }
        sleep(0.005);
	}
}
