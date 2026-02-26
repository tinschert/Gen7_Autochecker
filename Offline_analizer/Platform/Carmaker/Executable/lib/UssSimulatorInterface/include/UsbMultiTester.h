#pragma once

#ifndef USS_SIMULATOR_USB_H

#define USS_SIMULATOR_USB_H

#ifdef XENO


#include <linux/usbdevice_fs.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <errno.h>
#include <dirent.h>
#include <unistd.h>

#include "UssSimulator.h"

/* The following defines must not be changed */
#define USB_PROC_DEVICES     "/proc/bus/usb/devices"
#define USB_SYS_DEVICES      "/sys/bus/usb/devices"
#define USB_PROC_PATH        "/proc/bus/usb"
#define USB_DEV_PATH         "/dev/bus/usb"

#define MULTITESTER_VENDOR_ID       0x108c
#define MULTITESTER_PRODUCT_ID      0x0100
#define MULTITESTER_PRODUCT         "multi tester"

#define MULTITESTER_CFG_NO          1
#define MULTITESTER_IF_NO           1
#define MULTITESTER_EP_IN           0x82
#define MULTITESTER_EP_OUT          0x03
#define MULTITESTER_BUF_SIZE        512


/* Send operation timeout in ms */
#define BULK_TIMEOUT_WRITE      10

/* Read operation timeout in ms */
#define BULK_TIMEOUT_READ       10

typedef struct tMultiTesterUsbDevice {
    int	address;
    int	fd;
} tMultiTesterUsbDevice;

class UsbMultiTester: public UssSimulator
{
public:
	UsbMultiTester(void);
	virtual ~UsbMultiTester(void);

	uint8_t Init(const char* IpMultiTester, uint16_t ListeningPort) { return USSSIMULATOR_INVAL_ARG_ERR; }// call for UDP, invalid for USB
	uint8_t Init(uint8_t address); 
	uint8_t CloseUssSimulator(void);

private:
	uint8_t WriteCheck(void);
	uint8_t ReadCheck(void);
	//uint8_t WriteMsg(tMsg msg);
	uint8_t WriteMsg(void* msg, uint32_t messageSize);
	uint8_t ReadMsg(uint8_t readcheck, uint8_t address = NO_CLUSTER);
	uint8_t	ReadMsg(void);
	uint8_t ReadFirmware(void);
	void CleanUpInterface(void);

	static FILE * 	OpenFile(const char *devname, const char *attr);
	static int 		ReadAttrInt(const char *devname, const char *attr, int *value);
	static int 		ReadAttrHex(const char *devname, const char *attr, int *value);
	static int 		ReadAttrStr(const char *devname, const char *attr, char *str, int strln);

	tMultiTesterUsbDevice m_mtUsbDevice;
};

#endif // CM_HIL

#endif /* USS_SIMULATOR_USB_H */