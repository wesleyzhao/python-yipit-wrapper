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
            Example: lat=-37.74,lon=-76.00
          radius:
            Maximum distance of radius in miles to deal location from center 
            point. Defaults to 10. Requires lat and lon if used. [Optional]
            Example: radius=1.7
          division:
            A list of one or more division slugs. To see division slugs call
            Api.get_divisions() [Optional]
            Example: [new-york, atlanta]
          source:
            A list of one or more source slugs. To see source slugs call 
            Api.get_sources() [Optional]
            Example: [groupon, scoutmob]
          phone:
            Deals available at a business matching one of the phone numbers. See Businesses API for more details.
          tag:
          paid:
          limit:
        '''
