#include "RbDefines.h"

double deg2rad(double angle) { return (M_PI / 180)*angle; }
double rad2deg(double angle) { return (180 / M_PI)*angle; }

uss_vec3 operator+(const uss_vec3& vec_a, const uss_vec3& vec_b)
{
	uss_vec3 sum = { 0,0,0 };

	for (int i = 0; i < 3; ++i)
	{
		sum[i] = vec_a[i] + vec_b[i];
	}
	return sum;
}

uss_vec3 operator*(const uss_mat33& mat, const uss_vec3& vec)
{
	uint8_t i, j;
	const auto dim = mat.size();

	uss_vec3 prod = { 0,0,0 };

	for (i = 0; i < dim; i++) {
		prod[i] = 0.;
		for (j = 0; j < dim; j++)
			prod[i] += mat[i][j] * vec[j];
	}
	return prod;
}

uss_mat33 operator*(const uss_mat33& mat_a, const uss_mat33& mat_b) {

	uss_mat33 product{ { { 0,0,0 },{ 0,0,0 },{ 0,0,0 } } };
	const auto dim = mat_a.size(); //size of mat_a and mat_b are always the same
	uss_vec3 l_row = { 0,0,0 };
	uss_mat33 l_prod{ { { 0,0,0 },{ 0,0,0 },{ 0,0,0 } } };

	for (uint8_t row = 0; row < dim; row++) {
		for (uint8_t col = 0; col < dim; col++) {
			for (uint8_t inner = 0; inner < dim; inner++) {
				l_prod[row][col] += mat_a[row][inner] * mat_b[inner][col];
			}
			l_row[col] = l_prod[row][col];
		}
		product[row] = l_row;
	}

	return product;
}

uss_mat33 CalcRotationMatrix(double rot_x, double rot_y, double rot_z, eRotationType rot_type, eRotationOrder rot_order)
{
	uss_mat33 Rx;
	uss_mat33 Ry;
	uss_mat33 Rz;

	double l_sign = (double)rot_type;

	//fill matrix structures 
	Rx[0] = { 1,				0, 0 };
	Rx[1] = { 0,  std::cos(rot_x), l_sign * -std::sin(rot_x) };
	Rx[2] = { 0, l_sign * std::sin(rot_x), std::cos(rot_x) };
	
	Ry[0] = { std::cos(rot_y),	0, l_sign * std::sin(rot_y) };
	Ry[1] = { 0,				1,	0 };
	Ry[2] = { l_sign * -std::sin(rot_y),	0,	std::cos(rot_y) };

	Rz[0] = { std::cos(rot_z),	l_sign * -std::sin(rot_z), 0 };
	Rz[1] = { l_sign * std::sin(rot_z),	std::cos(rot_z), 0 };
	Rz[2] = { 0,				0,				 1 };

	switch (rot_order)
	{
	case ROTATIONORDER_XYZ:
	{
		//create rotation matrix for x-y-z direction
		return (Rx * Ry * Rz);
	}
	case ROTATIONORDER_ZYX:
	{
		//create rotation matrix for z-y-x direction
		return (Rz * Ry * Rx);
	}
	default:
		return (Rz * Ry * Rx);
	}	
}

uss_mat33 CalcTransposedMatrix33(uss_mat33 mat)
{
	uss_mat33 matrix_transposed;

	const auto dim = mat.size();

	for (uint8_t i = 0; i < dim; ++i)
	{
		for (uint8_t j = 0; j < dim; ++j)
		{
			matrix_transposed[j][i] = mat[i][j];
		}
	}

	return matrix_transposed;
}

uss_mat33 CalcInverseMatrix33(uss_mat33 mat)
{

	double determinant =
		mat[0][0] * (mat[1][1] * mat[2][2] - mat[2][1] * mat[1][2]) -
		mat[0][1] * (mat[1][0] * mat[2][2] - mat[1][2] * mat[2][0]) +
		mat[0][2] * (mat[1][0] * mat[2][1] - mat[1][1] * mat[2][0]);
	double inversedeterminant = 1 / determinant;

	uss_mat33 minv;
	uss_vec3 l_rows = { 0,0,0 };
	l_rows[0] = (mat[1][1] * mat[2][2] - mat[2][1] * mat[1][2]) * inversedeterminant;
	l_rows[1] = (mat[0][2] * mat[2][1] - mat[0][1] * mat[2][2]) * inversedeterminant;
	l_rows[2] = (mat[0][1] * mat[1][2] - mat[0][2] * mat[1][1]) * inversedeterminant;
	minv[0] = l_rows;
	l_rows[0] = (mat[1][2] * mat[2][0] - mat[1][0] * mat[2][2]) * inversedeterminant;
	l_rows[1] = (mat[0][0] * mat[2][2] - mat[0][2] * mat[2][0]) * inversedeterminant;
	l_rows[2] = (mat[1][0] * mat[0][2] - mat[0][0] * mat[1][2]) * inversedeterminant;
	minv[1] = l_rows;
	l_rows[0] = (mat[1][0] * mat[2][1] - mat[2][0] * mat[1][1]) * inversedeterminant;
	l_rows[1] = (mat[2][0] * mat[0][1] - mat[0][0] * mat[2][1]) * inversedeterminant;
	l_rows[2] = (mat[0][0] * mat[1][1] - mat[1][0] * mat[0][1]) * inversedeterminant;
	minv[2] = l_rows;
	return minv;
}

uss_vec3 CalcEulerAngles(uss_mat33 rot_mat)
{
	uss_vec3 l_rotations = { 0,0,0 };


	if (rot_mat[0][0] == 0 && rot_mat[1][0] == 0)
	{
		l_rotations[0] = std::atan2(rot_mat[0][1], rot_mat[1][1]);
		l_rotations[1] = M_PI_2;
		l_rotations[2] = 0;
	}
	else
	{

		l_rotations[0] = std::atan2(rot_mat[2][1], rot_mat[2][2]);
		l_rotations[1] = std::atan2(-rot_mat[2][0], sqrt(pow(rot_mat[0][0], 2) + pow(rot_mat[1][0], 2)));
		l_rotations[2] = std::atan2(rot_mat[1][0], rot_mat[0][0]);

		if (rot_mat[2][2] <= 0) //turn the rotation of the y-axis to the second valid case
		{
			l_rotations[0] = M_PI - l_rotations[0];
			l_rotations[1] = M_PI - l_rotations[1];
			l_rotations[2] = M_PI - l_rotations[2];
		}
	}

	return l_rotations;
}

 void coordinateRotation(const double& f_xAlpha, const double& f_yAlpha, const double& f_zAlpha,
 	double f_x, double f_y, double f_z,
 	double& f_xNew, double& f_yNew, double& f_zNew)
 {
 	//1. Step: transform in alternate coordinate system: rotation (z-axis)
 	f_xNew = f_x * ::std::cos(f_zAlpha) - f_y * ::std::sin(f_zAlpha);
 	f_yNew = f_x * ::std::sin(f_zAlpha) + f_y * ::std::cos(f_zAlpha);
 	f_zNew = f_z;

 	//2. Step: transform in alternate coordinate system: rotation (y-axis)
 	long double l_x = f_xNew * ::std::cos(f_yAlpha) + f_zNew * ::std::sin(f_yAlpha);
 	long double l_y = f_yNew;
 	long double l_z = -f_xNew * ::std::sin(f_yAlpha) + f_zNew * ::std::cos(f_yAlpha);

 	//3. Step: transform in alternate coordinate system: rotation (x-axis)
 	f_xNew = l_x;
 	f_yNew = l_y * ::std::cos(f_xAlpha) - l_z * ::std::sin(f_xAlpha);
 	f_zNew = l_y * ::std::sin(f_xAlpha) + l_z * ::std::cos(f_xAlpha);
 }

/**
 * @brief transforms a point
 *
 * @param f_point point in f_sourceCoordSystem to transform
 * @param f_sourceCoordSystem transformation from own (local) coordinate system to (source) coordinate system of the point
 * @return UssPoint transformed point from f_sourceCoordSystem into own (local) coordinate system
 */
UssPoint transformPointFromCoordSystem(UssPoint f_point, UssCoordinates f_sourceCoordSystem, eRotationOrder rot_order)
{
	return translatePointFromCoordSystem(rotatePointFromCoordSystem(f_point, f_sourceCoordSystem, rot_order), f_sourceCoordSystem);
}

UssPoint translatePointFromCoordSystem(UssPoint f_point, UssCoordinates f_sourceCoordSystem)
{
	return UssPoint(
		f_point.GetPositionX() + f_sourceCoordSystem.GetPositionX(),
		f_point.GetPositionY() + f_sourceCoordSystem.GetPositionY(),
		f_point.GetPositionZ() + f_sourceCoordSystem.GetPositionZ()
	);
}

UssPoint rotatePointFromCoordSystem(UssPoint f_point, UssCoordinates f_sourceCoordSystem, eRotationOrder rot_order)
{
	switch (rot_order)
	{
	case ROTATIONORDER_XYZ:
		{
			UssPoint result = rotateAroundX(f_point,f_sourceCoordSystem.GetRotationX());
			result = rotateAroundY(result, f_sourceCoordSystem.GetRotationY());
			return rotateAroundZ(result,f_sourceCoordSystem.GetRotationZ());	
		}	
	default:
		{
			UssPoint result = rotateAroundZ(f_point, f_sourceCoordSystem.GetRotationZ());
			//2. Step: transform in alternate coordinate system: rotation (y-axis)
			result = rotateAroundY(result, f_sourceCoordSystem.GetRotationY());
			//3. Step: transform in alternate coordinate system: rotation (x-axis)
			return rotateAroundX(result, f_sourceCoordSystem.GetRotationX());
		}
	}
}


/**
 * @brief transforms a point
 *
 * @param f_point point in own (local) coordinate system to transform
 * @param f_targetCoordSystem transformation from own (local) coordinate system to (target) coordinate system of the point
 * @return UssPoint transformed point from own (local) coordinate system into (target) coordinate system
 */
UssPoint transformPointToCoordSystem(UssPoint f_point, UssCoordinates f_targetCoordSystem)
{
	return rotatePointToCoordSystem(translatePointToCoordSystem(f_point, f_targetCoordSystem), f_targetCoordSystem);
}

UssPoint translatePointToCoordSystem(UssPoint f_point, UssCoordinates f_targetCoordSystem)
{
	// translate back
	return UssPoint(
		f_point.GetPositionX() - f_targetCoordSystem.GetPositionX(),
		f_point.GetPositionY() - f_targetCoordSystem.GetPositionY(),
		f_point.GetPositionZ() - f_targetCoordSystem.GetPositionZ()
	);
}


UssPoint rotatePointToCoordSystem(UssPoint f_point, UssCoordinates f_targetCoordSystem)
{
	//1. Step: rotate back around (x-axis)
	UssPoint result = rotateAroundX(f_point, -f_targetCoordSystem.GetRotationX());

	//2. Step: rotate back around (y-axis)
	result = rotateAroundY(result, -f_targetCoordSystem.GetRotationY());

	//3. Step: rotate back around (z-axis)
	return rotateAroundZ(result, -f_targetCoordSystem.GetRotationZ());
}

UssPoint rotateAroundX(UssPoint f_point, double angle)
{
	double f_xNew = f_point.GetPositionX();
	double f_yNew = f_point.GetPositionY() * ::std::cos(angle) - f_point.GetPositionZ() * ::std::sin(angle);
	double f_zNew = f_point.GetPositionY() * ::std::sin(angle) + f_point.GetPositionZ() * ::std::cos(angle);

	return UssPoint(f_xNew, f_yNew, f_zNew);
}

UssPoint rotateAroundY(UssPoint f_point, double angle)
{
	double f_xNew = f_point.GetPositionX() * ::std::cos(angle) + f_point.GetPositionZ() * ::std::sin(angle);
	double f_yNew = f_point.GetPositionY();
	double f_zNew = -f_point.GetPositionX() * ::std::sin(angle) + f_point.GetPositionZ() * ::std::cos(angle);

	return UssPoint(f_xNew, f_yNew, f_zNew);
}

UssPoint rotateAroundZ(UssPoint f_point, double angle)
{
	double f_xNew = f_point.GetPositionX() * ::std::cos(angle) - f_point.GetPositionY() * ::std::sin(angle);
	double f_yNew = f_point.GetPositionX() * ::std::sin(angle) + f_point.GetPositionY() * ::std::cos(angle);
	double f_zNew = f_point.GetPositionZ();

	return UssPoint(f_xNew, f_yNew, f_zNew);
}

double round3Digits(double val) 
{
	return (std::round(val * 1000) / 1000);
}

UssPoint MidUssPoint(UssPoint Pnt1, UssPoint Pnt2)
{
	UssPoint l_Point = UssPoint();

	l_Point.SetPositionX((Pnt1.GetPositionX() + Pnt2.GetPositionX()) / 2);
	l_Point.SetPositionY((Pnt1.GetPositionY() + Pnt2.GetPositionY()) / 2);
	l_Point.SetPositionZ((Pnt1.GetPositionZ() + Pnt2.GetPositionZ()) / 2);

	return l_Point;
}


std::vector<UssPoint> CreateContour3D(double length, double width, double height, 
	eContourType ContourType, eRefPointTypeContour RefPntContour)
{
	std::vector<UssPoint> l_ContourPointList;
	UssPoint l_PointData = UssPoint();
	double l_heightFactor = 1; //(RefPntContour == REF_PNT_MIDDLE_LOW) => DEFAULT
	double l_offsetX = 0; //(RefPntContour == REF_PNT_MIDDLE_LOW) => DEFAULT

	double Ot_Rectangle_Contour_X[] = { 0.5,0.5,0.5,0.5,0.5,0.5,0.4,0.3,0.2,0.1,0,-0.1,-0.2,-0.3,-0.4,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5,0.5,0.5,0.5,0.5,0.5 };
	double Ot_Rectangle_Contour_Y[] = { 0,0.1,0.2,0.3,0.4,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.4,0.3,0.2,0.1,0,-0.1,-0.2,-0.3,-0.4,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.4,-0.3,-0.2,-0.1,0 };

	double Ot_Car_Contour_X[] = { 2.25, 2.25, 2.2274, 2.1954, 2.1458, 2.0904, 2.0058, 1.857, 1.6091, 1.1424, 0.7165, 0.5736, 0.1448, -0.0652, -0.4473, -0.9549, -1.4362, -1.6753, -1.8912, -2.072, -2.1829, -2.2237, -2.25, -2.25, -2.25 };
	double Ot_Car_Contour_Y[] = { 0, 0.2319, 0.4011, 0.5002, 0.6286, 0.7336, 0.8094, 0.859, 0.8765, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.88, 0.8474, 0.8007, 0.7511, 0.6082, 0.4157, 0.1648, 0, 0 };

	constexpr auto CONTOUR_POINTS_MAX = 40;

	if (RefPntContour == REF_PNT_MIDDLE_MIDDLE)
	{
		l_heightFactor = 0.5;
	}
	if (RefPntContour == REF_PNT_REAR_LOW)
	{
		l_offsetX = length/2;
	}

	switch (ContourType)
	{
		case CONTOUR_TYPE_ELLIPSE:
		{
			double t_stepsize = 360 / CONTOUR_POINTS_MAX;
			double t_currentangle = 0;

			for (uint32_t pnt = 0; pnt < CONTOUR_POINTS_MAX+1; pnt++)
			{
				for (uint8_t vert_pnts = 0; vert_pnts < VERTICAL_POINTS_CONTOUR; ++vert_pnts)
				{
					l_PointData = UssPoint();
					l_PointData.SetPositionX(length/2 * std::cos(deg2rad(t_currentangle)) + l_offsetX);
					l_PointData.SetPositionY(width/2 * std::sin(deg2rad(t_currentangle)));
					l_PointData.SetPositionZ(height * (l_heightFactor - ((double)vert_pnts / (double)VERTICAL_POINTS_CONTOUR - 1)));
					l_ContourPointList.push_back(l_PointData);
				}
				t_currentangle += t_stepsize;
			}
			break;
		}
		case CONTOUR_TYPE_CAR:
		{
			double l_factor_length = length / 4.5;
			double l_factor_width = width / 1.8;

			uint8_t l_array_size = sizeof(Ot_Car_Contour_X) / sizeof(*Ot_Car_Contour_X);

			for (uint8_t pnts = 0; pnts < l_array_size; pnts++)
			{
				for (uint8_t vert_pnts = 0; vert_pnts < VERTICAL_POINTS_CONTOUR; ++vert_pnts)
				{
					l_PointData = UssPoint();
					l_PointData.SetPositionX((Ot_Car_Contour_X[pnts] * l_factor_length) + l_offsetX);
					l_PointData.SetPositionY((Ot_Car_Contour_Y[pnts] * l_factor_width));
					l_PointData.SetPositionZ(height * (l_heightFactor - ((double)vert_pnts / (double)(VERTICAL_POINTS_CONTOUR - 1))));
					l_ContourPointList.push_back(l_PointData);
				}
			}
			for (uint8_t pnts = l_array_size - 1; pnts > 0; pnts--)
			{
				for (uint8_t vert_pnts = 0; vert_pnts < VERTICAL_POINTS_CONTOUR; ++vert_pnts)
				{
					l_PointData = UssPoint();
					l_PointData.SetPositionX((Ot_Car_Contour_X[pnts] * l_factor_length) + l_offsetX);
					l_PointData.SetPositionY((-Ot_Car_Contour_Y[pnts] * l_factor_width));
					l_PointData.SetPositionZ(height * (l_heightFactor - ((double)vert_pnts / (double)(VERTICAL_POINTS_CONTOUR - 1))));
					l_ContourPointList.push_back(l_PointData);
				}
			}
			break;
		}
		
		case CONTOUR_TYPE_RECTANGLE:
		default:
		{
			uint8_t l_array_size = sizeof(Ot_Rectangle_Contour_X) / sizeof(*Ot_Rectangle_Contour_X);
			for (uint8_t pnts = 0; pnts < l_array_size; pnts++)
			{
				for (uint8_t vert_pnts = 0; vert_pnts < VERTICAL_POINTS_CONTOUR; ++vert_pnts)
				{
					l_PointData = UssPoint();
					l_PointData.SetPositionX((Ot_Rectangle_Contour_X[pnts] * length) + l_offsetX);
					l_PointData.SetPositionY((Ot_Rectangle_Contour_Y[pnts] * width));
					l_PointData.SetPositionZ(height * (l_heightFactor - ((double)vert_pnts / (double)(VERTICAL_POINTS_CONTOUR-1))));
					l_ContourPointList.push_back(l_PointData);
				}
			}
			break;
		}
	}



	return l_ContourPointList;
}