#include "UssCoordinates.h"
#include <cmath>
#define _USE_MATH_DEFINES
#include <math.h>


UssCoordinates::UssCoordinates()
{
	m_rot_x = 0;
	m_rot_y = 0;
	m_rot_z = 0;
}

UssCoordinates::UssCoordinates(double x, double y, double z, double rot_x, double rot_y, double rot_z) : UssPoint(x,y,z), m_rot_x(rot_x), m_rot_y(rot_y), m_rot_z(rot_z)
{

}


UssCoordinates::~UssCoordinates()
{
	//delete this;
}

/*
* @brief Get the rotation (X axis)
* @return X axis rotation [rad]
*/

double UssCoordinates::GetRotationX(void) { return m_rot_x; }

/*
* @brief Set the rotation (X axis)
* @param X axis rotation [rad]
*/

void UssCoordinates::SetRotationX(double rot) { m_rot_x = NormalizeRotationRange(rot); }

/*
* @brief Get the rotation (Y axis)
* @return Y axis rotation [rad]
*/

double UssCoordinates::GetRotationY(void) { return m_rot_y; }

/*
* @brief Set the rotation (Y axis)
* @param Y axis rotation [rad]
*/

void UssCoordinates::SetRotationY(double rot) { m_rot_y = NormalizeRotationRange(rot); }

/*
* @brief Get the rotation (Z axis)
* @return Z axis rotation [rad]
*/

double UssCoordinates::GetRotationZ(void) { return m_rot_z; }

/*
* @brief Set the rotation (Z axis)
* @param Z axis rotation [rad]
*/

void UssCoordinates::SetRotationZ(double rot) { m_rot_z = NormalizeRotationRange(rot); }

double UssCoordinates::NormalizeRotationRange(double rot)
{
	rot = std::fmod(rot + M_PI, 2 * M_PI);
	if (rot <= 0)
	{
		rot += 2 * M_PI;
	}

	return (rot - M_PI);
}
