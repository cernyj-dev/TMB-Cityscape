#pragma once

#include <cxxopts.hpp>

class Application;

class Component {
public:
    virtual ~Component() = default;

    virtual void registerOptions(cxxopts::Options& options);
    virtual void receiveOptions(const cxxopts::ParseResult& result);

protected:
    friend class Application;

    Application* application = nullptr;
};
