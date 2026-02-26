#include "UssSensorObject.h"
#define _USE_MATH_DEFINES
#include <cmath>
#include <fstream>



UssSensorObject::UssSensorObject()
{
	m_index = 99999;
	m_distance = 0;
	m_alpha = 0;
	m_beta = 0;
}


UssSensorObject::~UssSensorObject()
{
	//delete this;
}

uint64_t UssSensorObject::GetIndex(void)
{
	return m_index;
}

void UssSensorObject::SetIndex(uint64_t index)
{
	m_index = index;
}

double UssSensorObject::GetDistance(void)
{
	return m_distance;
}

double UssSensorObject::CalcDistance(void)
{
	//2D distance calculation used for current sensor model 
	m_distance = CalcDistance3D(GetPositionX(), GetPositionY(), GetPositionZ());
	return m_distance;
}

void UssSensorObject::SetDistance(double distance)
{
	m_distance = distance;
}

double UssSensorObject::GetAlpha(void)
{
	return m_alpha;
}

double UssSensorObject::CalcAlpha(void)
{
	m_alpha = std::atan2(GetPositionY(), GetPositionX());
	return m_alpha;
}

void UssSensorObject::SetAlpha(double angle)
{
	m_alpha = angle;
}

double UssSensorObject::GetBeta(void)
{
	return m_beta;
}

double UssSensorObject::CalcBeta(void)
{
	m_beta = std::atan2(GetPositionZ(), GetPositionX());
	return m_beta;
}

void UssSensorObject::SetBeta(double angle)
{
	m_beta = angle;
}