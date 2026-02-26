#ifndef CDifferentialGear_H
#define CDifferentialGear_H
/*!
********************************************************************************
@class CDifferentialGear
@ingroup driveTrain
@brief simulation of an differential gear for front/rear/4-wheel drive cars

@author Robert Erhart, ett2si (12.11.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
********************************************************************************
@remark
Differential gear simulation for front and/or rear wheel driven cars
- 4wheel-drive
    + rpm
@verbatim
        o_differentialGearRatio = ( p_uRear + p_uFront ) / 2.0 * p_uCenter;
        o_nDifferentialGear =
            p_uCenter / 2.0 *
            ( p_uFront / 2.0 * ( i_nWheelRightFront + i_nWheelLeftFront )
              + p_uRear / 2.0 * ( i_nWheelRightRear + i_nWheelLeftRear ) );
@endverbatim
    + Torque of the wheels
@verbatim
        o_MWheelRightFront = p_uFront / 2.0 * p_uCenter / 2.0 * i_MPowerTrain;
        o_MWheelLeftFront = o_MWheelRightFront;
        o_MWheelRightRear = p_uRear / 2.0 * p_uCenter / 2.0 * i_MPowerTrain;
        o_MWheelLeftRear  = o_MWheelRightRear;
@endverbatim
********************************************************************************
@param[in] i_nWheelRightFront       [rpm]  wheel rpm right-front
@param[in] i_nWheelLeftFront        [rpm]  wheel rpm left-front
@param[in] i_nWheelRightRear        [rpm]  wheel rpm right-rear
@param[in] i_nWheelLeftRear         [rpm]  wheel rpm left-rear
@param[in] i_MPowerTrain            [Nm]   torque power train
@param[in] i_frontWheelDrive        [bool] true: front wheel driven / false: non powered
@param[in] i_rearWheelDrive         [bool] true: rear wheel driven / false: non powered
********************************************************************************
@param[out] o_nDifferentialGear     [rpm]  rpm differential gear to engine
@param[out] o_differentialGearRatio [-]    current differential ratio
@param[out] o_MWheelLeftFront       [Nm]   torque wheel left-front
@param[out] o_MWheelRightFront      [Nm]   torque wheel right-front
@param[out] o_MWheelLeftRear        [Nm]   torque wheel left-rear
@param[out] o_MWheelRightRear       [Nm]   torque wheel right-rear
********************************************************************************
@param[in,out] p_uCenter            [ ]    differential transmission ratio center
@param[in,out] p_uFront             [ ]    differential transmission ratio front
@param[in,out] p_uRear;             [ ]    differential transmission ratio rear
********************************************************************************
@todo remove systemcall 'exit' ; for real time execution
********************************************************************************
*/
// online documentation of the messages for the scene generator
namespace CDifferentialGearDoc
{
    /* output */
    const auto o_nDifferentialGear = "[rpm] rpm differential gear to engine";
    const auto o_differentialGearRatio = "[-] current differential ratio";
    const auto o_MWheelLeftFront = "[Nm] torque wheel left-front";
    const auto o_MWheelRightFront = "[Nm] torque wheel right-front";
    const auto o_MWheelLeftRear = "[Nm] torque wheel left-rear";
    const auto o_MWheelRightRear = "[Nm] torque wheel right-rear";
    /* parameter */
    const auto p_uCenter = "[ ] differential transmission ratio center";
    const auto p_uFront = "[ ] differential transmission ratio front";
    const auto p_uRear = "[ ] differential transmission ratio rear";
}

#include <claraSim/framework/CModule.h>


////*********************************
//// CDifferentialGear
////*********************************
class CDifferentialGear : public CModule<>
{
    //*********************************
    // constructor/destructor/copy/move
    //*********************************
public:
    CDifferentialGear();
    virtual ~CDifferentialGear();

    //*******************************
    //classes
    //*******************************
public:
private:

    //*******************************
    //messages
    //*******************************
public:
    /* output */
    CMessageOutput<CFloat> o_nDifferentialGear;
    CMessageOutput<CFloat> o_differentialGearRatio;
    CMessageOutput<CFloat> o_MWheelLeftFront;
    CMessageOutput<CFloat> o_MWheelRightFront;
    CMessageOutput<CFloat> o_MWheelLeftRear;
    CMessageOutput<CFloat> o_MWheelRightRear;
    /* parameter */
    CMessageParameter<CFloat> p_uCenter;
    CMessageParameter<CFloat> p_uFront;
    CMessageParameter<CFloat> p_uRear;
private:
    /* input */
    CMessageInput<CFloat> i_nWheelRightFront;
    CMessageInput<CFloat> i_nWheelLeftFront;
    CMessageInput<CFloat> i_nWheelRightRear;
    CMessageInput<CFloat> i_nWheelLeftRear;
    CMessageInput<CFloat> i_MPowerTrain;
    CMessageInput<CBool> i_frontWheelDrive;
    CMessageInput<CBool> i_rearWheelDrive;

    //*******************************
    // methods
    //*******************************
public:
    void init( IMessage<CFloat>& f_nWheelRightFront,
               IMessage<CFloat>& f_nWheelLeftFront,
               IMessage<CFloat>& f_nWheelRightRear,
               IMessage<CFloat>& f_nWheelLeftRear,
               IMessage<CFloat>& f_MPowerTrain,
               IMessage<CBool>& f_frontWheelDrive,
               IMessage<CBool>& f_rearWheelDrive );
private:
    void calc( CFloat f_dT, CFloat f_time );

    //*******************************
    //variables
    //*******************************
public:
private:
};

#endif // CDifferentialGear_H
