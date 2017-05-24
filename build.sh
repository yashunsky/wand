cd src_c/extern_sm/
mv main.c tmp
mv *desktop* tmp
mv bsp.h tmp
cp python/* .
cd ../../
gcc -x c++ -dynamiclib -I/usr/local/include/python2.7/ -lpython2.7 src_c/*.cpp src_c/*.h src_c/extern_sm/*.c src_c/extern_sm/*.h
mv src_c/extern_sm/tmp/* src_c/extern_sm/
rm src_c/extern_sm/*python*.*
mv a.out src_py/c_wrap.so
cp src_py/c_wrap.so migration_to_c/c_wrap.so
