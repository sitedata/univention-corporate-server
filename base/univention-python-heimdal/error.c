/*
 * Python Heimdal
 *	Bindings for the error handling API of heimdal
 *
 * Copyright 2003-2019 Univention GmbH
 *
 * https://www.univention.de/
 *
 * All rights reserved.
 *
 * The source code of this program is made available
 * under the terms of the GNU Affero General Public License version 3
 * (GNU AGPL V3) as published by the Free Software Foundation.
 *
 * Binary versions of this program provided by Univention to you as
 * well as other copyrighted, protected or trademarked materials like
 * Logos, graphics, fonts, specific documentations and configurations,
 * cryptographic keys etc. are subject to a license agreement between
 * you and Univention and not subject to the GNU AGPL V3.
 *
 * In the case you use this program under the terms of the GNU AGPL V3,
 * the program is provided in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public
 * License with the Debian GNU/Linux or Univention distribution in file
 * /usr/share/common-licenses/AGPL-3; if not, see
 * <https://www.gnu.org/licenses/>.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <krb5.h>
#include <krb5_err.h>

#if PY_MAJOR_VERSION >= 3
#define PyInt_FromLong PyLong_FromLong
#endif

PyObject *Krb5_exception_class;

static PyObject *error_objects;

PyObject *krb5_exception(krb5_context context, int code, ...)
{
	PyObject *errobj;
	PyObject *info;

	if (code == ENOENT) {
		PyErr_SetObject(PyExc_IOError, Py_None);
	} else {
		PyObject *i = PyInt_FromLong(code);
		errobj = PyDict_GetItem(error_objects, i);
		if (errobj == NULL)
			errobj = Krb5_exception_class;
		info = Py_BuildValue("{s:i}", "code", code);

		PyErr_SetObject(errobj, info);
	}

	return NULL;
}

void error_init(PyObject *self)
{
	Krb5_exception_class = PyErr_NewException("heimdal.Krb5Error",
			NULL,
			NULL);
	PyDict_SetItemString(self, "Krb5Error", Krb5_exception_class);
	error_objects = PyDict_New();

#	define seterrobj2(n, o) { \
		PyObject *i = PyInt_FromLong(n);			\
		PyDict_SetItem(error_objects, i, o);			\
	}

#	define seterrobj(n) { \
		PyObject *e, *d = PyDict_New();				\
		PyDict_SetItemString(d, "code", PyInt_FromLong(n));	\
		e = PyErr_NewException("heimdal."#n,			\
				Krb5_exception_class, d);		\
		seterrobj2(n, e);					\
		PyDict_SetItemString(self, #n, e);			\
		Py_DECREF(e);						\
	}

#if 1
	seterrobj(KRB5KDC_ERR_NONE);
	seterrobj(KRB5KDC_ERR_NAME_EXP);
	seterrobj(KRB5KDC_ERR_SERVICE_EXP);
	seterrobj(KRB5KDC_ERR_BAD_PVNO);
	seterrobj(KRB5KDC_ERR_C_OLD_MAST_KVNO);
	seterrobj(KRB5KDC_ERR_S_OLD_MAST_KVNO);
	seterrobj(KRB5KDC_ERR_C_PRINCIPAL_UNKNOWN);
	seterrobj(KRB5KDC_ERR_S_PRINCIPAL_UNKNOWN);
	seterrobj(KRB5KDC_ERR_PRINCIPAL_NOT_UNIQUE);
	seterrobj(KRB5KDC_ERR_NULL_KEY);
	seterrobj(KRB5KDC_ERR_CANNOT_POSTDATE);
	seterrobj(KRB5KDC_ERR_NEVER_VALID);
	seterrobj(KRB5KDC_ERR_POLICY);
	seterrobj(KRB5KDC_ERR_BADOPTION);
	seterrobj(KRB5KDC_ERR_ETYPE_NOSUPP);
	seterrobj(KRB5KDC_ERR_SUMTYPE_NOSUPP);
	seterrobj(KRB5KDC_ERR_PADATA_TYPE_NOSUPP);
	seterrobj(KRB5KDC_ERR_TRTYPE_NOSUPP);
	seterrobj(KRB5KDC_ERR_CLIENT_REVOKED);
	seterrobj(KRB5KDC_ERR_SERVICE_REVOKED);
	seterrobj(KRB5KDC_ERR_TGT_REVOKED);
	seterrobj(KRB5KDC_ERR_CLIENT_NOTYET);
	seterrobj(KRB5KDC_ERR_SERVICE_NOTYET);
	seterrobj(KRB5KDC_ERR_KEY_EXPIRED);
	seterrobj(KRB5KDC_ERR_PREAUTH_FAILED);
	seterrobj(KRB5KDC_ERR_PREAUTH_REQUIRED);
	seterrobj(KRB5KDC_ERR_SERVER_NOMATCH);
	seterrobj(KRB5KDC_ERR_KDC_ERR_MUST_USE_USER2USER);
	seterrobj(KRB5KDC_ERR_PATH_NOT_ACCEPTED);
	seterrobj(KRB5KDC_ERR_SVC_UNAVAILABLE);
	seterrobj(KRB5KRB_AP_ERR_BAD_INTEGRITY);
	seterrobj(KRB5KRB_AP_ERR_TKT_EXPIRED);
	seterrobj(KRB5KRB_AP_ERR_TKT_NYV);
	seterrobj(KRB5KRB_AP_ERR_REPEAT);
	seterrobj(KRB5KRB_AP_ERR_NOT_US);
	seterrobj(KRB5KRB_AP_ERR_BADMATCH);
	seterrobj(KRB5KRB_AP_ERR_SKEW);
	seterrobj(KRB5KRB_AP_ERR_BADADDR);
	seterrobj(KRB5KRB_AP_ERR_BADVERSION);
	seterrobj(KRB5KRB_AP_ERR_MSG_TYPE);
	seterrobj(KRB5KRB_AP_ERR_MODIFIED);
	seterrobj(KRB5KRB_AP_ERR_BADORDER);
	seterrobj(KRB5KRB_AP_ERR_ILL_CR_TKT);
	seterrobj(KRB5KRB_AP_ERR_BADKEYVER);
	seterrobj(KRB5KRB_AP_ERR_NOKEY);
	seterrobj(KRB5KRB_AP_ERR_MUT_FAIL);
	seterrobj(KRB5KRB_AP_ERR_BADDIRECTION);
	seterrobj(KRB5KRB_AP_ERR_METHOD);
	seterrobj(KRB5KRB_AP_ERR_BADSEQ);
	seterrobj(KRB5KRB_AP_ERR_INAPP_CKSUM);
	seterrobj(KRB5KRB_AP_PATH_NOT_ACCEPTED);
	seterrobj(KRB5KRB_ERR_RESPONSE_TOO_BIG);
	seterrobj(KRB5KRB_ERR_GENERIC);
	seterrobj(KRB5KRB_ERR_FIELD_TOOLONG);
	seterrobj(KRB5_KDC_ERR_CLIENT_NOT_TRUSTED);
	seterrobj(KRB5_KDC_ERR_KDC_NOT_TRUSTED);
	seterrobj(KRB5_KDC_ERR_INVALID_SIG);
	seterrobj(KRB5_KDC_ERR_DH_KEY_PARAMETERS_NOT_ACCEPTED);
	seterrobj(KRB5_KDC_ERR_WRONG_REALM);
	seterrobj(KRB5_AP_ERR_USER_TO_USER_REQUIRED);
	seterrobj(KRB5_KDC_ERR_CANT_VERIFY_CERTIFICATE);
	seterrobj(KRB5_KDC_ERR_INVALID_CERTIFICATE);
	seterrobj(KRB5_KDC_ERR_REVOKED_CERTIFICATE);
	seterrobj(KRB5_KDC_ERR_REVOCATION_STATUS_UNKNOWN);
	seterrobj(KRB5_KDC_ERR_REVOCATION_STATUS_UNAVAILABLE);
	seterrobj(KRB5_KDC_ERR_CLIENT_NAME_MISMATCH);
	seterrobj(KRB5_KDC_ERR_INCONSISTENT_KEY_PURPOSE);
	seterrobj(KRB5_KDC_ERR_DIGEST_IN_CERT_NOT_ACCEPTED);
	seterrobj(KRB5_KDC_ERR_PA_CHECKSUM_MUST_BE_INCLUDED);
	seterrobj(KRB5_KDC_ERR_DIGEST_IN_SIGNED_DATA_NOT_ACCEPTED);
	seterrobj(KRB5_KDC_ERR_PUBLIC_KEY_ENCRYPTION_NOT_SUPPORTED);
	seterrobj(KRB5_ERR_RCSID);
	seterrobj(KRB5_LIBOS_BADLOCKFLAG);
	seterrobj(KRB5_LIBOS_CANTREADPWD);
	seterrobj(KRB5_LIBOS_BADPWDMATCH);
	seterrobj(KRB5_LIBOS_PWDINTR);
	seterrobj(KRB5_PARSE_ILLCHAR);
	seterrobj(KRB5_PARSE_MALFORMED);
	seterrobj(KRB5_CONFIG_CANTOPEN);
	seterrobj(KRB5_CONFIG_BADFORMAT);
	seterrobj(KRB5_CONFIG_NOTENUFSPACE);
	seterrobj(KRB5_BADMSGTYPE);
	seterrobj(KRB5_CC_BADNAME);
	seterrobj(KRB5_CC_UNKNOWN_TYPE);
	seterrobj(KRB5_CC_NOTFOUND);
	seterrobj(KRB5_CC_END);
	seterrobj(KRB5_NO_TKT_SUPPLIED);
	seterrobj(KRB5KRB_AP_WRONG_PRINC);
	seterrobj(KRB5KRB_AP_ERR_TKT_INVALID);
	seterrobj(KRB5_PRINC_NOMATCH);
	seterrobj(KRB5_KDCREP_MODIFIED);
	seterrobj(KRB5_KDCREP_SKEW);
	seterrobj(KRB5_IN_TKT_REALM_MISMATCH);
	seterrobj(KRB5_PROG_ETYPE_NOSUPP);
	seterrobj(KRB5_PROG_KEYTYPE_NOSUPP);
	seterrobj(KRB5_WRONG_ETYPE);
	seterrobj(KRB5_PROG_SUMTYPE_NOSUPP);
	seterrobj(KRB5_REALM_UNKNOWN);
	seterrobj(KRB5_SERVICE_UNKNOWN);
	seterrobj(KRB5_KDC_UNREACH);
	seterrobj(KRB5_NO_LOCALNAME);
	seterrobj(KRB5_MUTUAL_FAILED);
	seterrobj(KRB5_RC_TYPE_EXISTS);
	seterrobj(KRB5_RC_MALLOC);
	seterrobj(KRB5_RC_TYPE_NOTFOUND);
	seterrobj(KRB5_RC_UNKNOWN);
	seterrobj(KRB5_RC_REPLAY);
	seterrobj(KRB5_RC_IO);
	seterrobj(KRB5_RC_NOIO);
	seterrobj(KRB5_RC_PARSE);
	seterrobj(KRB5_RC_IO_EOF);
	seterrobj(KRB5_RC_IO_MALLOC);
	seterrobj(KRB5_RC_IO_PERM);
	seterrobj(KRB5_RC_IO_IO);
	seterrobj(KRB5_RC_IO_UNKNOWN);
	seterrobj(KRB5_RC_IO_SPACE);
	seterrobj(KRB5_TRANS_CANTOPEN);
	seterrobj(KRB5_TRANS_BADFORMAT);
	seterrobj(KRB5_LNAME_CANTOPEN);
	seterrobj(KRB5_LNAME_NOTRANS);
	seterrobj(KRB5_LNAME_BADFORMAT);
	seterrobj(KRB5_CRYPTO_INTERNAL);
	seterrobj(KRB5_KT_BADNAME);
	seterrobj(KRB5_KT_UNKNOWN_TYPE);
	seterrobj(KRB5_KT_NOTFOUND);
	seterrobj(KRB5_KT_END);
	seterrobj(KRB5_KT_NOWRITE);
	seterrobj(KRB5_KT_IOERR);
	seterrobj(KRB5_NO_TKT_IN_RLM);
	seterrobj(KRB5DES_BAD_KEYPAR);
	seterrobj(KRB5DES_WEAK_KEY);
	seterrobj(KRB5_BAD_ENCTYPE);
	seterrobj(KRB5_BAD_KEYSIZE);
	seterrobj(KRB5_BAD_MSIZE);
	seterrobj(KRB5_CC_TYPE_EXISTS);
	seterrobj(KRB5_KT_TYPE_EXISTS);
	seterrobj(KRB5_CC_IO);
	seterrobj(KRB5_FCC_PERM);
	seterrobj(KRB5_FCC_NOFILE);
	seterrobj(KRB5_FCC_INTERNAL);
	seterrobj(KRB5_CC_WRITE);
	seterrobj(KRB5_CC_NOMEM);
	seterrobj(KRB5_CC_FORMAT);
	seterrobj(KRB5_CC_NOT_KTYPE);
	seterrobj(KRB5_INVALID_FLAGS);
	seterrobj(KRB5_NO_2ND_TKT);
	seterrobj(KRB5_NOCREDS_SUPPLIED);
	seterrobj(KRB5_SENDAUTH_BADAUTHVERS);
	seterrobj(KRB5_SENDAUTH_BADAPPLVERS);
	seterrobj(KRB5_SENDAUTH_BADRESPONSE);
	seterrobj(KRB5_SENDAUTH_REJECTED);
	seterrobj(KRB5_PREAUTH_BAD_TYPE);
	seterrobj(KRB5_PREAUTH_NO_KEY);
	seterrobj(KRB5_PREAUTH_FAILED);
	seterrobj(KRB5_RCACHE_BADVNO);
	seterrobj(KRB5_CCACHE_BADVNO);
	seterrobj(KRB5_KEYTAB_BADVNO);
	seterrobj(KRB5_PROG_ATYPE_NOSUPP);
	seterrobj(KRB5_RC_REQUIRED);
	seterrobj(KRB5_ERR_BAD_HOSTNAME);
	seterrobj(KRB5_ERR_HOST_REALM_UNKNOWN);
	seterrobj(KRB5_SNAME_UNSUPP_NAMETYPE);
	seterrobj(KRB5KRB_AP_ERR_V4_REPLY);
	seterrobj(KRB5_REALM_CANT_RESOLVE);
	seterrobj(KRB5_TKT_NOT_FORWARDABLE);
	seterrobj(KRB5_FWD_BAD_PRINCIPAL);
	seterrobj(KRB5_GET_IN_TKT_LOOP);
	seterrobj(KRB5_CONFIG_NODEFREALM);
	seterrobj(KRB5_SAM_UNSUPPORTED);
	seterrobj(KRB5_SAM_INVALID_ETYPE);
	seterrobj(KRB5_SAM_NO_CHECKSUM);
	seterrobj(KRB5_SAM_BAD_CHECKSUM);
	seterrobj(KRB5_OBSOLETE_FN);
	seterrobj(KRB5_ERR_BAD_S2K_PARAMS);
	seterrobj(KRB5_ERR_NO_SERVICE);
	seterrobj(KRB5_CC_NOSUPP);
	seterrobj(KRB5_DELTAT_BADFORMAT);
#endif
}
