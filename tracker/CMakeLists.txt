cmake_minimum_required(VERSION 3.16)
project(thesis_tracker)

set(CMAKE_CXX_STANDARD 20)

set(OpenCV_DIR /usr/local/opt/opencv/lib/cmake/opencv4/)

find_package(OpenCV REQUIRED)
find_package(fmt REQUIRED)
find_package(Eigen3 3.3 REQUIRED NO_MODULE)

# Common library
add_library(
        common
        src/common/Marker.cpp
        src/common/ArUcoMarker.cpp
        src/common/TUIOSender.cpp
        src/common/Surface.cpp
        src/common/Object.cpp
        src/common/Object.hpp
        src/common/Driver.hpp
        src/common/TestDriver.cpp
        src/common/TestDriver.hpp
        src/common/Application.cpp
        src/common/Application.hpp
        src/common/Sender.hpp
        src/common/Sender.cpp
        src/common/Component.cpp
        src/common/Component.hpp
        src/common/Utils.cpp
        src/common/Capture.cpp
        src/common/Capture.hpp
        src/common/CameraCapture.cpp
        src/common/CameraCapture.hpp
        src/common/ArUcoDriver.cpp
        src/common/ArUcoDriver.hpp
        src/common/WindowSender.cpp
        src/common/WindowSender.hpp
)

target_include_directories(
        common PUBLIC
        src/common/
        lib/
        ${OpenCV_INCLUDE_DIRS}
)

target_link_libraries(
        common
        ${OpenCV_LIBS}
        Eigen3::Eigen
        fmt::fmt
)

# Marker generator
add_executable(
        generator
        src/generator/main.cpp
)

target_include_directories(
        generator PUBLIC
        lib/
)

target_link_libraries(
        generator
        common
        fmt::fmt
)

# Tracker
add_executable(
        tracker
        src/tracker/main.cpp
)

target_include_directories(
        tracker PUBLIC
        src/tracker
)

target_link_libraries(
        tracker
        common
        fmt::fmt
)

# Cropper
add_executable(
        cropper
        src/cropper/main.cpp
)

target_include_directories(
        cropper PUBLIC
        src/cropper
)

target_link_libraries(
        cropper
        common
        fmt::fmt
)