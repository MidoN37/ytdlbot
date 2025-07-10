#!/usr/bin/env python3
# coding: utf-8

# ytdlbot - direct.py

import logging
import os
import re
import pathlib
import subprocess
import tempfile
from pathlib import Path
from uuid import uuid4

import filetype
import requests

from config import TMPFILE_PATH
from engine.base import BaseDownloader


class DirectDownload(BaseDownloader):

    def _setup_formats(self) -> list | None:
        # direct download doesn't need to setup formats
        pass


    def _requests_download(self):
        logging.info("Requests download with url %s", self._url)
        response = requests.get(self._url, stream=True)
        response.raise_for_status()
        file = Path(self._tempdir.name).joinpath(uuid4().hex)
        with open(file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        ext = filetype.guess_extension(file)
        if ext is not None:
            new_name = file.with_suffix(f".{ext}")
            file.rename(new_name)

        return [file.as_posix()]


        except subprocess.TimeoutExpired:
            error_msg = "Download timed out after 5 minutes."
            logging.error(error_msg)
            self._bot_msg.edit_text(f"Download failed!❌\n\n{error_msg}")
            return []
        except Exception as e:
            self._bot_msg.edit_text(f"Download failed!❌\n\n`{e}`")
            return []
        finally:
            if self._process:
                self._process.terminate()
                self._process = None

    def __parse_progress(self, line: str) -> dict | None:
        if "Download complete:" in line or "(OK):download completed" in line:
            return {"status": "complete"}

        progress_match = re.search(
            r'\[#\w+\s+(?P<progress>[\d.]+[KMGTP]?iB)/(?P<total>[\d.]+[KMGTP]?iB)\(.*?\)\s+CN:\d+\s+DL:(?P<speed>[\d.]+[KMGTP]?iB)\s+ETA:(?P<eta>[\dhms]+)',
            line
        )

        if progress_match:
            return {
                "status": "downloading",
                "downloaded_bytes": self.__parse_size(progress_match.group("progress")),
                "total_bytes": self.__parse_size(progress_match.group("total")),
                "_speed_str": f"{progress_match.group('speed')}/s",
                "_eta_str": progress_match.group("eta")
            }

        # Fallback check for summary lines
        if "Download Progress Summary" in line and "MiB" in line:
            return {"status": "progress", "details": line}

        return None

    def __parse_size(self, size_str: str) -> int:
        units = {
            "B": 1, 
            "K": 1024, "KB": 1024, "KIB": 1024,
            "M": 1024**2, "MB": 1024**2, "MIB": 1024**2,
            "G": 1024**3, "GB": 1024**3, "GIB": 1024**3,
            "T": 1024**4, "TB": 1024**4, "TIB": 1024**4
        }
        match = re.match(r"([\d.]+)([A-Za-z]*)", size_str.replace("i", "").upper())
        if match:
            number, unit = match.groups()
            unit = unit or "B"
            return int(float(number) * units.get(unit, 1))
        return 0


    def _start(self):
        self._download()
        self._upload()
