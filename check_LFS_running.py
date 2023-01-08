import psutil


def is_lfs_running():
    for proc in psutil.process_iter():
        try:
            if proc.name() == "LFS.exe":

                return True

        except psutil.AccessDenied:
            print(
                "It seems like you do not have sufficient permissions to check for System Apps. Cannot automatically detect if LFS is running!")
            return True

    return False
