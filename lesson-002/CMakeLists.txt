cmake_minimum_required(VERSION 3.10)
project(lesson-002)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O3")

add_executable(hello helloworld.cpp)