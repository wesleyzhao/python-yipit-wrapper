#!/usr/bin/python2.5
# Created by Wesley Zhao
# Modeled after the python-twitter wrapper done by
# The Python-Twitter Developers (python-twitter@googlegroups.com)
#
#

class YipitError(Exception):
    '''Base class for Yipit errors'''
    
    @property # jzhao what is this?
    def message(self):
        ''' Returns the first argument used to construct this error. '''
        return self.args[0]

