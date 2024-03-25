#pragma once

#include <opencv2/opencv.hpp>

#include <Sender.hpp>

class WindowSender : public Sender {
public:
    void serializeSurface(const Surface &surface) override;
    void send() override;

private:
    cv::Mat output;
};
