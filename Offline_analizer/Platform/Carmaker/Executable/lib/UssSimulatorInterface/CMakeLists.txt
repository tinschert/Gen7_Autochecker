cmake_minimum_required(VERSION 3.8)

project(UssSimulatorInterface)

list(APPEND USS_SIMULATOR_INTERFACE_LIB_HEADERS
    ${CMAKE_CURRENT_LIST_DIR}/include/EchoGenerator.h
    ${CMAKE_CURRENT_LIST_DIR}/include/RbDefines.h
    ${CMAKE_CURRENT_LIST_DIR}/include/RbUltraSonics.h
    ${CMAKE_CURRENT_LIST_DIR}/include/UssSimulator.h
    ${CMAKE_CURRENT_LIST_DIR}/include/UdpMultiTester.h
	${CMAKE_CURRENT_LIST_DIR}/include/UsbMultiTester.h
    ${CMAKE_CURRENT_LIST_DIR}/include/UssCoordinates.h
    ${CMAKE_CURRENT_LIST_DIR}/include/UssPoint.h
    ${CMAKE_CURRENT_LIST_DIR}/include/UssSensor.h
    ${CMAKE_CURRENT_LIST_DIR}/include/UssSensorObject.h
)

list(APPEND USS_SIMULATOR_INTERFACE_LIB_SOURCES
    ${CMAKE_CURRENT_LIST_DIR}/src/EchoGenerator.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/RbDefines.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/RbUltraSonics.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/UssSimulator.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/UdpMultiTester.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/UsbMultiTester.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/UssCoordinates.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/UssPoint.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/UssSensor.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/UssSensorObject.cpp
)

add_library(${PROJECT_NAME} ${USS_SIMULATOR_INTERFACE_LIB_SOURCES} ${USS_SIMULATOR_INTERFACE_LIB_HEADERS})

list(APPEND USS_SIMULATOR_INTERFACE_INC_DIRS
    ${CMAKE_CURRENT_LIST_DIR}/include
)

IF(ARCH MATCHES "xeno")
# header "native/task.h" needed for XENO only provided by CarMaker includes 
list(APPEND USS_SIMULATOR_INTERFACE_INC_DIRS ${CARMAKER_INC_DIR})

ENDIF(ARCH MATCHES "xeno")

target_include_directories(${PROJECT_NAME} PUBLIC 
    ${USS_SIMULATOR_INTERFACE_INC_DIRS}
)