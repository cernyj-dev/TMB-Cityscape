#pragma once

#include <chrono>

#include <Driver.hpp>

class TestDriver : public Driver {
public:
    TestDriver();

    void processFrame(const std::vector<std::unique_ptr<Capture>>& captures) override;

private:
    Object* findOrCreate(int32_t sessionId);

    std::chrono::system_clock::time_point startTime;
};

