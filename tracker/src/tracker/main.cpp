#include <memory>

#include <Application.hpp>
#include <CameraCapture.hpp>
#include <ArUcoDriver.hpp>
#include <TestDriver.hpp>
#include <TUIOSender.hpp>
#include <WindowSender.hpp>

int main(int argc, const char* argv[]) {
    Application application { "tracker", "ArUco object tracker" };

    application.captures.push_back(std::make_unique<CameraCapture>());
    application.drivers.push_back(std::make_unique<ArUcoDriver>());
//    application.drivers.push_back(std::make_unique<TestDriver>());
    application.senders.push_back(std::make_unique<TUIOSender>());
    application.senders.push_back(std::make_unique<WindowSender>());

    application.main(argc, argv);
}