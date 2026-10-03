#include <iostream>
#include "include/SDL.h"
#include "transform.h"
#include "polygon.h"

using namespace egc;

//define window dimensions
const int WINDOW_WIDTH = 640;
const int WINDOW_HEIGHT = 480;

SDL_Window *window = NULL;
SDL_Renderer *windowRenderer = NULL;
SDL_Event currentEvent;

bool quit = false;

int mouseX, mouseY;

polygon p;

bool initWindow() {

    bool success = true;
    
    //Try to initialize SDL
    if(SDL_Init(SDL_INIT_VIDEO) < 0) {

        std::cout << "SDL initialization failed" << std::endl;
        success = false;

    } else {

        //Try to create the window
        window = SDL_CreateWindow(
                "SDL Hello World Example",
                SDL_WINDOWPOS_UNDEFINED,
                SDL_WINDOWPOS_UNDEFINED,
                WINDOW_WIDTH,
                WINDOW_HEIGHT,
                SDL_WINDOW_SHOWN | SDL_WINDOW_ALLOW_HIGHDPI);
        
        if(window == NULL) {

            std::cout << "Failed to create window: " << SDL_GetError() << std::endl;
            success = false;

        } else {

			// Create a renderer for the current window
			windowRenderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);

			if(windowRenderer == NULL) {

                std::cout << "Failed to create the renderer: " << SDL_GetError() << std::endl;
                success = false;

            } else {

                //Set background color
				SDL_SetRenderDrawColor(windowRenderer, 255, 255, 255, 255);
			
                //Apply background color
                SDL_RenderClear(windowRenderer);
            }
        }
    }
    
    return success;
}

void initPolygon() {
    p.addVertex(vec3(100.0f, 100.0f, 1.0f));
    p.addVertex(vec3(400.0f, 100.0f, 1.0f));
    p.addVertex(vec3(400.0f, 300.0f, 1.0f));
    p.addVertex(vec3(100.0f, 300.0f, 1.0f));

}

void processEvents() {

    //Check for events in queue
    SDL_PollEvent(&currentEvent);

    //User requests quit
    if(currentEvent.type == SDL_QUIT) {

        quit = true;
    }

    //Mouse event -> pressed button
    if(currentEvent.type == SDL_MOUSEBUTTONDOWN) {

        if(currentEvent.button.button == SDL_BUTTON_LEFT) {

            SDL_GetMouseState(&mouseX, &mouseY);
            std::cout << "Mouse click => " << "x: " << mouseX << ", y: " << mouseY << std::endl;
        }
    }

    //Mouse event -> mouse movement
    if(currentEvent.type == SDL_MOUSEMOTION) {

        if(SDL_GetMouseState(NULL, NULL) & SDL_BUTTON_LMASK) {

            SDL_GetMouseState(&mouseX, &mouseY);
            std::cout << "Mouse move => " << "x: " << mouseX << ", y: " << mouseY << std::endl;
        }
    }

    //Keyboard event
    if(currentEvent.type == SDL_KEYDOWN) {

        vec3 pct = (p.vertices.at(0) + p.vertices.at(1) + p.vertices.at(2) + p.vertices.at(3)) * (1.0/4.0);
       
        mat3 t = translate(pct.x, pct.y);
        mat3 ti = translate(-pct.x, -pct.y);
        mat3 s;
        mat3 r;
        mat3 m;

        switch(currentEvent.key.keysym.sym) {

            case SDLK_UP:
                s = scale(1.01, 1.01);
                m = t * s * ti;
                std::cout << m << std::endl;
                for (int i = 0; i < 4; i++) {
                    p.vertices.at(i) = m * p.vertices.at(i);
                    std::cout << p.vertices.at(i) << std::endl;
                }
                break;

            case SDLK_DOWN:
                s = scale(1.0/1.01, 1.0/1.01);
                m = t * s * ti;
                for (int i = 0; i < 4; i++) {
                    p.vertices.at(i) = m * p.vertices.at(i);
                    std::cout << p.vertices.at(i) << std::endl;
                }
                break;

            case SDLK_RIGHT:
                r = rotate(-10);
                m = t * r * ti;
                for (int i = 0; i < 4; i++) {
                    p.vertices.at(i) = m * p.vertices.at(i);
                    std::cout << p.vertices.at(i) << std::endl;
                }
                break;

            case SDLK_LEFT:
                r = rotate(10);
                m = t * r * ti;
                for (int i = 0; i < 4; i++) {
                    p.vertices.at(i) = m * p.vertices.at(i);
                    std::cout << p.vertices.at(i) << std::endl;
                }
                break;

            case SDLK_ESCAPE:
                quit = true;
                break;

            default:
                break;
        }
    }
}

void drawFrame() {

    //Clear the background
    SDL_SetRenderDrawColor(windowRenderer, 255, 255, 255, 255);
    SDL_RenderClear(windowRenderer);

    p.draw(windowRenderer);

    //Update window
    SDL_RenderPresent(windowRenderer);
}

void cleanup() {

    //Clear polygon
    p.clearVertices();

    //Destroy renderer
    if (windowRenderer) {

        SDL_DestroyRenderer(windowRenderer);
        windowRenderer = NULL;
    }

    //Destroy window
    if (window) {

        SDL_DestroyWindow(window);
        window = NULL;
    }

    //Quit SDL
    SDL_Quit();
}

int main(int argc, char * argv[]) {
    //Initialize window
    if(!initWindow()) {

        std::cout << "Failed to initialize" << std::endl;
        return -1;
    }

    //Initialize polygon
    initPolygon();

    //Game loop
    while (!quit) {

        processEvents();
        drawFrame();
    }

    cleanup();
    return 0;
}
