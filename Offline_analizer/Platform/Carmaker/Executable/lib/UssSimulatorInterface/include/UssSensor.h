#pragma once

#include "RbDefines.h"

class UssSensor
{
public:
	UssSensor(tSensor SensorID, double Position_x, double Position_y, double Position_z,
		double Orientation_y, double Orientation_z, double Range,
		double Aperture_Hoz, double Aperture_Vert);
	UssSensor(tSensor SensorID, double Position_x, double Position_y, double Position_z,
		double Orientation_y, double Orientation_z, double Range,
		double Aperture_Hoz, double Aperture_Vert, std::string Description,
		double HeightForHeightClassification, eSensorState SensorState);

	~UssSensor(void);


	/*Transfer object data (in world coordinats) to USS compatible object data
	* and add object to object list
	*/
	bool AddObject(UssObject ObjectData, UssCoordinates EgoVehicle);

	/*This function is used if the data is USS compatible */
	void AddObject(uint64_t GlobalID, UssPoint NearPnt, double NearPntDistance, double NearPntAlpha,
		double IncidentAlpha, double IncidentBeta, double Height);

	/*Get object list*/
	std::vector<UssObjectData> GetObjects(void);

	/*Clear object list, everything is set to 0 */
	void ClearObjects(void);

	/*
	* @brief Get the ID of the sensor
	* @return SensorId (tSensor)
	*/
	tSensor GetSensorID(void);

	/*
	* @brief Set the ID of the sensor
	* @param SensorId (tSensor)
	*/
	void SetSensorID(tSensor id);

	/*
	* @brief Get the coordinate information of the sensor
	* @return SensorId (tSensor)
	*/
	UssCoordinates GetSensorCoordinates(void);

	/*
	* @brief Get the range of the sensor
	* @return range [m]
	*/
	double GetSensorRange(void);

	/*
	* @brief Set the range of the sensor
	* @param range [m]
	*/
	void SetSensorRange(double range);

	/*
	* @brief Get the horizontal aperture of the sensor
	* @return aperture horizontal [rad]
	*/
	double GetSensorApertureHorizontal(void);

	/*
	* @brief Set the horizontal aperture of the sensor
	* @param aperture horizontal [rad]
	*/
	void SetSensorApertureHorizontal(double aper);

	/*
	* @brief Get the vertical aperture of the sensor
	* @return aperture vertical [rad]
	*/
	double GetSensorApertureVertical(void);

	/*
	* @brief Set the vertical aperture of the sensor
	* @param aperture vertical [rad]
	*/
	void SetSensorApertureVertical(double aper);


	/*
	* @brief Set the description of the sensor
	* @param description string of the sensor
	*/
	void SetSensorDescription(std::string description);

	/*
	* @brief Get the description of the sensor
	* @return the description of the sensor
	*/
	std::string GetSensorDescription(void);

	/*
	* @brief Set the height for the height classification of the sensor
	* @param height for the heigt classification
	*/
	void SetHeightForHeightClassification(double HeightForHeightClassification);
	
	/*
	* @brief Get the border from which height objects should be considered as high for the sensor
	* @return the height for the height classification of the sensor
	*/
	double GetHeightForHeightClassification(void);

	/*
	* @brief Set the state of the sensor. When the state is SENSOR_INACTIVE no calculations will be done.
	* @param SENSOR_INACTIVE or SENSOR_ACTIVE
	*/
	void SetSensorState(eSensorState SensorState);

	/*
	* @brief Get the state of the sensor. When the state is SENSOR_INACTIVE no calculations will be done.
	* @return SENSOR_INACTIVE or SENSOR_ACTIVE
	*/
	eSensorState GetSensorState(void);

private:
	
	//internal functions
	void SensorInitCommon(void);
	UssObjectData CreateObject(uint64_t GlobalID, UssPoint NearPnt, double NearPntDistance, double NearPntAlpha,
		double IncidentAlpha, double IncidentBeta, double Height);
	bool IsObjectInFoV(UssObject ObjectData, UssCoordinates EgoVehicle, UssPoint * NearPnt, double * NearPointDistance, double * NearPointAlpha, double *IncidentAlpha, double *IncidentBeta);
	bool IsPointInFoV(UssSensorObject PointData);
	UssSensorObject GetNearestPointBetweenTwoPoints(UssSensorObject pnt1, UssSensorObject pnt2, uint64_t index);
	double CalcIncidentAngle(UssSensorObject NearestPoint, UssSensorObject NeighbourPoint, uint8_t incAngleIdentifier);
	std::vector<UssSensorObject> GetObjectDataSensorCoord(UssObject ObjectData, UssCoordinates EgoVehicle);
	std::vector<UssSensorObject> GetObjectDataSensorCoord(UssObject ObjectData);
	//bool CompareUssSensorObjectDistance(UssSensorObject SObj1, UssSensorObject SObj2);

	/*
	* @brief Given three collinear points p, q, r, the function checks if  point q lies on line segment 'pr'
	*/
	bool IsPointOnSegment(UssPoint p, UssPoint q, UssPoint r);
	
	/*
	* @brief To find orientation of ordered triplet (p, q, r).
	* The function returns following values
	* 0 --> p, q and r are collinear
	* 1 --> Clockwise
	* 2 --> Counterclockwise
	*/
	uint8_t orientationTriplet(UssPoint p, UssPoint q, UssPoint r);
	
	/*
	* @brief The function that returns true if line segment 'p1q1' and 'p2q2' intersect.
	*/
	bool doLineSegmentsIntersect(UssPoint p1, UssPoint q1, UssPoint p2, UssPoint q2);

	/*
	* @brief Returns true if the given point (x,y) lies inside the given contour (or on the border)
	* @brief z -coordinate will be set to 0 and not considered
	* @param contour - 2D-contour (x,y) of the object 
	* @param sensorpos - position of the sensor (x,y)
	*/
	bool IsPointInsideContour(std::vector<UssPoint> contour, UssPoint sensorpos);


	//internal variables
	tSensor m_sensor_id;
	std::vector<UssObjectData> m_objects;
	UssCoordinates m_coordinates;
	double m_range;
	double m_aper_hoz;
	double m_aper_ver;
	std::string m_description;
	double m_HeightForHeightClassification;
	eSensorState m_SensorState;

	//helper functions
};

