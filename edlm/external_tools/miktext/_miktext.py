# coding=utf-8
"""
Miktex external tool
"""

import typing
from pathlib import Path

import elib

from edlm import HERE
from edlm.external_tools.base import BaseExternalTool

STR_OR_PATH = typing.Union[str, Path]

MPM_CONFIG = """;;; DO NOT EDIT THIS FILE!


[MPM]
AutoInstall=1

"""


class MikTex(BaseExternalTool):
    """
    Miktex external tool
    """
    url = r'https://www.dropbox.com/s/ivyb6s5itb5len2/miktex.7z?dl=1'
    # noinspection SpellCheckingInspection
    hash = 'fc20affd161264e7c5b816ddc85955cd'
    default_archive = Path(HERE, 'miktex.7z').absolute()
    default_install = Path(HERE, 'miktex').absolute()
    expected_version = '2.9.6354'

    def get_version(self) -> str:
        """
        Returns: Miktex version
        """
        if self._version is None:
            self._version = self('--version').split('\n')[0].split(' ')[1]
        return self._version

    def get_exe(self) -> Path:
        """
        Returns: Miktex executable
        """
        if self._exe is None:
            self._exe = Path(self.install_dir, 'miktex/texmfs/install/miktex/bin/pdflatex.exe').absolute()
        return self._exe

    @staticmethod
    def _create_new_mpm_settings_file(mpm_config_file):
        elib.path.ensure_dir(mpm_config_file.parent, must_exist=False, create=True)
        mpm_config_file.write_text(MPM_CONFIG, encoding='utf8')

    @staticmethod
    def _edit_auto_install_line(content):
        for index, line in enumerate(content):
            if 'AutoInstall=' in line:
                content[index] = 'AutoInstall=1'
                return True
        return False

    @staticmethod
    def _add_auto_install_line(content: list):
        for index, line in enumerate(content):
            if '[MPM]' in line:
                content.insert(index + 1, 'AutoInstall=1')
                return True
        return False

    @staticmethod
    def _add_mpm_section(content: list):
        content.append('[MPM]')
        content.append('AutoInstall=1\n')
        return True

    def _edit_existing_mpm_settings_file(self, mpm_config_file):
        content = mpm_config_file.read_text(encoding='utf8').split('\n')
        func_list = [self._edit_auto_install_line, self._add_auto_install_line, self._add_mpm_section]
        for func in func_list:  # pragma: no cover
            if func(content):
                mpm_config_file.write_text('\n'.join(content))
                return

    def _write_mpm_settings_file(self):
        mpm_config_file = Path(self.install_dir, 'texmfs/config/miktex/config/miktex.ini')
        if not mpm_config_file.exists():
            self._create_new_mpm_settings_file(mpm_config_file)
        else:
            self._edit_existing_mpm_settings_file(mpm_config_file)

    def setup(self):
        """
        Setup Miktex
        """
        super(MikTex, self).setup()
        self._write_mpm_settings_file()
