#include <iostream>
#include <pigpio.h>
#include <chrono>
#include <thread> // Include the thread header for sleep_for

// Use the std::chrono library for time measurements
using namespace std::chrono;

// Define a debounce time in milliseconds
const int debounceTimeMs = 100; // Adjust this value as needed

// Keep track of the last interrupt time
steady_clock::time_point lastInterruptTime = steady_clock::now();

// Interrupt callback function
void interrupt_callback(int gpio, int level, uint32_t tick) {
    // Get the current time
    auto now = steady_clock::now();

    // Calculate the time elapsed since the last interrupt
    auto durationSinceLastInterrupt = duration_cast<milliseconds>(now - lastInterruptTime);

    // Only accept the interrupt if enough time (the debounce time) has passed
    if (durationSinceLastInterrupt.count() > debounceTimeMs) {
        // Update the last interrupt time
        lastInterruptTime = now;

        // Wait for 100 ms before reading the GPIO state
        std::this_thread::sleep_for(milliseconds(100));

        // Read the current level of the GPIO pin
        int currentLevel = gpioRead(gpio);

        // gpio - GPIO pin number
        // currentLevel - The current level read from the GPIO pin
        // tick - The number of microseconds since boot
        std::cout << "Debounced interrupt detected on GPIO" << gpio << ". Level: " << currentLevel << " at tick: " << tick << std::endl;
    }
}

int main() {
    // Initialize pigpio
    if (gpioInitialise() < 0) {
        std::cerr << "Failed to initialize pigpio." << std::endl;
        return 1;
    }

    // GPIO pin number (BCM numbering)
    const int inputPin = 21;

    // Set the pin as an input
    gpioSetMode(inputPin, PI_INPUT);

    // Set a pull-up resistor on the pin
    gpioSetPullUpDown(inputPin, PI_PUD_UP);

    // Set up the interrupt callback for both rising and falling edge detection
    if (gpioSetISRFunc(inputPin, EITHER_EDGE, 0, interrupt_callback) < 0) {
        std::cerr << "Failed to set up ISR function." << std::endl;
        gpioTerminate();
        return 1;
    }

    // Main loop
    while (true) {
        // Your main program logic here
        // The interrupt callback will be called independently when the interrupt occurs

        // Sleep for a while to reduce CPU usage (optional)
        time_sleep(1.0);
    }

    // Cleanup and stop pigpio
    gpioTerminate();

    return 0;
}