#include "UssPoint.h"



UssPoint::UssPoint()
{
	m_pos_x = 0;
	m_pos_y = 0;
	m_pos_z = 0;
}

UssPoint::UssPoint(double x, double y, double z) :
	m_pos_x(x), m_pos_y(y), m_pos_z(z)
{

}

UssPoint::~UssPoint()
{

}

/*
* @brief Get the X position
* @return X position [m]
*/

double UssPoint::GetPositionX(void) { return m_pos_x; }

/*
* @brief Set the X position
* @param X position [m]
*/

void UssPoint::SetPositionX(double pos) { m_pos_x = pos; }

/*
* @brief Get the Y position
* @return Y position [m]
*/

double UssPoint::GetPositionY(void) { return m_pos_y; }

/*
* @brief Set the Y position
* @param Y position [m]
*/

void UssPoint::SetPositionY(double pos) { m_pos_y = pos; }

/*
* @brief Get the Z position
* @return Z position [m]
*/

double UssPoint::GetPositionZ(void) { return m_pos_z; }

/*
* @brief Set the Z position
* @param Z position [m]
*/

void UssPoint::SetPositionZ(double pos) { m_pos_z = pos; }
