#include "CameraCapture.hpp"

#include <fstream>

#include <json.hpp>

#include <Utils.hpp>

void CameraCapture::registerOptions(cxxopts::Options& options) {
    options.add_options()
        ("v,video_id", "Video device id", cxxopts::value<int>()->default_value("0"))
        ("w,video_width", "Video device width", cxxopts::value<int>()->default_value("640"))
        ("h,video_height", "Video device height", cxxopts::value<int>()->default_value("480"))
        ("c,corners", "Planar rectification JSON", cxxopts::value<std::string>());
}

void CameraCapture::receiveOptions(const cxxopts::ParseResult& result) {
    this->cap = cv::VideoCapture(result["v"].as<int>());
    this->cap.set(cv::CAP_PROP_FRAME_WIDTH, result["w"].as<int>());
    this->cap.set(cv::CAP_PROP_FRAME_HEIGHT, result["h"].as<int>());

    if (result.count("c") > 0) {
        std::ifstream i { result["c"].as<std::string>() };
        nlohmann::json j;
        i >> j;
        src = j;
    }
}

void CameraCapture::captureImage() {
    this->valid = this->cap.read(this->frame);

    if (!this->valid) {
        return;
    }

    if (dst.empty()) {
        dst.emplace_back(0, 0);
        dst.emplace_back(frame.cols, 0);
        dst.emplace_back(frame.cols, frame.rows);
        dst.emplace_back(0, frame.rows);
    }

    if (!this->dst.empty() && !this->src.empty()) {
        cv::Mat img = this->frame.clone();
        cv::Mat mat = cv::getPerspectiveTransform(this->src, this->dst);

        cv::warpPerspective(img, this->frame, mat, frame.size());
    }
}

const cv::Mat& CameraCapture::currentImage() {
    return this->frame;
}

bool CameraCapture::imageValid() {
    return this->valid && !this->frame.empty();
}
