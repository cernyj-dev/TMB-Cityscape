#pragma once

#include <Component.hpp>
#include <Surface.hpp>

class Application;

class Sender : public Component {
public:
    virtual void serializeSurface(const Surface& surface) = 0;
    virtual void send() = 0;
};