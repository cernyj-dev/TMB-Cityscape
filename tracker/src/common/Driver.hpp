#pragma once

#include <Component.hpp>
#include <Capture.hpp>
#include <Surface.hpp>

class Driver : public Component {
public:
    void setSurface(Surface* s) {
        this->surface = s;
    };

    virtual void processFrame(const std::vector<std::unique_ptr<Capture>>& captures) = 0;

protected:
    Surface* surface = nullptr;
};
