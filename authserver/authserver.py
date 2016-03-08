#!/usr/bin/env python

import argparse
import base64
import datetime
import hashlib
import json
import logging
import re
import os
import sys

from Crypto.PublicKey import RSA
import jwt

from flask import Flask, Response
from flask import (jsonify, request)

logging.basicConfig(
    level=logging.DEBUG, stream=sys.stderr, format='%(asctime)s - %(message)s')
LOG = logging.getLogger(__name__)

DEFAULT_CERT = os.path.join('..', 'certs', 'authserver.crt')
DEFAULT_KEY = os.path.join('..', 'certs', 'authserver.key')
DEFAULT_AUTH = os.path.join('users.auth')

# Signature key (PEM-encoded). Loaded on startup.
SIGNKEY = None
# Auth store dict of user-password entries. Loaded on startup.
AUTH_STORE = {}

app = Flask(__name__)

def response(status, data):
    """Produces a JSON :class:`flask.Response` object with a given status
    code and data dict.
    """    
    return Response(
        status=status,
        response=json.dumps(data, indent=2),
        mimetype='application/json')


def key_id(priv_key_pem):
    """For a given private RSA key, produce a key id (intended for inclusion in
    a JWT 'kid' header) for the *public* key of the key pair, which is used
    by the token receiving party to verify the signature. The key id
    algorithm was taken from
      https://github.com/docker/libtrust/blob/8f54f9250deedadb07a8d253d8be8fc591853449/util.go#L194-L207
    """
    pub_key_der = RSA.importKey(SIGNKEY).publickey().exportKey('DER')
    # SHA256 hash truncated to 240 bits (i.e., 30 bytes)
    sha256 = hashlib.sha256(pub_key_der).digest()[:30]
    # encode into 12 base32 groups like
    #   ABCD:EFGH:IJKL:MNOP:QRST:UVWX:YZ23:4567:ABCD:EFGH:IJKL:MNOP
    b32sha256 = base64.b32encode(sha256)
    buf = ""    
    for block_num in range(len(b32sha256) / 4):
        start = block_num * 4
        end = block_num * 4 + 4
        buf += b32sha256[start:end] + ":"
    return buf.rstrip(':')


def grant_access(request):
    """Produces a list of allowed actions, one for each access right
    requested in the request's `scope` header."""
    request_params = dict(request.args)
    allowed_actions = []
    for requested_permissions in request_params['scope']:
            # Each permission of form [u'repository:my/image:push,pull']
            type, name, actions = requested_permissions.split(':')
            actions = actions.split(',')
            allowed_actions.append({
                'type': type,
                'name': name,
                'actions': actions
            })
    return allowed_actions


@app.route('/api/auth')
def auth():
    """Respond to authentication requests as prescribed by
    https://github.com/docker/distribution/blob/master/docs/spec/auth/token.md
    """
    request_params = dict(request.args)
    LOG.debug("auth called: %s", request_params)
    LOG.debug("headers: %s", request.headers)
    if not 'Authorization' in request.headers:
        return response(400, {'error': 'basic auth required'})
    auth_header = re.match(r'Basic (\S+)', request.headers['Authorization'])
    if not auth_header:
        return response(400, {'error': 'malformed Authorization header'})
    user, password = base64.b64decode(auth_header.group(1)).split(':')
    if user in AUTH_STORE and AUTH_STORE[user] == password:
        # Docker registry expects a key id ('kid') header to include an
        # encoded version of the public key used to check the signature.
        keyid = key_id(SIGNKEY)
        
        granted_actions = None
        if 'scope' in request_params:
            # request to perform an action against registry
            granted_actions = grant_access(request)        
        
        signed_token = jwt.encode(
            {'iss': 'Elastisys',
             'aud': request_params['service'][0],
             'nbf': datetime.datetime.utcnow(),
             'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
             'access': granted_actions 
            }, SIGNKEY,
            algorithm='RS256',
            headers={'kid': keyid})
        LOG.debug("key id: '%s'" % keyid)
        LOG.debug("responding with token: %s" % signed_token)
        return response(200, {"token": signed_token})
    else:
        return response(401, {'error': 'incorrect username/password'})

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--auth", default=DEFAULT_AUTH,
        help='Dictionary of form {"user": "password", ... }.')
    parser.add_argument(
        "--port", type=int, default=8443, help="HTTPS port.")
    parser.add_argument(
        "--cert", default=DEFAULT_CERT, help="TLS cert (PEM file).")
    parser.add_argument(
        "--key",  default=DEFAULT_KEY, help="TLS key (PEM file).")
    args = parser.parse_args()

    with open(args.auth) as authfile:
        LOG.info("reading users from '%s' ...", args.auth)
        AUTH_STORE = json.load(authfile)
        LOG.info(AUTH_STORE)

    if not os.path.isfile(args.cert):
        raise ValueError("host cert file '%s' does not exist" % (args.cert))
    if not os.path.isfile(args.key):
        raise ValueError("host key file '%s' does not exist" % (args.key))

    with open(args.key) as keyfile:
        SIGNKEY = keyfile.read()
    
    ssl_cert = (args.cert, args.key)
    app.run(
        host='0.0.0.0', port=args.port,
        ssl_context=ssl_cert, threaded=True)

