#pragma once

#include <memory>
#include <vector>

#include <cxxopts.hpp>

#include <Capture.hpp>
#include <Driver.hpp>
#include <Sender.hpp>

class Application {
public:
    Application(const char* name, const char* description);
    virtual ~Application() = default;

    [[noreturn]]
    virtual void main(int argc, const char* argv[]);

    std::vector<std::unique_ptr<Capture>> captures;
    std::vector<std::unique_ptr<Driver>> drivers;
    std::vector<std::unique_ptr<Sender>> senders;

protected:
    void parseArguments(int argc, const char* argv[]);

    Surface surface { };

    cxxopts::Options options;
};
