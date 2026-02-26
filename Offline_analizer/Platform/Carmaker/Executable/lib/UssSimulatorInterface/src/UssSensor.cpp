#include "UssSensor.h"
#include <stdlib.h>
#include <iostream>


bool CompareUssSensorObjectDistance(UssSensorObject SObj1, UssSensorObject SObj2)
{
	return (SObj1.GetDistance() < SObj2.GetDistance());
}


UssSensor::UssSensor(tSensor SensorID, double Position_x, double Position_y, double Position_z,
	double Orientation_y, double Orientation_z, double Range,
	double Aperture_Hoz, double Aperture_Vert)
{
	SensorInitCommon();
	SetSensorID(SensorID);
	m_coordinates.SetPositionX(Position_x);
	m_coordinates.SetPositionY(Position_y);
	m_coordinates.SetPositionZ(Position_z);
	m_coordinates.SetRotationX(0); // rotation arround x axis makes no sense for our sensor model
	m_coordinates.SetRotationY(Orientation_y);
	m_coordinates.SetRotationZ(Orientation_z);
	SetSensorRange(Range);
	SetSensorApertureHorizontal(Aperture_Hoz);
	SetSensorApertureVertical(Aperture_Vert);
	SetSensorState(SENSOR_ACTIVE);
}

UssSensor::UssSensor(tSensor SensorID, double Position_x, double Position_y, double Position_z,
	double Orientation_y, double Orientation_z, double Range,
	double Aperture_Hoz, double Aperture_Vert, std::string Description,
	double HeightForHeightClassification, eSensorState SensorState)
{
	SensorInitCommon();
	SetSensorID(SensorID);
	m_coordinates.SetPositionX(Position_x);
	m_coordinates.SetPositionY(Position_y);
	m_coordinates.SetPositionZ(Position_z);
	m_coordinates.SetRotationX(0); // rotation arround x axis makes no sense for our sensor model
	m_coordinates.SetRotationY(Orientation_y);
	m_coordinates.SetRotationZ(Orientation_z);
	SetSensorRange(Range);
	SetSensorApertureHorizontal(Aperture_Hoz);
	SetSensorApertureVertical(Aperture_Vert);
	SetSensorDescription(Description);
	SetHeightForHeightClassification(HeightForHeightClassification);
	SetSensorState(SensorState);
}


UssSensor::~UssSensor(void)
{
	ClearObjects();
}

void UssSensor::SensorInitCommon(void)
{
	m_sensor_id = SInval;
	m_coordinates = UssCoordinates();
	m_range = 0;
	m_aper_hoz = 0;
	m_aper_ver = 0;
	m_description = "";
	SetHeightForHeightClassification(0.5);

	ClearObjects();
}


bool UssSensor::AddObject(UssObject ObjectData, UssCoordinates EgoVehicle)// world coordinates //currentobject , (sensor), egopos,
{
	/* Init for return values */
	uint64_t GlobalID = ObjectData.Id;
	UssPoint NearPnt = UssPoint();
	double NearPntDistance = 0;
	double NearPntAlpha = 0;
	double IncidentAlpha = 0;
	double IncidentBeta = 0;
	double Height = ObjectData.Height;

	/* calculate stuff */
	/* FoV check with Distance / Alpha / IncidentAngles calculation*/
	if (IsObjectInFoV(ObjectData, EgoVehicle, &NearPnt, &NearPntDistance, &NearPntAlpha, &IncidentAlpha, &IncidentBeta))
	{
		/* add the object to the Bosch object list*/
		AddObject(GlobalID, NearPnt, NearPntDistance, NearPntAlpha,
			IncidentAlpha, IncidentBeta, Height);
		//USS_DBG("Sensor %d | Object %d: Added with Distance: %f, Alpha: %f, IncidentAlpha: %f, IncidentBeta: %f and Height: %f NearPnt.x: %f NearPnt.y: %f !\n", GetSensorID() + 1, GlobalID, NearPntDistance, rad2deg(NearPntAlpha),
		//	rad2deg(IncidentAlpha), rad2deg(IncidentBeta), Height, NearPnt.GetPositionX(), NearPnt.GetPositionY());
		return true;
	}
	else return false;
}

//void UssSensor::AddObject() // sensor coordinates // currentobject


void UssSensor::AddObject(uint64_t GlobalID, UssPoint NearPnt, double NearPntDistance, double NearPntAlpha,
	double IncidentAlpha, double IncidentBeta, double Height)
{
	UssObjectData newObject = CreateObject(GlobalID, NearPnt, NearPntDistance, NearPntAlpha,
		IncidentAlpha, IncidentBeta, Height);
	if (m_objects.size() < MAX_OBJECTS)
	{
		m_objects.push_back(newObject);
	}
	else
	{
		//go through list and find object that is farther away then the new object
		for (std::vector<UssObjectData>::iterator it_obj = m_objects.begin(); it_obj != m_objects.end(); it_obj++)
		{
			if (newObject.NearPntDistance < it_obj->NearPntDistance)
			{
				m_objects.pop_back(); // remove last object
				m_objects.push_back(newObject); // add new object
				break; // no need to go further
			}
		}


	}

	//sort the list most relevant to least relevant object -> with NearPntDistance
	std::sort(m_objects.begin(), m_objects.end());
}

/*Get object list*/

std::vector<UssObjectData> UssSensor::GetObjects(void) { return m_objects; }

void UssSensor::ClearObjects(void)
{
	m_objects.clear();
}

UssObjectData UssSensor::CreateObject(uint64_t GlobalID, UssPoint NearPnt, double NearPntDistance, double NearPntAlpha,
	double IncidentAlpha, double IncidentBeta, double Height)
{
	UssObjectData objData;
	objData.GlobalId = GlobalID;
	objData.NearPnt[0] = NearPnt.GetPositionX();
	objData.NearPnt[1] = NearPnt.GetPositionY();
	objData.NearPnt[2] = NearPnt.GetPositionZ();
	//if (GlobalID == 3) USS_DBG("\nobjDataNearPnt: %f , %f , %f\n", objData.NearPnt[0], objData.NearPnt[1], objData.NearPnt[2]);
	//if (GlobalID == 3) USS_DBG("NearPnt: %f , %f , %f\n\n", NearPnt.GetPositionX(), NearPnt.GetPositionY(), NearPnt.GetPositionZ());
	objData.NearPntDistance = NearPntDistance;
	objData.NearPntAlpha = NearPntAlpha;
	objData.IncidentAlpha = IncidentAlpha;
	objData.IncidentBeta = IncidentBeta;
	objData.Height = Height;

	return objData;
}

bool UssSensor::IsObjectInFoV(UssObject ObjectData, UssCoordinates EgoVehicle, UssPoint * NearPnt, double * NearPointDistance, double * NearPointAlpha, double *IncidentAlpha, double *IncidentBeta)
{
	bool ObjectInFov = false;
	// int8_t PointCnt = 0;
	std::map<double, int8_t> PointsInFoV;

	/*temp variables*/
	double t_distance = 999; //initialize distance with high value so that the sorting to shorter distances will work
	uint64_t t_index = 0;
	UssPoint t_CurrentPointSensorCoord = UssPoint();
	UssPoint t_tempContourPoint = UssPoint();
	//UssPoint *p_ObjectContour = new UssPoint();
	std::vector<UssPoint> v_ObjectContour;

	/*Create list of all contour points in sensor coordinate system*/
	std::vector<UssPoint> PointsInSensorCoord;

	/*Ego vehicle position*/
	double EgoVehiclePosXWorldCoord = EgoVehicle.GetPositionX();
	double EgoVehiclePosYWorldCoord = EgoVehicle.GetPositionY();

	std::vector<UssSensorObject> ObjectDataSensorCoord;
	std::vector<UssSensorObject> t_RefPointsList;
	UssSensorObject t_RefPoint;

	UssSensorObject NearestPoint, NearestNeighbour, SecondNearestNeighbour;
	UssSensorObject FinalNearestPoint, FinalLeftPoint, FinalRightPoint;

	/*Check if the reference point of the object is within the OBSERVATION_RANGE*/
	if (ObjectData.ReferencePointCoordinates == COORDINATE_SYSTEM_EGOVEHICLE)
	{
		if ((ObjectData.ReferencePoint.GetPositionX() <= OBSERVATION_RANGE) &&
			(ObjectData.ReferencePoint.GetPositionX() >= -OBSERVATION_RANGE) &&
			(ObjectData.ReferencePoint.GetPositionY() <= OBSERVATION_RANGE) &&
			(ObjectData.ReferencePoint.GetPositionY() >= -OBSERVATION_RANGE))
		{
			ObjectDataSensorCoord = GetObjectDataSensorCoord(ObjectData);
		}
		else
		{
			return false;
		}
		
	}
	else if (ObjectData.ReferencePointCoordinates == COORDINATE_SYSTEM_WORLD)
	{
		if ((ObjectData.ReferencePoint.GetPositionX() <= EgoVehiclePosXWorldCoord + OBSERVATION_RANGE) &&
			(ObjectData.ReferencePoint.GetPositionX() >= EgoVehiclePosXWorldCoord - OBSERVATION_RANGE) &&
			(ObjectData.ReferencePoint.GetPositionY() <= EgoVehiclePosYWorldCoord + OBSERVATION_RANGE) &&
			(ObjectData.ReferencePoint.GetPositionY() >= EgoVehiclePosYWorldCoord - OBSERVATION_RANGE))
		{
			ObjectDataSensorCoord = GetObjectDataSensorCoord(ObjectData, EgoVehicle);
		}
		else
		{
			return false;
		}
	}
	else //not implemented
	{
		return false;
	}
		
	t_index = 0;

    //collect the contour in a vector so it can be used in IsPointInsideContour
	for (std::vector<UssSensorObject>::iterator it_pnt = ObjectDataSensorCoord.begin(); it_pnt != ObjectDataSensorCoord.end(); it_pnt++)
	{
		t_tempContourPoint = UssPoint(it_pnt->GetPositionX(), it_pnt->GetPositionY(), it_pnt->GetPositionZ());
		v_ObjectContour.push_back(t_tempContourPoint);
	}
	//check if the sensor position is within the contour of the object -> if yes no calculation done
	if (!IsPointInsideContour(v_ObjectContour, UssPoint(0, 0, 0)))
	{
		/* find the point with the shortest distance */
		for (std::vector<UssSensorObject>::iterator it_pnt = ObjectDataSensorCoord.begin(); it_pnt != ObjectDataSensorCoord.end(); it_pnt++)
		{
			if (it_pnt->GetDistance() < t_distance)
			{
				t_distance = it_pnt->GetDistance();
				t_index = it_pnt->GetIndex();
				NearestPoint = ObjectDataSensorCoord.at(t_index);
			}
		}

		if (t_distance > m_range) //no point in FoV -> no further checks needed
		{	
			return false;
		}

		/* Check if the plane between the nearest point and its neighbours is closer to the sensor */
		//with t_index == n -> index of nearest contour point
		//				n-1
		//				||
		//		n-3=====n=====n+3
		//				||
		//				n+1

		uint64_t t_NP_index = 0;
		t_RefPointsList.push_back(ObjectDataSensorCoord.at(t_index));
		if (t_index % VERTICAL_POINTS_CONTOUR != 0) // n - 1 case possible
		{
			t_RefPoint = GetNearestPointBetweenTwoPoints(ObjectDataSensorCoord.at(t_index), ObjectDataSensorCoord.at(t_index - 1), t_NP_index++);
			if (t_NP_index - 1 == t_RefPoint.GetIndex())
			{
				t_RefPointsList.push_back(t_RefPoint);
			}
			else
			{
				t_RefPointsList.push_back(ObjectDataSensorCoord.at(t_index - 1));
			}
				
		}

		if (t_index % VERTICAL_POINTS_CONTOUR != (VERTICAL_POINTS_CONTOUR - 1)) // n + 1 case possible
		{
			t_RefPoint = GetNearestPointBetweenTwoPoints(ObjectDataSensorCoord.at(t_index), ObjectDataSensorCoord.at(t_index + 1), t_NP_index++);
			if (t_NP_index - 1 == t_RefPoint.GetIndex())
			{
				t_RefPointsList.push_back(t_RefPoint);
			}
			else
			{
				t_RefPointsList.push_back(ObjectDataSensorCoord.at(t_index + 1));
			}
		}

		if ((int64_t)(t_index - VERTICAL_POINTS_CONTOUR) < 0) // handle values below 0
		{
			t_RefPoint = GetNearestPointBetweenTwoPoints(ObjectDataSensorCoord.at(t_index), ObjectDataSensorCoord.at(ObjectDataSensorCoord.size() - VERTICAL_POINTS_CONTOUR + t_index), t_NP_index++);
			if (t_NP_index - 1 == t_RefPoint.GetIndex())
			{
				t_RefPointsList.push_back(t_RefPoint);
			}
			else
			{
				t_RefPointsList.push_back(ObjectDataSensorCoord.at(ObjectDataSensorCoord.size() - VERTICAL_POINTS_CONTOUR + t_index));
			}
		}
		else
		{
			t_RefPoint = GetNearestPointBetweenTwoPoints(ObjectDataSensorCoord.at(t_index), ObjectDataSensorCoord.at(t_index - VERTICAL_POINTS_CONTOUR), t_NP_index++);
			if (t_NP_index - 1 == t_RefPoint.GetIndex())
			{
				t_RefPointsList.push_back(t_RefPoint);
			}
			else
			{
				t_RefPointsList.push_back(ObjectDataSensorCoord.at(t_index - VERTICAL_POINTS_CONTOUR));
			}

		}

		if (t_index + VERTICAL_POINTS_CONTOUR >= ObjectDataSensorCoord.size()) // handle values above the size
		{
			t_RefPoint = GetNearestPointBetweenTwoPoints(ObjectDataSensorCoord.at(t_index), ObjectDataSensorCoord.at(t_index + VERTICAL_POINTS_CONTOUR - ObjectDataSensorCoord.size()), t_NP_index++);
			if (t_NP_index - 1 == t_RefPoint.GetIndex())
			{
				t_RefPointsList.push_back(t_RefPoint);
			}
			else
			{
				t_RefPointsList.push_back(ObjectDataSensorCoord.at(t_index + VERTICAL_POINTS_CONTOUR - ObjectDataSensorCoord.size()));
			}
		}
		else
		{
			t_RefPoint = GetNearestPointBetweenTwoPoints(ObjectDataSensorCoord.at(t_index), ObjectDataSensorCoord.at(t_index + VERTICAL_POINTS_CONTOUR), t_NP_index++);
			if (t_NP_index - 1 == t_RefPoint.GetIndex())
			{
				t_RefPointsList.push_back(t_RefPoint);
			}
			else
			{
				t_RefPointsList.push_back(ObjectDataSensorCoord.at(t_index + VERTICAL_POINTS_CONTOUR));
			}
		}

		/* Sort the points by distance to the sensor */
		std::sort(t_RefPointsList.begin(), t_RefPointsList.end(), CompareUssSensorObjectDistance);

		/* Nearest point is the first one in the list */
		FinalNearestPoint = t_RefPointsList.at(0);
			
		/* Get the points on the left and on the right of the nearest point */
		for (uint8_t i = 1; i < t_RefPointsList.size(); ++i)
		{
			UssSensorObject t_tempObjectData = t_RefPointsList.at(i);
			/* Point is on the right side */
			if (FinalNearestPoint.GetAlpha() < t_tempObjectData.GetAlpha())
			{
				if (FinalRightPoint.GetIndex() == 99999) /* No data assigned until now */
				{
					FinalRightPoint = t_tempObjectData;
				}
				else if ((t_tempObjectData.GetAlpha() - FinalNearestPoint.GetAlpha()) < (FinalRightPoint.GetAlpha() - FinalNearestPoint.GetAlpha()))
				{
					FinalRightPoint = t_tempObjectData;
				}
			}
			/* Point is on the left side */
			else if (FinalNearestPoint.GetAlpha() > t_RefPointsList.at(i).GetAlpha())
			{
				if (FinalLeftPoint.GetIndex() == 99999) /* No data assigned until now */
				{
					FinalLeftPoint = t_tempObjectData;
				}
				else if ((t_tempObjectData.GetAlpha() - FinalNearestPoint.GetAlpha()) < (FinalLeftPoint.GetAlpha() - FinalNearestPoint.GetAlpha()))
				{
					FinalLeftPoint = t_tempObjectData;
				}
			}
		}

		if (IsPointInFoV(FinalNearestPoint)) 
		{
			ObjectInFov = true;
			//distance to nearest point
			t_CurrentPointSensorCoord.SetPositionX(FinalNearestPoint.GetPositionX());
			t_CurrentPointSensorCoord.SetPositionY(FinalNearestPoint.GetPositionY());
			t_CurrentPointSensorCoord.SetPositionZ(FinalNearestPoint.GetPositionZ());

			*NearPnt = t_CurrentPointSensorCoord;
			*NearPointDistance = FinalNearestPoint.GetDistance();
			/*Calculate the alpha angle to the the nearest point*/
			*NearPointAlpha = FinalNearestPoint.GetAlpha();
			*IncidentAlpha = CalcIncidentAngle(FinalNearestPoint, FinalRightPoint,0);
			*IncidentBeta = CalcIncidentAngle(FinalNearestPoint, FinalLeftPoint,1);
				
			/*UssPoint l_SensorPosWorldCoord = transformPointFromCoordSystem(UssPoint(m_coordinates.GetPositionX(), m_coordinates.GetPositionY(), m_coordinates.GetPositionZ()), EgoVehicle);
			std::cout << "PlotSensorFov(" << l_SensorPosWorldCoord.GetPositionX() << "," << l_SensorPosWorldCoord.GetPositionY() << "," 
						<< rad2deg(m_coordinates.GetRotationZ() + EgoVehicle.GetRotationZ()) << ",";
			switch (m_sensor_id)
			{
				case S1:
				case S7:
					std::cout << "'g'";
					break;
				case S2:
				case S8:
					std::cout << "'b'";
					break;
				case S3:
				case S9:
					std::cout << "'m'";
					break;
				case S4:
				case S10:
					std::cout << "'k'";
					break;
				case S5:
				case S11:
					std::cout << "'c'";
					break;
				case S6:
				case S12:
					std::cout << "'y'";
					break;
				case SInval:
				default:
					std::cout << "'g'";
					break;
			}
			std::cout << "," << FinalNearestPoint.GetDistance() <<")" << std::endl;*/
				
		}
	}

	return ObjectInFov;
}

bool UssSensor::IsPointInFoV(UssSensorObject PointData)
{
	/*Check if the distance is less then the range of the sensor*/
	if (PointData.GetDistance() <= GetSensorRange())
	{
		/*Check if the point is in front of the sensor*/
		if (PointData.GetPositionX() > 0)
		{
			/*Check that point is in the horizontal FoV of the sensor*/
			PointData.CalcAlpha();
			if (abs(PointData.GetAlpha()) <= (GetSensorApertureHorizontal() / 2))
			{
				/*Check that point is in the vertical FoV of the sensor*/
				PointData.CalcBeta();
				if (abs(PointData.GetBeta()) <= (GetSensorApertureVertical() / 2))
				{
					/*at least one point is in the FoV of the sensor*/
					return true;
				}
			}
		}
	}

	return false;
}

UssSensorObject UssSensor::GetNearestPointBetweenTwoPoints(UssSensorObject pnt1, UssSensorObject pnt2, uint64_t index)
{
	double straightOffset[3], straightFactor[3];
	straightOffset[0] = pnt1.GetPositionX();
	straightOffset[1] = pnt1.GetPositionY();
	straightOffset[2] = pnt1.GetPositionZ();

	straightFactor[0] = pnt2.GetPositionX() - pnt1.GetPositionX();
	straightFactor[1] = pnt2.GetPositionY() - pnt1.GetPositionY();
	straightFactor[2] = pnt2.GetPositionZ() - pnt1.GetPositionZ();

	//Straight vector = straightOffset + lambda*straightFactor
	double lambda = ((straightFactor[0] * (-straightOffset[0]) +
		straightFactor[1] * (-straightOffset[1]) +
		straightFactor[2] * (-straightOffset[2])) /
		(pow(straightFactor[0], 2) + pow(straightFactor[1], 2) + pow(straightFactor[2], 2)));


	//std::cout << "#lambda: " << lambda << std::endl;
	/* nearest point is not between the two points */
	if (lambda >= 1 || lambda <= 0)
	{
		return pnt1;
	}

	UssSensorObject NearestPointPlane;
	NearestPointPlane.SetPositionX(straightOffset[0] + lambda * straightFactor[0]);
	NearestPointPlane.SetPositionY(straightOffset[1] + lambda * straightFactor[1]);
	NearestPointPlane.SetPositionZ(straightOffset[2] + lambda * straightFactor[2]);
	NearestPointPlane.CalcDistance();
	NearestPointPlane.CalcAlpha();
	NearestPointPlane.CalcBeta();
	NearestPointPlane.SetIndex(index);
		
	return NearestPointPlane;
}

double UssSensor::CalcIncidentAngle(UssSensorObject NearestPoint, UssSensorObject NeighbourPoint,uint8_t incAngleIdentifier)
{
	double alphaNearPoint = NearestPoint.GetAlpha();
	double alphaNeighbourPoint = NeighbourPoint.GetAlpha();

	if (alphaNearPoint == alphaNeighbourPoint) return M_PI;

	double DifferenceX = NearestPoint.GetPositionX() - NeighbourPoint.GetPositionX();
	double DifferenceY = NearestPoint.GetPositionY() - NeighbourPoint.GetPositionY();
	double DifferenceZ = NearestPoint.GetPositionZ() - NeighbourPoint.GetPositionZ();
	
	double a = CalcDistance3D(DifferenceX, DifferenceY, DifferenceZ);
	double b = CalcDistance3D(NearestPoint.GetPositionX(), NearestPoint.GetPositionY(), NearestPoint.GetPositionZ());
	double c = CalcDistance3D(NeighbourPoint.GetPositionX(), NeighbourPoint.GetPositionY(), NeighbourPoint.GetPositionZ());
	
	double gamma = ((pow(a, 2) + pow(b, 2) - pow(c, 2)) / (2 * a*b));
	double incAngle = std::acos(gamma);

	if (alphaNearPoint != 0)
	{
		if (alphaNearPoint < alphaNeighbourPoint)
		{
			if (incAngleIdentifier == 0)
			{
				return ((2 * M_PI) - incAngle);
			}
			else return incAngle;
		}
		else if (alphaNearPoint > alphaNeighbourPoint)
		{
			if (incAngleIdentifier == 0)
			{
				return incAngle;
			}
			else return ((2 * M_PI) - incAngle);
		}
	}
	else //alpha = 0
	{
		return incAngle;
	}

	return 0;

}

/**
 * Retrieves the sensor coordinates for the given UssObject.
 * 
 * @param ObjectData The object data in the world coordinate system.
 * @param EgoVehicle The coordinates of the ego vehicle.
 * @return A vector of UssSensorObject containing the object data in the sensor's coordinate system.
 */
std::vector<UssSensorObject> UssSensor::GetObjectDataSensorCoord(UssObject ObjectData, UssCoordinates EgoVehicle)
{
	/*angle between sensor axis and world axis */
	double SensorRotationXWorldCoord = EgoVehicle.GetRotationX() + GetSensorCoordinates().GetRotationX();
	double SensorRotationYWorldCoord = EgoVehicle.GetRotationY() + GetSensorCoordinates().GetRotationY();
	double SensorRotationZWorldCoord = EgoVehicle.GetRotationZ() + GetSensorCoordinates().GetRotationZ();

	std::vector<UssSensorObject> ObjectPointsSensorCoordinates;

	UssPoint SensorPostion = UssPoint(GetSensorCoordinates().GetPositionX(),
		GetSensorCoordinates().GetPositionY(),
		GetSensorCoordinates().GetPositionZ());
	UssPoint l_SensorPositionWorld = transformPointFromCoordSystem(SensorPostion, EgoVehicle);
	UssCoordinates SensorPositionWorldCoordinates(l_SensorPositionWorld.GetPositionX(), l_SensorPositionWorld.GetPositionY(), l_SensorPositionWorld.GetPositionZ(),
		SensorRotationXWorldCoord, SensorRotationYWorldCoord, SensorRotationZWorldCoord);

	for (size_t i = 0; i < ObjectData.ContourPoints.size(); i++)
	{
		UssPoint l_PointToBeTransformed = UssPoint();
		UssSensorObject t_SensObj = UssSensorObject();
		
		l_PointToBeTransformed = transformPointFromCoordSystem(ObjectData.ContourPoints.at(i), ObjectData.ReferencePoint);
		l_PointToBeTransformed = transformPointToCoordSystem(l_PointToBeTransformed, SensorPositionWorldCoordinates);

		t_SensObj.SetPositionX(l_PointToBeTransformed.GetPositionX());
		t_SensObj.SetPositionY(l_PointToBeTransformed.GetPositionY());
		t_SensObj.SetPositionZ(l_PointToBeTransformed.GetPositionZ());
		t_SensObj.CalcDistance();
		t_SensObj.CalcAlpha();
		t_SensObj.CalcBeta();
		t_SensObj.SetIndex((uint64_t)i);
		ObjectPointsSensorCoordinates.push_back(t_SensObj);

	}

	return ObjectPointsSensorCoordinates;
}

/**
 * Retrieves the sensor coordinates for the given UssObject.
 *
 * @param ObjectData The object data in the ego vehicle coordinate system.
 * @return A vector of UssSensorObject containing the sensor coordinates.
 */
std::vector<UssSensorObject> UssSensor::GetObjectDataSensorCoord(UssObject ObjectData)
{
	std::vector<UssSensorObject> ObjectPointsSensorCoordinates;

	for (size_t i = 0; i < ObjectData.ContourPoints.size(); i++)
	{
		UssPoint l_PointToBeTransformed = UssPoint();
		UssSensorObject t_SensObj = UssSensorObject();
		
		//l_PointToBeTransformed = transformPointFromCoordSystem(ObjectData.ContourPoints.at(i), ObjectData.ReferencePoint);
		//l_PointToBeTransformed = transformPointToCoordSystem(l_PointToBeTransformed, m_coordinates);

		l_PointToBeTransformed = transformPointToCoordSystem(ObjectData.ContourPoints.at(i), m_coordinates);

		t_SensObj.SetPositionX(l_PointToBeTransformed.GetPositionX());
		t_SensObj.SetPositionY(l_PointToBeTransformed.GetPositionY());
		t_SensObj.SetPositionZ(l_PointToBeTransformed.GetPositionZ());
		t_SensObj.CalcDistance();
		t_SensObj.CalcAlpha();
		t_SensObj.CalcBeta();
		t_SensObj.SetIndex((uint64_t)i);
		ObjectPointsSensorCoordinates.push_back(t_SensObj);

	}

	return ObjectPointsSensorCoordinates;
}

tSensor UssSensor::GetSensorID(void) { return m_sensor_id; }

void UssSensor::SetSensorID(tSensor id) { m_sensor_id = id; } /*no check neccessary, already done within RbUltraSonics*/

UssCoordinates UssSensor::GetSensorCoordinates(void) { return m_coordinates; }

double UssSensor::GetSensorRange(void) { return m_range; }

void UssSensor::SetSensorRange(double range)
{
	if ((range < 2) || (range > 10))
	{
		USS_OUT("SetSensorRange: Sensor range out of bounds. Given value: %f m\n", range);
		range = 5;
		USS_OUT("Sensor range changed to %f m\n", range);
	}
	m_range = range;
}

double UssSensor::GetSensorApertureHorizontal(void) { return m_aper_hoz; }

void UssSensor::SetSensorApertureHorizontal(double aper)
{
	if ((aper > 2 * M_PI) || (aper <= 0))
	{
		USS_OUT("SetSensorApertureHorizontal: Aperture out of bounds. Given value: %f\n", aper);
		aper = deg2rad(DEFAULT_APER_HOZ);
		USS_OUT("Aperture changed to %f (%i degree)\n", aper, DEFAULT_APER_HOZ);
	}
	m_aper_hoz = aper;
}

double UssSensor::GetSensorApertureVertical(void) { return m_aper_ver; }

void UssSensor::SetSensorApertureVertical(double aper)
{
	if ((aper > 2 * M_PI) || (aper <= 0))
	{
		USS_OUT("SetSensorApertureVertical: Aperture out of bounds. Given value: %f\n", aper);
		aper = deg2rad(DEFAULT_APER_VER);
		USS_OUT("Aperture changed to %f (%i degree)\n", aper, DEFAULT_APER_VER);
	}
	m_aper_ver = aper;
}

bool UssSensor::IsPointOnSegment(UssPoint p, UssPoint q, UssPoint r)
{
	if (q.GetPositionX() <= std::max(p.GetPositionX(), r.GetPositionX()) && q.GetPositionX() >= std::min(p.GetPositionX(), r.GetPositionX()) &&
		q.GetPositionY() <= std::max(p.GetPositionY(), r.GetPositionY()) && q.GetPositionY() >= std::min(p.GetPositionY(), r.GetPositionY()))
	{
		return true;
	}
	return false;
}

uint8_t UssSensor::orientationTriplet(UssPoint p, UssPoint q, UssPoint r)
{
	double val = (q.GetPositionY() - p.GetPositionY()) * (r.GetPositionX() - q.GetPositionX()) -
				 (q.GetPositionX() - p.GetPositionX()) * (r.GetPositionY() - q.GetPositionY());

	if (val == 0)
	{
		return 0; // collinear
	}
	return (val > 0) ? 1 : 2; // clock or counterclock wise
}

bool UssSensor::doLineSegmentsIntersect(UssPoint p1, UssPoint q1, UssPoint p2, UssPoint q2)
{
	// Find the four orientations needed for general and
	// special cases
	uint8_t o1 = orientationTriplet(p1, q1, p2);
	uint8_t o2 = orientationTriplet(p1, q1, q2);
	uint8_t o3 = orientationTriplet(p2, q2, p1);
	uint8_t o4 = orientationTriplet(p2, q2, q1);

	// General case
	if (o1 != o2 && o3 != o4)
	{
		return true;
	}

	// Special Cases
	// p1, q1 and p2 are collinear and p2 lies on segment p1q1
	if (o1 == 0 && IsPointOnSegment(p1, p2, q1))
	{
		return true;
	}
	// p1, q1 and p2 are collinear and q2 lies on segment p1q1
	if (o2 == 0 && IsPointOnSegment(p1, q2, q1))
	{
		return true;
	}
	// p2, q2 and p1 are collinear and p1 lies on segment p2q2
	if (o3 == 0 && IsPointOnSegment(p2, p1, q2))
	{
		return true;
	}
	// p2, q2 and q1 are collinear and q1 lies on segment p2q2
	if (o4 == 0 && IsPointOnSegment(p2, q1, q2))
	{
		return true;
	}
	return false; // Doesn't fall in any of the above cases
}

bool UssSensor::IsPointInsideContour(std::vector<UssPoint> contour, UssPoint sensorpos)
{
	//when the contour has less then 3 points it does not make sense to check
	if (contour.size() < 3)
	{
		return false;
	}
	// Create a point for line segment from sensorpos to infinite
	UssPoint extreme = UssPoint(DBL_MAX, sensorpos.GetPositionY(), 0.0 );
	// Count intersections of the above line with sides of contour
	int count = 0, i = 0;
	
	do
	{
		int next = (i + 1) % contour.size();

		// Check if the line segment from 'sensorpos' to 'extreme' intersects
		// with the line segment from 'contour[i]' to 'contour[next]'
		if (doLineSegmentsIntersect(contour.at(i), contour.at(next), sensorpos, extreme))
		{
			// If the point 'sensorpos' is collinear with line segment 'i-next',
			// then check if it lies on segment. If it lies, return true,
			// otherwise false
			if (orientationTriplet(contour.at(i), sensorpos, contour.at(next)) == 0)
			{
				return IsPointOnSegment(contour.at(i), sensorpos, contour.at(next));
			}
			count++;
		}
		i = next;
	} while (i != 0);

	// Return true if count is odd, false otherwise
	return count & 1; // Same as (count%2 == 1)

}

void UssSensor::SetSensorDescription(std::string description) { m_description = description; }

std::string UssSensor::GetSensorDescription(void) { return m_description; }

void UssSensor::SetHeightForHeightClassification(double HeightForHeightClassification) { m_HeightForHeightClassification = HeightForHeightClassification; }

double UssSensor::GetHeightForHeightClassification(void) { return m_HeightForHeightClassification; }

void UssSensor::SetSensorState(eSensorState SensorState) { m_SensorState = SensorState; }

eSensorState UssSensor::GetSensorState(void) { return m_SensorState; }
