gcc -x c++ -dynamiclib -I/usr/local/include/python2.7/ -lpython2.7 src_c/*.cpp src_c/*.h
mv a.out migration_to_c/c_wrap.so
