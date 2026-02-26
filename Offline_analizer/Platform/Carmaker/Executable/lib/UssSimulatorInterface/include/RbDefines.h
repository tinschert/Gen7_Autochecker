#pragma once

#ifndef RBDEFINES_HEADER_
#define RBDEFINES_HEADER_

#include <algorithm>    // std::sort
#include <vector>       // std::vector
#include <map>
#include <array> 
#include <stdint.h>
#include <string>
#include <cmath>
#include <cfloat>

#define _USE_MATH_DEFINES
#include <math.h>

#include "UssCoordinates.h"
#include "UssSensorObject.h"

constexpr auto MAX_OBJECTS = 40;			// Maximum number of objects in the object list
constexpr auto MAX_SENSOR = 12;				// Maximum number of Uss sensors
constexpr auto DEFAULT_SENSOR_RANGE = 5;	// Default sensor range of simulated sensor [m]
constexpr auto DEFAULT_APER_HOZ = 120 ;		// Default horizontal opening angle (used if no or no correct value is delivered) [deg]
constexpr auto DEFAULT_APER_VER = 90 ;		// Default vertical opening angle (used if no or no correct value is delivered) [deg]
constexpr auto OBSERVATION_RANGE = 50 ;		// Maximum range an object is considered for calculation [m]
constexpr auto VERTICAL_POINTS_CONTOUR = 10; // amount of points used for the vertival contour of the objects

typedef std::array<double,3> uss_vec3;
typedef std::array<uss_vec3,3> uss_mat33;

enum eCoordinateSystem : uint8_t {
	COORDINATE_SYSTEM_WORLD = 0,
	COORDINATE_SYSTEM_EGOVEHICLE = 1,
	COORDINATE_SYSTEM_SENSOR = 2,
};

enum eRotationType : int8_t {
	ROTATION_ACTIVE = 1,
	ROTATION_PASSIVE = -1,
};

/* Enumeration for rotation order*/
enum eRotationOrder {
	ROTATIONORDER_XYZ,
	ROTATIONORDER_ZYX
};

enum eContourType : uint8_t {
	CONTOUR_TYPE_RECTANGLE = 0,
	CONTOUR_TYPE_ELLIPSE = 1,
	CONTOUR_TYPE_CAR = 2,
};

enum eRefPointTypeContour : uint8_t {
	REF_PNT_MIDDLE_MIDDLE = 0,
	REF_PNT_MIDDLE_LOW,
	REF_PNT_REAR_LOW
};

/* UssSimulator states*/
enum eUssSimulatorState : uint8_t {
	USSSIMULATOR_OK = 0,			/* operation successful */
	USSSIMULATOR_INVAL_ARG_ERR,     /* function called with invalid argument */
	USSSIMULATOR_THREAD_ERR,		/* communication thread error */
	USSSIMULATOR_THREAD_WARN,		/* communication thread warning */
	USSSIMULATOR_QUEUE_ERR,			/* message queue error */
	USSSIMULATOR_MUTEX_ERR,			/* communication mutex error */
	USSSIMULATOR_COM_ERR,			/* communication error */
	USSSIMULATOR_COM_WARN,			/* communication warning */
	USSSIMULATOR_COM_SOCKET_ERR,	/* Error while creating socket*/
	USSSIMULATOR_COM_SEND_ERR,		/* Error while sending data to UssSimulator */
	USSSIMULATOR_COM_RECV_ERR,		/* Error while receiving data from UssSimulator */
	USSSIMULATOR_DEV_ERR,			/* device error */
	USSSIMULATOR_BUSY_ERR,			/* UssSimulator thread still running */
	USSSIMULATOR_SENSOR_STATUS_ERR, /* Sensor configuration not matching ECU request */
	USSSIMULATOR_NO_UPDATE_ERR,		/* UssSimulator did not receive updated data from simulation */
	USSSIMULATOR_THREAD_ERR_HEALED,	/* Thread Error healed, transit to OK state*/
};

/*Error list*/
enum Rb_StatusList : uint8_t {
	USS_NO_ERROR = 0,
	USS_CLEAR_ERROR,
	ERR_UNEXPECTED_ERROR,
	ERR_INVALID_ARGUMENT,
	ERR_NO_INCJECTION_ACTIVE,
	ERR_SENSORLIST_EMPTY,
	ERR_SENSORLIST_INCOMPLETE,
	ERR_SENSORDATA_WRONG_MAJOR,
	ERR_SENSORDATA_WRONG_MINOR,
	ERR_SENSORDATA_WRONG_STATUS,
	ERR_SENSORDATA_FIRMWARE_MISMATCH,
	ERR_USSSIM_DEVICE_ERR,
	ERR_USSSIM_COMMUNICATION_NO_RESPONSE,
	ERR_USSSIM_COMMUNICATION_NOT_SENT,
	ERR_USSSIM_COMMUNICATION_WARN,
	ERR_USSSIM_COMMUNICATION_SOCKET_ERR,
	ERR_USSSIM_COMMUNICATION_THREAD_ERR,
	ERR_USSSIM_COMMUNICATION_THREAD_WARN,
	ERR_USSSIM_COMMUNICATION_MUTEX_ERR,
	ERR_USSSIM_COMMUNICATION_STILL_RUNNING,
	ERR_USSSIM_COMMUNICATION_NO_UPDATE,
	
};

enum Rb_FcnList {
	RB_INIT,
	RB_TESTRUN_START,
	RB_CALC,
	RB_SHUTDOWN,
	RB_LAST_STATUS,

};

typedef enum tSensor : uint8_t {
	S1,
	S2,
	S3,
	S4,
	S5,
	S6,
	S7,
	S8,
	S9,
	S10,
	S11,
	S12,
	SInval
} tSensor;

enum eSensorState : uint8_t {
	SENSOR_ACTIVE,
	SENSOR_INACTIVE,
};

struct UssObject {
	uint64_t Id;
	UssCoordinates ReferencePoint; /*Object reference point*/
	eCoordinateSystem ReferencePointCoordinates;
	std::vector<UssPoint> ContourPoints; /*Contour points relativ to reference point*/
	double Height;
	uint32_t Type; //for debugging
};

struct UssObjectData {
	int32_t GlobalId;
	double  NearPnt[3];			// [m,m,m]
	double 	NearPntDistance; 	// [m]
	double	NearPntAlpha; 		// [rad]
	double 	IncidentAlpha; 		// [rad]
	double 	IncidentBeta;		// [rad]
	double	Height;				// [m]

	/*operator for sorting the objects vector according to the NearPntDistance */
	bool operator<(UssObjectData const &r) const { return NearPntDistance < r.NearPntDistance; }
};


struct t_SensorData {
	UssObjectData AllObjectList[MAX_OBJECTS];
	double Position_x;						// Mounting position x of the sensor in system coordinates [m]
	double Position_y;						// Mounting position y of the sensor in system coordinates [m]
	double Position_z;						// Mounting position z of the sensor in system coordinates [m]
	double Orientation_y;					// Orientation of the sensor, rotation arround the y-axis [rad]
	double Orientation_z;					// Orientation of the sensor, rotation arround the z-axis [rad]
	double Range;							// Detection range of the sensor [m]
	double Aperture_Hoz;					// Horizontal opening angle of the simulated sensor [rad], optional
	double Aperture_Vert;					// vertical opening angle of the simulated sensor[rad], optional
	int8_t SensorType;						// Sensor Type see @ref eUssSensorTypes
	int8_t SensorVersion;					// Sensor Type see @ref eUssSensorSilicon
	std::string Description;				// Additional description of the sensor, normally the position, optional
	double HeightForHeightClassification;	// When an object is higher then this value it will be considered as "high" by the sensor [m], optional
	eSensorState SensorState;				// When the state is SENSOR_INACTIVE no calculations will be done. [SENSOR_ACTIVE; SENSOR_INACTIVE]
};

 struct tRbSensorConfig {
	int8_t FrontSensorsType;
	int8_t FrontSensorsSilicon;
	int8_t RearSensorsType;
	int8_t RearSensorsSilicon;
	int8_t FrontCornerSensorsType;
	int8_t FrontCornerSensorsSilicon;
	int8_t RearCornerSensorsType;
	int8_t RearCornerSensorsSilicon;
};


//  Sensor type external
enum eUssSensorTypes : int8_t {
	USS_SENSOR_NOT_USED		= -1,
	USS_SENSOR_TYPE_6_0		= 0,
	USS_SENSOR_TYPE_6_1		= 1,
	USS_SENSOR_TYPE_6_5		= 2,
	USS_SENSOR_TYPE_6_50	= 3,
	USS_SENSOR_TYPE_6_51	= 4,
};

//  Sensor type configuration -> used for the message to UssSimulator
enum eUssSensorTypesConfiguration : uint8_t {
	CONF_USS_SENSOR_NOT_USED  = 0x00,
	CONF_USS_SENSOR_TYPE_6_0  = 0x60,
	CONF_USS_SENSOR_TYPE_6_1  = 0x61,
	CONF_USS_SENSOR_TYPE_6_5  = 0x65,
	CONF_USS_SENSOR_TYPE_6_50 = 0x66,
	CONF_USS_SENSOR_TYPE_6_51 = 0x67,
};

// Silicon type external
enum eUssSensorSilicon : int8_t {
	USS_SENSOR_SILICON_AA = 0,
	USS_SENSOR_SILICON_AB = 1,
	USS_SENSOR_SILICON_BA = 2,
	USS_SENSOR_SILICON_CA = 3,
	USS_SENSOR_SILICON_BB = 4,
	USS_SENSOR_SILICON_CC = 5,
};

//  Silicon type configuration -> used for the message to UssSimulator
enum eUssSensorSiliconConfiguration : uint8_t {
	CONF_USS_SENSOR_SILICON_AA = 0xAA,
	CONF_USS_SENSOR_SILICON_AB = 0xAB,
	CONF_USS_SENSOR_SILICON_BA = 0xBA,
	CONF_USS_SENSOR_SILICON_CA = 0xCA,
	CONF_USS_SENSOR_SILICON_BB = 0xBB,
	CONF_USS_SENSOR_SILICON_CC = 0xCC,
};

enum tUssSensorErrorEnum {
	NoError = 0,
	SHORT_TO_GROUND = 1, // set line short to ground
	SHORT_TO_SUPPLY = 2, // set line short to supply voltage
	SENSOR_DISTURBED = 3, // set sensor disturbed
	SENSOR_COM_LINE_OPEN = 4, // set sensor line open
	SENSOR_BLOCKED = 5, // set sensor blocked/blind
	SENSOR_VERSION_WRONG = 6, // set sensor wrong sensor version
	SENSORCLUSTER_OVERCURRENT = 7, // set sensor cluster overcurrent
	SENSOR_COMMUNICATION_ERROR = 8, // set sensor communication error
	SENSOR_INCORRECT_SENDPULSE = 9, // set sensor incorrect send pulse
	SENSOR_OUT_OF_SYNC = 10, // set sensor out of sync
	SENSOR_INTERNAL_ERROR = 11, // set sensor internal error
};


struct tSensorFaultMapping {
	uint8_t SensorNumber;
	tUssSensorErrorEnum SensorError;

	tSensorFaultMapping(uint8_t _sensornumber, tUssSensorErrorEnum _sensorError)
	{
		SensorNumber = _sensornumber;
		SensorError = _sensorError;
	}
};


//has to be cleaned / corrected for BSI integration
#define USS_OUT(fmt, ...) \
	do { \
		printf(fmt, ## __VA_ARGS__); \
	} while (0);
#ifdef XENO
	#include "Log.h"
	#define USS_DBG(fmt, ...) \
	do { \
		Log(fmt, ## __VA_ARGS__); \
	} while (0);
#elif !defined (SUPPRESS_DBG_MESSAGE)
	#define USS_DBG(fmt, ...) \
	do { \
		printf(fmt, ## __VA_ARGS__); \
	} while (0);
#else
	#define USS_DBG(fmt, ...) \
	do { \
	} while (0);
#endif

/*helper functions*/
double deg2rad(double angle);
double rad2deg(double angle);

/*Rotate the coordinate system in zyx order*/
// void coordinateRotation(const double& f_xAlpha, const double& f_yAlpha, const double& f_zAlpha,
// 	double f_x, double f_y, double f_z,
// 	double& f_xNew, double& f_yNew, double& f_zNew);

UssPoint transformPointFromCoordSystem(UssPoint f_point, UssCoordinates f_sourceCoordSystem, eRotationOrder rot_order=ROTATIONORDER_ZYX);

UssPoint translatePointFromCoordSystem(UssPoint f_point, UssCoordinates f_sourceCoordSystem);

UssPoint rotatePointFromCoordSystem(UssPoint f_point, UssCoordinates f_sourceCoordSystem, eRotationOrder rot_order);

UssPoint transformPointToCoordSystem(UssPoint f_point, UssCoordinates f_targetCoordSystem);

UssPoint translatePointToCoordSystem(UssPoint f_point, UssCoordinates f_targetCoordSystem);

UssPoint rotatePointToCoordSystem(UssPoint f_point, UssCoordinates f_targetCoordSystem);

UssPoint rotateAroundX(UssPoint f_point, double angle);

UssPoint rotateAroundY(UssPoint f_point, double angle);

UssPoint rotateAroundZ(UssPoint f_point, double angle);

template <typename T> T CalculateDifference(T &current, T &previous) {
	return (current - previous);
}

template <typename T> bool  allequal(const T &t, const T &u) {
	return t == u;
}
template <typename T, typename... Others> bool allequal(const T &t, const T &u, Others const &... args) {
	return (t == u) && allequal(u, args...);
}

template <typename T> T CalcDistance2D(T val1, T val2) {
	return sqrt(pow(val1, 2) + pow(val2, 2));
}

template <typename T> T CalcDistance3D(T val1, T val2, T val3) {
	return sqrt(pow(val1, 2) + pow(val2, 2) + pow(val3, 2));
}

double round3Digits(double val);
UssPoint MidUssPoint(UssPoint Pnt1, UssPoint Pnt2);

std::vector<UssPoint> CreateContour3D(double length, double width, double height,
	eContourType ContourType, eRefPointTypeContour RefPntContour);

//sum up two vetors (3x1)
uss_vec3 operator+(const uss_vec3& vec_a, const uss_vec3& vec_b);
//multiply 3x3 matrix with vector(3x1)
uss_vec3 operator*(const uss_mat33& mat, const uss_vec3& vec);
//multiply 3x3 matrix with 3x3 matrix
uss_mat33 operator*(const uss_mat33& mat_a, const uss_mat33& mat_b);

uss_mat33 CalcRotationMatrix(double rot_x, double rot_y, double rot_z, eRotationType rot_type, eRotationOrder rot_order=ROTATIONORDER_ZYX);
uss_mat33 CalcTransposedMatrix33(uss_mat33 mat);
uss_mat33 CalcInverseMatrix33(uss_mat33 mat);
uss_vec3 CalcEulerAngles(uss_mat33 rotationmatrix);

#endif //RBDEFINES_HEADER_