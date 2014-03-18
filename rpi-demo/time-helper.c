#include <sys/time.h>
long time_diff(struct timeval t0, struct timeval t1)
{
    t1.tv_sec -= t0.tv_sec;
    t0.tv_sec = 0;

    int t = (t1.tv_sec * 1000000UL + t1.tv_usec) - t0.tv_usec;
    return t;
}
