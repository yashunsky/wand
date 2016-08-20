gcc -x c++ -dynamiclib -I/usr/local/include/python2.7/ -lpython2.7 src_c/*.cpp src_c/*.h src_c/extern_sm/*.c src_c/extern_sm/*.h
mv a.out migration_to_c/c_wrap.so
