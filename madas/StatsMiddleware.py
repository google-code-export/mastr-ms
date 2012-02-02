import re
from operator import add
from time import time
from django.db import connection
import logging
logger = logging.getLogger('stats')

class StatsMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):

        # turn on debugging in db backend to capture time
        from django.conf import settings
        
        if settings.DEBUG:
            # get number of db queries before we do anything
            n = len(connection.queries)
        else:
            n = 0
        # time the view
        start = time()
        response = view_func(request, *view_args, **view_kwargs)
        totTime = time() - start
        dbTime = 0.0
        if settings.DEBUG:
            # compute the db time for the queries just run
            queries = len(connection.queries) - n
            if queries:
                dbTime = reduce(add, [float(q['time']) 
                                    for q in connection.queries[n:]])

        pyTime = totTime - dbTime

        stats = {
            'totTime': totTime,
            'pyTime': pyTime,
            'dbTime': dbTime,
            'queries': queries,
            'sql': connection.queries
            }

        path = request.META.get('PATH_INFO', 'Unknown')
        ajax = request.META.get('HTTP_X_REQUESTED_WITH', False) == 'XMLHttpRequest'
        
        if settings.DEBUG:
            logger.debug("Path:%s, AJAX:%s, Total:%.2f, Py:%2f, DB:%2f (%d)" % (path, ajax, stats['totTime'], stats['pyTime'], stats['dbTime'], stats['queries']) )
        else:
            logger.debug("Path:%s, AJAX:%s, Total:%.2f" % (path, ajax, stats['totTime']) )
        return response

