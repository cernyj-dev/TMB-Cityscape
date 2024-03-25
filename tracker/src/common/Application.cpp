#include "Application.hpp"

#include <thread>

#include <fmt/format.h>

#include <Utils.hpp>

Application::Application(const char* name, const char* description)
    : options { name, description }
{ }

[[noreturn]]
void Application::main(int argc, const char* argv[]) {
    // Set refs
    for (const auto& capture : this->captures) {
        capture->application = this;
    }

    for (const auto& driver : this->drivers) {
        driver->application = this;
    }

    for (const auto& sender : this->senders) {
        sender->application = this;
    }

    // Process args
    try {
        this->parseArguments(argc, argv);
    }
    catch (const cxxopts::OptionException& e) {
        fmt::print(stderr, "Error: {}\n", e.what());
        fmt::print("{}", this->options.help());
        exit(1);
    }

    for (const auto& driver : this->drivers) {
        driver->setSurface(&this->surface);
    }

    // Main loop
    while (true) {
        for (const auto& capture : this->captures) {
            capture->captureImage();
        }

        for (const auto& driver : this->drivers) {
            driver->processFrame(this->captures);
        }

        for (const auto& sender : this->senders) {
            sender->serializeSurface(this->surface);
            sender->send();
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(16));
    }
}

void Application::parseArguments(int argc, const char* argv[]) {
    this->options.add_options()
        ("s,surface", "Surface name", cxxopts::value<std::string>()->default_value(getHostname()));

    for (const auto& capture : this->captures) {
        capture->registerOptions(this->options);
    }
    for (const auto& driver : this->drivers) {
        driver->registerOptions(this->options);
    }
    for (const auto& sender : this->senders) {
        sender->registerOptions(this->options);
    }

    auto result = this->options.parse(argc, argv);

    this->surface.name = result["surface"].as<std::string>();
    fmt::print("{}\n", this->surface.name);

    for (const auto& capture : this->captures) {
        capture->receiveOptions(result);
    }
    for (const auto& driver : this->drivers) {
        driver->receiveOptions(result);
    }
    for (const auto& sender : this->senders) {
        sender->receiveOptions(result);
    }
}

