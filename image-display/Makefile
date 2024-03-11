# Define the compiler and the linker. The linker is usually the same as the compiler but doesn't have to be
CXX := g++
LD := $(CXX)

# Define the directories
SRCDIR := src
BINDIR := bin
INCDIR := include
CPPZMQ_INCDIR := 3rdparty/cppzmq # Path to cppzmq includes

# Compiler flags. -I is to include the header file directories.
CXXFLAGS := -Wall -I$(INCDIR) -I$(CPPZMQ_INCDIR) -std=c++11 $(shell GraphicsMagick++-config --cxxflags --cppflags) -I/usr/local/include

# Linker flags. You'll need to link your executable with required libraries.
# Added -lzmq to link against ZeroMQ
LDFLAGS := -lrt -lm -lpthread -lzmq $(shell GraphicsMagick++-config --ldflags --libs)

# Linker flags for gpio-test, assuming pigpio is installed in standard lib directories
LDFLAGS_GPIO_TEST := -lrt -lm -lpthread -lpigpio

# Additional flags for the RGB Matrix library, replace with your path
RGB_INCDIR := 3rdparty/rpi-rgb-led-matrix/include
RGB_LIBDIR := 3rdparty/rpi-rgb-led-matrix/lib
RGB_LIBRARY_NAME := rgbmatrix
RGB_LDFLAGS := -L$(RGB_LIBDIR) -l$(RGB_LIBRARY_NAME)

# Path to the rpi-rgb-led-matrix library Makefile
RGB_MATRIX_LIB_MAKEFILE := $(RGB_LIBDIR)/Makefile

# Source files for image-display
SRCS_IMAGE_DISPLAY := $(SRCDIR)/main.cpp

# Source files for gpio-test
SRCS_GPIO_TEST := $(SRCDIR)/gpio_test.cpp

# Object files for image-display
OBJS_IMAGE_DISPLAY := $(SRCS_IMAGE_DISPLAY:.cpp=.o)

# Object files for gpio-test
OBJS_GPIO_TEST := $(SRCS_GPIO_TEST:.cpp=.o)

# Target executable names
TARGET_IMAGE_DISPLAY := $(BINDIR)/image-display
TARGET_GPIO_TEST := $(BINDIR)/gpio-test

# Target for the rpi-rgb-led-matrix library
RGB_MATRIX_LIB_TARGET := $(RGB_LIBDIR)/lib$(RGB_LIBRARY_NAME).a

# Default 'all' target
all: $(TARGET_IMAGE_DISPLAY) $(TARGET_GPIO_TEST)

# Build the rpi-rgb-led-matrix library first
$(RGB_MATRIX_LIB_TARGET): $(RGB_MATRIX_LIB_MAKEFILE)
	$(MAKE) -C $(dir $(RGB_MATRIX_LIB_MAKEFILE))

# Link the image-display binary
$(TARGET_IMAGE_DISPLAY): $(OBJS_IMAGE_DISPLAY) $(RGB_MATRIX_LIB_TARGET)
	mkdir -p $(BINDIR)
	$(LD) $(OBJS_IMAGE_DISPLAY) -o $@ $(LDFLAGS) $(RGB_LDFLAGS)

# Link the gpio-test binary
$(TARGET_GPIO_TEST): $(OBJS_GPIO_TEST)
	mkdir -p $(BINDIR)
	$(LD) $(OBJS_GPIO_TEST) -o $@ $(LDFLAGS_GPIO_TEST)

# Compile the source files into object files
$(SRCDIR)/%.o: $(SRCDIR)/%.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) -I$(RGB_INCDIR)

# 'clean' target to remove build artifacts
clean:
	rm -f $(OBJS_IMAGE_DISPLAY) $(OBJS_GPIO_TEST)
	rm -f $(TARGET_IMAGE_DISPLAY) $(TARGET_GPIO_TEST)
	$(MAKE) -C $(RGB_LIBDIR) clean