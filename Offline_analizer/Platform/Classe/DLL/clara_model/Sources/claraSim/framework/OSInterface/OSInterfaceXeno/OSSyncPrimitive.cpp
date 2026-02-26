/*!
********************************************************************************
@class OSSyncPrimitive
@ingroup framework
@brief interface OSSyncPrimitive for Xenolation use case

@author Robert Erhart, ett2si (2024.01.17)
@copyright (c) Robert Bosch GmbH 2024. All rights reserved.
********************************************************************************
@remark
********************************************************************************
*/

#include "../OSSyncPrimitive.h"
#include <string>

#include <xenolation/frameworkCore/CEvent.h>
#include <xenolation/frameworkCore/CMutex.h>


// MUTEX primitive
struct mutex_t::impl
{
    CMutex Mutex;
};
mutex_t::mutex_t() : impl_p{::std::make_unique<impl>()} {}
mutex_t::~mutex_t() = default;

bool MutexCreate( mutex_t& hMutex )
{
    hMutex.impl_p->Mutex.create(); //currently CMutex throw an exception, if not successful
    return true;
}

bool MutexCreate( mutex_t& hMutex, ::std::string f_name )
{
    hMutex.impl_p->Mutex.setName(f_name);
    hMutex.impl_p->Mutex.create(); //currently CMutex throw an exception, if not successful
    return true;
}

bool MutexCreate( mutex_t& hMutex, ::std::string f_name, uint32_t f_referenceCounter )
{
    hMutex.impl_p->Mutex.setName(f_name + ::std::to_string(f_referenceCounter));
    hMutex.impl_p->Mutex.create(); //currently CMutex throw an exception, if not successful
    return true;
}

bool MutexAcquire( mutex_t& hMutex, long double f_sTimeout )
{
    uint64_t l_nsTimeout = f_sTimeout*1E9L;
    MutexAcquire( hMutex, l_nsTimeout );
    return true;
}

bool MutexAcquire( mutex_t& hMutex, uint64_t f_nsTimeout )
{
    hMutex.impl_p->Mutex.acquire(f_nsTimeout); //currently CMutex throw an exception, if not successful
    return true;
}

void MutexRelease( mutex_t& hMutex )
{
    hMutex.impl_p->Mutex.release(); //currently CMutex throw an exception, if not successful
}

void MutexClose( mutex_t& hMutex )
{
    hMutex.impl_p->Mutex.remove(); //currently CMutex throw an exception, if not successful
}


// EVENT primitive
struct event_t::impl
{
    CEvent Event;
};
event_t::event_t() : impl_p{::std::make_unique<impl>()} {}
event_t::~event_t() = default;

bool EventCreate( event_t& hEvent )
{
    hEvent.impl_p->Event.create(); //currently CEvent throw an exception, if not successful
    return true;
}

bool EventCreate( event_t& hEvent, ::std::string f_name )
{
    hEvent.impl_p->Event.setName(f_name);
    hEvent.impl_p->Event.create(); //currently CEvent throw an exception, if not successful
    return true;
}

bool EventCreate( event_t& hEvent, ::std::string f_name, uint32_t f_referenceCounter )
{
    hEvent.impl_p->Event.setName(f_name + ::std::to_string(f_referenceCounter));
    hEvent.impl_p->Event.create(); //currently CEvent throw an exception, if not successful
    return true;
}

bool EventWait( event_t& hEvent, long double f_sTimeout )
{
    uint64_t l_nsTimeout = f_sTimeout*1E9L;
    EventWait( hEvent, l_nsTimeout ); //currently CEvent throw an exception, if not successful
    return true;
}

bool EventWait( event_t& hEvent, uint64_t f_nsTimeout )
{
    hEvent.impl_p->Event.wait(f_nsTimeout); //currently CEvent throw an exception, if not successful
    return true;
}

void EventSet( event_t& hEvent )
{
    hEvent.impl_p->Event.signal(); //currently CEvent throw an exception, if not successful
}

void EventReset( event_t& hEvent )
{
    hEvent.impl_p->Event.clear(); //currently CEvent throw an exception, if not successful
}

void EventClose( event_t& hEvent )
{
    hEvent.impl_p->Event.remove(); //currently CEvent throw an exception, if not successful
}
