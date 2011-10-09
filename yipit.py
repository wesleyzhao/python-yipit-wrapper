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
__version__ = "0.2.1"

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
SOURCES_URL = "http://api.yipit.com/v1/sources/"
DIVISIONS_URL = "http://api.yipit.com/v1/divisions/"
TAGS_URL = "http://api.yipit.com/v1/tags/"
BUSINESSES_URL = "http://api.yipit.com/v1/businesses/"

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
        deals = self.get_yipit_list_by_params(url,
                                              yipit_type_key = 'deals',
                                              **parameters)
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
        except YipitError as err:
            # this should only raise an error if the id was incorrect
            if err._error_code == 404:
                return None
            else:
                # if it wasn't a bad deal id, then raise a YipitError
                raise err
        
        return deals[0] # should be one and only one Deal

    def get_yipit_list_by_params(self,
                                 url,
                                 yipit_type_key,
                                 **params):
        '''Returns a list of object instances from calling the api with the
        url and given parameters. The object type is determined by the 
        yipit_type_key.

        Args:
          url:
            The string url to be requested.
          yipit_type_key:
            The string key to be found inside the 'response' section of the
            Yipit API call. The following keys are known to currently work:
              'deals',
              'sources',
              'divisions',
              'tags',
              'businesses'              
          **params: 
            A packed dictionary of values to be translated into a query
            string. [Optional]
            
        Returns:
          A list of yipit.Deal/yipit.Source/yipit.Division/yipit.Tag/
          yipit.Business (depending on the yipit_type_key given) instances 
          grabbed and processed from the url with the given parameters
        '''

        json = self.fetch_url(url, **params)
        data = self.parse_and_check_yipit(json)
        # first check to make sure we got some results
        if len(data['response']) == 0:
            return [] # immediately return empty list if there were no results

        yipit_objects = []
        
        for object_json_dict in data['response'][yipit_type_key]:
            # first must determine which object we are trying to use
            if yipit_type_key == 'deals':
                class_ = Deal
            elif yipit_type_key == 'sources':
                class_ = Source
            elif yipit_type_key == 'divisions':
                class_ = Division
            elif yipit_type_key == 'tags':
                class_ = Tag
            elif yipit_type_key == 'businesses':
                class_ = Business
            else:
                raise YipitError("Please use a correct Yipit object type key. Available: 'deals', 'sources', 'divisions', 'tags', and 'businesses.' You used: '%s'" % (yipit_type_key))

            temp = class_.new_from_json_dict(object_json_dict)
            yipit_objects.append(temp)

        return yipit_objects 
        
    def get_sources(self,
                  division = None,
                  paid = None,
                  limit = 20):
        '''Return Sources from Yipit given the parameters'
        
        Args:
          division:
            A list of one or more division slugs. To see division slugs call
            Api.get_divisions() which lists yipit.Division instances[Optional]
            Example: division=["new-york", "atlanta"]
          paid:
            If set to True, returns only deals Yipit pays you as a dev.
            If set to False (default/recommended), returns deals Yipit
            does not pay you for. [Optional]
            Example: paid=True
          limit:
            Sets maximum number of items returned. Default 20. Max 1000.
            [Optional]
            Example: limit=300
            
        Returns:
          A list of yipit.Source instances, each matching the parameters given
        '''

        # Build request parameters
        parameters = {}
            
        if division is not None:
            parameters['division'] = ','.join(division)

        if paid is not None:
            parameters['paid'] = paid
            
        parameters['limit'] = limit

        # Make and send requests
        url = SOURCES_URL
        sources = self.get_yipit_list_by_params(url,
                                                yipit_type_key = 'sources',
                                                **parameters)
        return sources
    def get_divisions(self,
                      source = None,
                      lat = None,
                      lon = None,
                      radius = None,
                      limit = 20):
        '''Return Divisions from Yipit given the parameters'

        Args:
          source:
            A list of one or more source slugs. To see source slugs call 
            Api.get_sources() which lists yipit.Source instances [Optional]
            Example: source=["groupon", "scoutmob"]
          lat,lon:
            Latitude and longitude (respectively) of point to sort divisions
            by proximity to. Uses radius. [Optional]
            Example: lat=-37.74,lon=-76.00
          radius:
            Maximum distance of radius in miles to deal location from center
            point. Defaults to 10. Requires lat and lon if used. [Optional]
            Example: radius=1.7
          limit:
            Sets maximum number of items returned. Default 20. Max 200.
            [Optional]
            Example: limit=200        
            
        Returns:
          A list of yipit.Division instances, each matching the parameters
          given
        '''

        # Build request parameters
        parameters = {}
            
        if lat is not None and lon is not None:
            parameters['lat'] = lat
            parameters['lon'] = lon
            if radius is not None:
                # radius requires lat&lon so it is located here
                parameters['radius'] = radius
            
        if source is not None:
            parameters['source'] = ','.join(source)

        parameters['limit'] = limit

        # Make and send requests
        url = DIVISIONS_URL
        divisions = self.get_yipit_list_by_params(url,
                                                  yipit_type_key = 'divisions',
                                                **parameters)
        return divisions
            
    def get_tags(self):
        '''Return Tags from Yipit given the parameters'
        
        Note: Yipit currently does not have any parameters to specify
        tag search.

        Returns:
          A list of yipit.Tag instances, each matching the parameters
          given
        '''

        # Make and send requests
        url = TAGS_URL
        tags = self.get_yipit_list_by_params(url, yipit_type_key = 'tags')
        return tags

    def get_businesses(self,
                       lat = None,
                       lon = None,
                       radius = None,
                       division = None,
                       phone = None):
        '''Return businesses from Yipit given the parameters'
        Args:
          lat,lon:
            Latitude and longitude (respectively) of point to sort
            businesses by proximity to. Uses radius. [Optional]
            Example: lat=-37.74,lon=-76.00
          radius:
            Maximum distance of radius in miles to businesses location 
            from center point. Defaults to 10. Requires lat and lon if 
            used. [Optional]
            Example: radius=1.7
          division:
            A list of one or more division slugs. To see division slugs call
            Api.get_divisions() which lists yipit.Division instances[Optional]
            Example: division=["new-york", "atlanta"]
          phone:
            A phone numbers of the specific bussiness. [Optional]
            Example: phone=2124134259
            
        NOTE: The Business API has NOT YET BEEN FULLY IMPLEMENTED. Not all
        businesses are listed. The Business API is intended to be used to
        look up a business.

        Returns:
          A list of yipit.Business instances, each matching the parameters 
          given
        '''

        # Build request parameters
        parameters = {}
        
        if lat is not None and lon is not None:
            parameters['lat'] = lat
            parameters['lon'] = lon
            if radius is not None:
                # radius requires lat&lon so it is located here
                parameters['radius'] = radius
            
        if division is not None:
            parameters['division'] = ','.join(division)

        if phone is not None:
            parameters['phone'] = phone
            
        # Make and send requests
        url = BUSINESSES_URL
        deals = self.get_yipit_list_by_params(url,
                                              yipit_type_key = 'businesses',
                                              **parameters)
        return deals
        

    def fetch_url(self,
                   url,
                   **parameters):
        '''Fetch the data from a url with the given parameters
        
        Args:
          url:
            The URL to retrieve
          parameters:
            A packed dictionary whose key/value pairs will be added to 
            the query string. [Optional]
            
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
        
        Args:
          data:
            A converted JSON dict with a response from the Yipit API. 
            Should always have the keys 'meta' and 'response'
            
        Raises:
          YipitError wrapping for yipit error message if one exists
        """
        meta = data['meta']
        if meta['code'] != 200:
            # if everything is NOT OK
            raise YipitError("code: %s, name: %s, message: %s" %(str(meta['code']), meta['name'], meta['message']), error_code=meta['code'])

class Deal(object):
    '''A class representing the deal structure used by the Yipit API

    The deal structure exposes the following properties:
    
      deal._title
      deal._id
      deal._url
      deal._yipit_title
      deal._yipit_url
      deal._active
      deal._business
      deal._date_added
      deal._division
      deal._end_date
      deal._images
      deal._mobile_url
      deal._discount
      deal._price
      deal._value
      deal._purchased
      deal._source
      deal._tags
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
        self._title = title
        self._url = url
        self._yipit_title = yipit_title
        self._yipit_url = yipit_url
        self._active = active
        self._business = business
        self._date_added = date_added
        self._division = division
        self._end_date = end_date
        self._id = id
        self._images = images
        self._mobile_url = mobile_url
        self._discount = discount
        self._price = price
        self._value = value
        self._purchased = purchased
        self._source = source
        self._tags = tags

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
    
    def as_json_string(self):
        '''A JSON string representation of this yipit.Deal instance.
        
        Returns:
          A JSON string representation of this yipit.Deal instance
        '''
        return simplejson.dumps(self.as_dict(), sort_keys=True)
    
    def as_dict(self):
        '''A dict representation of this yipit.Deal instance.
        
        The return value uses the same key names as the JSON representation.
        
        Return:
          A dict represention this yipit.Deal instance
        '''
        # jzhao what is a better way to make this available to all the classes?
        data = self.make_dict_from_kwargs(title = self._title,
                                          url = self._url,
                                          yipit_title = self._yipit_title,
                                          active = self._active,
                                          business = self._business,
                                          date_added = self._date_added,
                                          division = self._division,
                                          end_date = self._end_date,
                                          id = self._id,
                                          images = self._images,
                                          mobile_url = self._mobile_url,
                                          discount = self._discount,
                                          price = self._price,
                                          value = self._value,
                                          purchased = self._purchased,
                                          source = self._source,
                                          tags = self._tags)
        return data                       
        
    def make_dict_from_kwargs(self, **kwargs):
        '''Returns a dictionary of all parameters with specified keys
        
        Args:
          **kwargs:
            Default python packaging of un-specified params with keys
        
        Returns:
          A dictionary of all params with specified keys
        '''
        return kwargs
    
    def __str__(self):
        '''A string representation of this yipit.Deal instance.
        
        The return value is the same as the JSON representation.
        
        Returns:
          A string representation of this yipit.Deal instance.
        '''
        return self.as_json_string()

class Source(object):
    '''A class representing the source structure used by the Yipit API

    The source structure exposes the following properties:
    
      source._name
      source._slug
      source._paid
      source._url
    '''

    def __init__(self,
                 name = None,
                 slug = None,
                 paid = None,
                 url = None):
        '''An object to hold a Yipit Source

        This class is normally instantiated by the yipit.Api class and
        returned in a sequence

        Args:
          name:
            The name of the source. [Optional]
          slug:
            The slug of the source. [Optional]
          paid:
            If Yipit pays you for source link click. Integer 1/0. [Optional]
          url:
            The url of the source. [Optional]
        '''
        self._name = name
        self._slug = slug
        self._paid = paid
        self._url = url

    @staticmethod
    def new_from_json_dict(data):
        '''Create a new instance based on a JSON dict.
        
        Args:
          data: A JSON dict, as converted from the JSON in the Yipit
          API.
        Returns:
          A yipit.Source instance
        '''
        return Source(name = data.get('name', None),
                    slug = data.get('slug', None),
                    paid = data.get('paid', None),
                    url = data.get('url', None))
    
    def as_json_string(self):
        '''A JSON string representation of this yipit.Source instance.
        
        Returns:
          A JSON string representation of this yipit.Source instance
        '''
        return simplejson.dumps(self.as_dict(), sort_keys=True)
    
    def as_dict(self):
        '''A dict representation of this yipit.Source instance.
        
        The return value uses the same key names as the JSON representation.
        
        Return:
          A dict represention this yipit.Source instance
        '''
        # jzhao what is a better way to make this available to all the classes?
        data = self.make_dict_from_kwargs(name = self._name,
                                          slug = self._slug,
                                          paid = self._paid,
                                          url = self._url)
        return data                       
        
    def make_dict_from_kwargs(self, **kwargs):
        '''Returns a dictionary of all parameters with specified keys
        
        Args:
          **kwargs:
            Default python packaging of un-specified params with keys
        
        Returns:
          A dictionary of all params with specified keys
        '''
        return kwargs
    
    def __str__(self):
        '''A string representation of this yipit.Source instance.
        
        The return value is the same as the JSON representation.
        
        Returns:
          A string representation of this yipit.Source instance.
        '''
        return self.as_json_string()

class Division(object):
    '''A class representing the division structure used by the Yipit API

    The division structure exposes the following properties:
    
      division._name
      division._slug
      division._active
      division._time_zone_diff
      division._lat
      division._lon
      division._url
    '''

    def __init__(self,
                 name = None,
                 slug = None,
                 active = None,
                 time_zone_diff = None,
                 lat = None,
                 lon = None,
                 url = None):
        '''An object to hold a Yipit Division

        This class is normally instantiated by the yipit.Api class and
        returned in a sequence

        Args:
          name:
            The name of the division. [Optional]
          slug:
            The slug of the division. [Optional]
          active:
            Whether or not Yipit gets active deals from this Division.
            Integer 1/0. [Optional]
          time_zone_diff:
            The difference in time zone from UTC as an integer. [Optional]
          lat:
            The latitude of the division as a float. [Optional]
          lon:
            The longitude of the division as a float. [Optional]
          url:
            The url of the source. [Optional]
        '''
        self._name = name
        self._slug = slug
        self._active = active
        self._time_zone_diff = time_zone_diff
        self._lat = lat
        self._lon = lon
        self._url = url

    @staticmethod
    def new_from_json_dict(data):
        '''Create a new instance based on a JSON dict.
        
        Args:
          data: A JSON dict, as converted from the JSON in the Yipit
          API.
        Returns:
          A yipit.Division instance
        '''
        return Division(name = data.get('name', None),
                        slug = data.get('slug', None),
                        active = data.get('active', None),
                        time_zone_diff = data.get('time_zone_diff', None),
                        lat = data.get('lat', None),
                        lon = data.get('lon', None),
                        url = data.get('url', None))
    
    def as_json_string(self):
        '''A JSON string representation of this yipit.Division instance.
        
        Returns:
          A JSON string representation of this yipit.Divison instance
        '''
        return simplejson.dumps(self.as_dict(), sort_keys=True)
    
    def as_dict(self):
        '''A dict representation of this yipit.Division instance.
        
        The return value uses the same key names as the JSON representation.
        
        Return:
          A dict represention this yipit.Division instance
        '''
        # jzhao what is a better way to make this available to all the classes?
        data = self.make_dict_from_kwargs(name = self._name,
                                          slug = self._slug,
                                          active = self._active,
                                          time_zone_diff = self._time_zone_diff,
                                          lat = self._lat,
                                          lon = self._lon,
                                          url = self._url)
        return data                       
        
    def make_dict_from_kwargs(self, **kwargs):
        '''Returns a dictionary of all parameters with specified keys
        
        Args:
          **kwargs:
            Default python packaging of un-specified params with keys
        
        Returns:
          A dictionary of all params with specified keys
        '''
        return kwargs
    
    def __str__(self):
        '''A string representation of this yipit.Division instance.
        
        The return value is the same as the JSON representation.
        
        Returns:
          A string representation of this yipit.Division instance.
        '''
        return self.as_json_string()

class Tag(object):
    '''A class representing the tag structure used by the Yipit API

    The tag structure exposes the following properties:
    
      tag._name
      tag._slug
      tag._url
    '''

    def __init__(self,
                 name = None,
                 slug = None,
                 url = None):
        '''An object to hold a Yipit Tag

        This class is normally instantiated by the yipit.Api class and
        returned in a sequence

        Args:
          name:
            The name of the tag. [Optional]
          slug:
            The slug of the tag. [Optional]
          url:
            The url of thetag. [Optional]
        '''
        self._name = name
        self._slug = slug
        self._url = url

    @staticmethod
    def new_from_json_dict(data):
        '''Create a new instance based on a JSON dict.
        
        Args:
          data: A JSON dict, as converted from the JSON in the Yipit
          API.
        Returns:
          A yipit.Tag instance
        '''
        return Tag(name = data.get('name', None),
                   slug = data.get('slug', None),
                   url = data.get('url', None))
    
    def as_json_string(self):
        '''A JSON string representation of this yipit.Tag instance.
        
        Returns:
          A JSON string representation of this yipit.Tag instance
        '''
        return simplejson.dumps(self.as_dict(), sort_keys=True)
    
    def as_dict(self):
        '''A dict representation of this yipit.Tag instance.
        
        The return value uses the same key names as the JSON representation.
        
        Return:
          A dict represention this yipit.Tag instance
        '''
        # jzhao what is a better way to make this available to all the classes?
        data = self.make_dict_from_kwargs(name = self._name,
                                          slug = self._slug,
                                          url = self._url)
        return data                       
        
    def make_dict_from_kwargs(self, **kwargs):
        '''Returns a dictionary of all parameters with specified keys
        
        Args:
          **kwargs:
            Default python packaging of un-specified params with keys
        
        Returns:
          A dictionary of all params with specified keys
        '''
        return kwargs
    
    def __str__(self):
        '''A string representation of this yipit.Tag instance.
        
        The return value is the same as the JSON representation.
        
        Returns:
          A string representation of this yipit.Tag instance.
        '''
        return self.as_json_string()


class Business(object):
    '''A class representing the business structure used by the Yipit API

    The business structure exposes the following properties:
    
      business._id
      business._name
      business._url
      business._locations

    NOTE: The Businesses API has not yet been fully implemented by Yipit.
    The Businesses API is intended to be used to look up businesses.
    '''

    def __init__(self,
                 id = None,
                 name = None,
                 url = None,
                 locations = None):
        '''An object to hold a Yipit Business

        This class is normally instantiated by the yipit.Api class and
        returned in a sequence

        Args:
          id:
            Id number of the business. [Optional]
          name:
            The name of the business. [Optional]
          url:
            The url of the business. [Optional]
          locations:
            A list of location dictionaries of the business. [Optional]
            Example:
              locations = [
                            {
                              "id": 19185,
                              "address" : "126 2nd Ave.",
                              "locality" : "New York",
                              "phone" : "212-477-2477",
                              "lat" : 40.728,
                              "lon" : -73.987
                             },
                             { *another location}
                           ]
        '''
        self._id = id
        self._name = name
        self._url = url
        self._locations = locations

    @staticmethod
    def new_from_json_dict(data):
        '''Create a new instance based on a JSON dict.
        
        Args:
          data: A JSON dict, as converted from the JSON in the Yipit
          API.
        Returns:
          A yipit.Business instance
        '''
        return Business(id = data.get('id', None),
                        name = data.get('name', None),
                        url = data.get('url', None),
                        locations = data.get('locations', None))
    
    def as_json_string(self):
        '''A JSON string representation of this yipit.Business instance.
        
        Returns:
          A JSON string representation of this yipit.Business instance
        '''
        return simplejson.dumps(self.as_dict(), sort_keys=True)
    
    def as_dict(self):
        '''A dict representation of this yipit.Business instance.
        
        The return value uses the same key names as the JSON representation.
        
        Return:
          A dict represention this yipit.Business instance
        '''
        # jzhao what is a better way to make this available to all the classes?
        data = self.make_dict_from_kwargs(id = self._id,
                                          name = self._name,
                                          url = self._url,
                                          locations = self._locations)
        return data                       
        
    def make_dict_from_kwargs(self, **kwargs):
        '''Returns a dictionary of all parameters with specified keys
        
        Args:
          **kwargs:
            Default python packaging of un-specified params with keys
        
        Returns:
          A dictionary of all params with specified keys
        '''
        return kwargs
    
    def __str__(self):
        '''A string representation of this yipit.Business instance.
        
        The return value is the same as the JSON representation.
        
        Returns:
          A string representation of this yipit.Business instance.
        '''
        return self.as_json_string()
