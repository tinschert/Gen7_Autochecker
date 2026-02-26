import ctypes
from ctypes import wintypes

class _DISPLAY_DEVICEA(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('DeviceName', wintypes.WCHAR * 32),
        ('DeviceString', wintypes.WCHAR * 128),
        ('StateFlags', wintypes.DWORD),
        ('DeviceID', wintypes.WCHAR * 128),
        ('DeviceKey', wintypes.WCHAR * 128)
    ]

class _MONITORINFOEXA(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('rcMonitor', wintypes.RECT),
        ('rcWork', wintypes.RECT),
        ('dwFlags', wintypes.DWORD),
        ('szDevice', wintypes.WCHAR * 32)        
    ]

class LUID(ctypes.Structure):
    _fields_ = [
        ('LowPart', wintypes.DWORD),
        ('HighPart', wintypes.LONG),
    ]

class DISPLAYCONFIG_PATH_SOURCE_INFO(ctypes.Structure):
    _fields_ = [
        ('adapterId', LUID),
        ('id', ctypes.c_uint32),
        ('modeInfoIdx', ctypes.c_uint32),
        ('statusFlags', ctypes.c_uint32)
    ]

class DISPLAYCONFIG_RATIONAL(ctypes.Structure):
    _fields_ = [
        ('Numerator', ctypes.c_uint32),
        ('Denominator', ctypes.c_uint32),
    ]

class DISPLAYCONFIG_PATH_TARGET_INFO(ctypes.Structure):
    _fields_ = [
        ('adapterId', LUID),
        ('id', ctypes.c_uint32),
        ('modeInfoIdx', ctypes.c_uint32),
        ('outputTechnology', ctypes.c_uint32),
        ('rotation', ctypes.c_uint32),
        ('scaling', ctypes.c_uint32),
        ('refreshRate', DISPLAYCONFIG_RATIONAL),
        ('scanLineOrdering', ctypes.c_uint32),
        ('targetAvailable', wintypes.BOOL),
        ('statusFlags', ctypes.c_uint32)
    ]

class DISPLAYCONFIG_PATH_INFO(ctypes.Structure):
    _fields_ = [
        ('sourceInfo', DISPLAYCONFIG_PATH_SOURCE_INFO),
        ('targetInfo', DISPLAYCONFIG_PATH_TARGET_INFO),
        ('flags', ctypes.c_uint32)
    ]

class DISPLAYCONFIG_2DREGION(ctypes.Structure):
    _fields_ = [
        ('cx', ctypes.c_uint32),
        ('cy', ctypes.c_uint32),
    ]

class DISPLAYCONFIG_VIDEO_SIGNAL_INFO(ctypes.Structure):
    _fields_ = [
        ('pixelRate', ctypes.c_uint64),
        ('hSyncFreq', wintypes.DWORD),
        ('vSyncFreq', wintypes.DWORD),
        ('activeSize', DISPLAYCONFIG_2DREGION),
        ('totalSize', DISPLAYCONFIG_2DREGION),
        ('videoStandard', ctypes.c_uint32),
        ('scanLineOrdering', ctypes.c_uint32),
    ]

class DISPLAYCONFIG_TARGET_MODE(ctypes.Structure):
    _fields_ = [
        ('targetVideoSignalInfo', DISPLAYCONFIG_VIDEO_SIGNAL_INFO)
    ]

class DISPLAYCONFIG_SOURCE_MODE(ctypes.Structure):
    _fields_ = [
        ('width', ctypes.c_uint32),
        ('height', ctypes.c_uint32),
        ('pixelFormat', ctypes.c_uint32),
        ('position', DISPLAYCONFIG_2DREGION)
    ]

class DISPLAYCONFIG_MODE_INFO(ctypes.Structure):
    _fields_ = [
        ('infoType', ctypes.c_uint32),
        ('id', ctypes.c_uint32),
        ('adapterId', LUID),
        ('signalInfo', DISPLAYCONFIG_TARGET_MODE),
        ('sourceMode', DISPLAYCONFIG_SOURCE_MODE)
    ]

class DISPLAYCONFIG_DEVICE_INFO_HEADER(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.c_uint32),
        ('size', ctypes.c_uint32),
        ('adapterId', LUID),
        ('id', ctypes.c_uint32),
    ]

class DISPLAYCONFIG_SOURCE_DEVICE_NAME(ctypes.Structure):
    _fields_ = [
        ('header', DISPLAYCONFIG_DEVICE_INFO_HEADER),
        ('viewGdiDeviceName', wintypes.WCHAR * 32),
    ]

class DISPLAYCONFIG_TARGET_DEVICE_NAME(ctypes.Structure):
    _fields_ = [
        ('header', DISPLAYCONFIG_DEVICE_INFO_HEADER),
        ('flags', ctypes.c_uint32),
        ('outputTechnology', ctypes.c_uint32),
        ('edidManufactureId', ctypes.c_uint16),
        ('edidProductCodeId', ctypes.c_uint16),
        ('connectorInstance', ctypes.c_uint32),
        ('monitorFriendlyDeviceName', wintypes.WCHAR * 64),
        ('monitorDevicePath', wintypes.WCHAR * 128)
    ]

MONITORENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)

monitors = list()

def monitorEnumCallback(hmonitor, hdc, lprect, lparam):
    monitors.append(wintypes.HMONITOR(hmonitor))
    return True

def getMonitorName(monitor):
    DISPLAYCONFIG_TOPOLOGY_ID = ctypes.c_uint32
    MONITORINFOEXW = _MONITORINFOEXA
    info = MONITORINFOEXW()
    info.cbSize = ctypes.sizeof(info)
    GetMonitorInfoW = ctypes.windll.user32.GetMonitorInfoW
    GetMonitorInfoW.restype = ctypes.c_bool
    if not GetMonitorInfoW(monitor, ctypes.byref(info)):
        raise Exception("GetMonitorInfoW failed")

    requiredPaths = ctypes.c_uint32()
    requiredModes = ctypes.c_uint32()

    GetDisplayConfigBufferSizes = ctypes.windll.user32.GetDisplayConfigBufferSizes
    GetDisplayConfigBufferSizes.restype = ctypes.c_int32
    QDC_ONLY_ACTIVE_PATHS = 2
    if GetDisplayConfigBufferSizes(QDC_ONLY_ACTIVE_PATHS, ctypes.byref(requiredPaths), ctypes.byref(requiredModes)) != 0:
        raise Exception("GetDisplayConfigBufferSizes failed")

    paths = (DISPLAYCONFIG_PATH_INFO * requiredPaths.value)()
    modes = (DISPLAYCONFIG_MODE_INFO * requiredModes.value)()
    currentTopologyId = DISPLAYCONFIG_TOPOLOGY_ID()
    QueryDisplayConfig = ctypes.windll.user32.QueryDisplayConfig
    QueryDisplayConfig.restype = ctypes.c_int32
    QDC_DATABASE_CURRENT = 4

    if QueryDisplayConfig(QDC_DATABASE_CURRENT, ctypes.byref(requiredPaths), paths, ctypes.byref(requiredModes), modes, ctypes.byref(currentTopologyId)) != 0:
        raise Exception("QueryDisplayConfig failed")

    for p in paths:
        DISPLAYCONFIG_DEVICE_INFO_GET_SOURCE_NAME = 1
        sourceName = DISPLAYCONFIG_SOURCE_DEVICE_NAME()
        sourceName.header.type = DISPLAYCONFIG_DEVICE_INFO_GET_SOURCE_NAME
        sourceName.header.size = ctypes.sizeof(sourceName)
        sourceName.header.adapterId = p.sourceInfo.adapterId
        sourceName.header.id = p.sourceInfo.id

        DisplayConfigGetDeviceInfo = ctypes.windll.user32.DisplayConfigGetDeviceInfo
        DisplayConfigGetDeviceInfo.restype = ctypes.c_int32

        if DisplayConfigGetDeviceInfo(ctypes.byref(sourceName.header)) != 0:
            raise Exception("DisplayConfigGetDeviceInfo failed")
        

        if info.szDevice == sourceName.viewGdiDeviceName:
            DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_NAME = 2
            name = DISPLAYCONFIG_TARGET_DEVICE_NAME()
            name.header.type = DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_NAME
            name.header.size = ctypes.sizeof(name)
            name.header.adapterId = p.sourceInfo.adapterId
            name.header.id = p.targetInfo.id

            if DisplayConfigGetDeviceInfo(ctypes.byref(name.header)) != 0:
                raise Exception("DisplayConfigGetDeviceInfo failed")
            
            return name.monitorFriendlyDeviceName

    return "unknown"

def get_esi_monitor_mapping(): 

    monitors.clear()

    EnumDisplayMonitors = ctypes.windll.user32.EnumDisplayMonitors
    EnumDisplayMonitors.restype = ctypes.c_bool   

    res = EnumDisplayMonitors(None, None, MONITORENUMPROC(monitorEnumCallback), 0)

    monitorMapping = dict()
    monitorMapping["ESI_FMC5_4K"] = -1
    monitorMapping["ESI_FMC6_4K"] = -1

    monitorID = 0

    for monitor in monitors:
        try:
            monitorName = getMonitorName(monitor)
            if monitorName in monitorMapping:
                monitorMapping[monitorName] = monitorID
        except Exception as e:
            print(f"Error: {e}")
        monitorID += 1

    return monitorMapping
        

def main():
    mapping = get_esi_monitor_mapping()

    for key, value in mapping.items():
        print(f"{key} {value}")


if __name__ == "__main__":
    main()