#pragma once

#include <memory>
#include <vector>
#include <string>

#include <Object.hpp>

class Surface {
public:
    Object* findObject(int32_t sessionId);

    std::string name = "Surface";
    std::vector<std::unique_ptr<Object>> objects;
};
