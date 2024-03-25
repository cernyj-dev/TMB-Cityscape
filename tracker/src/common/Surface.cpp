#include "Surface.hpp"

Object* Surface::findObject(int32_t sessionId) {
    for (const auto& object : this->objects) {
        if (object->sessionId == sessionId) {
            return object.get();
        }
    }

    return nullptr;
}
