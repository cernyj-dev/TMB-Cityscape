#pragma once

#include <opencv2/opencv.hpp>

#include <Component.hpp>

class Capture : public Component {
public:
    virtual void captureImage() = 0;
    virtual const cv::Mat& currentImage() = 0;
    virtual bool imageValid() = 0;
};
