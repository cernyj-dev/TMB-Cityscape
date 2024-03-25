#pragma once

#include <string>

#include <opencv2/opencv.hpp>
#include <json.hpp>

std::string getHostname();

namespace cv {
    void to_json(nlohmann::json& j, const cv::Point2f& p);
    void from_json(const nlohmann::json& j, cv::Point2f& p);
}