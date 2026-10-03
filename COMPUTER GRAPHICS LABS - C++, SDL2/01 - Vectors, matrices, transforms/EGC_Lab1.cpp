//
//  main.cpp
//  SDL_Lab1
//
//  Created by CGIS on 16/02/16.
//  Copyright © 2016 CGIS. All rights reserved.
//

#include <iostream>
#include "include\SDL.h"

//define window dimensions
const int WINDOW_WIDTH = 640;
const int WINDOW_HEIGHT = 480;

SDL_Window *window = NULL;
SDL_Surface *windowSurface = NULL;
SDL_Event currentEvent;

SDL_Rect rectangleCoordinates = {100, 100, 200, 200};
Uint32 rectagleColor;

bool quit = false;

int mouseX, mouseY;

bool initWindow()
{
    bool success = true;
    
    //Try to initialize SDL
    if(SDL_Init(SDL_INIT_VIDEO) < 0)
    {
        std::cout << "SDL initialization failed" << std::endl;
        success = false;
    }
    else{
        //Try to create the window
        window = SDL_CreateWindow("SDL Hello World Example", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, WINDOW_WIDTH, WINDOW_HEIGHT, SDL_WINDOW_SHOWN | SDL_WINDOW_ALLOW_HIGHDPI);
        
        if(window == NULL)
        {
            std::cout << "Failed to create window: " << SDL_GetError() << std::endl;
            success = false;
        }
        else
        {
            //Try to get the window surface
            windowSurface = SDL_GetWindowSurface(window);
            
            if(windowSurface == NULL)
            {
                std::cout << "Failed to get the window surface: " << SDL_GetError() << std::endl;
                success = false;
            }
            else
            {
                //Initialize surface color
                SDL_FillRect(windowSurface, NULL, SDL_MapRGB(windowSurface->format, 255, 255, 255));
                
                //Update the surface
                SDL_UpdateWindowSurface(window);
            }

        }
    }
    
    return success;
}

void destroyWindow()
{
    //Destroy window
    SDL_DestroyWindow(window);
    window = NULL;
    
    //Quit SDL
    SDL_Quit();
}

int main(int argc, char * argv[]) {
    char currColor = NULL;
    int r = 0;
    int g = 0;
    int b = 0;

    if(!initWindow())
    {
        std::cout << "Failed to initialize" << std::endl;
        return -1;
    }
    
    rectagleColor = SDL_MapRGB(windowSurface->format, 0, 0, 0);
    
    while (!quit) {
        //Handle events on queue
        if(SDL_WaitEvent(&currentEvent) != 0)
        {
            //User requests quit
            if(currentEvent.type == SDL_QUIT)
            {
                quit = true;
            }
            
            //Mouse event -> pressed button
            if(currentEvent.type == SDL_MOUSEBUTTONDOWN)
            {
                if(currentEvent.button.button == SDL_BUTTON_LEFT)
                {
                    SDL_GetMouseState(&mouseX, &mouseY);
                    std::cout << "Mouse click => " << "x: " << mouseX << ", y: " << mouseY << std::endl;
                }
            }
            
            //Mouse event -> mouse movement
            if (currentEvent.button.button == SDL_BUTTON_LEFT)
            {
                if (currentEvent.type == SDL_MOUSEMOTION)
                {

                    SDL_GetMouseState(&mouseX, &mouseY);
                }
            }
         
            
            //Keyboard event
            if(currentEvent.type == SDL_KEYDOWN)
            {
                switch(currentEvent.key.keysym.sym)
                {
                    case SDLK_UP:
                        switch (currColor)
                        {
                        case 'r':
                            r += 10;
                            rectagleColor = SDL_MapRGB(windowSurface->format, r, g, b);
                            currColor = NULL;
                            break;
                        case 'g':
                            g += 10;
                            rectagleColor = SDL_MapRGB(windowSurface->format, r, g, b);
                            currColor = NULL;
                            break;
                        case 'b':
                            b += 10;
                            rectagleColor = SDL_MapRGB(windowSurface->format, r, g, b);
                            currColor = NULL;
                            break;
                        case NULL:
                            break;
                        }
                        break;
                        
                    case SDLK_RIGHT:
                        //rectangleCoordinates.x += 10;
                        break;
                        
                    case SDLK_LEFT:
                       // rectangleCoordinates.x -= 10;
                        break;

                    case SDLK_DOWN:
                        switch (currColor)
                        {
                        case 'r':
                            r -= 10;
                            rectagleColor = SDL_MapRGB(windowSurface->format, r, g, b);
                            currColor = NULL;
                            break;
                        case 'g':
                            g -= 10;
                            rectagleColor = SDL_MapRGB(windowSurface->format, r, g, b);
                            currColor = NULL;
                            break;
                        case 'b':
                            b -= 10;
                            rectagleColor = SDL_MapRGB(windowSurface->format, r, g, b);
                            currColor = NULL;
                            break;
                        case NULL:
                            break;
                        }
                        break;
                    case SDLK_r:
                        currColor = 'r';
                        break;
                    case SDLK_g:
                        currColor = 'g';
                        break;
                    case SDLK_b:
                        currColor = 'b';
                        break;
                }
            }
            
            SDL_FillRect(windowSurface, NULL, SDL_MapRGB(windowSurface->format, 255, 255, 255));
            SDL_FillRect(windowSurface, &rectangleCoordinates, rectagleColor);
            
            SDL_UpdateWindowSurface(window);
        }
    }
    
    destroyWindow();
    return 0;
}
