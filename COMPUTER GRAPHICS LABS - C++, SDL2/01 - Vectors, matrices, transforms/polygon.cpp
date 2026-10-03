//
// Created by adi on 09.03.2022.
//

#include "polygon.h"

namespace egc {


    polygon::polygon() {

    }

    void polygon::addVertex(vec3 vertex) {

        this->vertices.push_back(vertex);
    }

    void polygon::clearVertices() {

        this->vertices.clear();
    }

    void polygon::draw(SDL_Renderer *windowRenderer) {

        if (this->vertices.size() >= 2) {

            SDL_SetRenderDrawColor(windowRenderer, 0, 0, 255, 255);
            for (int i = 0; i < 3; i++) {
                SDL_RenderDrawLine(
                    windowRenderer,
                    static_cast<int>(this->vertices.at(i).x),
                    static_cast<int>(this->vertices.at(i).y),
                    static_cast<int>(this->vertices.at(i + 1).x),
                    static_cast<int>(this->vertices.at(i + 1).y));
            }
            SDL_RenderDrawLine(
                windowRenderer,
                static_cast<int>(this->vertices.at(3).x),
                static_cast<int>(this->vertices.at(3).y),
                static_cast<int>(this->vertices.at(0).x),
                static_cast<int>(this->vertices.at(0).y));
        }
    }


}