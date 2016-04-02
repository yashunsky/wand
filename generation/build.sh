gcc -dynamiclib -I/usr/local/include/python2.7/ -lpython2.7 src_c/*.c src_c/*.h
mv a.out migration_to_c/c_wrap.so
