#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# Univention Blog Portal Entry
#
# Copyright 2017-2020 Univention GmbH
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
"""
Create a portal entry for the Univention Blog for all Core Edition users.
"""

import base64
import subprocess


def handler(config_registry, changes):
	if config_registry.get('server/role') != 'domaincontroller_master':
		return
	ldap_base = config_registry.get('ldap/base')

	try:
		_, new_val = changes.get('license/base', [None, None])
	except ValueError:  # UCR module initialization
		new_val = changes['license/base']

	if new_val in ("UCS Core Edition", "Free for personal use edition"):
		if config_registry.is_false('portal/create-univention-blog-entry', False):
			return
		if subprocess.call(['/usr/bin/univention-ldapsearch', '-LLL', '-s', 'base', '-b', 'cn=portal,cn=univention,%s' % (ldap_base,), 'dn']) == 32:  # LDAP no such object
			return
		with open('/usr/share/univention-portal/univention-blog.png', 'rb') as fd:
			icon = base64.b64encode(fd.read()).decode('ASCII')
		cmd = [
			'univention-directory-manager', 'settings/portal_entry', 'create', '--ignore_exists',
			'--position', 'cn=portal,cn=univention,%s' % (ldap_base,),
			'--set', 'name=univentionblog',
			'--set', 'activated=TRUE',
			'--set', 'icon=%s' % (icon,),
			'--append', 'link=https://www.univention.com/news/blog-en/',
			'--append', 'description="en_US" "News, tips and best practices"',
			'--append', 'description="de_DE" "News, Tipps und Best Practices"',
			'--append', 'description="fr_FR" "Nouvelles, conseils et bonne pratique"',
			'--append', 'displayName="en_US" "Univention Blog"',
			'--append', 'displayName="de_DE" "Univention Blog"',
			'--append', 'displayName="fr_FR" "Univention Blog"',
			'--set', 'category=admin',
			'--set', 'authRestriction=anonymous',
			'--set', 'linkTarget=newwindow',
			'--set', 'portal=cn=domain,cn=portal,cn=univention,%s' % (ldap_base,)
		]
	else:
		cmd = ['univention-directory-manager', 'settings/portal_entry', 'remove', '--ignore_not_exists', '--dn', 'cn=univentionblog,cn=portal,cn=univention,%s' % (ldap_base,)]

	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
	stdout = process.communicate()[0].decode('UTF-8', 'replace')
	if process.returncode:
		raise Exception('Modifying blog entry failed: %d: %s %r' % (process.returncode, stdout, cmd))
