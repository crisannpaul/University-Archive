cmake_minimum_required(VERSION 3.17)
project(Lab3 C)

set(CMAKE_C_STANDARD 99)
set(GCC_ENABLE_WARNINGS "-O1 -Wall")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${GCC_ENABLE_WARNINGS}")
add_executable(Lab3 main.c; util.h; util.c)