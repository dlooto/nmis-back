#coding=utf-8

import logging

from django.db import connection
from django.middleware.csrf import get_token

from utils import eggs


logger = logging.getLogger('django')


class PrintSqlMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info('Agent: %s' % request.META.get('HTTP_USER_AGENT'))
        for sql in connection.queries:
            logger.debug('[DEBUG-SQL]%s;   time: %s' % (sql['sql'], sql['time']))
        response = self.get_response(request)
        return response


class GetTokenMiddleware(object):

    def process_response(self, request, response):
        if request.method in ("POST", "PUT", "DELETE"):
            get_token(request)
        return response
    
                
OFFSET_CONST = '0yp*wsx90oyt90n'
                
def _check_sig(req, client):
    """
    path = /v1/auths/login?client_key=xxx&sig=xxxxxx
    sig = md5(path+SALT)
    """
    param_sig = req.REQUEST.get('sig')
    if not param_sig:
        return False
    path = req.get_full_path()
    path = path.replace('&sig=%s' % param_sig, '').replace('sig=%s&' % param_sig, '').replace('sig=%s' % param_sig, '')
    return True if eggs.make_sig(path, client.secret_key, offset=OFFSET_CONST) == param_sig else False                
                

class PrintRequestParamsMiddleware(object):
    """
     Add this middleware for printing request params when api requesting
    """
    def process_request(self, request):
        logger.debug('')
        logger.debug('------------------ Request Params pre-view ------------------ begin')
        logger.debug('%s %s' % (request.method, request.path))
        logger.debug('Params: %s' % request.REQUEST)
        logger.debug('Http User Agent: %s' % request.META.get('HTTP_USER_AGENT', None))
        
        # only for testing, remove when online
        # client = get_authedapp(app_key=request.REQUEST.get('app_key', ''))
        # if not client:
        #    return
        # logger.info('sig: %s' % eggs.make_sig(request.get_full_path(), client.secret_key))
        #
        # logger.info('FILES: %s' % request.FILES)
        logger.debug('------------------ Request Params pre-view  ----------------- end')
        logger.debug('')
        
        return None
