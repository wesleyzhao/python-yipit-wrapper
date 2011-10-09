#!/usr/bin/python
# Created by Wesley Zhao
# Modeled after the python-twitter wrapper done by
# The Python-Twitter Developers (python-twitter@googlegroups.com)
#
#
#
#
#
''' A library that provides a Python interface to the Yipit API  '''
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

class YipitError(Exception):
    '''Base class for Yipit errors

    Will hold the following attributes:
      _error_code:
        Integer representation of the YipitError, as specified by the
        Yipit API Docs. We have the following error codes and what they
        represent:
          400 - Invalid Request (Bad or missing parameters)
          401 - Authentication Error Unauthorized
          404 - Named resource not found
          500 - Internal Service error
          502 - Bad Gateway -- Yipit is down or is being upgraded.
    '''
    
    def __init__(self, message, error_code=None):
        '''Instantiate a new YipitError object
        
        Args:
          message:
            Inherited from Exception, it is just the error message to be
            printed out when the Error is raised.
          error_code:
            Integer representation of the Yipit Error, as specified by the
            Yipit API Docs. We have the following error codes and what they
            represent:
              400 - Invalid Request (Bad or missing parameters)
              401 - Authentication Error Unauthorized
              404 - Named resource not found
              500 - Internal Service error
              502 - Bad Gateway -- Yipit is down or is being upgraded.
        '''
        Exception.__init__(self, message)
        self._error_code = error_code

    @property # jzhao what is this?
    def message(self):
        ''' Returns the first argument used to construct this error. '''
        return self.args[0]


class Api(object):
    '''A python interface into the Yipit API
    
    All calls require to to pass in your Yipit API Key as api_key
    For example:
    
      >> import yipit
      >> api = yipit.Api(api_key='jkldskfjdfl88234llkj')
    '''

    def __init__(self,
                 api_key):
        '''Instantiate a new yipit.Api object.

        Args:
          api_key:
            Your Yipit API Key.
        '''
        self._urllib = urllib # urllib2...read() loads json to python dict, urllib...read() loads raw json string
        self.set_credentials(api_key)
    
    def set_credentials(self, api_key):
        self._api_key = api_key

    def get_deals(self,
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
            Example: division=["new-york", "atlanta"]
          source:
            A list of one or more source slugs. To see source slugs call 
            Api.get_sources() which lists yipit.Source instances [Optional]
            Example: source=["groupon", "scoutmob"]
          phone:
            A list of phone numbers of specific bussinesses. Deals available 
            at a business matching one of the phone numbers. [Optional]
            Example: phone=[2124134259,2124655555]
          tag:
            A list of one or more tag slugs. To see tag slugs call 
            Api.get_tags() which lists yipit.Tag instances [Optional]
            Example: tag=["restaurants","bar-club"]
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
        
        if lat and lon:
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
        print "url :" + url
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
        try:
            deals = self.get_deals_list_by_params(url)
        except YipitError:
            # this should only raise an error if the id was incorrect
            return None
        
        return deals[0] # should be one and only one Deal
        
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
        if len(data['response']) == 0:
            return [] # immediately return empty list if there were no results

        deals = []

        for deal_json_dict in data['response']['deals']:
            temp = Deal.new_from_json_dict(deal_json_dict)
            deals.append(temp)

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

        url = self.build_url(url, params)
        
        url_data = self._urllib.urlopen(url).read() # urllib.urlopen.read() gets raw json, urllib2.urlopen.read() loads json as python dict
        
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
        """Raises a YipitError if Yipit returns an error 
        """
        
        return True

class Deal(object):
    '''A class representing the deal structure used by the Yipit API

    The deal structure exposes the following properties:
    
      deal.title
      deal.id
      deal.url
      deal.yipit_title
      deal.yipit_url
      deal.active
      deal.business
      deal.date_added
      deal.division
      deal.end_date
      deal.images
      deal.mobile_url
      deal.discount
      deal.price
      deal.value
      deal.purchased
      deal.source
      deal.tags
    '''

    def __init__(self,
                 title=None,
                 url=None,
                 yipit_title=None,
                 yipit_url=None,
                 active=None,
                 business=None,
                 date_added=None,
                 division=None,
                 end_date=None,
                 id=None,
                 images=None,
                 mobile_url=None,
                 discount=None,
                 price=None,
                 value=None,
                 purchased=None,
                 source=None,
                 tags=None):
        '''An object to hold a Yipit Deal

        This class is normally instantiated by the yipit.Api class and
        returned in a sequence
        
        Note: Dates are posted in the form "2011-10-10 00:00:00"
        time zone difference is calculated from UTC

        Args:
          title:
            The title of the deal from the source. [Optional]
          url:
            The URL of the deal from the source. [Optional]
          yipit_title:
            The title that Yipit uses for the deal. [Optional]
          yipit_url:
            The url to the deal hosted on Yipit. [Optional]
          active:
            Signifies if the deal is still active. [Optional]
            Example: active=1 or active=0
          business:
            A dictionary storing all the information of a business.
            [Optional]
            Example: { "id" : 64996,
                       "locations" : [
                            {
                                 "address" : "1442 ne 32nd ave",
                                 "id" : 264383,
                                 "lat" : 137.2,
                                 "lon" : -142.2,
                                 "locality" : "",
                                 "phone" : None,
                                 "smart_locality" : "",
                                 "state" : "New York",
                                 "zip_code" : "10019"
                             }
                        ],
                        "name" : "Lunafest",
                        "url" : "http://www.lunafest.org"
                      }
           date_added:
             Formatted date/time of when deal was added. [Optional]
             Example: "2011-10-08 07:24:01"
           end_date:
             Formatted date/time for when the deal ends. [Optional]
             Example: "2011-10-10 00:00:00"
           id:
             Integer id of the deal for Yipit. [Optional]
           images:
             A dictionary storing the images for this deal. [Optional]
             Example: {"image_big" : "http://bigimage.yipit.com",
                       "image_small" : "http://smallimage.yipit.com"}
           mobile_url:
             The mobile url to find the Yipit deal
           division:
             A dictionary storing all the information of the division
             the deal is in. [Optional]
             Example: {
                        "active" : 1,
                        "lat" : 40.714,
                        "lon" : -74.005,
                        "name" : "New York",
                        "slug" : "new-york",
                        "time_zone_diff" : -5,
                        "url" : "http://yipit.com/new-york/"
                        }
           price:
             A dictionary storing all the price information which usually
             includes 'formatted' and 'raw'. [Optional]
             Example: {"formatted" : "$40", "raw" : 40.00}
           value:
             A dictionary storying all the value information of the deal
             usually including 'formatted' and 'raw'. [Optional]
             Example: {"formatted" : "$80", "raw" : 80.00}
           purchased:
             A number representing how many people have bought the deal so
             far. [Optional]
           source:
             A dictionary storying all the information of the source the
             deal is from. [Optional]
             Example: {"name" : "Groupon",
                       "paid" : 0,
                       "slug" : "groupon",
                       "url" : "http://groupon.com"
                       }
           tags:
             A list storying all the tag dictionaries the deal falls under.
             [Optional]
             Example: [{
                        "name" : "Theater",
                        "slug" : "theater",
                        "url" : ""
                       }]
        '''
        self.title = title
        self.url = url
        self.yipit_title = yipit_title
        self.yipit_url = yipit_url
        self.active = active
        self.business = business
        self.date_added = date_added
        self.division = division
        self.end_date = end_date
        self.id = id
        self.images = images
        self.mobile_url = mobile_url
        self.discount = discount
        self.price = price
        self.value = value
        self.purchased = purchased
        self.source = source
        self.tags = tags

    @staticmethod
    def new_from_json_dict(data):
        '''Create a new instance based on a JSON dict.
        
        Args:
          data: A JSON dict, as converted from the JSON in the Yipit
          API.
        Returns:
          A yipit.Deal instance
        '''
        return Deal(title = data.get('title', None),
                    url = data.get('url', None),
                    yipit_title = data.get('yipit_title', None),
                    yipit_url = data.get('yipit_url', None),
                    active = data.get('active', None),
                    business = data.get('business', None),
                    date_added = data.get('date_added', None),
                    division = data.get('division', None),
                    end_date = data.get('end_date', None),
                    id = data.get('id', None),
                    images = data.get('images', None),
                    mobile_url = data.get('mobile_url', None),
                    discount = data.get('discount', None),
                    price = data.get('price', None),
                    value = data.get('value', None),
                    purchased = data.get('purchased', None),
                    source = data.get('source', None),
                    tags = data.get('tags', None))


