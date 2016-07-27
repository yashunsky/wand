GCC := gcc
PYTHON := env python2

OSFLAG 				:=
CCFLAG              :=

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	OSFLAG += -D LINUX
	CCFLAG += -shared -fpic
endif
ifeq ($(UNAME_S),Darwin)
	OSFLAG += -D OSX
	CCFLAG += -dynamiclib
endif

UNAME_P := $(shell uname -p)
ifeq ($(UNAME_P),x86_64)
	OSFLAG += -D AMD64
endif
	ifneq ($(filter %86,$(UNAME_P)),)
OSFLAG += -D IA32
	endif
ifneq ($(filter arm%,$(UNAME_P)),)
	OSFLAG += -D ARM
endif

INCLUDES := -I/usr/local/include/python2.7/ -I/usr/include/python2.7/ -lpython2.7

migration_to_c/c_wrap_imu.so:
	$(GCC) $(OSFLAG) $(CCFLAG) $(INCLUDES) src_c/wrap_imu.c -o $@

all: migration_to_c/c_wrap_imu.so

test: all
	$(PYTHON) migration_to_c/test_imu.py

clean:
	rm migration_to_c/c_wrap_imu.so
