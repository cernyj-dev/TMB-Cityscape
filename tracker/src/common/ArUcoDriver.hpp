#pragma once

#include <opencv2/opencv.hpp>
#include <opencv2/aruco.hpp>

#include <Driver.hpp>

class ArUcoDriver : public Driver {
public:
    void registerOptions(cxxopts::Options& options) override;
    void receiveOptions(const cxxopts::ParseResult& result) override;

    void processFrame(const std::vector<std::unique_ptr<Capture>> &captures) override;

private:
    int sessionIdCounter = 1;

    cv::Ptr<cv::aruco::DetectorParameters> parameters;
    cv::Ptr<cv::aruco::Dictionary> dictionary;

    std::vector<std::vector<cv::Point2f>> markerCorners;
    std::vector<std::vector<cv::Point2f>> rejectedCandidates;
    std::vector<int> markerIds;
};
