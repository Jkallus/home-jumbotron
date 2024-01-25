#include "led-matrix.h"
#include <math.h>
#include <signal.h>
#include <unistd.h>
#include <exception>
#include <Magick++.h>
#include <zmq.hpp>

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

    while (!interrupt_received) {
        // Receive message
        zmq::message_t update;
        subscriber.recv(&update);

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

        // Display image on the matrix
        FrameCanvas *offscreen_canvas = matrix->CreateFrameCanvas();
        CopyImageToCanvas(image, offscreen_canvas);
        offscreen_canvas = matrix->SwapOnVSync(offscreen_canvas);
        // No need to sleep, as we'll just wait for the next image
    }

    matrix->Clear();

    return 0;
}