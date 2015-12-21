gcc -dynamiclib -I/usr/include/python2.7/ -lpython2.7 c/imu.c c/MadgwickAHRS/MadgwickAHRS.c c/MadgwickAHRS/MadgwickAHRS.h
mv a.out python/imu.so
