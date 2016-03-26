gcc -dynamiclib -I/usr/local/include/python2.7/ -lpython2.7 src/*.c src/*.h
mv a.out c_wrap.so
