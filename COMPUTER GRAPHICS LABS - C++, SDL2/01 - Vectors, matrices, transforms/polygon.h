//
// Created by adi on 09.03.2022.
//

#pragma once

#include <vector>
#include "include/SDL.h"
#include "vec3.h"
#include "mat3.h"

namespace egc {

    class polygon {
    public:
        std::vector<vec3> vertices;
        mat3 transformationMatrix;

        polygon();
        void addVertex(vec3 vertex);
        void clearVertices();
        void draw(SDL_Renderer *windowRenderer);
    };
}
