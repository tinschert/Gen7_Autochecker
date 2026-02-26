#pragma once

#include "UssPoint.h"
#include "RbDefines.h"

class UssSensorObject : public UssPoint
{
public:
	UssSensorObject();

	~UssSensorObject();
	uint64_t GetIndex(void);
	void SetIndex(uint64_t index);
	double GetDistance(void);
	double CalcDistance(void);
	void SetDistance(double distance);
	double GetAlpha(void);
	double CalcAlpha(void);
	void SetAlpha(double angle);
	double GetBeta(void);
	double CalcBeta(void);
	void SetBeta(double angle);
	



private:
	uint64_t m_index;
	double m_distance;
	double m_alpha;
	double m_beta;
	

};