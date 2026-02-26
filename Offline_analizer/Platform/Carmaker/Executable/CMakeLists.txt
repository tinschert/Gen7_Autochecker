cmake_minimum_required(VERSION 3.12)

project(CarMakerFord)

IF(NOT DEFINED CARMAKER_DIR)
    set(CARMAKER_DIR C:/IPG/carmaker/win64-12.0.2)
ENDIF()

IF(NOT EXISTS ${CARMAKER_DIR})
    message( FATAL_ERROR "Could not find CarMaker installation folder '${CARMAKER_DIR}'")
ENDIF()

# CarMaker version info
set(CARMAKER_VER 12.0.2)
set(CARMAKER_NUMVER 120002)
set(CARMAKER_SETVER 12.0.2)

list(APPEND WIN64_LIBS  
    ws2_32
    psapi
    winspool
    user32
    advapi32
    legacy_stdio_definitions
)

add_definitions(-DWIN32 -DWIN64 -DCM_NUMVER=${CARMAKER_NUMVER} -DCM_SIL -D__USE_MINGW_ANSI_STDIO)

option(USS_USE_BSI "Use USS Interface with BSI" ON)
# option(RBS_USE_BSI "Use RBS with BSI" ON)
# option(USE_BSI "Use with BSI" ON)

set(CMAKE_CXX_STANDARD 23)

set(ARCH win64)

set(EXE_EXT ".${ARCH}.exe")
set(APP_VER "Car_Generic <insert.your.version.no>")
set(APP_NAME "CarMaker")

set(TARGET_SUFFIX "${EXE_EXT}")

set(CARMAKER_BIN_DIR ${CARMAKER_DIR}/bin)
set(CARMAKER_LIB_DIR ${CARMAKER_DIR}/lib)
list(APPEND CARMAKER_INC_DIR ${CARMAKER_DIR}/include)
set(CARMAKER_GUI_DIR ${CARMAKER_DIR}/GUI)

# CarMaker Libraries
set(CARMAKER_LIB 	carmaker)
set(CAR_LIB 	    car)
set(MCYCLE_LIB 	    mcycle)
set(TRUCK_LIB 	    truck)
set(DRIVER_LIB 	    ipgdriver)
set(ROAD_LIB 	    ipgroad)
set(TIRE_LIB 	    ipgtire)
set(APO_LIB 	    apo-client-win64)
set(INFO_LIB 	    infofile)
set(Z_LIB 		    z-${ARCH})
set(URI_LIB         uriparser)

list(APPEND CARMAKER_CORE_LIBS 
    ${CARMAKER_LIB_DIR}/lib${CAR_LIB}.a
    ${CARMAKER_LIB_DIR}/lib${CARMAKER_LIB}.a
    ${CARMAKER_LIB_DIR}/lib${DRIVER_LIB}.a
    ${CARMAKER_LIB_DIR}/lib${ROAD_LIB}.a
    ${CARMAKER_LIB_DIR}/lib${TIRE_LIB}.a    
    ${CARMAKER_LIB_DIR}/lib${INFO_LIB}.a
    ${CARMAKER_LIB_DIR}/lib${Z_LIB}.a 
    ${CARMAKER_LIB_DIR}/lib${URI_LIB}.a
    ${CARMAKER_LIB_DIR}/libcompat_${ARCH}.a
    ${WIN64_LIBS}
)

# list used for creation of app_tmp.c (includes path and file extension)
list(APPEND APP_TMP_CORE_LIB_LIST 
    ${CARMAKER_LIB_DIR}/${CAR_LIB}
    ${CARMAKER_LIB_DIR}/${CARMAKER_LIB}
    ${CARMAKER_LIB_DIR}/${DRIVER_LIB}
    ${CARMAKER_LIB_DIR}/${ROAD_LIB}
    ${CARMAKER_LIB_DIR}/${TIRE_LIB}   
)

IF(EXISTS ${CARMAKER_BIN_DIR}/cmplugutil)
    set(CMPU ${CARMAKER_BIN_DIR}/cmplugutil)
ENDIF()

set(CARMAKER_APPINFO_CMD ${CARMAKER_BIN_DIR}/CreateCarMakerAppInfo.exe CACHE FILEPATH "Binary program that is run inside CarMaker install folder to generate some files to compile CarMaker templates")

IF(CMAKE_BUILD_TYPE MATCHES Debug)
    message("Building Binaries for Debugging...")
ELSE()
    add_definitions(-DNDEBUG)
ENDIF()

link_directories(${CARMAKER_LIB_DIR})

add_definitions(-DVFC_ENABLE_FLOAT64_TYPE)

add_subdirectory(${CMAKE_SOURCE_DIR}/../Common/UdpPacket ${CMAKE_SOURCE_DIR}/buildx64/common)
# add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/../../../RbSimAdapter/CarMaker/platform CarMakerAdapterPlatform)
add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/lib/UssSimulatorInterface UssSimulatorInterface)

# define new unique target name
set(FORD_HIL_TARGET ${CMAKE_PROJECT_NAME}AdasHil)


list(APPEND FORD_HIL_HEADERS
    ${CMAKE_CURRENT_LIST_DIR}/src/RB_CarMaker_Custom.h
    ${CMAKE_CURRENT_LIST_DIR}/src/User.h
    ${CMAKE_CURRENT_LIST_DIR}/src/ussInterfaceAdapterFord.h
    ${CMAKE_CURRENT_LIST_DIR}/src/common/objectData.h
    ${CMAKE_CURRENT_LIST_DIR}/src/car/carParametersDVAs.h
    ${CMAKE_CURRENT_LIST_DIR}/src/car/fillCarParameters.h
    ${CMAKE_CURRENT_LIST_DIR}/src/groundTruth/fillLineData.h
    ${CMAKE_CURRENT_LIST_DIR}/src/groundTruth/lineDataDVAs.h
    ${CMAKE_CURRENT_LIST_DIR}/src/radarObject/fillRadarObjectData.h
    ${CMAKE_CURRENT_LIST_DIR}/src/radarObject/radarObjectDataDVAs.h
    ${CMAKE_CURRENT_LIST_DIR}/src/traffic/trafficDVAs.h
    ${CMAKE_CURRENT_LIST_DIR}/src/traffic/fillTrafficObject.h
    ${CMAKE_CURRENT_LIST_DIR}/src/trafficSign/trafficSignDVAs.h
    ${CMAKE_CURRENT_LIST_DIR}/src/trafficSign/fillTrafficSignData.h
    ${CMAKE_CURRENT_LIST_DIR}/src/videoObject/fillVideoObjectData.h
    ${CMAKE_CURRENT_LIST_DIR}/src/videoObject/videoObjectDataDVAs.h
    ${CMAKE_CURRENT_LIST_DIR}/src/motion/fillMotion.h
    ${CMAKE_CURRENT_LIST_DIR}/src/motion/motionDVAs.h
    ${CMAKE_CURRENT_LIST_DIR}/src/radarTS/RadarTS.h
)

list(APPEND FORD_HIL_SOURCES
    ${CMAKE_CURRENT_LIST_DIR}/src/CM_Main.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/CM_Vehicle.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/IO.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/RB_CarMaker_Custom.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/User.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/UdpClient.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/ussInterfaceAdapterFord.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/car/carParametersDVAs.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/car/fillCarParameters.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/groundTruth/fillLineData.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/groundTruth/lineDataDVAs.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/radarObject/fillRadarObjectData.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/radarObject/radarObjectDataDVAs.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/traffic/fillTrafficObject.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/traffic/trafficDVAs.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/trafficSign/trafficSignDVAs.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/trafficSign/fillTrafficSignData.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/videoObject/fillVideoObjectData.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/videoObject/videoObjectDataDVAs.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/motion/fillMotion.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/motion/motionDVAs.cpp
)

# add RB custom libs (built by this project)
list(APPEND FORD_HIL_CUSTOM_LIBS
    # RbRoadEvaluation
    # RbTrafficEvaluation
    # RbAudiRbsAdapterCM
    UssSimulatorInterface
    UdpPacket
    ${CMAKE_CURRENT_LIST_DIR}/lib/ROTA/libRadarTS_GUI_Apo_${ARCH}.a
    ${CMAKE_CURRENT_LIST_DIR}/lib/ROTA/libRadarTS_${ARCH}.a
    ${CMAKE_CURRENT_LIST_DIR}/lib/ROTA/libsudp_${ARCH}.a
)


# fetch git commit; remark: needs to re-run cmake configure to have effect
execute_process(
    COMMAND git log -1 --format=%h
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    OUTPUT_VARIABLE GIT_COMMIT
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

# custom command to generate app_tmp.c source file
add_custom_command(
    OUTPUT  app_tmp.c
    COMMAND ${CARMAKER_APPINFO_CMD}
        =av "ADAS-HIL CarMaker Simulation (commit: ${GIT_COMMIT})"
        =sv "${CARMAKER_SETVER}"
        =arch "${ARCH}"
        =c "Created using cmake"
        =cf "Flags auto determined"
        =libs ${FORD_HIL_CUSTOM_LIBS} ${APP_TMP_CORE_LIB_LIST} > app_tmp.c
    COMMENT "Generating app_tmp.c"
    DEPENDS ${FORD_HIL_CUSTOM_LIBS}
)

add_executable(${FORD_HIL_TARGET} ${FORD_HIL_SOURCES} ${FORD_HIL_HEADERS} ${CMAKE_CURRENT_BINARY_DIR}/app_tmp.c)

set_target_properties(${FORD_HIL_TARGET} PROPERTIES OUTPUT_NAME ${APP_NAME})
set_target_properties(${FORD_HIL_TARGET} PROPERTIES SUFFIX ${TARGET_SUFFIX})

target_include_directories(${FORD_HIL_TARGET} PRIVATE
    ${CARMAKER_INC_DIR}
    ${CMAKE_SOURCE_DIR}/../Common/
    src
)

target_link_libraries(${FORD_HIL_TARGET}
    ${FORD_HIL_CUSTOM_LIBS}
    ${CARMAKER_CORE_LIBS}
)

target_compile_definitions(${FORD_HIL_TARGET} PRIVATE 
    UDP_INTERFACE_ON
    RB_INTERFACE_ON
    RB_RADAR_OBJ_SIM_ON
    RB_VIDEO_OBJ_SIM_ON
    RB_TRAFFIC_OBJ_SIM_ON
    RB_TRAFFIC_SIGN_SIM_ON
    RB_LINE_SIM_ON
    RB_VEH_MODEL_SIM_ON
    #RB_INT_VARIANT_HANDLING_ON
    #WITH_RadarTS
    SIMULATE_USS 
    USS_SIM_TYPE=UDP
)

add_custom_command(
    TARGET ${FORD_HIL_TARGET}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different 
            $<TARGET_FILE:${FORD_HIL_TARGET}>  # Gets the full path to the target executable
            ${CMAKE_CURRENT_LIST_DIR}/../                 # Destination directory (root in this case)
    COMMENT "Copying $<TARGET_FILE:${FORD_HIL_TARGET}> to root platform carmaker folder"
)

install(TARGETS ${FORD_HIL_TARGET}
    DESTINATION ${CMAKE_CURRENT_LIST_DIR}
)