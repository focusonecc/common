# -*- encoding: utf-8 -*- 
# @file: appstore
# @author: theol
# @Date: 2018/1/23 16:38
# @Updated: 2018/1/2316:38

import json
import requests
from requests.exceptions import RequestException


class InAppPurchaseValidationError(Exception):
    raw_response = None


    def __init__(self, raw_response=None):
        super(InAppPurchaseValidationError, self).__init__()
        self.raw_response = raw_response


api_ok = 0
api_result_errors = {
    21000: InAppPurchaseValidationError('Bad Json'),
    21002: InAppPurchaseValidationError('Bad Receipt data'),
    21003: InAppPurchaseValidationError('Unauthenticated receipt'),
    21004: InAppPurchaseValidationError('Unmatch shared secret'),
    21005: InAppPurchaseValidationError('Recipt Server not available'),
    21006: InAppPurchaseValidationError('Subscription has expired'),
    21007: InAppPurchaseValidationError('Test receipt sent to production env'),
    21008: InAppPurchaseValidationError('Production receipt sent to test env'),
    21010: InAppPurchaseValidationError('Unauthorized receipt')
}
TEST_URL = 'https://sandbox.itunes.apple.com/verifyReceipt'
PROD_URL = 'https://buy.itunes.apple.com/verifyReceipt'


class AppStoreValidator(object):
    """
    AppStore 应用内购买凭证验证
    """
    bundle_id = None
    validate_url = None
    sandbox = None
    auto_retry_wrong_env_request = False


    def __init__(self, bundle_id, sandbox=False, auto_retry_wrong_env_request=False):
        self.bundle_id = bundle_id
        self.sandbox = sandbox
        if not self.bundle_id:
            raise InAppPurchaseValidationError('`bundle_id` can not be empty')
        self.auto_retry_wrong_env_request = auto_retry_wrong_env_request
        self._adjust_url_by_sandbox()


    def validate(self, receipt, shared_secret=None):
        """
        验证用户应用内购买收据凭证

        :param receipt: 收据数据
        :param shared_secret: 可选的共享密码
        :return: 验证结果或异常
        """

        # 根据APP传递的支付收据数据来确定收据验证 URL
        if isinstance(receipt,(str,)):
            receipt = json.loads(receipt)
        env = receipt.get('environment', 'prod').lower()
        self.sandbox = True if env == 'sandbox' else False

        receipt_json = {'receipt-data': receipt}
        if shared_secret:
            receipt_json['password'] = shared_secret

        api_response = self.post_json(receipt_json)
        status = api_response['status']

        if status in [21007, 21008] and self.auto_retry_wrong_env_request:
            self.sandbox = not self.sandbox
            api_response = self.post_json(receipt_json)
            status = api_response['status']

        if status != api_ok:
            error = api_result_errors.get(status, InAppPurchaseValidationError('Unknown API status'))
            error.raw_response = api_response
            raise error

        return api_response


    def post_json(self, request_json):
        self._adjust_url_by_sandbox()
        try:
            return requests.post(self.url, json=request_json).json()
        except (ValueError, RequestException):
            raise InAppPurchaseValidationError('HTTP error')


    def _adjust_url_by_sandbox(self):
        """
        根据sandbox的值来选择相应的App Store 验证URL
        """
        self.url = TEST_URL if self.sandbox else PROD_URL


if __name__ == '__main__':
    bundle_id = 'com.focusonecc.test'
    validator = AppStoreValidator(bundle_id)
    receipt_str = '''
    { 
        "signature" : "XXXX",
        "purchase-info" : "XXXX",
        "environment" : "Sandbox",
        "pod" : "100",
        "signing-status" : "0"
    }
    '''
    try:
        validate_result = validator.validate(receipt_str)
    except InAppPurchaseValidationError as ex:
        response_from_apple = ex.raw_response
        print(response_from_apple)
        pass
