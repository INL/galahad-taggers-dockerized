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

STATUS_FOLDER = "status"
PROCESS_FOLDER = "process"

log_format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(stream=sys.stdout, format=log_format, level=logging.INFO)


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
        with open(self.status_path, encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                logging.error(f"Error decoding status file { self.status_path }")
                self.init("Restarting due to invalid JSON status file.")
                return self.get_status()

    def delete_status(self) -> None:
        """
        Deletes the file storage associated with this status, as well as the process status if present.
        """
        if self.exists():
            os.remove(self.status_path)
        # We might have to remove its process status as well.
        process_status = ProcessStatus(self.filename)
        if process_status.exists():
            process_status.kill()

    def _dump_status(self, status: dict[str, Any]) -> None:
        """
        Logs the current status, replacing the previous one.
        """
        f = open(self.status_path, "w", encoding="utf-8")
        json.dump(status, f)
        f.close()

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
        self.filename = filename
        self.status_path = os.path.join(PROCESS_FOLDER, filename)
        if pid is not None:
            self._dump_status({"pid": pid})
        else:
            pid = self.get_pid()
            if pid is not None:
                try:
                    os.kill(pid, 0)
                except:
                    # No process with this pid exists.
                    # delete ourselves, otherwise the tagger thinks we are busy.
                    self.delete_status()
                    StatusLogger(self.filename).init(
                        "File processing ended. Retry later."
                    )

    def get_pid(self) -> Optional[int]:
        """
        Process ID of the current thread (i.e. mp.pool).
        """
        if not self.exists():
            return None
        with open(self.status_path, encoding="utf-8") as f:
            status = json.load(f)
            return status["pid"]

    def kill(self) -> None:
        """
        Kill the thread (i.e. mp.pool) that is currently tagging the file.
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
        if self.exists():
            os.remove(self.status_path)
        # Note that calling the super would cause recursion.
