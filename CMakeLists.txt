
cmake_minimum_required(VERSION 3.5)
project( proj )

set(ExecutableName "name")

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/build)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/build)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_CXX_STANDARD 17)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CXX g++)

# add files in src folder

file(GLOB_RECURSE SRC "src/*")

# exectuable

add_executable ( ${ExecutableName} ${SRC})
set_target_properties(${ExecutableName} PROPERTIES LINKER_LANGUAGE CXX)

# Enable Debug mode if required

if ( NOT "${CMAKE_BUILD_TYPE}" )
    message(STATUS "Build Type not set, defaulting to Debug..." )
    set( CMAKE_BUILD_TYPE Debug )
endif()
if (${CMAKE_BUILD_TYPE} STREQUAL "Debug")
    message(STATUS "Building in Debug mode...")
    target_compile_options(${ExecutableName} PRIVATE -DDEBUG_ON -g -ggdb -W -Wall -Wextra -Wno-unused-parameter -fstrict-enums)
else()
    message(STATUS "Building in Release mode...")
    target_compile_options(${ExecutableName} PRIVATE -g -W -Wall -Wextra -Wno-unused-parameter -ffold-simple-inlines -fstrict-enums)
endif()

# Stacktrace on segfault

if (EXISTS "./lib/backward-cpp")
    add_subdirectory("./lib/backward-cpp")
    message(STATUS "optional dependency backward-cpp found")

    # Add Backward to target (NOTE: either Backward::Interface, Backward::Object, or Backward::Backward)
    target_link_libraries(${ExecutableName} PUBLIC Backward::Interface)
else()
    message(STATUS "optional dependency backward-cpp not found - disabling stacktrace")
endif()

# Tests

set(TestName "${ExecutableName}-tests")
find_package(Catch2)
if (${Catch2_FOUND})
    # for tests no main file
    list(REMOVE_ITEM SRC "${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp")
    add_executable(${TestName} ${SRC})
    target_compile_options(${TestName} PRIVATE -g -ggdb -DCATCH2 -DCATCH2_VERSION=${Catch2_VERSION_MAJOR} -Wno-literal-suffix -Wno-unused-parameter -fstrict-enums)
    # NOTE: for tests no compiler warnings are required, since these will be emitted by the main file already
    target_link_libraries(${TestName} PRIVATE Catch2::Catch2WithMain)

    # run tests

    add_custom_command(TARGET ${TestName}
        POST_BUILD
        COMMENT "Running tests..."
        COMMAND $<TARGET_FILE:${TestName}>
    )
    
else()
    message(WARNING "Testing disabled - Catch2 not found!")
endif()

# Doxygen

list(FILTER SRC EXCLUDE REGEX "${CMAKE_CURRENT_SOURCE_DIR}/lib/.*")
list(FILTER SRC EXCLUDE REGEX "${CMAKE_CURRENT_SOURCE_DIR}/src/backward(\.cpp|\.hpp)")

find_package(Doxygen)
set(DOXYGEN_GENERATE_HTML YES)
set(DOXYGEN_GENERATE_MAN YES)
doxygen_add_docs(
        "docs"
        ${SRC}
        ALL
        WORKING_DIRECTORY "./docs"
    )
