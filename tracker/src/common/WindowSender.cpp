#include "WindowSender.hpp"

#include <fmt/format.h>

#include <Application.hpp>

void WindowSender::serializeSurface(const Surface& surface) {
    if (this->application->captures.empty()) {
        return;
    }

    this->output = this->application->captures[0]->currentImage().clone();

    for (const auto& object : surface.objects) {
        cv::Point2f center { object->x * (float)this->output.cols, object->y * (float)this->output.rows};
        cv::circle(output, center, 4, cv::Scalar(0, 255, 0));
        cv::putText(output, fmt::format("{}", object->classId), center, cv::FONT_HERSHEY_PLAIN, 1.0, cv::Scalar(255, 255, 255));
    }
}

void WindowSender::send() {
    if (this->output.empty()) {
        return;
    }

    cv::imshow("Window", this->output);
    cv::waitKey(1);
}
