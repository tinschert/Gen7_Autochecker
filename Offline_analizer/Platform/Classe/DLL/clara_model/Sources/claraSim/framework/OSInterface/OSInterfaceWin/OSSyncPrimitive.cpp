/*!
********************************************************************************
@class OSSyncPrimitive
@ingroup framework
@brief interface OSSyncPrimitive for windows use case with event handling

@author Robert Erhart, ett2si (2024.01.17)
@copyright (c) Robert Bosch GmbH 2024. All rights reserved.
********************************************************************************
@remark
todo: move name string to CreateXXX lpName
********************************************************************************
*/

#include "../OSSyncPrimitive.h"

#include <windows.h>
#include <string>


// MUTEX primitive
struct mutex_t::impl
{
    HANDLE handle;
    ::std::string name;
};
mutex_t::mutex_t() : impl_p{::std::make_unique<impl>()} {}
mutex_t::~mutex_t() = default;

bool MutexCreate( mutex_t& hMutex )
{
    return (hMutex.impl_p->handle = CreateMutex( NULL, false, NULL )) != NULL;
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
    DWORD l_msTimout = static_cast<DWORD>( f_sTimeout * 1E3 );
    return WaitForSingleObject( hMutex.impl_p->handle, l_msTimout ) == WAIT_OBJECT_0;
};

bool MutexAcquire( mutex_t& hMutex, uint64_t f_nsTimeout )
{
    DWORD l_msTimout = static_cast<DWORD>( f_nsTimeout / 1E6 );
    return WaitForSingleObject( hMutex.impl_p->handle, l_msTimout ) == WAIT_OBJECT_0;
};

void MutexRelease( mutex_t& hMutex )
{
    ReleaseMutex( hMutex.impl_p->handle );
}

void MutexClose( mutex_t& hMutex )
{
    CloseHandle( hMutex.impl_p->handle );
}


// EVENT primitive
struct event_t::impl
{
    HANDLE handle;
    ::std::string name;
};
event_t::event_t() : impl_p{::std::make_unique<impl>()} {}
event_t::~event_t() = default;

bool EventCreate( event_t& hEvent )
{
    return (hEvent.impl_p->handle = CreateEvent( NULL, true, true, NULL )) != NULL;
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
    DWORD l_msTimout = static_cast<DWORD>( f_sTimeout * 1E3 );
    return WaitForSingleObject( hEvent.impl_p->handle, l_msTimout ) == WAIT_OBJECT_0;
}

bool EventWait( event_t& hEvent, uint64_t f_nsTimeout )
{
    DWORD l_msTimout = static_cast<DWORD>( f_nsTimeout / 1E6 );
    return WaitForSingleObject( hEvent.impl_p->handle, l_msTimout) == WAIT_OBJECT_0;
}

void EventSet( event_t& hEvent )
{
    SetEvent(hEvent.impl_p->handle);
}

void EventReset( event_t& hEvent )
{
    ResetEvent( hEvent.impl_p->handle );
}

void EventClose( event_t& hEvent )
{
    CloseHandle( hEvent.impl_p->handle );
}
