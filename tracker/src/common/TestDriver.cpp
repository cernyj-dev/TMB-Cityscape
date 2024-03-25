#include "TestDriver.hpp"

#include <cmath>

TestDriver::TestDriver()
{
    this->startTime = std::chrono::system_clock::now();
}

void TestDriver::processFrame(const std::vector<std::unique_ptr<Capture>>& captures) {
    auto a = this->findOrCreate(1);
    auto b = this->findOrCreate(2);

    auto t = std::chrono::duration_cast<std::chrono::duration<float>>(std::chrono::system_clock::now() - this->startTime).count();

    a->x = ((std::sin(t) + 1.0f) / 2.0f) * 0.8f + 0.1f;
    a->y = ((std::cos(t) + 1.0f) / 2.0f) * 0.8f + 0.1f;

    b->x = 0.5f;
    b->y = (std::sin(t * 2.0f) * 0.5f + 0.5f) * 0.8f + 0.1f;
    b->a = t * 2.0f * M_PI;
}

Object* TestDriver::findOrCreate(int32_t sessionId) {
    auto* object = this->surface->findObject(sessionId);

    if (object != nullptr) {
        return object;
    }

    auto newObject = std::make_unique<Object>();

    newObject->sessionId = sessionId;
    newObject->classId = sessionId;

    object = newObject.get();

    this->surface->objects.push_back(std::move(newObject));

    return object;
}
