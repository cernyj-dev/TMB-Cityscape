#include "ArUcoDriver.hpp"

#include <fmt/format.h>

void ArUcoDriver::registerOptions(cxxopts::Options &options) {
    Component::registerOptions(options);
}

void ArUcoDriver::receiveOptions(const cxxopts::ParseResult& result) {
    this->parameters = cv::aruco::DetectorParameters::create();
    this->dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_6X6_50);
}

void ArUcoDriver::processFrame(const std::vector<std::unique_ptr<Capture>>& captures) {
    for (const auto& capture : captures) {
        const cv::Mat& frame = capture->currentImage();

        cv::aruco::detectMarkers(
            frame,
            this->dictionary,
            this->markerCorners, this->markerIds,
            this->parameters,
            this->rejectedCandidates
        );

        for (size_t i = 0; i < this->markerCorners.size(); i++) {
            float x = 0;
            float y = 0;
            for (const cv::Point2f& corner : this->markerCorners[i]) {
                x += corner.x;
                y += corner.y;
            }

            cv::Point2f center {
                x / (float)this->markerCorners[i].size(),
                y / (float)this->markerCorners[i].size(),
            };

            cv::Point2f dir = this->markerCorners[i][0] - center;
            float a = atan2(dir.x, dir.y) - M_PI / 4.0f;

            // Normalize coords
            center.x /= (float)frame.cols;
            center.y /= (float)frame.rows;
            int id = markerIds[i];

            bool found = false;
            for (const auto& object : this->surface->objects) {
                if (object->classId == id) {
                    found = true;

                    object->x = center.x;
                    object->y = center.y;
                    object->a = a;
                }
            }

            if (!found) {
                auto newObject = std::make_unique<Object>();

                newObject->sessionId = this->sessionIdCounter++;
                newObject->classId = id;

                newObject->x = center.x;
                newObject->y = center.y;
                newObject->a = a;

                this->surface->objects.push_back(std::move(newObject));
            }
        }

        this->surface->objects.erase(
            std::remove_if(
                this->surface->objects.begin(),
                this->surface->objects.end(),
                [&](const std::unique_ptr<Object>& o) {
                    return std::find(markerIds.begin(), markerIds.end(), o->classId) == markerIds.end();
                }
            ),
            this->surface->objects.end()
        );
    }
}
