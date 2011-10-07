"""
created by Wesley Zhao
"""

__author__ = "wesley.zhao@gmil.com"
__version__ = "0.1.1"

try:
    # Python >= 2.6
    import json as simplejson
except ImportError:
    try:
        # Python < 2.6
        import simplejson
    except ImportError:
        raise ImportError, "Noob try getting a json library like simplejson"

import urllib
import urllib2

DEALS_URL = "http://api.yipit.com/v1/deals"

class Api(object):
    
    def __init__(self,
                 api_key):
        set_credentials(api_key)
    
    def set_credentials(api_key):
        self._api_key = api_key

    def get_deals(self,
                  deal_id = None,
                  lat = None,
                  lon = None,
                  radius = None,
                  division = None,
                  source = None,
                  phone = None,
                  tag = None,
                  paid = None,
                  limit = 20):
        '''Return deals from Yipit given the parameters'
        Args:
          deal_id:
            returns a yipit.Deal instance with the an id matching deal_id
            or nothing if it does not exist
          lat,lon:
            Latitude and longitude (respectively) of point to sort deals by 
            proximity to. Uses radius. [Optional]
            Example lat=-37.74,lon=-76.00
          radius:
          division:
          source:
          phone:
          tag:
          paid:
          limit:
        '''
