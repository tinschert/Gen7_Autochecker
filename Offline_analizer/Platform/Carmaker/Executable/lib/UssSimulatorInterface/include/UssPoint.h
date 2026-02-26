#pragma once
class UssPoint
{
public:
	UssPoint();
	UssPoint(double x, double y, double z);
	~UssPoint();


	/*
	* @brief Get the X position
	* @return X position [m]
	*/
	double GetPositionX(void);

	/*
	* @brief Set the X position
	* @param X position [m]
	*/
	void SetPositionX(double pos);

	/*
	* @brief Get the Y position
	* @return Y position [m]
	*/
	double GetPositionY(void);

	/*
	* @brief Set the Y position
	* @param Y position [m]
	*/
	void SetPositionY(double pos);

	/*
	* @brief Get the Z position
	* @return Z position [m]
	*/
	double GetPositionZ(void);

	/*
	* @brief Set the Z position
	* @param Z position [m]
	*/
	void SetPositionZ(double pos);

private:
	double m_pos_x;
	double m_pos_y;
	double m_pos_z;
};