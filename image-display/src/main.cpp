#include "led-matrix.h"
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

using namespace rgb_matrix;

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

// Function to compute mean and standard deviation
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

    // ZeroMQ initialization
    zmq::context_t context(1);
    zmq::socket_t subscriber(context, ZMQ_SUB);
    subscriber.connect("tcp://localhost:5555"); // or other appropriate address
    subscriber.setsockopt(ZMQ_SUBSCRIBE, "/frames", 7);

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

        // Scale image to fit the display
        image.scale(Magick::Geometry(matrix->width(), matrix->height()));
        CopyImageToCanvas(image, offscreen_canvas);
        offscreen_canvas = matrix->SwapOnVSync(offscreen_canvas);
        // No need to sleep, as we'll just wait for the next image

        auto end_time = std::chrono::steady_clock::now();
        auto frame_latency = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();
        auto receive_latency = std::chrono::duration_cast<std::chrono::milliseconds>(received_time - start_time).count();

        // Frame display finished, output the latency.
        std::cout << "[Timestamp: " << std::chrono::duration_cast<std::chrono::seconds>(end_time.time_since_epoch()).count()
                  << "] Frame Latency: " << frame_latency << "ms (Receive Latency: " << receive_latency << "ms)\n";

        // Calculate and output the framerate.
        auto frame_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - last_update_time);
        if (frame_duration.count() > 0) {
            auto fps = 1000.0 / frame_duration.count();
            fps_values.push_back(fps); // Store each FPS measurement
            std::cout << "Framerate: " << fps << " FPS\n";
        }

        last_update_time = end_time;
    }

    matrix->Clear();

    ComputeStatistics(fps_values); // Compute and output the statistics

    return 0;
}