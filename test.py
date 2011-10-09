#!/usr/bin/env python
import sys
import yipit
import optparse

API_KEY = 'YOUR_API_KEY'

class YipitTest(object):
    """ Used just to test the main methods for this wrapper
    
    Proper usage:
    $ python test.py YIPIT_API_KEY
    """
    def main():
        # jzhao why is this main function not being called automatically?

        """
        commented out while weird characters plague my ish!!
        parser = optparse.OptionParser() # only doing this for the 1st arg
        (opts, args) = parser.parse_args()
        try:
            API_KEY = str(args[0]) # avoid random python chars
        
            # API_KEY.replace('\xc2\x96','')
 
        except IndexError:
            # no args were given, user needs to input API_KEY
            print "Please paste your API key as an arg. This is how you should use test.py. >> python test.py my_yipit_api_key"
            exit(-1)
        """
        API_KEY = sys.argv[1]
        # print API_KEY
        api = yipit.Api(api_key = API_KEY)
        
        deals = api.get_deals()
        
        # test deals general fetch
        print "Deals : "
        print deals
        # test filtered deals fetch
        print "Filtered Deals: lat=40.7654629, lon=-73.97724, radius=25, division=['new-york','atlanta'], source=['groupon', 'living-social'], tag=['restaurants','bar-club'],paid=False,limit=100"
        # this filter also allows the following params: phone
        print api.get_deals(lat=40.7654629,
                            lon=-73.97724,
                            radius=25,
                            division=['new-york','atlanta'],
                            source=['groupon', 'living-social'],
                            tag=['restaurants', 'bar-club'],
                            paid=False,
                            limit=100) 
        # test individual deals
        print "Individual Deal: "
        print deals[0]
        
        
        print ""
        # test sources general fetch
        sources = api.get_sources()
        print "Sources: "
        print sources
        # test filtered source fetch
        print "Filtered Sources: division=['new-york','atlanta'], paid=False, limit=10"
        print api.get_sources(division=['new-york','atlanta'],
                              paid=False,
                              limit=10)
        # test individual source
        print "Individual Source:"
        print sources[0]

        print ""
        # test divisions general fetch
        divisions = api.get_divisions()
        print "Divisions: "
        print divisions
        # test filtered division fetch
        print "Filtered Divisions: source=['groupon','living-social'],lat=40.7654629, lon=-73.97724, radius=25, limit=10"
        print api.get_divisions(source=['groupon', 'living-social'],
                                lat=40.7654629, 
                                lon=-73.97724,
                                radius=25,
                                limit=10)
        # test individual division
        print "Individual division:"
        print divisions[0]

        print ""
        # test tags general fetch
        tags = api.get_tags()
        print "Tags:"
        print tags
        # test filtered tags fetch
        # PSYCH THERE IS NO FILTERED TAG SEARCH LULZ
        # test individual tag
        print "Tag:"
        print tags[0]

        print ""
        # test businesses general fetch
        businesses = api.get_businesses()
        print "Businesses:"
        print businesses
        # test filtered business fetch
        print "Businesses Filtered: lat=40.7654629, lon=-73.97724, radius=25,division=['new-york']"
        # this filter also allows search by the param 'phone', but it often does
        # not work because Yipit has not fully implemented the Businesses API
        print api.get_businesses(lat=40.7654629, 
                                 lon=-73.97724,
                                 radius=25,
                                 division=['new-york'])
        # test individual business
        print "Business:"
        print businesses[0]

    if __name__ == "__main__":
        main()
