#********************************************************************************
#@class makefile
#@brief
#
#$Source: makefile $
#$Date: 2016/11/24 15:57:57CET $
#$Revision: 1.1 $
#@author Robert Erhart, ett2si (13.02.2008)
#@author Xenolation framework is part of CLARA
#@author (c) Copyright Robert Bosch GmbH 2008 All rights reserved.
#********************************************************************************
#@remark
#- abspath in make 3.80 nicht unterstützt
#- switch to make 3.81
#********************************************************************************
#@todo
#- search automatical srcfiles in ./simulation/CAN1 => makefile is normaly project independent
#********************************************************************************

# chosse shell
SHELL = /bin/sh

# delete suffix
.SUFFIXES:

# choose compiler
#CXX := g++

# where to install
BUILDDIR := ./builddir
BUILDNAME := heapsort

# where are include files kept
INCLUDE := -I/usr/claraNG_DE/claraSim/framework/unit_test

# which libs are used
#LIBS := -lpthread -lrtdm -lnative -lfcBase
#LIBSDIR := -L/usr/xenomai/lib

# compiler options for development (-xc++) -Wextra
CFLAGS = -O0 -g3 -Wall -c -fmessage-length=0

# compiler options for release
#CFLAGS = -O3 -Wall -c -fmessage-length=0

# claraHIL opjects
SRC = \
./test_heapsort.cpp \


OBJ = $(addprefix $(BUILDDIR)/_prj/,$(SRC:.cpp=.o) )

#.cpp.o:
#	$(CXX) $(INCLUDE) $(CFLAGS) -MMD -MP  -MT"$(@)" -MT"$(@:%.o=%.d)" -o"$(@)" "$(addprefix ../../, $(@D)/$(<F))"	
#   $(CXX) $(INCLUDE) $(CFLAGS) -MMD -MP -MF"$(BUILDDIR)/$(@F:%.o=%.d)" -MT"$(BUILDDIR)/$(@F:%.o=%.d)" -o"$(BUILDDIR)/$(@F)" "$(@D)/$(<F)"	

$(BUILDDIR)/_prj/%.o: %.cpp
	$(CXX) $(INCLUDE) $(CFLAGS) -MMD -MP  -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$(@)" "$(subst builddir/_prj/,,$(@D)/$(<F))"

-include $(OBJ:.o=.d)

.PHONY: all
all: createDir claraHil

.PHONY: createDir
createDir:
	@mkdir -p $(dir $(OBJ))

.PHONY: claraHil
claraHil: $(OBJ)
	@echo ' '
	@echo 'Building target: $(BUILDNAME)'
	@echo 'Invoking: GCC C++ Linker'
	$(CXX) $(LIBSDIR) -o $(BUILDNAME) $(LIBS) $(OBJ)
	@echo '***************************************'
	@echo 'Finished building target: $(BUILDNAME)'
	@echo '***************************************'

.PHONY: clean	
clean:
	@echo '***************************************'
	@echo 'Clean: $(BUILDDIR) $(BUILDNAME)'
	rm -rf  $(BUILDDIR)
	rm -f $(BUILDNAME)
	@echo '- Finished -'
	@echo '***************************************'	

.SECONDARY:

