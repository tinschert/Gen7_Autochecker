/*
 *
 *	UsbMultiTester.cpp
 *
 *  Created on: 09.12.2020
 * @author BNC1LR
 */

#ifdef XENO

#include "UsbMultiTester.h"

UsbMultiTester::UsbMultiTester(void)
{
	this->m_UssSimulatorType = USB;
}

UsbMultiTester::~UsbMultiTester(void)
{	
}

uint8_t UsbMultiTester::Init(uint8_t address)
{
	if (this->m_multitester.m_UssSimulatorLoopRunning)
		return USSSIMULATOR_BUSY_ERR;

	this->InitializeMemberVariables();

	int  fd, idVendor, idProduct, busnum, devnum, dev_found;
	char sbuf[256];

	dev_found = 0;

	unsigned short value = 0;
	struct usbdevfs_ctrltransfer ctrl;


	DIR *devices = opendir(USB_SYS_DEVICES);
	if (devices != NULL) {
		struct dirent *entry;
		while ((entry = readdir(devices))) {
			if ((!isdigit(entry->d_name[0]) && strncmp(entry->d_name, "usb", 3))
				|| strchr(entry->d_name, ':'))
				continue;

			if (ReadAttrHex(entry->d_name, "idVendor", &idVendor) < 0
				|| idVendor != MULTITESTER_VENDOR_ID)
				continue;
			printf(" VendorId  = %04x\n", idVendor);

			if (ReadAttrHex(entry->d_name, "idProduct", &idProduct) < 0
				|| idProduct != MULTITESTER_PRODUCT_ID)
				continue;
			printf(" ProductId = %04x\n", idProduct);

			if (ReadAttrStr(entry->d_name, "product", sbuf, sizeof(sbuf)) < 0
				|| strcmp(sbuf, MULTITESTER_PRODUCT) != 0)
				continue;
			printf(" Product   = %s\n", sbuf);

			if (ReadAttrInt(entry->d_name, "busnum", &busnum) < 0)
				continue;

			if (ReadAttrInt(entry->d_name, "devnum", &devnum) < 0)
				continue;

			dev_found = 1;
			break;
		}
		closedir(devices);

	}
	else {
		FILE  *fp;
		if ((fp = fopen(USB_PROC_DEVICES, "r")) == NULL)
			return USSSIMULATOR_DEV_ERR;

		while (!dev_found && fgets(sbuf, sizeof(sbuf), fp)) {
			if (sscanf(sbuf, "T: Bus=%d Lev=%*d Prnt=%*d Port=%*d Cnt=%*d Dev#=%d",
				&busnum, &devnum)) {
				idVendor = idProduct = 0;
				sbuf[0] = 0;
			}
			else if (sscanf(sbuf, "P: Vendor=%x ProdID=%x", &idVendor, &idProduct)) {
			}
			else if (sscanf(sbuf, "S: Product=%30s", sbuf)) {

				if (idVendor != MULTITESTER_VENDOR_ID)
					continue;
				printf(" VendorId  = %04x\n", idVendor);

				if (idProduct != MULTITESTER_PRODUCT_ID)
					continue;
				printf(" ProductId = %04x\n", idProduct);

				if (strcmp(sbuf, MULTITESTER_PRODUCT) != 0)
					continue;
				printf(" Product   = %s\n", sbuf);

				dev_found = 1;
				break;
			}
		}
		fclose(fp);
	}

	if (dev_found == 0) {
		printf(" USB Device not found\n");
		return USSSIMULATOR_DEV_ERR;
	}

	/* Open the device */
	sprintf(sbuf, "%s/%03d/%03d", USB_DEV_PATH, busnum, devnum);
	if ((fd = open(sbuf, O_RDWR)) < 0) {
		sprintf(sbuf, "%s/%03d/%03d", USB_PROC_PATH, busnum, devnum);
		if ((fd = open(sbuf, O_RDWR)) < 0) {
			printf(" Open USB Device '%s' failed: %s\n", sbuf, strerror(errno));
			return USSSIMULATOR_DEV_ERR;
		}
	}

	m_mtUsbDevice.fd = fd;
	m_mtUsbDevice.address = address;

	struct usbdevfs_setinterface intf;
	intf.interface = MULTITESTER_IF_NO;
	intf.altsetting = 0;

	/* Claim interface of device */
	if (ioctl(m_mtUsbDevice.fd, USBDEVFS_CLAIMINTERFACE, &intf) < 0) {
		printf("ioctl USBDEVFS_CLAIMINTERFACE failed: %s\n", strerror(errno));
		goto Error;
	}

	ctrl.bRequestType = (0x02 << 5) | 0x80;
	ctrl.bRequest = 0x05;
	ctrl.wValue = 0;
	ctrl.wIndex = 1;
	ctrl.wLength = 12;
	ctrl.timeout = 2;
	ctrl.data = (void *)&value;

	if (ioctl(m_mtUsbDevice.fd, USBDEVFS_CONTROL, &ctrl) < 0) {
		printf("ioctl USBDEVFS_CONTROL SIO_POLL_MODEM_STATUS failed: %s\n", strerror(errno));
	}

	ctrl.bRequestType = 0x02 << 5;
	ctrl.bRequest = 0x00;

	if (ioctl(m_mtUsbDevice.fd, USBDEVFS_CONTROL, &ctrl) < 0) {
		printf("ioctl USBDEVFS_CONTROL SIO_RESET failed: %s\n", strerror(errno));
	}

	ctrl.bRequestType = 0x02 << 5;
	ctrl.bRequest = 0x09;
	/* Latency timeout in ms */
	ctrl.wValue = 0;

	if (ioctl(m_mtUsbDevice.fd, USBDEVFS_CONTROL, &ctrl) < 0) {
		printf("ioctl USBDEVFS_CONTROL SIO_SET_LATENCY_TIMEOUT failed: %s\n", strerror(errno));
	}

	/* Ensure that no messages are left over from a previous session */
	struct usbdevfs_bulktransfer bulk;
	unsigned char buf[MULTITESTER_BUF_SIZE];
	int len;
	bulk.ep = MULTITESTER_EP_IN;
	bulk.timeout = BULK_TIMEOUT_READ;
	bulk.data = buf;
	bulk.len = MULTITESTER_BUF_SIZE;
	while ((len = ioctl(m_mtUsbDevice.fd, USBDEVFS_BULK, &bulk)) > 2) {
		SleepMs(2000);
	}

	this->m_multitester_statistics.overruns = 0;
	this->m_multitester_statistics.readCount = 0;
	this->m_multitester_statistics.writeCount = 0;
	this->m_multitester_statistics.iterations = 1;
	this->m_multitester_statistics.missingMsgs = 0;

	/* Online check of UssSimulator*/
	if (WriteCheck() != USSSIMULATOR_OK)
	{
		PrintError("WriteCheck");
		return USSSIMULATOR_COM_SEND_ERR;
	}
	if (ReadCheck() != USSSIMULATOR_OK)
	{
		PrintError("ReadCheck");
		return USSSIMULATOR_COM_RECV_ERR;
	}

	/* Read firmware version of UssSimulator */
	if (ReadFirmware() != USSSIMULATOR_OK)
	{
		PrintError("ReadFirmware");
		return USSSIMULATOR_COM_SEND_ERR;
	}
	
	printf("UssSimulator: Firmware version %d.%d detected\n", getFirmwareMajor(), getFirmwareMinor());

	CreateMtThread("CommunicationThread");

	SleepMs(1000);

	return USSSIMULATOR_OK;

Error:
	ioctl(m_mtUsbDevice.fd, USBDEVFS_RELEASEINTERFACE, &intf);
	ioctl(m_mtUsbDevice.fd, USBDEVFS_RESET);
	close(m_mtUsbDevice.fd);

	return USSSIMULATOR_COM_ERR;
}

uint8_t UsbMultiTester::CloseUssSimulator(void)
{
	if (m_multitester.m_UssSimulatorLoopRunning)
	{
		m_multitester.m_UssSimulatorLoopRunning = false;
	}
	CleanUpInterface();
	rt_queue_delete(&m_multitester.m_msgQueue);
	rt_mutex_delete(&m_multitester.m_UssSimulatorMutex);
	rt_task_delete(&m_UssSimulatorLoop);

	return USSSIMULATOR_OK;
}

uint8_t UsbMultiTester::WriteCheck(void)
{
	tMsg msg;
	msg.startBytes = 0xFFFF;
	msg.address = m_mtUsbDevice.address << 1;
	msg.cmdIdentifier = 0xFE;

	struct usbdevfs_bulktransfer bulk;
	bulk.ep = MULTITESTER_EP_OUT;
	bulk.len = 4;
	bulk.timeout = BULK_TIMEOUT_WRITE;
	bulk.data = &msg;

	if (ioctl(m_mtUsbDevice.fd, USBDEVFS_BULK, &bulk) < 0) {
		printf("ioctl USBDEVFS_BULK (write): %s\n", strerror(errno));
		return USSSIMULATOR_INVAL_ARG_ERR;
	}

	return USSSIMULATOR_OK;
}

uint8_t UsbMultiTester::ReadCheck(void)
{
	struct usbdevfs_bulktransfer bulk;
	unsigned char sbuf[MULTITESTER_BUF_SIZE];
	double time;
	int len, res, i;

	bulk.ep = MULTITESTER_EP_IN;
	bulk.timeout = BULK_TIMEOUT_READ;
	bulk.data = sbuf;
	bulk.len = MULTITESTER_BUF_SIZE;

	res = 0;
	time = GetTime() + MSG_TIMEOUT_MS;
	while ((len = ioctl(m_mtUsbDevice.fd, USBDEVFS_BULK, &bulk)) >= 0 && GetTime() < time) {

		//DBG("%.3f - Msg rcvd : ", GetWallTime());

		for (i = 0; i < len; i++) {
			//DBG(" %02x", sbuf[i]);
			if ((sbuf[i] == 0xFE) || (sbuf[i] == 0xFD))
				res = 1;
		}
		//DBG("\n");
	}
	if (res == 0)
	{
		printf("MT_ReadCheck : Timeout occurred\n");
		return USSSIMULATOR_COM_ERR;
	}

	return USSSIMULATOR_OK;
}

uint8_t UsbMultiTester::WriteMsg(void* msg, uint32_t messageSize)
{
	struct usbdevfs_bulktransfer bulk;
	bulk.ep = MULTITESTER_EP_OUT;
	bulk.len = messageSize;
	bulk.timeout = BULK_TIMEOUT_WRITE;
	bulk.data = msg;

	if (ioctl(m_mtUsbDevice.fd, USBDEVFS_BULK, &bulk) < 0) {
		printf("ioctl USBDEVFS_BULK (write): %s\n", strerror(errno));
		m_multitester.m_UssSimulatorLoopRunning = 0;
		return USSSIMULATOR_COM_ERR;
	}
	//if (this->m_mtDevice.iterations % MULTITESTER_DEBUG_PERIOD == 0)
	//  USS_DBG("Msg sent : ");
	//uint8_t* dbgMsg = reinterpret_cast<uint8_t*>(msg);
	//for (uint32_t cnt = 0; cnt < messageSize; cnt++)
	//{
	//	//USS_DBG("%02x ", dbgMsg[cnt]);
	//USS_DBG("%d ", dbgMsg[cnt]);
	//}
	//USS_DBG("\n");
	//this->m_mtDevice.writeCount++;

	return USSSIMULATOR_OK;

}

uint8_t UsbMultiTester::ReadMsg(uint8_t readcheck, uint8_t address)
{
	return ReadMsg();
}

uint8_t UsbMultiTester::ReadMsg(void)
{
	struct usbdevfs_bulktransfer bulk;
	unsigned char sbuf[MULTITESTER_BUF_SIZE];
	double time;
	int len;

	bulk.ep = MULTITESTER_EP_IN;
	bulk.timeout = BULK_TIMEOUT_READ;
	bulk.data = sbuf;
	bulk.len = MULTITESTER_BUF_SIZE;

	time = GetTime() + MSG_TIMEOUT_MS;
	while ((len = ioctl(m_mtUsbDevice.fd, USBDEVFS_BULK, &bulk)) >= 0 && GetTime() < time) {

		/* first two bytes of response are modem status */
		//if ((this->m_mtDevice.iterations % MULTITESTER_DEBUG_PERIOD == 0) && _MULTITESTER_Debug_Verbose)
		//	DBG("%.3f - Msg rcvd : ", GetWallTime());
		int i;
		for (i = 0; i < len; i++) {

			/* Skip messages of type 0xFF which occur sometimes during initialization */
			if (sbuf[i] != 0xFF) {
				this->m_multitester_statistics.readCount++;
				//if ((this->m_mtDevice.iterations % MULTITESTER_DEBUG_PERIOD == 0) && _MULTITESTER_Debug_Verbose)
				//	DBG(" %02x", sbuf[i]);
			}
		}
		//if ((this->m_mtDevice.iterations % MULTITESTER_DEBUG_PERIOD == 0) && _MULTITESTER_Debug_Verbose)
			//DBG("\n");

		return len - 2;
	}
	//this->m_mtDevice.missingMsgs++;

	return USSSIMULATOR_OK;
}

uint8_t UsbMultiTester::ReadFirmware(void)
{
	tMsg msg;
	msg.startBytes = 0xFFFF;
	msg.address = m_mtUsbDevice.address << 1;
	msg.cmdIdentifier = 0xF1;

	struct usbdevfs_bulktransfer bulk;
	unsigned char sbuf[MULTITESTER_BUF_SIZE];
	bulk.ep = MULTITESTER_EP_OUT;
	bulk.len = 4;
	bulk.timeout = BULK_TIMEOUT_WRITE;
	bulk.data = &msg;

	if (ioctl(m_mtUsbDevice.fd, USBDEVFS_BULK, &bulk) < 0) {
		printf("ioctl USBDEVFS_BULK (write): %s\n", strerror(errno));
		return USSSIMULATOR_INVAL_ARG_ERR;
	}
	//UssSimulator_Debug("Msg sent : ", &msg, 4);

	double time;
	uint8_t len;

	bulk.ep = MULTITESTER_EP_IN;
	bulk.timeout = BULK_TIMEOUT_READ;
	bulk.data = sbuf;
	bulk.len = MULTITESTER_BUF_SIZE;

	time = GetTime() + MSG_TIMEOUT_MS;
	while ((len = ioctl(m_mtUsbDevice.fd, USBDEVFS_BULK, &bulk)) >= 0 && GetTime() < time) {

		//DBG("%.3f - Msg rcvd : ", GetWallTime());

		//for (uint8_t i = 0; i < len; i++) {
			//DBG(" %02x", sbuf[i]);
		//}
		m_FirmwareMajor = sbuf[0];
		m_FirmwareMinor = sbuf[1];
		//DBG("\n");
	}

	return USSSIMULATOR_OK;
}

void UsbMultiTester::CleanUpInterface(void)
{
	struct usbdevfs_setinterface intf;
	intf.interface = MULTITESTER_IF_NO;
	intf.altsetting = 0;
	if (ioctl(m_mtUsbDevice.fd, USBDEVFS_RELEASEINTERFACE, &intf) < 0)
	{
		printf("ioctl USBDEVFS_RELEASEINTERFACE: %s\n", strerror(errno));
	}
	ioctl(m_mtUsbDevice.fd, USBDEVFS_RESET);
	close(m_mtUsbDevice.fd);
}

FILE * UsbMultiTester::OpenFile(const char * devname, const char * attr)
{
	char filename[PATH_MAX];
	FILE *fd;

	snprintf(filename, PATH_MAX, "%s/%s/%s", USB_SYS_DEVICES, devname, attr);
	fd = fopen(filename, "r");

	return fd;
}

int UsbMultiTester::ReadAttrInt(const char * devname, const char * attr, int * value)
{
	int  ret;
	FILE *fd;

	fd = OpenFile(devname, attr);
	if (fd == NULL)
		return -1;

	ret = fscanf(fd, "%d", value);
	fclose(fd);

	if (ret != 1)
		return -1;

	return 0;
}

int UsbMultiTester::ReadAttrHex(const char * devname, const char * attr, int * value)
{
	int  ret;
	FILE* fd;

	fd = OpenFile(devname, attr);
	if (fd == NULL)
		return -1;

	ret = fscanf(fd, "%x", value);
	fclose(fd);

	if (ret != 1)
		return -1;

	return 0;
}

int UsbMultiTester::ReadAttrStr(const char * devname, const char * attr, char * str, int strln)
{
	char buf[128];
	int  ret;
	FILE *fd;

	ret = -1;

	fd = OpenFile(devname, attr);
	if (fd == NULL)
		return ret;

	if (fgets(buf, sizeof(buf), fd) != NULL) {
		int len = strlen(buf);
		if (0 < len && len <= strln) {
			if (buf[len - 1] == '\n')
				buf[--len] = '\0';
			strcpy(str, buf);
			ret = 0;
		}
	}
	fclose(fd);

	return ret;
}

#endif