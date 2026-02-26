#pragma once

#include <Config.h>

#include <array>
#include <cstdint>

namespace RBSData
{

/// @brief An enum for radar positions in the tRBSData m_radars array
enum Radar : int32_t
{
    FC = 0,
    FL = 1,
    FR = 2,
    RR = 3,
    RL = 4
};

/// @brief A structure defining the data of a single carmaker object
#pragma pack(push, 1) // Force 1-byte alignment
struct ObjectData
{
    uint32_t m_objID {0};
    uint32_t m_classification {0};
    uint32_t m_radarType {0};

    double m_dxN {0.0};
    double m_dyN {0.0};
    double m_dzN {0.0};

    double m_vxN {0.0};
    double m_vyN {0.0};

    double m_axN {0.0};
    double m_ayN {0.0};

    double m_dWidthN {0.0};
    double m_dLengthN {0.0};

    double m_RCS {0.0};
    double m_SNR {0.0};
    double m_alpPiYawAngleN {0.0};
    double m_SignalStrength {0.0};
};
#pragma pack(pop) // End force 1-byte alignment

/// @brief A structure defining the data of a single radar from CarMaker
#pragma pack(push, 1) // Force 1-byte alignment
struct RadarData
{
    double m_mountPosX {0.0};

    double m_mountPosY {0.0};

    double m_mountPosZ {0.0};

    uint32_t m_sensorBlocked {0};

    uint32_t m_objectCount {0};

    std::array<ObjectData, Config::Radar::MAX_RADAR_OBJECTS> m_objects;
};
#pragma pack(pop) // End force 1-byte alignment

/// @brief A structure representing the RBS data to send from CarMaker to CANoe
struct tRBSData
{
    std::array<RadarData, Config::Radar::TOTAL_RADAR_COUNT> m_radars;
};

};