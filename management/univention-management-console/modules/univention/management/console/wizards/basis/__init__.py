#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Univention Management Console
#  wizard: basis configuration
#
# Copyright 2007-2010 Univention GmbH
#
# http://www.univention.de/
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
# <http://www.gnu.org/licenses/>.

import univention.management.console as umc
import univention.management.console.protocol as umcp
import univention.management.console.handlers as umch
import univention.management.console.dialog as umcd
import univention.management.console.tools as umct

import univention.debug as ud
import univention_baseconfig as ub

import notifier
import notifier.popen

import os, re, subprocess

import _revamp

_ = umc.Translation( 'univention.management.console.wizards.basis' ).translate

icon = 'wizards/basis/module'
short_description = _( 'Base' )
long_description = _( 'Base configuration' )
categories = [ 'wizards' ]

command_description = {
	'wizard/basis/show': umch.command(
		short_description = _( 'Base configuration' ),
		long_description = _( 'View base configuration' ),
		method = 'basis_show',
		values = {},
		startup = True,
		priority = 100
	),
	'wizard/basis/set': umch.command(
		short_description = _( 'Base configuration' ),
		long_description = _( 'Set base configuration' ),
		method = 'basis_set',
		values = { 'hostname' : umc.String( _( 'Hostname' ), regex = r'^[a-z]([a-z0-9-]*[a-z0-9])*$' ),
				   'domainname' : umc.String( _( 'Domain name' ), regex = r'^([a-z0-9]([a-z0-9-]*[a-z0-9])*[.])*[a-z0-9]([a-z0-9-]*[a-z0-9])*$' ),
				   'windows_domain' : umc.String( _( 'Windows domain' ), regex = r'^([a-z]([a-z0-9-]*[a-z0-9])*[.])*[a-z]([a-z0-9-]*[a-z0-9])*$' ),
				   'ldap_base' : umc.String( _( 'LDAP base' ), regex = r'^((dc|cn|c|o|l)=[^ ,=]+,)*(dc|cn|c|o|l)=[^ ,=]+$' ), },
	),
}

class handler( umch.simpleHandler, _revamp.Web ):
	def __init__( self ):
		global command_description
		umch.simpleHandler.__init__( self, command_description )
		_revamp.Web.__init__( self )

	def basis_show( self, object ):
		umc.baseconfig.load()
		self.finished( object.id(), { 'hostname' : umc.baseconfig.get( 'hostname', '' ),
									  'ldap_base' : umc.baseconfig.get( 'ldap/base', '' ),
									  'domainname' : umc.baseconfig.get( 'domainname', '' ),
									  'windows_domain' : umc.baseconfig.get( 'windows/domain', '' ), } )

	def basis_set( self, object ):
		umc.baseconfig.load()
		fp = open( '/var/cache/univention-system-setup/profile', 'w' )
		fp.write( "UMC_MODE=true\n" )
		for key, value in object.options.items():
			if value != umc.baseconfig.get( key.replace( '_', '/' ) ):
				fp.write( "%s=%s\n" % ( key.replace( '_', '/' ), value ) )
		fp.close()
		cb = notifier.Callback( self._basis_set, object )
		func = notifier.Callback( self._basis_run, object )
		thread = notifier.threads.Simple( 'basis', func, cb )
		thread.run()

	def _basis_run( self, object ):
		_path = '/usr/lib/univention-system-setup/scripts/basis/'
		failed = []
		for script in os.listdir( _path ):
			filename = os.path.join( _path, script )
			ud.debug( ud.ADMIN, ud.INFO, 'run script: %s' % filename )
			if os.path.isfile( filename ):
				if subprocess.call( ( filename, ) ):
					failed.append( script )
		return failed

	def _basis_set( self, thread, result, object ):
		if result:
			self.finished( object.id(), None,
						   report = _( 'The following scripts failed: %(scripts)s' ) % \
						   { 'scripts' : ', '.join( failed ) }, success = False )
		else:
			self.finished( object.id(), None )
