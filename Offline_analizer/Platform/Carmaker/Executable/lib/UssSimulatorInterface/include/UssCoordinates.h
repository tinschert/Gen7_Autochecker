#pragma once
#include "UssPoint.h"
class UssCoordinates : public UssPoint
{
public:
	UssCoordinates();
	UssCoordinates(double x, double y, double z,
				   double rot_x, double rot_y, double rot_z);

	~UssCoordinates();


	/*
	* @brief Get the rotation (X axis) / Roll angle
	* @return X axis rotation [rad]
	*/
	double GetRotationX(void);

	/*
	* @brief Set the rotation (X axis) / Roll angle
	* @param X axis rotation [rad]
	*/
	void SetRotationX(double rot);

	/*
	* @brief Get the rotation (Y axis) / Pitch angle
	* @return Y axis rotation [rad]
	*/
	double GetRotationY(void);

	/*
	* @brief Set the rotation (Y axis) / Pitch angle
	* @param Y axis rotation [rad]
	*/
	void SetRotationY(double rot);

	/*
	* @brief Get the rotation (Z axis) / Yaw angle
	* @return Z axis rotation [rad]
	*/
	double GetRotationZ(void);

	/*
	* @brief Set the rotation (Z axis) / Yaw angle
	* @param Z axis rotation [rad]
	*/
	void SetRotationZ(double rot);


private:
	/*
	* @brief Normalize the given rotation to [-M_PI , M_PI]
	* @param axis rotation [rad]
	*/
	double NormalizeRotationRange(double rot);

	double m_rot_x;
	double m_rot_y;
	double m_rot_z;
};

