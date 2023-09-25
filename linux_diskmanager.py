import os
import getpass

volumeNameBuffer = os.path.join('/media', f'{getpass.getuser()}')  # Replace 'your_username' with your actual username
fileSystemNameBuffer = None

def SetDriveVolumeName(mount_point):
    try:
        file_system_stat = os.statvfs(mount_point)
        fileSystemNameBuffer = os.path.basename(mount_point)
        return mount_point
    except FileNotFoundError as e:
        return e

def GetDriveVolumeName(mount_point):
    if fileSystemNameBuffer:
        return f"{fileSystemNameBuffer} ({mount_point})"
    else:
        return f"{mount_point}"

def GetFileSytemNameBuffer():
    return fileSystemNameBuffer

# Example usage
drive_letter = '/media/cyber/'  # Replace with your actual mount point
SetDriveVolumeName(drive_letter)
print(GetDriveVolumeName(drive_letter))
print(GetFileSytemNameBuffer())
