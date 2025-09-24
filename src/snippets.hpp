#pragma once
//
// SNIPPETS.h
//
// common C++ snippets & functions

/*
The MIT License (MIT)
---------------------

Copyright (c) 2025 Oskar Pietzsch

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 
*/

// macros
#define __FILENAME__ (strrchr(__FILE__, '/') ? strrchr(__FILE__, '/') + 1 : __FILE__)

// custom keywords
#define abstract = 0

#include <sys/types.h>
// integer/float types names
typedef __UINT8_TYPE__ uint8;
typedef __U16_TYPE uint16;
typedef __U32_TYPE uint32;
typedef __U64_TYPE uint64;

typedef __INT8_TYPE__ int8;
typedef __S16_TYPE int16;
typedef __S32_TYPE int32;
typedef __S64_TYPE int64;

typedef __SSIZE_T_TYPE ssize;
typedef unsigned __SSIZE_T_TYPE usize;

typedef float float32;
typedef double float64;
typedef long double float80;

// template callable type
template <typename T, typename... K>
using callable = T (*)(K...);

// string literal
#include <string>
inline std::string operator ""_s (const char* c, usize){
    return std::string(c);
}

// catch2 fallback
#ifndef CATCH2
    #define CONCAT2(a, b) a##b
    #define CONCAT(a, b) CONCAT2(a, b)
    
    // define all needed macros to be unused functions
    #define TEST_CASE(a, b) [[unused]] void CONCAT(_test_case_,CONCAT(__COUNTER__, CONCAT(_, __LINE__))) (const char* _a=a, const char* _b=b)
    #define TEMPLATE_TEST_CASE(a,b, ...) [[unused]] CONCAT(_test_case_,CONCAT(__COUNTER__, CONCAT(_, __LINE__))) (const char* a, const char* b, __VA_ARGS__)
    #define REQUIRE(a)
    #define BENCHMARK(a)
    #define SECTION(a)
    #define GENERATE(a, ...) a
#else

    // disable main function.
    // NOTE: requires no other used function with name 'main'
    #define main [[unused]] _no_main_
    #if(CATCH2_VERSION < 3)
        #include <catch2/catch.hpp>
    #else
        #include <catch2/catch_all.hpp>
    #endif
#endif





