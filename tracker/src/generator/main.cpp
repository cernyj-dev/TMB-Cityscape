#include "cxxopts.hpp"

#include <fmt/format.h>

#include <opencv2/opencv.hpp>
#include <opencv2/aruco.hpp>

int main(int argc, const char* argv[]) {
    cxxopts::Options options("generator", "ArUco marker generator");

    options.add_options()
            ("s,size", "Marker size in pixels", cxxopts::value<int>()->default_value("128"))
            ("ids", "Marker IDs to generate", cxxopts::value<std::vector<int>>());

    options.parse_positional({ "ids" });

    try {
        auto result = options.parse(argc, argv);

        int size = result["size"].as<int>();
        assert(size > 0 && size <= 1024);

        cv::Mat markerImage;
        cv::Ptr<cv::aruco::Dictionary> dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_50);

        for (const int& id : result["ids"].as<std::vector<int>>()) {
            cv::aruco::drawMarker(dictionary, id, result["size"].as<int>(), markerImage);
            cv::imwrite(fmt::format("marker_{}.png", id), markerImage);
        }
    }
    catch (const cxxopts::OptionException& e) {
        fmt::print(stderr, "{}\n", e.what());
        fmt::print(stderr, "{}\n", options.help());
        return 1;
    }

    return 0;
}
