# Define the compiler and the linker. The linker is usually the same as the compiler but doesn't have to be
CXX := g++
LD := $(CXX)

# Define the directories
SRCDIR := src
BINDIR := bin
INCDIR := include
CPPZMQ_INCDIR := 3rdparty/cppzmq # Path to cppzmq includes

# Compiler flags. -I is to include the header file directories.
CXXFLAGS := -Wall -Iinclude -I$(CPPZMQ_INCDIR) -std=c++11 $(shell GraphicsMagick++-config --cxxflags --cppflags)

# Linker flags. You'll need to link your executable with required libraries.
# Added -lzmq to link against ZeroMQ
LDFLAGS := -lrt -lm -lpthread -lzmq $(shell GraphicsMagick++-config --ldflags --libs)

# Additional flags for the RGB Matrix library, replace with your path
RGB_INCDIR := 3rdparty/rpi-rgb-led-matrix/include
RGB_LIBDIR := 3rdparty/rpi-rgb-led-matrix/lib
RGB_LIBRARY_NAME := rgbmatrix
RGB_LDFLAGS := -L$(RGB_LIBDIR) -l$(RGB_LIBRARY_NAME)

# Path to the rpi-rgb-led-matrix library Makefile
RGB_MATRIX_LIB_MAKEFILE := $(RGB_LIBDIR)/Makefile

# Source files
SRCS := $(SRCDIR)/main.cpp

# Object files
OBJS := $(SRCS:.cpp=.o)

# Target executable name
TARGET := $(BINDIR)/image-display

# Target for the rpi-rgb-led-matrix library
RGB_MATRIX_LIB_TARGET := $(RGB_LIBDIR)/lib$(RGB_LIBRARY_NAME).a

# Default 'all' target
all: $(TARGET)

# Build the rpi-rgb-led-matrix library first
$(RGB_MATRIX_LIB_TARGET): $(RGB_MATRIX_LIB_MAKEFILE)
	$(MAKE) -C $(dir $(RGB_MATRIX_LIB_MAKEFILE))

# Link the target binary
$(TARGET): $(OBJS) $(RGB_MATRIX_LIB_TARGET)
	mkdir -p $(BINDIR)
	$(LD) $(OBJS) -o $@ $(LDFLAGS) $(RGB_LDFLAGS)

# Compile the source files into object files
$(SRCDIR)/%.o: $(SRCDIR)/%.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) -I$(RGB_INCDIR) -I$(INCDIR)

# 'clean' target to remove build artifacts
clean:
	rm -f $(OBJS)
	rm -f $(TARGET)
	$(MAKE) -C $(RGB_LIBDIR) clean