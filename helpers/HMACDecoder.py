from starlette.datastructures import Headers
from helpers.Logger import getLogger
from typing import Dict
import time
import hmac
import hashlib
import os

class HMACHelper:
    def __init__(self):
        self.logger = getLogger('HMACHelper')
        self.ACCESS_KEY = os.getenv('ACCESS_KEY', 'False')
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'False')
        if self.ACCESS_KEY == 'False' or self.SECRET_KEY == 'False':
            self.DO_HMAC = False
            self.logger.info('Disabling HMAC due to lack of credentials')
        else:
            self.DO_HMAC = True


    def generateAuthHeaders(self, 
                            secret_key: str, 
                            access_key: str, 
                            endpoint: str, 
                            timeVar: str, 
                            type: bytes
                            ) -> Dict[str, str]:
        hmac_obj = hmac.new(key=secret_key.encode(), digestmod=hashlib.sha256)
        hmac_obj.update(timeVar.encode())
        hmac_obj.update(type)
        hmac_obj.update(f'/{endpoint}'.encode())
        hmac_digest = hmac_obj.hexdigest()

        req_headers = {"X-Date": timeVar}
        req_headers['Authorization'] = f'HMAC-SHA256 Credential={access_key},Signature={hmac_digest}'

        return req_headers

    def verifyHMACRequest(self, 
                          headers: Headers, 
                          endpoint: str, 
                          type: bytes, 
                          allowed_skew_ms: int=5 * 60 * 1000
                          ) -> bool:
        if not self.DO_HMAC:
            return True

        client_date = headers.get("X-Date")
        client_auth = headers.get("Authorization", "")

        if not client_date or not client_auth.startswith("HMAC-SHA256"):
            return False

        try:
            client_timestamp = int(client_date)
        except ValueError:
            return False

        now = int(time.time() * 1000)
        if abs(now - client_timestamp) > allowed_skew_ms:
            return False

        expected_auth_header = self.generateAuthHeaders(self.SECRET_KEY, self.ACCESS_KEY, endpoint, client_date, type)
        
        return hmac.compare_digest(client_auth, expected_auth_header['Authorization'])
