#pragma once

#include <Capture.hpp>

class CameraCapture : public Capture {
public:
    void registerOptions(cxxopts::Options& options) override;
    void receiveOptions(const cxxopts::ParseResult& result) override;

    void captureImage() override;
    const cv::Mat& currentImage() override;
    bool imageValid() override;

private:
    cv::VideoCapture cap;
    bool valid = false;
    cv::Mat frame;

    std::vector<cv::Point2f> src { };
    std::vector<cv::Point2f> dst { };
};
