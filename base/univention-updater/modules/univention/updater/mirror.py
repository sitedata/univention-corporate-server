#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
Mirror Univention repository server.
"""
# Copyright 2009-2020 Univention GmbH
#
# https://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <https://www.gnu.org/licenses/>.

from __future__ import absolute_import
import os
import errno
import re
import subprocess
import itertools
import logging
import json
from operator import itemgetter

from .tools import UniventionUpdater, UCSHttpServer
from .repo_url import UcsRepoUrl
from univention.lib.ucs import UCS_Version
try:
    import univention.debug as ud
except ImportError:
    import univention.debug2 as ud
try:
    from typing import Iterator, Tuple  # noqa F401
except ImportError:
    pass


def makedirs(dirname, mode=0o755):
    """
    Recursively create directory hierarchy will all parent directories.

    :param str dirname: Name of the directory to create.
    :param int mode: Directory permissions.
    """
    try:
        os.makedirs(dirname, mode)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise


def filter_releases_json(releases, start=None, end=None):
    # type: (str, Optional[UCS_Version], Optional[UCS_Version]) -> None
    """
    Filter releases that are not mirrored from the upstream repository
    Filtering is done inplace!

    :param str releases: The upstream releases object from releases.json.
    :param UCS_Version start: First UCS version that is being mirrored.
    :param UCS_Version end: Last UCS version that is being mirrored.
    """

    max_minor = 99
    max_patchlevel = 99

    def _include_version(major, minor=None, patchlevel=None):
        bigger_as_start = start is None or start <= UCS_Version((
            major,
            max_minor if minor is None else minor,
            max_patchlevel if patchlevel is None else patchlevel
        ))
        smaller_as_end = end is None or end >= UCS_Version((
            major,
            0 if minor is None else minor,
            0 if patchlevel is None else patchlevel
        ))
        return bigger_as_start and smaller_as_end

    def _filter_majors():
        releases['releases'] = [major for major in releases['releases'] if _include_version(major['major'])]

    def _filter_minors():
        for major in releases['releases']:
            major['minors'] = [minor for minor in major['minors'] if _include_version(major['major'], minor['minor'])]

    def _filter_patchlevels():
        for major in releases['releases']:
            for minor in major['minors']:
                minor['patchlevels'] = [
                    patchlevel for patchlevel in minor['patchlevels']
                    if _include_version(major['major'], minor['minor'], patchlevel['patchlevel'])
                ]

    _filter_majors()
    _filter_minors()
    _filter_patchlevels()
    return None


class UniventionMirror(UniventionUpdater):

    def __init__(self, check_access=True):
        """
        Create new mirror with settings from UCR.

        :param bool check_access: Check if repository server is reachable on init.
        :raises ConfigurationError: if configured server is not available immediately.
        """
        UniventionUpdater.__init__(self, check_access)
        self.log = logging.getLogger('updater.Mirror')
        self.log.addHandler(logging.NullHandler())
        self.repository_path = self.configRegistry.get('repository/mirror/basepath', '/var/lib/univention-repository')

        version_end = self.configRegistry.get('repository/mirror/version/end') or self.current_version
        self.version_end = UCS_Version(version_end)
        version_start = self.configRegistry.get('repository/mirror/version/start') or (self.version_major, 0, 0)
        self.version_start = UCS_Version(version_start)
        # set architectures to mirror
        archs = self.configRegistry.get('repository/mirror/architectures', '')
        if archs:
            self.architectures = archs.split(' ')

    def config_repository(self):
        """
        Retrieve configuration to access repository. Overrides :py:class:`univention.updater.UniventionUpdater`.
        """
        self.online_repository = self.configRegistry.is_true('repository/mirror', True)
        self.repourl = UcsRepoUrl(self.configRegistry, 'repository/mirror')
        self.sources = self.configRegistry.is_true('repository/mirror/sources', False)
        self.timeout = float(self.configRegistry.get('repository/mirror/timeout', 30))
        self.http_method = self.configRegistry.get('repository/mirror/httpmethod', 'HEAD').upper()
        self.script_verify = self.configRegistry.is_true('repository/mirror/verify', True)

    def release_update_available(self, ucs_version=None, errorsto='stderr'):
        """
        Check if an update is available for the `ucs_version`.

        :param str ucs_version: The UCS release to check.
        :param str errorsto: Select method of reporting errors; on of 'stderr', 'exception', 'none'.
        :returns: The next UCS release or None.
        :rtype: str or None
        """
        if not ucs_version:
            ucs_version = self.current_version
        return self.get_next_version(UCS_Version(ucs_version), [], errorsto)

    def mirror_repositories(self):
        """
        Uses :command:`apt-mirror` to copy a repository.
        """
        # check if the repository directory structure exists, otherwise create it
        makedirs(self.repository_path)

        # these sub-directories are required by apt-mirror
        for dirname in ('skel', 'mirror', 'var'):
            path = os.path.join(self.repository_path, dirname)
            makedirs(path)
        path = os.path.join(self.repository_path, 'mirror', 'univention-repository')
        try:
            os.symlink('.', path)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise

        log = open('/var/log/univention/repository.log', 'a')
        try:
            return subprocess.call('/usr/bin/apt-mirror', stdout=log, stderr=log, shell=False)
        finally:
            log.close()

    def mirror_update_scripts(self):
        """
        Mirrors the :file:`preup.sh` and :file:`postup.sh` scripts.
        """
        start = self.version_start
        end = self.version_end
        parts = self.parts
        archs = []  # only 'all'

        repos = self._iterate_version_repositories(start, end, parts, archs)  # returns generator

        components = self.get_components(only_localmirror_enabled=True)
        comp = self._iterate_component_repositories(components, start, end, archs, for_mirror_list=True)  # returns generator

        all_repos = itertools.chain(repos, comp)  # concatenate all generators into a single one
        for server, struct, phase, path, script in UniventionUpdater.get_sh_files(all_repos, self.script_verify):
            self.log.info('Mirroring %s:%r/%s to %s', server, struct, phase, path)
            assert script is not None, 'No script'

            # use prefix if defined - otherwise file will be stored in wrong directory
            if server.prefix:
                filename = os.path.join(self.repository_path, 'mirror', server.prefix, path)
            else:
                filename = os.path.join(self.repository_path, 'mirror', path)

            # Check disabled, otherwise files won't get refetched if they change on upstream server
            # if os.path.exists(filename):
            #   ud.debug(ud.NETWORK, ud.ALL, "Script already exists, skipping: %s" % filename)
            #   continue

            makedirs(os.path.dirname(filename))
            fd = open(filename, "w")
            try:
                fd.write(script)
                ud.debug(ud.ADMIN, ud.INFO, "Successfully mirrored: %s" % filename)
            finally:
                fd.close()

    def list_local_repositories(self, start=None, end=None, maintained=True, unmaintained=False):
        """
        This function returns a sorted list of local (un)maintained repositories.

        :param start: smallest version that shall be returned.
        :type start: UCS_Version or None
        :param end: largest version that shall be returned.
        :type end: UCS_Version or None
        :param bool maintained: True if list shall contain maintained repositories.
        :param bool unmaintained: True if list shall contain unmaintained repositories.
        :returns: A sorted list of repositories as (directory, UCS_Version, is_maintained) tuples.
        :rtype: list[tuple(str, UCS_Version, bool)]
        """
        result = []
        repobase = os.path.join(self.repository_path, 'mirror')
        RErepo = re.compile('^%s/(\d+[.]\d)/(maintained|unmaintained)/(\d+[.]\d+-\d+)$' % (re.escape(repobase),))
        for dirname, subdirs, files in os.walk(repobase):
            match = RErepo.match(dirname)
            if match:
                if not maintained and match.group(2) == 'maintained':
                    continue
                if not unmaintained and match.group(2) == 'unmaintained':
                    continue

                version = UCS_Version(match.group(3))
                if start is not None and version < start:
                    continue
                if end is not None and end < version:
                    continue

                result.append((dirname, version, match.group(2) == 'maintained'))

        result.sort(key=itemgetter(1))

        return result

    def write_releases_json(self):
        """
        Write a releases.json including only the mirrored releases.
        """
        start = self.version_start
        end = self.version_end
        _code, _size, data = self.server.access(None, 'releases.json', get=True)
        try:
            releases = json.loads(data)
        except ValueError as exc:
            ud.debug(ud.NETWORK, ud.ERROR, 'Querying maintenance information failed: %s' % (exc,))
            if isinstance(self.server, UCSHttpServer) and self.server.proxy_handler.proxies:
                ud.debug(ud.NETWORK, ud.WARN, 'Maintenance information malformed, blocked by proxy?')
            raise
        filter_releases_json(releases, start=start, end=end)
        releases_json_path = os.path.join(self.repository_path, 'mirror', 'releases.json')
        makedirs(os.path.dirname(releases_json_path))
        with open(releases_json_path, 'w') as releases_json:
            json.dump(releases, releases_json)

    def run(self):
        """
        starts the mirror process.
        """
        self.mirror_repositories()
        self.mirror_update_scripts()
        self.write_releases_json()


if __name__ == '__main__':
    import doctest
    exit(doctest.testmod()[0])
