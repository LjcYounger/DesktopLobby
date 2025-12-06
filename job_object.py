import win32job
import ctypes
from ctypes import wintypes

PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_TERMINATE = 0x0001

def get_process_handle(pid):
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not handle:
        return ctypes.WinError()
    return handle


def create_job_object():
    job = win32job.CreateJobObject(None, "DesktopLobbyJob")
    extended_info = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)

    extended_info['BasicLimitInformation']['LimitFlags'] = win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, extended_info)
    return job

def assign_process_to_job(job, process):
    process_handle = get_process_handle(process.pid)
    win32job.AssignProcessToJobObject(job, process_handle)