#include <pigpio.h>
#include "led-matrix.h"
#include "spdlog/spdlog.h"
#include "spdlog/sinks/stdout_color_sinks.h"

#include <math.h>
#include <signal.h>
#include <unistd.h>
#include <exception>
#include <Magick++.h>
#include <zmq.hpp>
#include <chrono>
#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <cmath>
#include <thread>


using namespace rgb_matrix;
using namespace std::chrono;


// Global variables for managing the ZeroMQ connection
std::string current_address = "";
std::string new_address = "";
std::string default_address = "tcp://jumbotron:5555";
zmq::context_t context(1);
zmq::socket_t subscriber(context, ZMQ_SUB);
bool connection_changed = false;
bool initial_connection_made = false;

// Define the GPIO pin number
const int inputPin = 21;

// Define a debounce time in milliseconds
const int debounceTimeMs = 20;

// Keep track of the last interrupt time
steady_clock::time_point lastInterruptTime = steady_clock::now();

// Interrupt callback function
void interrupt_callback(int gpio, int level, uint32_t tick) {
    auto now = steady_clock::now();
    auto durationSinceLastInterrupt = duration_cast<milliseconds>(now - lastInterruptTime);

    if (durationSinceLastInterrupt.count() > debounceTimeMs) {
        lastInterruptTime = now;
        std::this_thread::sleep_for(milliseconds(10)); // Debounce delay
        int currentLevel = gpioRead(gpio);

        // Determine the new address based on the input level
        new_address = (currentLevel == 1) ? "tcp://jumbotron:5555" : "tcp://localhost:5555";

        // Check if the address has changed
        if (current_address != new_address) {
            connection_changed = true; // Set flag to handle connection change in the main loop
        }
    }
}

// // Interrupt callback function
// void interrupt_callback(int gpio, int level, uint32_t tick) {
//     // Get the current time
//     auto now = steady_clock::now();

//     // Calculate the time elapsed since the last interrupt
//     auto durationSinceLastInterrupt = duration_cast<milliseconds>(now - lastInterruptTime);

//     // Only accept the interrupt if enough time (the debounce time) has passed
//     if (durationSinceLastInterrupt.count() > debounceTimeMs) {
//         // Update the last interrupt time
//         lastInterruptTime = now;

//         // Wait for 100 ms before reading the GPIO state
//         std::this_thread::sleep_for(milliseconds(10));

//         // Read the current level of the GPIO pin
//         int currentLevel = gpioRead(gpio);

//         // gpio - GPIO pin number
//         // currentLevel - The current level read from the GPIO pin
//         // tick - The number of microseconds since boot
//         std::cout << "Debounced interrupt detected on GPIO" << gpio << ". Level: " << currentLevel << " at tick: " << tick << std::endl;
//     }
// }

void InitializeDigitalInput() {
    if (gpioInitialise() < 0) {
        throw std::runtime_error("Failed to initialize pigpio.");
    }

    gpioSetMode(inputPin, PI_INPUT);
    gpioSetPullUpDown(inputPin, PI_PUD_UP);

    if (gpioSetISRFunc(inputPin, EITHER_EDGE, 0, interrupt_callback) < 0) {
        gpioTerminate();
        throw std::runtime_error("Failed to set up ISR function.");
    }
}

void ConnectToZmq(const std::string &address) {
    try {
        // Disconnect from current address if connected
        if (!current_address.empty()) {
            std::cout << "Disconnecting from " << current_address << std::endl;
            subscriber.disconnect(current_address);
            std::cout << "Disconnected from " << current_address << std::endl;
        }

        // Connect to the new address
        std::cout << "Connecting to " << address << std::endl;
        subscriber.connect(address);
        std::cout << "Connected to " << address << std::endl;

        // Subscribe to the topic
        subscriber.setsockopt(ZMQ_SUBSCRIBE, "/frames", 7);
        std::cout << "Subscribed to /frames" << std::endl;

        // Update current address
        current_address = address;
    } catch (const zmq::error_t &e) {
        std::cerr << "ZMQ Exception: " << e.what() << " (" << zmq_strerror(e.num()) << ")" << std::endl;
    } catch (const std::exception &e) {
        std::cerr << "Standard Exception: " << e.what() << std::endl;
    } catch (...) {
        std::cerr << "Unknown Exception occurred during ZMQ connection." << std::endl;
    }
}

volatile bool interrupt_received = false;
static void InterruptHandler(int signo) {
    interrupt_received = true;
}

void CopyImageToCanvas(const Magick::Image &image, Canvas *canvas)
{
    const int offset_x = 0, offset_y = 0; // If you want to move the image.
    // Copy all the pixels to the canvas.
    for (size_t y = 0; y < image.rows(); ++y)
    {
        for (size_t x = 0; x < image.columns(); ++x)
        {
            const Magick::Color &c = image.pixelColor(x, y);
            if (c.alphaQuantum() < 256)
            {
                canvas->SetPixel(x + offset_x, y + offset_y,
                                 ScaleQuantumToChar(c.redQuantum()),
                                 ScaleQuantumToChar(c.greenQuantum()),
                                 ScaleQuantumToChar(c.blueQuantum()));
            }
        }
    }
}

//Function to compute mean and standard deviation
void ComputeStatistics(const std::vector<double> &fps_values) {
    if (fps_values.empty()) {
        std::cout << "No data to compute statistics." << std::endl;
        return;
    }

    double min_fps = *std::min_element(fps_values.begin(), fps_values.end());
    double max_fps = *std::max_element(fps_values.begin(), fps_values.end());
    double sum_fps = std::accumulate(fps_values.begin(), fps_values.end(), 0.0);
    double mean_fps = sum_fps / fps_values.size();

    double accum = 0.0;
    std::for_each(fps_values.begin(), fps_values.end(), [&](const double fps) {
        accum += (fps - mean_fps) * (fps - mean_fps);
    });
    double stddev_fps = std::sqrt(accum / (fps_values.size() - 1));

    std::cout << "FPS Statistics:" << std::endl;
    std::cout << "Min FPS: " << min_fps << std::endl;
    std::cout << "Max FPS: " << max_fps << std::endl;
    std::cout << "Mean FPS: " << mean_fps << std::endl;
    std::cout << "StdDev FPS: " << stddev_fps << std::endl;
}

int main(int argc, char *argv[]) {
    spdlog::set_level(spdlog::level::debug);
    spdlog::set_pattern("[%Y-%m-%d %H:%M:%S] [%l] %v");

    auto console = spdlog::stdout_color_mt("console");
    
    console->info("Welcome to spdlog!");
    console->error("An error occurred");
    console->warn("This is a warning");
    console->debug("This is a debug message");

    return 0;

    InitializeDigitalInput(); // Initialize the digital input for interrupts
    Magick::InitializeMagick(*argv);
    RGBMatrix::Options matrix_options;
    RuntimeOptions runtime_opt;

    if (!ParseOptionsFromFlags(&argc, &argv, &matrix_options, &runtime_opt)) {
        // Handle parsing error...
        return 1;
    }

    signal(SIGTERM, InterruptHandler);
    signal(SIGINT, InterruptHandler);

    std::unique_ptr<RGBMatrix> matrix(RGBMatrix::CreateFromOptions(matrix_options, runtime_opt));
    if (matrix == nullptr) {
        // Handle error...
        return 1;
    }

    // while (!interrupt_received) {
    //     // Your main program logic here
    //     // The interrupt callback will be called independently when the interrupt occurs

    //     // Sleep for a while to reduce CPU usage (optional)
    //     time_sleep(1.0);
    // }

    ConnectToZmq(default_address); // Connect to the initial address

    FrameCanvas *offscreen_canvas = matrix->CreateFrameCanvas();
    auto last_update_time = std::chrono::steady_clock::now();

    std::vector<double> fps_values; // Vector to hold FPS values

    while (!interrupt_received) {
        auto start_time = std::chrono::steady_clock::now();

        // Receive message
        zmq::message_t update;
        try {
            subscriber.recv(&update);
        } catch (const zmq::error_t& e) {
            if (e.num() == EINTR) {
                // Interrupted system call - likely due to the signal
                break; // Exit the loop
            } else {
                // Handle other errors that might occur
                std::cerr << "ZeroMQ error: " << e.what() << std::endl;
                break; // Or decide if you want to continue or exit the loop
            }
        }
        auto received_time = std::chrono::steady_clock::now();

        // Extract image data from message (assuming the first part is the channel)
        std::string image_data(static_cast<char*>(update.data()) + 7, update.size() - 7);

        // Convert binary PNG data to Magick::Image
        Magick::Blob blob(image_data.data(), image_data.size());
        Magick::Image image;
        try {
            image.read(blob);
        } catch (const Magick::Exception &e) {
            // Handle error...
            continue;
        }

        //Scale image to fit the display
        image.scale(Magick::Geometry(matrix->width(), matrix->height()));
        CopyImageToCanvas(image, offscreen_canvas);
        offscreen_canvas = matrix->SwapOnVSync(offscreen_canvas);
        //No need to sleep, as we'll just wait for the next image

        auto end_time = std::chrono::steady_clock::now();
        auto frame_latency = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();
        auto receive_latency = std::chrono::duration_cast<std::chrono::milliseconds>(received_time - start_time).count();

        // Frame display finished, output the latency.
        //std::cout << "[Timestamp: " << std::chrono::duration_cast<std::chrono::seconds>(end_time.time_since_epoch()).count()
                  //<< "] Frame Latency: " << frame_latency << "ms (Receive Latency: " << receive_latency << "ms)\n";

        // Calculate and output the framerate.
        auto frame_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - last_update_time);
        if (frame_duration.count() > 0) {
            auto fps = 1000.0 / frame_duration.count();
            fps_values.push_back(fps); // Store each FPS measurement
            //std::cout << "Framerate: " << fps << " FPS\n";
        }

        last_update_time = end_time;

        if (connection_changed) {
            // Gracefully end the current connection and start a new connection
            ConnectToZmq(new_address);
            connection_changed = false; // Reset the flag
        }
    }

    std::cout << "Interrupt received cleaning up";

    matrix->Clear();
    gpioTerminate(); // Cleanup and stop pigpio
    ComputeStatistics(fps_values); // Compute and output the statistics

    std::cout << "Exiting";
    return 0;
}