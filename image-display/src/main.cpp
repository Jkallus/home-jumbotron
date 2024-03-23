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

const std::string dev_address = "tcp://jkallus-pc:5555";
const std::string prod_address = "tcp://jumbotron:5555";

// Global variables for managing the ZeroMQ connection
const std::string default_address = prod_address;
zmq::context_t context(1);
zmq::socket_t subscriber(context, ZMQ_SUB);
bool zmq_connected = false;
std::string current_zmq_connection = "";
bool connection_change_queued = false;
std::string new_address = "";


// Define the GPIO pin number
const int inputPin = 21;

// Define a debounce time in milliseconds
const int debounceTimeMs = 20;

// Keep track of the last interrupt time
steady_clock::time_point lastInterruptTime = steady_clock::now();

// Interrupt callback function
void button_interrupt_callback(int gpio, int level, uint32_t tick) {
    auto now = steady_clock::now();
    auto durationSinceLastInterrupt = duration_cast<milliseconds>(now - lastInterruptTime);

    spdlog::debug("Got button interrupt, level: {}, tick: {}", level, tick);

    if (durationSinceLastInterrupt.count() > debounceTimeMs) {
        lastInterruptTime = now;
        std::this_thread::sleep_for(milliseconds(10)); // Debounce delay
        int currentLevel = gpioRead(gpio);
        new_address = (currentLevel == 1) ? prod_address : dev_address;
        spdlog::info("Queuing connection change to {}", new_address);
        connection_change_queued = true;
    }
}

void InitializeDigitalInput() {
    spdlog::info("Initializing DigitalInput");
    if (gpioInitialise() < 0) {
        spdlog::error("Failed to initialize pigpio");
        throw std::runtime_error("Failed to initialize pigpio.");
    }

    gpioSetMode(inputPin, PI_INPUT);
    gpioSetPullUpDown(inputPin, PI_PUD_UP);

    if (gpioSetISRFunc(inputPin, EITHER_EDGE, 0, button_interrupt_callback) < 0) {
        gpioTerminate();
        spdlog::error("Failed to set up ISR function.");
        throw std::runtime_error("Failed to set up ISR function.");
    }
    spdlog::info("Initialized DigitalInput");
}

void ConnectToZmq(const std::string &address) {
    try {
        if(zmq_connected){
            spdlog::info("Disconnecting from zmq source: {}", current_zmq_connection);
            subscriber.disconnect(current_zmq_connection);
            spdlog::info("Disconnected from zmq source: {}", current_zmq_connection);
            zmq_connected = false;
        }

        spdlog::info("Connecting to zmq source: {}", address);
        subscriber.connect(address);
        spdlog::info("Connected to zmq source: {}", address);
        zmq_connected = true;
        
        subscriber.setsockopt(ZMQ_SUBSCRIBE, "/frames", 7);
        spdlog::info("Subscribed to /frames");
        current_zmq_connection = address;  
    } catch (const zmq::error_t &e) {
         spdlog::error("ZMQ Exception: {} ({})", e.what(), zmq_strerror(e.num()));
    } catch (const std::exception &e) {
        spdlog::error("ZMQ Exception: {}", e.what());
    } catch (...) {
        spdlog::error("Unknown Exception occured during ZMQ connection.");
    }
}

volatile bool console_interrupt_received = false;
static void ConsoleInterruptHandler(int signo) {
    console_interrupt_received = true;
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

void ComputeStatistics(const std::vector<double> &fps_values) {
    if (fps_values.empty()) {
        spdlog::warn("No data to compute statistics for.");
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
    
    spdlog::info("Statistics:");
    std::cout << "FPS Statistics:" << std::endl;
    std::cout << "Min FPS: " << min_fps << std::endl;
    std::cout << "Max FPS: " << max_fps << std::endl;
    std::cout << "Mean FPS: " << mean_fps << std::endl;
    std::cout << "StdDev FPS: " << stddev_fps << std::endl;
}

int main(int argc, char *argv[]) {
    spdlog::set_level(spdlog::level::info);
    spdlog::set_pattern("[%Y-%m-%d %H:%M:%S] [%^%l%$] %v");

    auto console = spdlog::stdout_color_mt("console");

    spdlog::info("Image Display starting...");

    InitializeDigitalInput(); // Initialize the digital input for interrupts
    Magick::InitializeMagick(*argv);
    RGBMatrix::Options matrix_options;
    RuntimeOptions runtime_opt;

    if (!ParseOptionsFromFlags(&argc, &argv, &matrix_options, &runtime_opt)) {
        // Handle parsing error...
        return 1;
    }

    signal(SIGTERM, ConsoleInterruptHandler);
    signal(SIGINT, ConsoleInterruptHandler);

    std::unique_ptr<RGBMatrix> matrix(RGBMatrix::CreateFromOptions(matrix_options, runtime_opt));
    if (matrix == nullptr) {
        spdlog::error("Failed to instantiate RGBMatrix");
        return 1;
    }

    int timeout_ms = 1000;
    subscriber.setsockopt(ZMQ_RCVTIMEO, &timeout_ms, sizeof(timeout_ms));
    ConnectToZmq(default_address); // Connect to the initial address

    FrameCanvas *offscreen_canvas = matrix->CreateFrameCanvas();
    auto last_update_time = std::chrono::steady_clock::now();

    std::vector<double> fps_values; // Vector to hold FPS values

    while (!console_interrupt_received) {
        auto start_time = std::chrono::steady_clock::now();
        bool new_frame_received = false;
        zmq::message_t update;
        try {
            new_frame_received = subscriber.recv(&update);
        } catch (const zmq::error_t& e) {
            if (e.num() == EINTR) {
                // Interrupted system call - likely due to the signal
                break; // Exit the loop
            } else {
                // Handle other errors that might occur
                spdlog::error("ZMQ error: {} ({})", e.what(), zmq_strerror(e.num()));
            }
        }
        auto received_time = std::chrono::steady_clock::now();

        if(new_frame_received){
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
            spdlog::trace("[Timestamp: {}] Frame Latency: {}ms (Receive Latency: {}ms)", std::chrono::duration_cast<std::chrono::seconds>(end_time.time_since_epoch()).count(), frame_latency, receive_latency);

            // Calculate and output the framerate.
            auto frame_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - last_update_time);
            if (frame_duration.count() > 0) {
                auto fps = 1000.0 / frame_duration.count();
                fps_values.push_back(fps); // Store each FPS measurement
            }
            last_update_time = end_time;
        }
        
        if(connection_change_queued){
            matrix->Clear();
            ConnectToZmq(new_address);
            connection_change_queued = false;
            new_address = "";
        }
    }

    std::cout << "Interrupt received cleaning up";

    matrix->Clear();
    gpioTerminate(); // Cleanup and stop pigpio
    ComputeStatistics(fps_values); // Compute and output the statistics


    std::cout << "Exiting";
    return 0;
}