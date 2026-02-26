/*!
********************************************************************************
@class OSSyncPrimitive
@ingroup framework
@brief interface OSSyncPrimitive for linux use case with event handling

@author Robert Erhart, ett2si (2024.01.17)
@copyright (c) Robert Bosch GmbH 2024. All rights reserved.
********************************************************************************
@remark

********************************************************************************
*/

#include "../OSSyncPrimitive.h"

#include <semaphore.h>
#include <string>


// MUTEX primitive
struct mutex_t::impl
{
    pthread_mutex_t handle;
    ::std::string name;
};
mutex_t::mutex_t() : impl_p{::std::make_unique<impl>()} {}
mutex_t::~mutex_t() = default;

bool MutexCreate( mutex_t& hMutex )
{
    return 0 == pthread_mutex_init( &(hMutex.impl_p->handle), NULL );
}

bool MutexCreate( mutex_t& hMutex, ::std::string f_name )
{
    hMutex.impl_p->name = f_name;
    return MutexCreate( hMutex );
}

bool MutexCreate( mutex_t& hMutex, ::std::string f_name, uint32_t f_referenceCounter )
{
    hMutex.impl_p->name = f_name + ::std::to_string(f_referenceCounter);
    return MutexCreate( hMutex );
}

bool MutexAcquire( mutex_t& hMutex, long double f_sTimeout )
{
    uint64_t l_nsTimeout = f_sTimeout*1E9L;
    return MutexAcquire( hMutex, l_nsTimeout );
};

bool MutexAcquire( mutex_t& hMutex, uint64_t f_nsTimeout )
{
    struct timespec l_timeoutTime;
    clock_gettime(CLOCK_REALTIME, &l_timeoutTime);
    l_timeoutTime.tv_nsec += f_nsTimeout;
    while( l_timeoutTime.tv_nsec >= 1000000000LL )
    {
        ++l_timeoutTime.tv_sec;
        l_timeoutTime.tv_nsec -= 1000000000LL;
    }
    return 0 == pthread_mutex_timedlock(&(hMutex.impl_p->handle), &l_timeoutTime);
};

void MutexRelease( mutex_t& hMutex )
{
    pthread_mutex_unlock(&(hMutex.impl_p->handle));
}

void MutexClose( mutex_t& hMutex )
{
    pthread_mutex_destroy(&(hMutex.impl_p->handle));
}


// EVENT primitive
struct event_t::impl
{
    pthread_mutex_t mutex;
    pthread_cond_t cond;
    bool triggered;
    ::std::string name;
};
event_t::event_t() : impl_p{::std::make_unique<impl>()} {}
event_t::~event_t() = default;

bool EventCreate( event_t& hEvent )
{
    bool returnState = pthread_mutex_init(&(hEvent.impl_p->mutex), 0);
    returnState |= pthread_cond_init(&(hEvent.impl_p->cond), 0);
    hEvent.impl_p->triggered = false;
    return 0 == returnState;
}

bool EventCreate( event_t& hEvent, ::std::string f_name )
{
    hEvent.impl_p->name = f_name;
    return EventCreate( hEvent );
}

bool EventCreate( event_t& hEvent, ::std::string f_name, uint32_t f_referenceCounter )
{
    hEvent.impl_p->name = f_name + ::std::to_string(f_referenceCounter);
    return EventCreate( hEvent );
}

bool EventWait( event_t& hEvent, long double f_sTimeout )
{
    uint64_t l_nsTimeout = f_sTimeout*1E9L;
    return EventWait( hEvent, l_nsTimeout );
}

bool EventWait( event_t& hEvent, uint64_t f_nsTimeout )
{
    bool returnState = pthread_mutex_lock(&(hEvent.impl_p->mutex));
    struct timespec l_timeoutTime;
    clock_gettime(CLOCK_REALTIME, &l_timeoutTime);
    l_timeoutTime.tv_nsec += f_nsTimeout;
    while( l_timeoutTime.tv_nsec >= 1000000000LL )
    {
        ++l_timeoutTime.tv_sec;
        l_timeoutTime.tv_nsec -= 1000000000LL;
    }
    while (!hEvent.impl_p->triggered and 0 == returnState)
    {
         returnState |= pthread_cond_timedwait(&(hEvent.impl_p->cond), &(hEvent.impl_p->mutex), &l_timeoutTime);
    }
    returnState |= pthread_mutex_unlock(&(hEvent.impl_p->mutex));
    return 0 == returnState;
}

void EventSet( event_t& hEvent )
{
    pthread_mutex_lock(&(hEvent.impl_p->mutex));
    hEvent.impl_p->triggered = true;
    pthread_cond_signal(&(hEvent.impl_p->cond));
    //pthread_cond_broadcast(&(hEvent.impl_p->cond));
    pthread_mutex_unlock(&(hEvent.impl_p->mutex));
}

void EventReset( event_t& hEvent )
{
    pthread_mutex_lock(&(hEvent.impl_p->mutex));
    hEvent.impl_p->triggered = false;
    pthread_mutex_unlock(&(hEvent.impl_p->mutex));
}

void EventClose( event_t& hEvent )
{
    pthread_mutex_destroy(&(hEvent.impl_p->mutex));
    pthread_cond_destroy(&(hEvent.impl_p->cond));
}
