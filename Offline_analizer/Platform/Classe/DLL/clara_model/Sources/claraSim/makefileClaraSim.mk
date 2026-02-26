#********************************************************************************
#@brief   makefile extension for claraSim
#
#@author Robert Erhart, ett2si (26.06.2007)
#@author Xenolation framework is part of CLARA
#@author (c) Copyright Robert Bosch GmbH 2007-2024. All rights reserved.
#********************************************************************************
#@remark
#********************************************************************************

SRCCLARASIMOSINTERFACE = \
$(CLARAROOT)/claraSim/framework/OSInterface/OSInterfaceXeno/OSSyncPrimitive.cpp

SRCCLARASIMFRAMEWORK = \
$(CLARAROOT)/claraSim/framework/CBool.cpp \
$(CLARAROOT)/claraSim/framework/CClass_ct.cpp \
$(CLARAROOT)/claraSim/framework/CFloat.cpp \
$(CLARAROOT)/claraSim/framework/CFloatVector.cpp \
$(CLARAROOT)/claraSim/framework/CInt.cpp \
$(CLARAROOT)/claraSim/framework/CIntVector.cpp \
$(CLARAROOT)/claraSim/framework/CClothoid.cpp \
$(CLARAROOT)/claraSim/framework/CLowPass.cpp \
$(CLARAROOT)/claraSim/framework/CLowPass2ndOrder.cpp \
$(CLARAROOT)/claraSim/framework/CLowPass3rdOrder.cpp \
$(CLARAROOT)/claraSim/framework/CMessage.cpp \
$(CLARAROOT)/claraSim/framework/CMessageInput.cpp \
$(CLARAROOT)/claraSim/framework/CMessageOutput.cpp \
$(CLARAROOT)/claraSim/framework/CMessageParameter.cpp \
$(CLARAROOT)/claraSim/framework/CModule.cpp \
$(CLARAROOT)/claraSim/framework/CSplineAkima.cpp \
$(CLARAROOT)/claraSim/framework/CTable.cpp \
$(CLARAROOT)/claraSim/framework/CViewSegment.cpp \
$(CLARAROOT)/claraSim/framework/CLine.cpp \

SRCCLARASIMWORLD = \
$(CLARAROOT)/claraSim/world/CWorld.cpp \
$(CLARAROOT)/claraSim/world/CWorldTruck.cpp \
$(CLARAROOT)/claraSim/world/CWorldBike.cpp \
$(CLARAROOT)/claraSim/world/roadNetwork/CRoad.cpp \
$(CLARAROOT)/claraSim/world/roadNetwork/CLane.cpp \
$(CLARAROOT)/claraSim/world/roadNetwork/CRoadNetwork.cpp \
$(CLARAROOT)/claraSim/world/obstacle/CObstacles.cpp \
$(CLARAROOT)/claraSim/world/obstacle/CObstacleDynamic.cpp \
$(CLARAROOT)/claraSim/world/obstacle/CObstacleStatic.cpp \
$(CLARAROOT)/claraSim/world/vehicle/CVehicle.cpp \
$(CLARAROOT)/claraSim/world/vehicle/CVehicleTwoWheeler.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CArticulation.cpp \
$(CLARAROOT)/claraSim/world/vehicle/dashboard/CDashboard.cpp \
$(CLARAROOT)/claraSim/world/vehicle/driver/CDriver.cpp \
$(CLARAROOT)/claraSim/world/vehicle/driver/CLeaning.cpp \
$(CLARAROOT)/claraSim/world/vehicle/sensor/CSensor.cpp \
$(CLARAROOT)/claraSim/world/vehicle/sensor/CRadar.cpp \
$(CLARAROOT)/claraSim/world/vehicle/sensor/CVideo.cpp \
$(CLARAROOT)/claraSim/world/vehicle/sensor/CLidar.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CAirResistance.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CChassisCar.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CChassisTwoWheeler.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CStaticCar.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CStaticTwoWheeler.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CDynamic.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CKinetics.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CKineticsVertical.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CSuspension.cpp \
$(CLARAROOT)/claraSim/world/vehicle/chassis/CWheel.cpp \
$(CLARAROOT)/claraSim/world/vehicle/driveTrain/CBrakeSystem.cpp \
$(CLARAROOT)/claraSim/world/vehicle/driveTrain/CBrakeSystemTwoWheeler.cpp \
$(CLARAROOT)/claraSim/world/vehicle/driveTrain/CDifferentialGear.cpp \
$(CLARAROOT)/claraSim/world/vehicle/driveTrain/CMotor.cpp \
$(CLARAROOT)/claraSim/world/vehicle/driveTrain/CDriveTrain.cpp \
$(CLARAROOT)/claraSim/world/vehicle/driveTrain/CDriveTrainTwoWheeler.cpp \
$(CLARAROOT)/claraSim/world/vehicle/driveTrain/CTransmission.cpp \
$(CLARAROOT)/claraSim/world/vehicle/steeringSystem/CSteeringSystem.cpp\
$(CLARAROOT)/claraSim/world/vehicle/steeringSystem/CSteeringSystemTwoWheeler.cpp

OBJ += $(addprefix $(BUILDDIR)/,$(SRCCLARASIMOSINTERFACE:.cpp=.o) )
OBJ += $(addprefix $(BUILDDIR)/,$(SRCCLARASIMFRAMEWORK:.cpp=.o) )
OBJ += $(addprefix $(BUILDDIR)/,$(SRCCLARASIMWORLD:.cpp=.o) )

