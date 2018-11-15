# coding=utf-8
#
# Created by junn, on 14/04/2017
#

# 签名工具模块

import logging
import base64

logger = logging.getLogger(__name__)


from django.core.signing import TimestampSigner
signer = TimestampSigner()
sign = lambda string: base64.b64encode(signer.sign(string))
unsign = lambda signed: signer.unsign(base64.b64decode(signed))