"""
Status objects for files at the tagger.
These classes are wrappers around json stored in files with file names reflecting the input document to be tagged.
StatusLoggers live in /status, ProcessStatuses live in /process.

The only purpose of the ProcessStatus is to store the PID of the process that is currently tagging the file.
This is used to kill the process if the user wants to cancel the tagging.

The StatusLogger is the main class. It is used to log the status of a file. The status is a json object of the form:
{
  message: str,
  pending: bool
  busy: bool,
  error: bool,
  finished: bool
}
At most one of pending, busy, error, finished is true; or the file was not found.
"""

# Standard library
from __future__ import annotations
import os
import signal
import json
import sys
import logging
from typing import Any, Optional
import pathlib
import time
import fcntl

STATUS_FOLDER = "status"
PROCESS_FOLDER = "process"

log_format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(stream=sys.stdout, format=log_format, level=logging.INFO)


class FileMutex:
    """
    A mutex for file access. First acquires a lock on a lock file named original_file.lock, creating it if needed.
    Then opens the original file. When the mutex is released, the lock file is removed in an attempt to clean up.
    """

    def __init__(self, file_path: str, timeout: int = 5):
        """
        Create a new mutex for the file_path. timeout is the maximum time to wait for the lock.
        """
        self.timeout = timeout
        # Paths
        self.file_path = file_path
        self._lock_path = file_path + ".lock"
        # Files
        self._lock = None
        self.file = None

    def acquire(self, file_mode: str) -> None:
        """
        Acquire the lock and open the file in file_mode, once the lock is acquired. Sets self.file.
        """
        start_time = time.time()
        # Try to acquire the lock, if it fails, wait for a bit and try again.
        while True:
            try:
                self._lock = open(self._lock_path, "a+", encoding="utf-8")
                fcntl.flock(self._lock, fcntl.LOCK_EX)
                break  # Acquired!
            except (IOError, OSError):
                if time.time() - start_time > self.timeout:
                    raise TimeoutError(
                        "Timeout occurred while trying to acquire the lock."
                    )
                time.sleep(0.1)
        # Open the file after acquiring the lock.
        self.file = open(self.file_path, file_mode, encoding="utf-8")

    def release(self) -> None:
        """
        Release the lock and close the file. Try to remove the lock file.
        """
        if self.file:
            self.file.close()
            self.file = None

        if self._lock:
            fcntl.flock(self._lock, fcntl.LOCK_UN)
            self._lock.close()
            self._lock = None
            try:
                pathlib.Path(self._lock_path).unlink(missing_ok=True)
            except:
                pass  # Well, we tried.


class StatusLogger:
    """
    A status object for files at the tagger. Keeps a json status that can be sent to the server.
    """

    @staticmethod
    def _get_all_statusloggers() -> list[StatusLogger]:
        # initializing ProcessStatusses checks for non-existing processes and frees up the tagger
        ProcessStatus.get_all_statusloggers()
        return list(
            map(lambda filename: StatusLogger(filename), os.listdir(STATUS_FOLDER))
        )

    @staticmethod
    def get_all_statusses() -> dict[str, Any]:
        ret = {}
        for sl in StatusLogger._get_all_statusloggers():
            ret[sl.filename] = sl.get_status()
        return ret

    @staticmethod
    def get_all_pending_tasks() -> list[StatusLogger]:
        """
        A pending task is waiting to be tagged.
        """
        return list(
            filter(lambda sl: sl.is_pending(), StatusLogger._get_all_statusloggers())
        )

    @staticmethod
    def busy_task_exists() -> bool:
        return any(
            sl.get_status()["busy"] for sl in StatusLogger._get_all_statusloggers()
        )

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.status_path: str = os.path.join(STATUS_FOLDER, filename)

    def exists(self) -> bool:
        return os.path.isfile(self.status_path)

    def is_pending(self) -> bool:
        """
        A pending task is waiting to be tagged.
        """
        status = self.get_status()
        return status["pending"]

    def get_status(self) -> dict[str, Any]:
        """
        Retrieve the status object from file storage.
        """
        if not self.exists():
            return {
                "message": "File not on server",
                "pending": False,
                "busy": False,
                "error": False,
                "finished": False,
            }
        try:
            mutex = FileMutex(self.status_path)
            mutex.acquire("r")
            return json.load(mutex.file)
        except Exception as e:
            return {
                "message": f"Could not read status file. {e}",
                "pending": False,
                "busy": False,
                "error": False,
                "finished": False,
            }
        finally:
            mutex.release()

    def delete_status(self) -> None:
        """
        Deletes the file storage associated with this status, as well as the process status if present.
        """
        self.delete_status_file()
        # We might have to remove its process status as well.
        process_status = ProcessStatus(self.filename)
        if process_status.exists():
            process_status.kill()

    def delete_status_file(self) -> None:
        """
        Delete only the status file. Used by ProcessStatus to avoid recursion.
        """
        try:
            pathlib.Path(self.status_path).unlink(missing_ok=True)
        except:
            raise

    def _dump_status(self, status: dict[str, Any]) -> None:
        """
        Logs the current status, replacing the previous one.
        """
        try:
            mutex = FileMutex(self.status_path)
            mutex.acquire("w")
            json.dump(status, mutex.file)
        except:
            raise
        finally:
            mutex.release()

    # Logging functions

    def busy(self, message: str) -> None:
        logging.info(f"{self.filename} - BUSY: {message}")
        status = {
            "message": message,
            "pending": False,
            "busy": True,
            "error": False,
            "finished": False,
        }
        self._dump_status(status)

    def error(self, message: str) -> None:
        logging.error(f"{self.filename} - ERROR: {message}")
        status = {
            "message": message,
            "pending": False,
            "busy": False,
            "error": True,
            "finished": False,
        }
        self._dump_status(status)

    def finished(self, message: str) -> None:
        logging.info(f"{self.filename} - FINISHED: {message}")
        status = {
            "message": message,
            "pending": False,
            "busy": False,
            "error": False,
            "finished": True,
        }
        self._dump_status(status)

    def init(self, message: str) -> None:
        logging.info(f"{self.filename} - PENDING: {message}")
        status = {
            "message": message,
            "pending": True,
            "busy": False,
            "error": False,
            "finished": False,
        }
        self._dump_status(status)


class ProcessStatus(StatusLogger):
    """
    A status file for when a input file is currently being tagged.
    The status is simply the process ID where the tagger runs.
    """

    @staticmethod
    def get_all_statusloggers() -> list[ProcessStatus]:
        return list(
            map(lambda filename: ProcessStatus(filename), os.listdir(PROCESS_FOLDER))
        )

    def __init__(self, filename: str, pid: Optional[int] = None) -> None:
        """
        When no pid is given, we try to find the pid from the file. Otherwise, we create a new status file.
        """
        self.filename = filename
        self.status_path = os.path.join(PROCESS_FOLDER, filename)
        if pid is not None:
            self._dump_status({"pid": pid})
        else:
            pid = self.get_pid()
            if pid is not None:
                try:
                    os.kill(pid, 0)  # Check if alive.
                except:
                    # No process with this pid exists.
                    # delete ourselves, otherwise the tagger thinks we are busy.
                    self.delete_status()
                    StatusLogger(self.filename).init(
                        "File processing ended. Retry later."
                    )

    def get_pid(self) -> Optional[int]:
        """
        Process ID of the current thread.
        """
        if not self.exists():
            return None
        return self.get_status()["pid"]

    def kill(self) -> None:
        """
        Kill the thread that is currently tagging the file.
        """
        pid = self.get_pid()
        if pid is not None:
            os.kill(pid, signal.SIGKILL)
        self.delete_status()

    def delete_status(self) -> None:
        """
        Called when a processed is killed, or naturally ends.
        Removes ourselves, signifying the tagger is no longer busy.
        """
        self.delete_status_file()
        # Note that calling the super would cause recursion.
