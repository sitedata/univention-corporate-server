# -*- coding: utf-8 -*-
#
# Univention S4 Connector
#  this file defines the mapping beetween S4 and UCS
#
# Copyright 2004-2011 Univention GmbH
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

import univention.s4connector.s4
import univention.s4connector.s4.mapping
import univention.s4connector.s4.password
import univention.s4connector.s4.sid_mapping
import univention.s4connector.s4.dns

global_ignore_subtree=['cn=univention,@%@ldap/base@%@','cn=policies,@%@ldap/base@%@',
			'cn=shares,@%@ldap/base@%@','cn=printers,@%@ldap/base@%@',
			'cn=networks,@%@ldap/base@%@', 'cn=kerberos,@%@ldap/base@%@',
			'cn=dhcp,@%@ldap/base@%@',
			'cn=mail,@%@ldap/base@%@',
			'cn=samba,@%@ldap/base@%@','cn=nagios,@%@ldap/base@%@',
			'CN=RAS and IAS Servers Access Check,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=FileLinks,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=WinsockServices,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=RID Manager$,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=Dfs-Configuration,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=Server,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=ComPartitionSets,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=ComPartitions,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=IP Security,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=DFSR-GlobalSettings,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=DomainUpdates,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=Password Settings Container,CN=System,@%@connector/s4/ldap/base@%@',
			'DC=RootDNSServers,CN=MicrosoftDNS,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=Default Domain Policy,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=File Replication Service,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=RpcServices,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=Meetings,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=Policies,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=AdminSDHolder,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=WMIPolicy,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=BCKUPKEY_c490e871-a375-4b76-bd24-711e9e49fe5e Secret,CN=System,@%@connector/s4/ldap/base@%@',
			'CN=BCKUPKEY_PREFERRED Secret,CN=System,@%@connector/s4/ldap/base@%@',
			'ou=Grp Policy Users,@%@connector/s4/ldap/base@%@',
			'cn=Builtin,@%@connector/s4/ldap/base@%@',
			'cn=ForeignSecurityPrincipals,@%@connector/s4/ldap/base@%@',
			'cn=Program Data,@%@connector/s4/ldap/base@%@',
			'cn=Configuration,@%@connector/s4/ldap/base@%@',
			'cn=opsi,@%@ldap/base@%@',
			'cn=Microsoft Exchange System Objects,@%@connector/s4/ldap/base@%@']


s4_mapping = {
	'user': univention.s4connector.property (
			ucs_default_dn='cn=users,@%@ldap/base@%@',
			con_default_dn='cn=users,@%@connector/s4/ldap/base@%@',

			ucs_module='users/user',

			# read, write, sync, none
			sync_mode='@%@connector/s4/mapping/syncmode@%@',
			scope='sub',

			con_search_filter='(&(objectClass=user)(!(objectClass=computer))(userAccountControl:1.2.840.113556.1.4.803:=512))',
			match_filter='(&(|(&(objectClass=posixAccount)(objectClass=krb5Principal))(objectClass=user))(!(objectClass=univentionHost)))',
			ignore_filter='(|(uid=root)(uid=pcpatch)(cn=pcpatch)(CN=pcpatch)(uid=ucs-s4sync)(CN=ucs-s4sync))',

			ignore_subtree = global_ignore_subtree,
			
			con_create_objectclass=['top', 'user', 'person', 'organizationalPerson'],

			dn_mapping_function=[ univention.s4connector.s4.user_dn_mapping ],

			# aus UCS Modul
			attributes= {
					'samAccountName': univention.s4connector.attribute (
							ucs_attribute='username',
							ldap_attribute='uid',
							con_attribute='sAMAccountName',
							required=1,
							compare_function=univention.s4connector.compare_lowercase,
						),
					'givenName' : univention.s4connector.attribute (
							ucs_attribute='firstname',
							ldap_attribute='givenName',
							con_attribute='givenName',
						),
					'sn': univention.s4connector.attribute (
							ucs_attribute='lastname',
							ldap_attribute='sn',
							con_attribute='sn',
						),
				},

			ucs_create_functions = [ univention.s4connector.set_ucs_passwd_user,
						 univention.s4connector.check_ucs_lastname_user,
						 univention.s4connector.set_primary_group_user
						 ],

			post_con_create_functions = [ univention.s4connector.s4.normalise_userAccountControl,
						 ],

			post_con_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_s4,
							univention.s4connector.s4.password.password_sync_ucs_to_s4,
						    univention.s4connector.s4.primary_group_sync_from_ucs,
						    univention.s4connector.s4.disable_user_from_ucs,
						    ],

			post_ucs_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_ucs,
							univention.s4connector.s4.password.password_sync_s4_to_ucs,
						    univention.s4connector.s4.primary_group_sync_to_ucs,
						    univention.s4connector.s4.object_memberships_sync_to_ucs,
						    univention.s4connector.s4.disable_user_to_ucs,
						    ],

			post_attributes={
					'organisation': univention.s4connector.attribute (
							ucs_attribute='organisation',
							ldap_attribute='o',
							con_attribute='department',
						),
					'description': univention.s4connector.attribute (
						ucs_attribute='description',
						ldap_attribute='description',
						con_attribute='description',
					),
					'mailPrimaryAddress': univention.s4connector.attribute (
						ucs_attribute='mailPrimaryAddress',
						ldap_attribute='mailPrimaryAddress',
						con_attribute='mail',
					),
					'street': univention.s4connector.attribute (
							ucs_attribute='street',
							ldap_attribute='street',
							con_attribute='streetAddress',
						),
					'city': univention.s4connector.attribute (
							ucs_attribute='city',
							ldap_attribute='l',
							con_attribute='l',
						),
					'postcode': univention.s4connector.attribute (
							ucs_attribute='postcode',
							ldap_attribute='postalCode',
							con_attribute='postalCode',
						),
					#'telephoneNumber': univention.s4connector.attribute ( # die Syntax erlaubt in AD mehr als in UCS
					#		ucs_attribute='phone',
					#		ldap_attribute='telephoneNumber',
					#		con_attribute='otherTelephone',
					#	),
					'profilepath': univention.s4connector.attribute (
							ucs_attribute='profilepath',
							ldap_attribute='sambaProfilePath',
							con_attribute='profilePath',
						),
					'scriptpath': univention.s4connector.attribute (
							ucs_attribute='scriptpath',
							ldap_attribute='sambaLogonScript',
							con_attribute='scriptPath',
						),
			},

		),

	'group': univention.s4connector.property (
			ucs_default_dn='cn=groups,@%@ldap/base@%@',
			con_default_dn='cn=Users,@%@connector/s4/ldap/base@%@',

			ucs_module='groups/group',

			sync_mode='@%@connector/s4/mapping/syncmode@%@',
			scope='sub',

			ignore_filter='(|(sambaGroupType=5)(groupType=5)(cn=Windows Hosts)(cn=DC Slave Hosts)(cn=DC Backup Hosts))',

			ignore_subtree = global_ignore_subtree,
			
			con_search_filter='objectClass=group',

			con_create_objectclass=['top', 'group'],

			post_con_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_s4,
							univention.s4connector.s4.group_members_sync_from_ucs,
							univention.s4connector.s4.object_memberships_sync_from_ucs
							],

			post_ucs_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_ucs,
							univention.s4connector.s4.group_members_sync_to_ucs,
							univention.s4connector.s4.object_memberships_sync_to_ucs
							],

			dn_mapping_function=[ univention.s4connector.s4.group_dn_mapping ],

			attributes= {
					'cn': univention.s4connector.attribute (
							ucs_attribute='name',
							ldap_attribute='cn',
							con_attribute='sAMAccountName',
							required=1,
							compare_function=univention.s4connector.compare_lowercase,
						),
					'description': univention.s4connector.attribute (
							ucs_attribute='description',
							ldap_attribute='description',
							con_attribute='description',
						),
					'mailAddress': univention.s4connector.attribute (
						ucs_attribute='mailAddress',
						ldap_attribute='mailPrimaryAddress',
						con_attribute='mail',
					),
				},
		),
	'dc_master': univention.s4connector.property (
			ucs_default_dn='cn=computers,@%@ldap/base@%@',
			con_default_dn='OU=Domain Controllers,@%@connector/s4/ldap/base@%@',
			ucs_module='computers/domaincontroller_master',

			sync_mode='@%@connector/s4/mapping/syncmode@%@',

			position_mapping = [( ',cn=dc,cn=computers,@%@ldap/base@%@', ',ou=Domain Controllers,@%@connector/s4/ldap/base@%@' )],

			scope='sub',

			con_search_filter='(&(objectClass=computer)(userAccountControl:1.2.840.113556.1.4.803:=532480)(operatingSystem=Univention Corporate Server - DC Master))',

			match_filter='(|(&(objectClass=univentionDomainController)(univentionServerRole=master))(&(objectClass=computer)(operatingSystem=Univention Corporate Server - DC Master)))',

			ignore_filter='',

			ignore_subtree = global_ignore_subtree,
			
			con_create_objectclass=['top', 'computer' ],

			con_create_attributes=[
									('userAccountControl', ['532480']),
									('operatingSystem', ['Univention Corporate Server - DC Master']),
								  ],

			#post_con_create_functions = [ univention.connector.s4.computers.
			post_con_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_s4,
							univention.s4connector.s4.password.password_sync_ucs_to_s4,
						    ],

			post_ucs_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_ucs,
							univention.s4connector.s4.password.password_sync_s4_to_ucs,
						    ],

			attributes= {
					'cn': univention.s4connector.attribute (
							ucs_attribute='name',
							ldap_attribute='cn',
							con_attribute='cn',
							required=1,
							compare_function=univention.s4connector.compare_lowercase,
						),
					'description': univention.s4connector.attribute (
							ucs_attribute='description',
							ldap_attribute='description',
							con_attribute='description'
						),
				},

		),
	'dc_backup': univention.s4connector.property (
			ucs_default_dn='cn=computers,@%@ldap/base@%@',
			con_default_dn='OU=Domain Controllers,@%@connector/s4/ldap/base@%@',
			ucs_module='computers/domaincontroller_backup',

			sync_mode='@%@connector/s4/mapping/syncmode@%@',

			scope='sub',

			con_search_filter='(&(objectClass=computer)(userAccountControl:1.2.840.113556.1.4.803:=532480)(operatingSystem=Univention Corporate Server - DC Backup))',

			match_filter='(|(&(objectClass=univentionDomainController)(univentionServerRole=backup))(&(objectClass=computer)(operatingSystem=Univention Corporate Server - DC Backup)))',

			position_mapping = [( ',cn=dc,cn=computers,@%@ldap/base@%@', ',ou=Domain Controllers,@%@connector/s4/ldap/base@%@' )],

			ignore_filter='',

			ignore_subtree = global_ignore_subtree,
			
			con_create_objectclass=['top', 'computer' ],

			con_create_attributes=[
									('userAccountControl', ['532480']),
									('operatingSystem', ['Univention Corporate Server - DC Backup']),
								  ],

			#post_con_create_functions = [ univention.connector.s4.computers.
			post_con_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_s4,
							univention.s4connector.s4.password.password_sync_ucs_to_s4,
						    ],

			post_ucs_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_ucs,
							univention.s4connector.s4.password.password_sync_s4_to_ucs,
						    ],

			attributes= {
					'cn': univention.s4connector.attribute (
							ucs_attribute='name',
							ldap_attribute='cn',
							con_attribute='cn',
							required=1,
							compare_function=univention.s4connector.compare_lowercase,
						),
					'description': univention.s4connector.attribute (
							ucs_attribute='description',
							ldap_attribute='description',
							con_attribute='description'
						),
				},

		),
	'dc_slave': univention.s4connector.property (
			ucs_default_dn='cn=computers,@%@ldap/base@%@',
			con_default_dn='OU=Domain Controllers,@%@connector/s4/ldap/base@%@',
			ucs_module='computers/domaincontroller_slave',

			sync_mode='@%@connector/s4/mapping/syncmode@%@',

			scope='sub',

			con_search_filter='(&(objectClass=computer)(userAccountControl:1.2.840.113556.1.4.803:=532480)(operatingSystem=Univention Corporate Server - DC Slave))',

			match_filter='(|(&(objectClass=univentionDomainController)(univentionServerRole=slave))(&(objectClass=computer)(operatingSystem=Univention Corporate Server - DC Slave)))',

			ignore_filter='',

			position_mapping = [( ',cn=dc,cn=computers,@%@ldap/base@%@', ',ou=Domain Controllers,@%@connector/s4/ldap/base@%@' )],

			ignore_subtree = global_ignore_subtree,
			
			con_create_objectclass=['top', 'computer' ],

			con_create_attributes=[
									('userAccountControl', ['532480']),
									('operatingSystem', ['Univention Corporate Server - DC Slave']),
								  ],

			#post_con_create_functions = [ univention.connector.s4.computers.
			post_con_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_s4,
							univention.s4connector.s4.password.password_sync_ucs_to_s4,
						    ],

			post_ucs_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_ucs,
							univention.s4connector.s4.password.password_sync_s4_to_ucs,
						    ],

			attributes= {
					'cn': univention.s4connector.attribute (
							ucs_attribute='name',
							ldap_attribute='cn',
							con_attribute='cn',
							required=1,
							compare_function=univention.s4connector.compare_lowercase,
						),
					'description': univention.s4connector.attribute (
							ucs_attribute='description',
							ldap_attribute='description',
							con_attribute='description'
						),
				},

		),
	'windowsdc': univention.s4connector.property (
			ucs_default_dn='cn=computers,@%@ldap/base@%@',
			con_default_dn='OU=Domain Controllers,@%@connector/s4/ldap/base@%@',
			ucs_module='computers/windows_domaincontroller',

			sync_mode='@%@connector/s4/mapping/syncmode@%@',

			scope='sub',

			con_search_filter='(&(objectClass=computer)(userAccountControl:1.2.840.113556.1.4.803:=532480))',

			match_filter='(|(&(objectClass=univentionHost)(univentionServerRole=windows_domaincontroller))(&(objectClass=computer)(!(|(operatingSystem=Samba)(operatingSystem=Univention*)))))',

			position_mapping = [( ',cn=dc,cn=computers,@%@ldap/base@%@', ',ou=Domain Controllers,@%@connector/s4/ldap/base@%@' )],

			ignore_filter='',

			ignore_subtree = global_ignore_subtree,
			
			con_create_objectclass=['top', 'computer' ],

			con_create_attributes=[
									('userAccountControl', ['532480']),
								  ],

			#post_con_create_functions = [ univention.connector.s4.computers.
			post_con_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_s4,
							univention.s4connector.s4.password.password_sync_ucs_to_s4,
						    ],

			post_ucs_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_ucs,
							univention.s4connector.s4.password.password_sync_s4_to_ucs,
						    ],

			attributes= {
					'cn': univention.s4connector.attribute (
							ucs_attribute='name',
							ldap_attribute='cn',
							con_attribute='cn',
							required=1,
							compare_function=univention.s4connector.compare_lowercase,
						),
					'description': univention.s4connector.attribute (
							ucs_attribute='description',
							ldap_attribute='description',
							con_attribute='description'
						),
					'operatingSystem': univention.s4connector.attribute (
							ucs_attribute='operatingSystem',
							ldap_attribute='univentionOperatingSystem',
							con_attribute='operatingSystem'
						),
					'operatingSystemVersion': univention.s4connector.attribute (
							ucs_attribute='operatingSystemVersion',
							ldap_attribute='univentionOperatingSystemVersion',
							con_attribute='operatingSystemVersion'
						),
				},

		),
	'windowscomputer': univention.s4connector.property (
			ucs_default_dn='cn=computers,@%@ldap/base@%@',
			con_default_dn='cn=computers,@%@connector/s4/ldap/base@%@',
			ucs_module='computers/windows',

			sync_mode='@%@connector/s4/mapping/syncmode@%@',

			scope='sub',

			con_search_filter='(&(objectClass=computer)(userAccountControl:1.2.840.113556.1.4.803:=4096))',

			# ignore_filter='userAccountControl=4096',
			match_filter='(|(&(objectClass=univentionWindows)(!(univentionServerRole=windows_domaincontroller)))(objectClass=univentionMemberServer)(objectClass=computer))',

			ignore_subtree = global_ignore_subtree,
			
			ignore_filter='',

			con_create_objectclass=['top', 'computer' ],

			con_create_attributes=[('userAccountControl', ['4096'])],

			#post_con_create_functions = [ univention.connector.s4.computers.
			post_con_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_s4,
							# univention.s4connector.s4.password.password_sync_ucs_to_s4,
						    ],

			post_ucs_modify_functions=[
							univention.s4connector.s4.sid_mapping.sid_to_ucs,
							# univention.s4connector.s4.password.password_sync_s4_to_ucs,
						    ],

			attributes= {
					'cn': univention.s4connector.attribute (
							ucs_attribute='name',
							ldap_attribute='cn',
							con_attribute='cn',
							required=1,
							compare_function=univention.s4connector.compare_lowercase,
						),
					'description': univention.s4connector.attribute (
							ucs_attribute='description',
							ldap_attribute='description',
							con_attribute='description'
						),
					'operatingSystem': univention.s4connector.attribute (
							ucs_attribute='operatingSystem',
							ldap_attribute='univentionOperatingSystem',
							con_attribute='operatingSystem'
						),
					'operatingSystemVersion': univention.s4connector.attribute (
							ucs_attribute='operatingSystemVersion',
							ldap_attribute='univentionOperatingSystemVersion',
							con_attribute='operatingSystemVersion'
						),
				},

		),
	'dns': univention.s4connector.property (
			ucs_default_dn='cn=dns,@%@ldap/base@%@',
			con_default_dn='CN=MicrosoftDNS,CN=System,@%@connector/s4/ldap/base@%@',
			ucs_module='dns/dns',
			
			identify=univention.s4connector.s4.dns.identify,

			sync_mode='@%@connector/s4/mapping/syncmode@%@',

			scope='sub',

			con_search_filter='(|(objectClass=dnsNode)(objectClass=dnsZone))',

			position_mapping = [( ',cn=dns,@%@ldap/base@%@', ',CN=MicrosoftDNS,CN=System,@%@connector/s4/ldap/base@%@' )],

			ignore_filter='(DC=_ldap._tcp.Default-First-Site-Name._site)',

			ignore_subtree = global_ignore_subtree,
			
			con_sync_function = univention.s4connector.s4.dns.ucs2con,
			ucs_sync_function = univention.s4connector.s4.dns.con2ucs,

		),
	'container': univention.s4connector.property (
			ucs_module='container/cn',

			sync_mode='@%@connector/s4/mapping/syncmode@%@',

			scope='sub',

			con_search_filter='(|(objectClass=container)(objectClass=builtinDomain))', # builtinDomain is cn=builtin (with group cn=Administrators)

			ignore_filter='(|(cn=mail)(cn=kerberos))',

			ignore_subtree = global_ignore_subtree,
			
			con_create_objectclass=['top', 'container' ],

			attributes= {
					'cn': univention.s4connector.attribute (
							ucs_attribute='name',
							ldap_attribute='cn',
							con_attribute='cn',
							required=1,
							compare_function=univention.s4connector.compare_lowercase,
						),
					'description': univention.s4connector.attribute (
							ucs_attribute='description',
							ldap_attribute='description',
							con_attribute='description'
						),
				},

		),

	'ou': univention.s4connector.property (
			ucs_module='container/ou',

			sync_mode='@%@connector/s4/mapping/syncmode@%@',

			scope='sub',

			con_search_filter='objectClass=organizationalUnit',

			ignore_filter='',

			ignore_subtree = global_ignore_subtree,

			con_create_objectclass=[ 'top', 'organizationalUnit' ],

			attributes= {
					'ou': univention.s4connector.attribute (
							ucs_attribute='name',
							ldap_attribute='ou',
							con_attribute='ou',
							required=1,
							compare_function=univention.s4connector.compare_lowercase,
						),
					'description': univention.s4connector.attribute (
							ucs_attribute='description',
							ldap_attribute='description',
							con_attribute='description'
						),
				},
		),
}



