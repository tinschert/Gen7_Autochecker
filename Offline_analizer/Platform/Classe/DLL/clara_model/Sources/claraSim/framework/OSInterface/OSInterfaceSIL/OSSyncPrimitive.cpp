/*!
********************************************************************************
@class OSSyncPrimitive
@ingroup framework
@brief dummy interface OSSyncPrimitive for SIL use case

@author Robert Erhart, ett2si (2024.01.12)
@copyright (c) Robert Bosch GmbH 2024. All rights reserved.
********************************************************************************
@remark
In the SIL use case no os sync stuff and model multiprocessing is useful to
fulfil the full reproducibility. Ths is the reason for this dummy interface.
********************************************************************************
*/

#include "../OSSyncPrimitive.h"


// MUTEX primitive
struct mutex_t::impl
{

};
mutex_t::mutex_t() : impl_p{::std::make_unique<impl>()} {}
mutex_t::~mutex_t() = default;

bool MutexCreate( mutex_t& hMutex )
{
    return true;
}

bool MutexCreate( mutex_t& hMutex, ::std::string f_name )
{
    return true;
}

bool MutexCreate( mutex_t& hMutex, ::std::string f_name, uint32_t f_referenceCounter )
{
    return true;
}

bool MutexAcquire( mutex_t& hMutex, long double f_sTimeout )
{
    return true;
}

bool MutexAcquire( mutex_t& hMutex, uint64_t f_nsTimeout )
{
    return true;
}

void MutexRelease( mutex_t& hMutex )
{}

void MutexClose( mutex_t& hMutex )
{}


// EVENT primitive
struct event_t::impl
{

};
event_t::event_t() : impl_p{::std::make_unique<impl>()} {}
event_t::~event_t() = default;

bool EventCreate( event_t& hEvent )
{
    return true;
}

bool EventCreate( event_t& hEvent, ::std::string f_name )
{
    return true;
}

bool EventCreate( event_t& hEvent, ::std::string f_name, uint32_t f_referenceCounter )
{
    return true;
}

bool EventWait( event_t& hEvent, long double f_sTimeout )
{
    return true;
}

bool EventWait( event_t& hEvent, uint64_t f_nsTimeout )
{
    return true;
}

void EventSet( event_t& hEvent )
{}

void EventReset( event_t& hEvent )
{}

void EventClose( event_t& hEvent )
{}
