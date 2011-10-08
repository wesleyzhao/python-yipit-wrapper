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

DEALS_URL = "http://api.yipit.com/v1/deals/"

class Api(object):
    
    def __init__(self,
                 api_key):
        self._urllib = urllib2
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
            Api.get_divisions() which lists yipit.Division instances[Optional]
            Example: division=[new-york, atlanta]
          source:
            A list of one or more source slugs. To see source slugs call 
            Api.get_sources() which lists yipit.Source instances [Optional]
            Example: source=[groupon, scoutmob]
          phone:
            A list of phone numbers of specific bussinesses. Deals available 
            at a business matching one of the phone numbers. [Optional]
            Example: phone=[2124134259,2124655555]
          tag:
            A list of one or more tag slugs. To see tag slugs call 
            Api.get_tags() which lists yipit.Tag instances [Optional]
            Example: tag=[restaurants,bar-club]
          paid:
            If set to True, returns only deals Yipit pays you as a dev.
            If set to False (default/recommended), returns deals Yipit
            does not pay you for. [Optional]
            Example: paid=True
          limit:
            Sets maximum number of items returned. Default 20. Max 5000.
            [Optional]
            Example: limit=300
            
        Returns:
          A list of yipit.Deal instances, each matching the parameters given
        '''

        # Build request parameters
        parameters = {}
        
        if lat & lon:
            parameters['lat'] = lat
            parameters['lon'] = lon
            if radius:
                # radius requires lat&lon so it is located here
                parameters['radius'] = radius
            
        if division:
            parameters['division'] = ','.join(division)
            
        if source:
            parameters['source'] = ','.join(source)
            
        if phone:
            parameters['phone'] = ','.join(phone)
            
        if tag:
            parameters['tag'] = ','.join(tag)

        if paid is not None:
            parameters['paid'] = paid
            
        parameters['limit'] = limit

        # Make and send requests
        url = DEALS_URL
        deals = self.get_deals_list_by_params(url, parameters)
        return deals
        

    def get_deal_by_id(self, deal_id):
        '''Return a deal from Yipit based off its Yipit deal id
        Args:
          deal_id:
            returns a yipit.Deal instance with the an id matching deal_id
            or nothing if it does not exist
            
        Returns:
          A yipit.Deal instance, matching the deal_id. Or None if none
          match.
        '''
        
        url = DEALS_URL + deal_id # example: api.yipit.com/vi/deals/16721
        deals = self.get_deals_list_by_params(url)
        if deals:
            # if there are any elements
            return deals[0] # should be one and only one element
        else:
            return None
        
    def get_deals_list_by_params(self,
                                 url,
                                 parameters = None):
        '''Returns a list of Deal instances from calling the api with the
        url and given parameters
        Args:
          url:
            The string url to be requested.
          parameters: 
            A dictionary object with the param key and value. [Optional]
            
        Returns:
          A list of yipit.Deal instances grabbed and processed from the url
          with the given parameters
        '''

        json = self.fetch_url(url, parameters=parameters)
        data = self.parse_and_check_yipit(json)
        
        # first check to make sure we got some results
        if len(data['results']) == 0:
            return [] # immediately return empty list if there were no results

        deals = []

        for deal_json_dict in data['results']['deals']:
            temp = Deal.new_from_json_dict(deal_json_dict)
            results.append(temp)

        return deals 
        
    def fetch_url(self,
                   url,
                   parameters = None):
        '''Fetch the data from a url with the given parameters
        
        Args:
          url:
            The URL to retrieve
          parameters:
            A dictionary whose key/value pairs will be added to the query
            string. [Optional]
            
        Returns:
          A string representation of the body of the response
        '''
        params = {'key' : self._api_key}
        if parameters:
            params.update(parameters)

        url = self.build_url(url, parameters)
        
        url_data = self._urllib.urlopen(url).read()
        
        return url_data

    def parse_and_check_yipit(self, json):
        '''Try and parse the JSON returned from Yipit's API
        
        Args:
          json:
            The JSON string 
          
        Returns:
          A dictionary object of the parsed JSON, or if there was some
          error then return the error information
        '''
        data = simplejson.loads(json)
        self.check_for_yipit_error(data)

        return data

    def build_url(self, 
                  url,
                  parameters = None):
        '''Builds a url with a proper query string based off the parameters
        
        Args:
          url:
            The base of the URL
          parameters:
            A dictionary whose key/value paris will be translated to a query
            string and appended to the base URL. [Optional]

        Returns:
          A string of the concacted base URL and query string
        '''
        
        if parameters:
            query_string = urllib.urlencode(parameters)
            url = url + "?" + query_string
        return url
    
    def check_for_yipit_error(self, data):
        """place holder as I see errors
        """
        return True

class Deal(object):
    
    def new_from_json_dict(json_dict):
        return True


