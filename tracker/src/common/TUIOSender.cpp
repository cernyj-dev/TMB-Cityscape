#include "TUIOSender.hpp"

#include <chrono>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>

#include <fmt/format.h>

TUIOSender::~TUIOSender() {
    ::close(this->sock);
}

void TUIOSender::registerOptions(cxxopts::Options& options) {
    options.add_options()
        ("a,address", "Server address", cxxopts::value<std::string>()->default_value("127.0.0.1"))
        ("p,port", "Server port", cxxopts::value<uint16_t>()->default_value("3333"));
}

void TUIOSender::receiveOptions(const cxxopts::ParseResult& result) {
    std::string hostname = result["address"].as<std::string>();
    uint16_t port = result["port"].as<uint16_t>();

    this->destination.sin_family = AF_INET;
    this->destination.sin_addr.s_addr = inet_addr(hostname.c_str());
    this->destination.sin_port = htons(port);

    this->sock = ::socket(AF_INET, SOCK_DGRAM, 0);
}

void TUIOSender::serializeSurface(const Surface& surface) {
    auto now = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch());

    this->packet = { buffer.data(), buffer.size() };

    this->packet
        .openBundle(now.count());

    // Send SOURCE message
    this->packet
        .openMessage("/tuio/2Dobj", 2)
            .string("source")
            .string(surface.name.c_str())
        .closeMessage();

    // Send ALIVE message
    this->packet
        .openMessage("/tuio/2Dobj", 1 + surface.objects.size())
        .string("alive");

    for (const auto& object : surface.objects) {
        this->packet.int32(object->sessionId);
    }

    this->packet
        .closeMessage();

    // Send SET messages
    for (const auto& object : surface.objects) {
        this->packet
            .openMessage("/tuio/2Dobj", 11)
                .string("set")
                .int32(object->sessionId)
                .int32(object->classId)
                .float32(object->x)
                .float32(object->y)
                .float32(object->a)
                .float32(0.0f)
                .float32(0.0f)
                .float32(0.0f)
                .float32(0.0f)
                .float32(0.0f)
            .closeMessage();
    }

    // Send FSEQ message
    // TODO: Detect FSEQ overflow
    this->packet
        .openMessage("/tuio/2Dobj", 2)
            .string("fseq")
            .int32(this->fseq++)
        .closeMessage();

    this->packet
        .closeBundle();
}

void TUIOSender::send() {
    size_t n_bytes = ::sendto(
        this->sock,
        this->buffer.data(), this->packet.size(),
        0,
        reinterpret_cast<sockaddr*>(&this->destination), sizeof(this->destination)
    );
    fmt::print("Sent {} bytes.\n", n_bytes);
}
