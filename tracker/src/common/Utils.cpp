#include "Utils.hpp"

#include <unistd.h>

std::string getHostname() {
    char hostname[256];
    gethostname(hostname, 256);
    return { hostname };
}

void cv::to_json(nlohmann::json& j, const cv::Point2f& p) {
    j = nlohmann::json { {"x", p.x }, { "y", p.y } };
}

void cv::from_json(const nlohmann::json& j, cv::Point2f& p) {
    j.at("x").get_to(p.x);
    j.at("y").get_to(p.y);
}
