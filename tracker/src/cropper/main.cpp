#include <opencv2/opencv.hpp>
#include <fmt/format.h>
#include <json.hpp>

std::vector<cv::Point2f> src { };
std::vector<cv::Point2f> dst { };

bool done = false;

void mouseCallback(int event, int x, int y, int flags, void *userdata) {
    if (done || event != cv::EVENT_LBUTTONDOWN) {
        return;
    }

    src.emplace_back((float)x, (float)y);
    if (src.size() == 4) {
        done = true;
    }
}

int main(int argc, const char* argv[]) {
    auto cam = cv::VideoCapture(0);
    cam.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cam.set(cv::CAP_PROP_FRAME_HEIGHT, 480);

    cv::Mat frame;

    while (true) {
        bool ret = cam.read(frame);
        if (!ret || frame.empty()) {
            fmt::print("Failed to grab frame :(\n");
            continue;
        }

        if (dst.empty()) {
            dst.emplace_back(0, 0);
            dst.emplace_back(frame.cols, 0);
            dst.emplace_back(frame.cols, frame.rows);
            dst.emplace_back(0, frame.rows);
        }

        cv::Mat out = frame.clone();

        if (done) {
            cv::Mat mat = cv::getPerspectiveTransform(src, dst);
            cv::warpPerspective(frame, out, mat, frame.size());
        }
        else {
            for (const auto& point : src) {
                cv::circle(out, point, 2, cv::Scalar(0, 255, 0));
            }
        }

        cv::imshow("live", out);
        cv::setMouseCallback("live", mouseCallback);

        if (cv::waitKey(1) >= 0) {
            break;
        }
    }

    nlohmann::json j = src;
    fmt::print("{}\n", j.dump(2));
}