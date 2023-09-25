import ctypes

kernel32 = ctypes.windll.kernel32

volumeNameBuffer = ctypes.create_unicode_buffer(1024)
fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)

serial_number = None
max_component_length = None
file_system_flags = None

def SetDriveVolumeName(drive_letter):
    rc = kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(f"{drive_letter}\\"),
        volumeNameBuffer,
        ctypes.sizeof(volumeNameBuffer),
        serial_number,
        max_component_length,
        file_system_flags,
        fileSystemNameBuffer,
        ctypes.sizeof(fileSystemNameBuffer)
    )
    return drive_letter

def GetDriveVolumeName(drive_letter):
    if volumeNameBuffer.value != "":
        return f"{volumeNameBuffer.value} ({drive_letter})"
    else: return f"USB Drive ({drive_letter})"
    
def GetFileSytemNameBuffer(): return fileSystemNameBuffer.value
