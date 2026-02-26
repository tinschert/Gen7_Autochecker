import ctypes, os

try:
    dll = ctypes.WinDLL(os.path.abspath(__file__) + r'../../../../Classe/DLL/Release64/RoadObj.dll')
except:
    dll = ctypes.WinDLL(r'../../Classe/DLL/Release64/RoadObj.dll')

# Alias für: ?oa_Read_ByteArray_RA6LGU_Azimuth@@YANQEAEH@Z
oa_Read_ByteArray_RA6LGU_Azimuth = getattr(dll, '?oa_Read_ByteArray_RA6LGU_Azimuth@@YANQEAEH@Z')
oa_Read_ByteArray_RA6LGU_Azimuth.restype = ctypes.c_double
oa_Read_ByteArray_RA6LGU_Azimuth.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

# Alias für: ?oa_Read_ByteArray_RA6LGU_Mounting_Position_X@@YANQEAE@Z
oa_Read_ByteArray_RA6LGU_Mounting_Position_X = getattr(dll, '?oa_Read_ByteArray_RA6LGU_Mounting_Position_X@@YANQEAE@Z')
oa_Read_ByteArray_RA6LGU_Mounting_Position_X.restype = ctypes.c_double
oa_Read_ByteArray_RA6LGU_Mounting_Position_X.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
]

# Alias für: ?oa_Read_ByteArray_RA6LGU_Mounting_Position_Y@@YANQEAE@Z
oa_Read_ByteArray_RA6LGU_Mounting_Position_Y = getattr(dll, '?oa_Read_ByteArray_RA6LGU_Mounting_Position_Y@@YANQEAE@Z')
oa_Read_ByteArray_RA6LGU_Mounting_Position_Y.restype = ctypes.c_double
oa_Read_ByteArray_RA6LGU_Mounting_Position_Y.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
]

# Alias für: ?oa_Read_ByteArray_RA6LGU_Mounting_Position_Yaw@@YANQEAE@Z
oa_Read_ByteArray_RA6LGU_Mounting_Position_Yaw = getattr(dll, '?oa_Read_ByteArray_RA6LGU_Mounting_Position_Yaw@@YANQEAE@Z')
oa_Read_ByteArray_RA6LGU_Mounting_Position_Yaw.restype = ctypes.c_double
oa_Read_ByteArray_RA6LGU_Mounting_Position_Yaw.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
]

# Alias für: ?oa_Read_ByteArray_RA6LGU_Mounting_Position_Z@@YANQEAE@Z
oa_Read_ByteArray_RA6LGU_Mounting_Position_Z = getattr(dll, '?oa_Read_ByteArray_RA6LGU_Mounting_Position_Z@@YANQEAE@Z')
oa_Read_ByteArray_RA6LGU_Mounting_Position_Z.restype = ctypes.c_double
oa_Read_ByteArray_RA6LGU_Mounting_Position_Z.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
]

# Alias für: ?oa_Read_ByteArray_RA6LGU_Num_Valid_Loc@@YANQEAE@Z
oa_Read_ByteArray_RA6LGU_Num_Valid_Loc = getattr(dll, '?oa_Read_ByteArray_RA6LGU_Num_Valid_Loc@@YANQEAE@Z')
oa_Read_ByteArray_RA6LGU_Num_Valid_Loc.restype = ctypes.c_double
oa_Read_ByteArray_RA6LGU_Num_Valid_Loc.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
]

# Alias für: ?oa_Read_ByteArray_RA6LGU_RCS@@YANQEAEH@Z
oa_Read_ByteArray_RA6LGU_RCS = getattr(dll, '?oa_Read_ByteArray_RA6LGU_RCS@@YANQEAEH@Z')
oa_Read_ByteArray_RA6LGU_RCS.restype = ctypes.c_double
oa_Read_ByteArray_RA6LGU_RCS.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

# Alias für: ?oa_Read_ByteArray_RA6LGU_Radial_Distance@@YANQEAEH@Z
oa_Read_ByteArray_RA6LGU_Radial_Distance = getattr(dll, '?oa_Read_ByteArray_RA6LGU_Radial_Distance@@YANQEAEH@Z')
oa_Read_ByteArray_RA6LGU_Radial_Distance.restype = ctypes.c_double
oa_Read_ByteArray_RA6LGU_Radial_Distance.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

# Alias für: ?oa_Read_ByteArray_RA6LGU_Radial_Velocity@@YANQEAEH@Z
oa_Read_ByteArray_RA6LGU_Radial_Velocity = getattr(dll, '?oa_Read_ByteArray_RA6LGU_Radial_Velocity@@YANQEAEH@Z')
oa_Read_ByteArray_RA6LGU_Radial_Velocity.restype = ctypes.c_double
oa_Read_ByteArray_RA6LGU_Radial_Velocity.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Distance_X@@YANQEAEH@Z
oa_Read_ByteArray_RA6SGU_Distance_X = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Distance_X@@YANQEAEH@Z')
oa_Read_ByteArray_RA6SGU_Distance_X.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Distance_X.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Distance_Y@@YANQEAEH@Z
oa_Read_ByteArray_RA6SGU_Distance_Y = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Distance_Y@@YANQEAEH@Z')
oa_Read_ByteArray_RA6SGU_Distance_Y.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Distance_Y.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Mounting_Position_X@@YANQEAE@Z
oa_Read_ByteArray_RA6SGU_Mounting_Position_X = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Mounting_Position_X@@YANQEAE@Z')
oa_Read_ByteArray_RA6SGU_Mounting_Position_X.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Mounting_Position_X.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Mounting_Position_Y@@YANQEAE@Z
oa_Read_ByteArray_RA6SGU_Mounting_Position_Y = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Mounting_Position_Y@@YANQEAE@Z')
oa_Read_ByteArray_RA6SGU_Mounting_Position_Y.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Mounting_Position_Y.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Mounting_Position_Yaw@@YANQEAE@Z
oa_Read_ByteArray_RA6SGU_Mounting_Position_Yaw = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Mounting_Position_Yaw@@YANQEAE@Z')
oa_Read_ByteArray_RA6SGU_Mounting_Position_Yaw.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Mounting_Position_Yaw.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Mounting_Position_Z@@YANQEAE@Z
oa_Read_ByteArray_RA6SGU_Mounting_Position_Z = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Mounting_Position_Z@@YANQEAE@Z')
oa_Read_ByteArray_RA6SGU_Mounting_Position_Z.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Mounting_Position_Z.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Num_Valid_Obj@@YANQEAE@Z
oa_Read_ByteArray_RA6SGU_Num_Valid_Obj = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Num_Valid_Obj@@YANQEAE@Z')
oa_Read_ByteArray_RA6SGU_Num_Valid_Obj.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Num_Valid_Obj.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_RCS@@YANQEAEH@Z
oa_Read_ByteArray_RA6SGU_RCS = getattr(dll, '?oa_Read_ByteArray_RA6SGU_RCS@@YANQEAEH@Z')
oa_Read_ByteArray_RA6SGU_RCS.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_RCS.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Reference_Point@@YANQEAEH@Z
oa_Read_ByteArray_RA6SGU_Reference_Point = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Reference_Point@@YANQEAEH@Z')
oa_Read_ByteArray_RA6SGU_Reference_Point.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Reference_Point.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Velocity_X@@YANQEAEH@Z
oa_Read_ByteArray_RA6SGU_Velocity_X = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Velocity_X@@YANQEAEH@Z')
oa_Read_ByteArray_RA6SGU_Velocity_X.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Velocity_X.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Velocity_Y@@YANQEAEH@Z
oa_Read_ByteArray_RA6SGU_Velocity_Y = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Velocity_Y@@YANQEAEH@Z')
oa_Read_ByteArray_RA6SGU_Velocity_Y.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Velocity_Y.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

# Alias für: ?oa_Read_ByteArray_RA6SGU_Yaw_Angle@@YANQEAEH@Z
oa_Read_ByteArray_RA6SGU_Yaw_Angle = getattr(dll, '?oa_Read_ByteArray_RA6SGU_Yaw_Angle@@YANQEAEH@Z')
oa_Read_ByteArray_RA6SGU_Yaw_Angle.restype = ctypes.c_double
oa_Read_ByteArray_RA6SGU_Yaw_Angle.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int,
]

