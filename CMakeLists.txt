
cmake_minimum_required(VERSION 3.5)
project( proj )

set(ExecutableName "name")

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/build)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/build)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_CXX_STANDARD 17)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# add files in src folder

file(GLOB_RECURSE SRC "src/*")

if (EXISTS "./lib/tracy")
    list(APPEND SRC lib/tracy/public/TracyClient.cpp) # add tracy
endif()

# exectuable

add_executable ( ${ExecutableName} ${SRC})
set_target_properties(${ExecutableName} PROPERTIES LINKER_LANGUAGE CXX)

# get Version name

execute_process(COMMAND git rev-parse HEAD OUTPUT_VARIABLE VersionName)
execute_process(COMMAND git branch COMMAND grep "\*" OUTPUT_VARIABLE VersionNameBranch)
execute_process(COMMAND git tag --points-at HEAD OUTPUT_VARIABLE VersionTag)
string(LENGTH ${VersionNameBranch} VersionNameBranchLen)
math(EXPR idx "${VersionNameBranchLen}-3" OUTPUT_FORMAT DECIMAL)
string(SUBSTRING ${VersionNameBranch} 2 ${idx} VersionNameBranch)
if ( NOT ${VersionNameBranch} STREQUAL "" )
    set(VersionName "${VersionNameBranch}-${VersionName}")
elseif ( NOT ${VersionTag} STREQUAL "" )
    set(VersionName "${VersionTag}")
endif()
string(LENGTH ${VersionName} VersionNameLen)
math(EXPR idx "${VersionNameLen}-1" OUTPUT_FORMAT DECIMAL)
string(SUBSTRING ${VersionName} 0 ${idx} VersionName)
message(STATUS "Building version ${VersionName}")

# Enable Debug mode if required

if ( NOT "${CMAKE_BUILD_TYPE}" )
    message(STATUS "Build Type not set, defaulting to Debug..." )
    set( CMAKE_BUILD_TYPE Debug )
endif()
if (${CMAKE_BUILD_TYPE} STREQUAL "Debug")
    message(STATUS "Building in Debug mode...")
    target_compile_options(${ExecutableName} PRIVATE "-DVERSION_NAME=\"${VersionName}\"" -DENABLE_DEBUG -DTRACY_ENABLE -g -ggdb -W -Wall -Wextra -Wno-unused-parameter -fstrict-enums)
elseif(${CMAKE_BUILD_TYPE} STREQUAL "Profiling")
    message(STATUS "Building in Profiling mode...")
    target_compile_options(${ExecutableName} PRIVATE "-DVERSION_NAME=\"${VersionName}\"" -DTRACY_ENABLE -g -ggdb -W -Wall -Wextra -Wno-unused-parameter -ffold-simple-inlines -fstrict-enums)
else()
    message(STATUS "Building in Release mode...")
    target_compile_options(${ExecutableName} PRIVATE -g -W -Wall -Wextra -Wno-unused-parameter -ffold-simple-inlines -fstrict-enums)
endif()

find_program(CLANG_TIDY "clang-tidy")
if(CLANG_TIDY)
    message(STATUS "clang-tidy found: ${CLANG_TIDY}")
    add_custom_command(TARGET ${ExecutableName}
        PRE_BUILD
        COMMENT "running clang-tidy checks..."
        COMMAND clang-tidy ARGS ${SRC}
    )
else()
    message(WARNING "clang-tidy not found!")
endif()

# Stacktrace on segfault

if (EXISTS "./lib/backward-cpp")
    add_subdirectory("./lib/backward-cpp")
    message(STATUS "optional dependency backward-cpp found")
    
    # libdl is required for tracy client
    target_link_libraries(${ExecutableName} PUBLIC ${CMAKE_DL_LIBS})
    
    # libpthread too
    find_package(Threads REQUIRED)
    target_link_libraries(${ExecutableName} PUBLIC Threads::Threads)

    # Add Backward to target (NOTE: either Backward::Interface, Backward::Object, or Backward::Backward)
    target_link_libraries(${ExecutableName} PUBLIC Backward::Interface)
else()
    message(STATUS "optional dependency backward-cpp not found - disabling stacktrace")
endif()

# Profiling

if (EXISTS "./lib/tracy")
    # available options : TRACY_ENABLE , TRACY_LTO , TRACY_ON_DEMAND , TRACY_NO_BROADCAST , TRACY_NO_CODE_TRANSFER , ...
    option ( TRACY_ENABLE " " ON )
    option ( TRACY_ON_DEMAND " " ON )
    add_subdirectory (lib/tracy) # target : TracyClient or alias Tracy :: TracyClient
    
    message(STATUS "optional dependency tracy found")
    
    target_link_libraries(${ExecutableName} PUBLIC Tracy::TracyClient)
else()
    message(STATUS "optional dependency tracy not found - disabling profiling")
endif()

# Tests

set(TestName "${ExecutableName}-tests")
find_package(Catch2)
if (${Catch2_FOUND})
    # for tests no main file
    list(REMOVE_ITEM SRC "${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp")

    add_custom_command(
        OUTPUT build/doctests.cpp
        DEPENDS ${SRC} src/main.cpp
        COMMENT "collecting doc tests..."
        COMMAND "python3" ARGS generate_doc_tests.py build/doctests.cpp ${SRC};src/main.cpp
    )

    add_executable(${TestName} ${SRC} build/doctests.cpp)
    target_compile_options(${TestName} PRIVATE "-DVERSION_NAME=\"${VersionName}\"" -g -ggdb -DCATCH2 -DCATCH2_VERSION=${Catch2_VERSION_MAJOR} -fstrict-enums)
    # NOTE: for tests no compiler warnings are required, since these will be emitted by the main file already
    target_link_libraries(${TestName} PRIVATE Catch2::Catch2WithMain)

    # run tests

    if (NOT (${CMAKE_BUILD_TYPE} STREQUAL "Tests"))
        add_custom_command(TARGET ${TestName}
            POST_BUILD
            COMMENT "Running tests..."
            COMMAND $<TARGET_FILE:${TestName}>
        )
    endif()
    
else()
    message(WARNING "Testing disabled - Catch2 not found!")
endif()

# Doxygen

list(FILTER SRC EXCLUDE REGEX "${CMAKE_CURRENT_SOURCE_DIR}/lib/.*")
list(FILTER SRC EXCLUDE REGEX "${CMAKE_CURRENT_SOURCE_DIR}/src/backward(\.cpp|\.hpp)")

find_package(Doxygen)
set(DOXYGEN_GENERATE_HTML YES)
# Set to true for man pages
#set(DOXYGEN_GENERATE_MAN YES)
set(DOXYGEN_QUIET YES)
doxygen_add_docs(
        "docs"
        ${SRC}
        ALL
        WORKING_DIRECTORY "./docs"
    )
