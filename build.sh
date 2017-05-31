rm -r output
./src_py/export_sources.py $1 python
gcc -x c++ -dynamiclib -I/usr/local/include/python2.7/ -lpython2.7 output/*.cpp output/*.c output/*.h
mv a.out src_py/c_wrap.so
rm -r output
./src_py/export_sources.py $1 fw
