#ifndef OSSyncPrimitive_H_
#define OSSyncPrimitive_H_

#include <string>
#include <memory>

//PIMPL implementation
struct mutex_t
{
    struct impl;
    ::std::unique_ptr<impl> impl_p;
public:
    mutex_t();
    ~mutex_t();
};

bool MutexCreate( mutex_t& hMutex );
bool MutexCreate( mutex_t& hMutex, ::std::string f_name );
bool MutexCreate( mutex_t& hMutex, ::std::string f_name, uint32_t f_referenceCounter );
bool MutexAcquire( mutex_t& hMutex, long double f_sTimeout );
bool MutexAcquire( mutex_t& hMutex, uint64_t f_nsTimeout );
void MutexRelease( mutex_t& hMutex );
void MutexClose( mutex_t& hMutex );


struct event_t
{
    struct impl;
    ::std::unique_ptr<impl> impl_p;
public:
    event_t();
    ~event_t();
};

bool EventCreate( event_t& hEvent );
bool EventCreate( event_t& hEvent, ::std::string f_name );
bool EventCreate( event_t& hEvent, ::std::string f_name, uint32_t f_referenceCounter );
bool EventWait( event_t& hEvent, long double f_sTimeout );
bool EventWait( event_t& hEvent, uint64_t f_nsTimeout );
void EventSet( event_t& hEvent );
void EventReset( event_t& hEvent );
void EventClose( event_t& hEvent );

#endif //OSSyncPrimitive_H_
