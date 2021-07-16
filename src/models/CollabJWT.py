import jwt
import requests
import datetime
import json
from cachetools import TTLCache
from src.views import Logger
import sys

LOGGER = Logger.init_logger(__name__)


class CollabJWT:
    def __init__(self, domain, key, secret, cert):
        LOGGER.debug("")
        self.domain = domain
        self.key = key
        self.secret = secret
        self.cert = cert
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=5.0)
        header = {"alg": "RS256", "typ": "JWT"}
        claims = {"iss": self.key, "sub": self.key, "exp": exp}
        self.assertion = jwt.encode(claims, self.secret)
        self.grant_type = "urn:ietf:params:oauth:grant-type:jwt-bearer"
        self.payload = {"grant_type": self.grant_type, "assertion": self.assertion}
        self.verify_cert = cert
        self.jcache = None

    def get_key(self):
        LOGGER.debug("")
        return self.key

    def get_secret(self):
        LOGGER.debug("")
        return self.secret

    def set_JWT(self):
        LOGGER.debug("")
        # Create request with header, payload, signature
        endpoint = "https://" + self.domain + "/token"
        if self.jcache != None:
            try:
                token = self.jcache["jwtoken"]
                return token
            except KeyError as e:
                LOGGER.error(str(e))
                pass
        r = requests.post(
            endpoint, data=self.payload, auth=(self.key, self.secret), verify=self.cert
        )

        if r.status_code == 200:
            json_valores = json.loads(r.text)
            self.jcache = TTLCache(maxsize=1, ttl=json_valores["expires_in"])
            self.jcache["jwtoken"] = json_valores["access_token"]
        elif r.status_code == 401:
            LOGGER.warning(
                "Your Collaborate credentials are not valid, check it with developers@blackboard.com"
            )
        elif r.status_code == 400:
            LOGGER.warning("Your json Config.py is not valid")
        else:
            LOGGER.error(f"[auth:jotToken()] ERROR: {str(r)}")

    def get_JWT(self):
        LOGGER.debug("")
        try:
            if self.jcache != None:
                token = self.jcache["jwtoken"]
                return token
            else:
                sys.exit()
        except KeyError as e:
            LOGGER.error(str(e))
            self.create_session()
            return self.jcache["jwtoken"]
