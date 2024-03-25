#pragma once

#include <netinet/in.h>
#include <array>

#include <oscpp/client.hpp>

#include <Sender.hpp>

class TUIOSender : public Sender {
public:
    ~TUIOSender() override;

    void registerOptions(cxxopts::Options &options) override;
    void receiveOptions(const cxxopts::ParseResult &result) override;

    void serializeSurface(const Surface& surface) override;
    void send() override;

private:
    sockaddr_in destination {};
    int sock = 0;

    int32_t fseq = 1;

    std::array<uint8_t, 512> buffer {};
    OSCPP::Client::Packet packet {};
};
