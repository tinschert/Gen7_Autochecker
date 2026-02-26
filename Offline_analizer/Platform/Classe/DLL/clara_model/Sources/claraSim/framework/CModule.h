/*!
********************************************************************************
@class CModule
@ingroup framework
@brief Basis class for implementation for all multitask safe modules

@author Robert Erhart, ett2si (18.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- integration method is inherited from CClass_ct
********************************************************************************
@param[in]  NumberOfStates             [CInt]   number of states
@param[in]  NumberOfIntegrationSteps   [CInt]   number of integration steps
********************************************************************************
@ToDo: os independent interface (mutex and event)
********************************************************************************
*/
#ifndef CMODULE_CT_H
#define CMODULE_CT_H

#include <vector>

#include "./OSInterface/OSSyncPrimitive.h"

#include "CClass_ct.h"

class CModuleInterface
{
    //*******************************
    // constructor/destructor/copy
    //*******************************
public:
    CModuleInterface()
    {
        __moduleInstanceCounter__++;
    };
    virtual ~CModuleInterface() {};

    //*******************************
    // methods
    //*******************************
    virtual void process( CFloat f_dT, CFloat f_time ) = 0;

protected:
    static uint16_t __moduleInstanceCounter__;
};


//*******************************
//Specialization for ExternTrigger Base
//*******************************
template < uint16_t NumberOfStates = 0, uint16_t NumberOfIntegrationSteps = 2, bool ExternTrigger = false >
class CModule

{
private:
    CModule() {};
    virtual ~CModule() {};
};

//Specialization for ExternTrigger = true
template < uint16_t NumberOfStates, uint16_t NumberOfIntegrationSteps>
class CModule<NumberOfStates, NumberOfIntegrationSteps, true> :  public CClass_ct<NumberOfStates, NumberOfIntegrationSteps>, public CModuleInterface
{
    //*******************************
    // constructor/destructor/copy
    //*******************************
public:
    CModule():
        m_EventEndProcess(),
        m_externSync( false ),
        m_externSyncTrigger( false )
    {
        EventCreate(m_EventEndProcess, "CModuleInterface", __moduleInstanceCounter__);
        m_messageParameter_a.clear();
        m_messageInput_a.clear();
        m_messageOutput_a.clear();
    };
    virtual ~CModule() {};

private:
    CModule( const CModule<NumberOfStates, NumberOfIntegrationSteps>& f_module ) = delete;

    //*******************************
    // methods
    //*******************************
public:
    void process( CFloat f_dT, CFloat f_time )
    {
        m_externSyncTrigger = m_externSync;
        for( ::std::vector<CMessageParameterInterface*>::const_iterator myiter = m_messageParameter_a.begin(); myiter != m_messageParameter_a.end(); ++myiter )
        {
            ( *myiter )->copyValueComToWork( f_dT, f_time );
        }
        for( ::std::vector<CMessageInputInterface*>::const_iterator myiter = m_messageInput_a.begin(); myiter != m_messageInput_a.end(); ++myiter )
        {
            ( *myiter )->copyValueComToWork( f_dT, f_time );
        }
        CClass_ct<NumberOfStates, NumberOfIntegrationSteps>::process( f_dT, f_time );
        for( ::std::vector<CMessageParameterInterface*>::const_iterator myiter = m_messageParameter_a.begin(); myiter != m_messageParameter_a.end(); ++myiter )
        {
            ( *myiter )->copyValueWorkToCom( f_time );
        }
        for( ::std::vector<CMessageOutputInterface*>::const_iterator myiter = m_messageOutput_a.begin(); myiter != m_messageOutput_a.end(); ++myiter )
        {
            ( *myiter )->copyValueWorkToCom( f_time );
        }
        if( m_externSyncTrigger == true )
        {
            m_externSync = false;
            EventSet( m_EventEndProcess );
        }
    };

    /*!
      * manually activate external trigger, without waiting for event (normally use externSyncProcess!)
      */
    void setExternTrigger()
    {
        m_externSync = true;
    }

    void externSyncProcess( long double f_timeout )
    {
        m_externSync = true;
        EventWait( m_EventEndProcess, f_timeout );
        EventReset( m_EventEndProcess );
    };

    bool getExternTrigger()
    {
        return m_externSyncTrigger;
    };

protected:
    void initializationMessages()
    {
        EventReset( m_EventEndProcess );

        for( ::std::vector<CMessageParameterInterface*>::const_iterator myiter = m_messageParameter_a.begin(); myiter != m_messageParameter_a.end(); ++myiter )
        {
            ( *myiter )->copyValueInit();
        }
        for( ::std::vector<CMessageOutputInterface*>::const_iterator myiter = m_messageOutput_a.begin(); myiter != m_messageOutput_a.end(); ++myiter )
        {
            ( *myiter )->copyValueInit();
        }
        //take the output value of the CMessageOutput, if linked
        for( ::std::vector<CMessageInputInterface*>::const_iterator myiter = m_messageInput_a.begin(); myiter != m_messageInput_a.end(); ++myiter )
        {
            ( *myiter )->copyValueComToWork( 0, 0 );
        }
    };

    template<typename T1, typename T2, uint32_t HistoryBufferLength>
    void addMessageParameter( CMessageParameter<T1, HistoryBufferLength>& f_message, T2 f_initValue )
    {
        f_message.init( static_cast<T1>( f_initValue ) );
        m_messageParameter_a.push_back( &f_message );
    };

    template<typename T1, typename T2, uint32_t HistoryBufferLength>
    void addMessageParameter( CMessageParameter<T1, HistoryBufferLength>& f_message, T2 f_initValue, const char* f_messageDescription )
    {
        f_message.setMessageDescription( f_messageDescription );
        f_message.init( static_cast<T1>( f_initValue ) );
        m_messageParameter_a.push_back( &f_message );
    };


    template<typename T1, typename T2>
    void addMessageInput( CMessageInput<T1>& f_message, T2 f_initValue )
    {
        f_message.init( static_cast<T1>( f_initValue ) );
        m_messageInput_a.push_back( &f_message );
    };

    template < typename T, typename module >
    void addMessageInput( CMessageInput<T, module, CModuleVector<module> >& f_message )
    {
        //f_message.init( f_initValue );
        m_messageInput_a.push_back( &f_message );
    };

    template<typename T1, typename T2, uint32_t HistoryBufferLength>
    void addMessageOutput( CMessageOutput<T1, HistoryBufferLength>& f_message, T2 f_initValue )
    {
        f_message.init( static_cast<T1>( f_initValue ) );
        m_messageOutput_a.push_back( &f_message );
    };

    template<typename T1, typename T2, uint32_t HistoryBufferLength>
    void addMessageOutput( CMessageOutput<T1, HistoryBufferLength>& f_message, T2 f_initValue, const char* f_messageDescription )
    {
        f_message.setMessageDescription( f_messageDescription );
        f_message.init( static_cast<T1>( f_initValue ) );
        m_messageOutput_a.push_back( &f_message );
    };


    //virtual void calcPre( CFloat f_dT );                      // "virtual" because the derivated class can overload this method
    //virtual void calc( CFloat f_dT ) = 0;                     // abstract method for NumberOfStates=0, because the derivated class must overload this method
    //virtual CFloatVector & ddt( CFloatVector & state ) = 0;   // abstract method for NumberOfStates>0, because the derivated class must overload this method
    //virtual void calcPost( CFloat f_dT );                     // "virtual" because the derivated class can overload this method

    //*******************************
    //variables
    //*******************************
private:
    ::std::vector<CMessageParameterInterface*> m_messageParameter_a;
    ::std::vector<CMessageInputInterface*> m_messageInput_a;
    ::std::vector<CMessageOutputInterface*> m_messageOutput_a;

    event_t m_EventEndProcess;
    bool m_externSync;
    bool m_externSyncTrigger;
};


//Specialization for ExternTrigger = false
template < uint16_t NumberOfStates, uint16_t NumberOfIntegrationSteps>
class CModule<NumberOfStates, NumberOfIntegrationSteps, false> :  public CClass_ct<NumberOfStates, NumberOfIntegrationSteps>, public CModuleInterface
{
    //*******************************
    // constructor/destructor/copy
    //*******************************
public:
    CModule()
    {
        m_messageParameter_a.clear();
        m_messageInput_a.clear();
        m_messageOutput_a.clear();
    };
    virtual ~CModule() {};

private:
    CModule( const CModule<NumberOfStates, NumberOfIntegrationSteps>& f_module )
    {};

    //*******************************
    // methods
    //*******************************
public:
    void process( CFloat f_dT, CFloat f_time )
    {
        for( ::std::vector<CMessageParameterInterface*>::const_iterator myiter = m_messageParameter_a.begin(); myiter != m_messageParameter_a.end(); ++myiter )
        {
            ( *myiter )->copyValueComToWork( f_dT, f_time );
        }
        for( ::std::vector<CMessageInputInterface*>::const_iterator myiter = m_messageInput_a.begin(); myiter != m_messageInput_a.end(); ++myiter )
        {
            ( *myiter )->copyValueComToWork( f_dT, f_time );
        }
        CClass_ct<NumberOfStates, NumberOfIntegrationSteps>::process( f_dT, f_time );
        for( ::std::vector<CMessageParameterInterface*>::const_iterator myiter = m_messageParameter_a.begin(); myiter != m_messageParameter_a.end(); ++myiter )
        {
            ( *myiter )->copyValueWorkToCom( f_time );
        }
        for( ::std::vector<CMessageOutputInterface*>::const_iterator myiter = m_messageOutput_a.begin(); myiter != m_messageOutput_a.end(); ++myiter )
        {
            ( *myiter )->copyValueWorkToCom( f_time );
        }
    };

protected:
    void initializationMessages()
    {
        for( ::std::vector<CMessageParameterInterface*>::const_iterator myiter = m_messageParameter_a.begin(); myiter != m_messageParameter_a.end(); ++myiter )
        {
            ( *myiter )->copyValueInit();
        }
        for( ::std::vector<CMessageOutputInterface*>::const_iterator myiter = m_messageOutput_a.begin(); myiter != m_messageOutput_a.end(); ++myiter )
        {
            ( *myiter )->copyValueInit();
        }
        //take the output value of the CMessageOutput, if linked
        for( ::std::vector<CMessageInputInterface*>::const_iterator myiter = m_messageInput_a.begin(); myiter != m_messageInput_a.end(); ++myiter )
        {
            ( *myiter )->copyValueComToWork( 0, 0 );
        }
    };

    template<typename T1, typename T2, uint32_t HistoryBufferLength>
    void addMessageParameter( CMessageParameter<T1, HistoryBufferLength>& f_message, T2 f_initValue )
    {
        f_message.init( static_cast<T1>( f_initValue ) );
        m_messageParameter_a.push_back( &f_message );
    };

    template<typename T1, typename T2, uint32_t HistoryBufferLength>
    void addMessageParameter( CMessageParameter<T1, HistoryBufferLength>& f_message, T2 f_initValue, const char* f_messageDescription )
    {
        f_message.setMessageDescription( f_messageDescription );
        f_message.init( static_cast<T1>( f_initValue ) );
        m_messageParameter_a.push_back( &f_message );
    };

    template<typename T1, typename T2>
    void addMessageInput( CMessageInput<T1>& f_message, T2 f_initValue )
    {
        f_message.init( static_cast<T1>( f_initValue ) );
        m_messageInput_a.push_back( &f_message );
    };

    template < typename T, typename module >
    void addMessageInput( CMessageInput<T, module, CModuleVector<module> >& f_message )
    {
        //f_message.init( f_initValue );
        m_messageInput_a.push_back( &f_message );
    };

    template<typename T1, typename T2, uint32_t HistoryBufferLength>
    void addMessageOutput( CMessageOutput<T1, HistoryBufferLength>& f_message, T2 f_initValue )
    {
        f_message.init( static_cast<T1>( f_initValue ) );
        m_messageOutput_a.push_back( &f_message );
    };

    template<typename T1, typename T2, uint32_t HistoryBufferLength>
    void addMessageOutput( CMessageOutput<T1, HistoryBufferLength>& f_message, T2 f_initValue, const char* f_messageDescription )
    {
        f_message.setMessageDescription( f_messageDescription );
        f_message.init( static_cast<T1>( f_initValue ) );
        m_messageOutput_a.push_back( &f_message );
    };

    //virtual void calcPre( CFloat f_dT );                      // "virtual" because the derivated class can overload this method
    //virtual void calc( CFloat f_dT ) = 0;                   // abstract method for NumberOfStates=0, because the derivated class must overload this method
    //virtual CFloatVector & ddt( CFloatVector & state ) = 0; // abstract method for NumberOfStates>0, because the derivated class must overload this method
    //virtual void calcPost( CFloat f_dT );                     // "virtual" because the derivated class can overload this method

    //*******************************
    //variables
    //*******************************
private:
    ::std::vector<CMessageParameterInterface*> m_messageParameter_a;
    ::std::vector<CMessageInputInterface*> m_messageInput_a;
    ::std::vector<CMessageOutputInterface*> m_messageOutput_a;
};

#endif // CMODULE_CT_H
