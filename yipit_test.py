import yipit

API_KEY = '4rZUnBn4z9YgACck'

class YipitTest(object):
    def __main__(self):
        # jzhao why is this main function not being called automatically?

        api = yipit.Api(api_key = API_KEY)
        
        deals = api.get_deals()
        
        # test deals general fetch
        print "Deals : "
        print deals
        # test individual deals
        print "Individual Deal: "
        print deals[0]
        
        print ""
        # test sources general fetch
        sources = api.get_sources()
        print "Sources: "
        print sources
        # test individual source
        print "Individual Source:"
        print sources[0]

        print ""
        # test divisions general fetch
        divisions = api.get_divisions()
        print "Divisions: "
        print divisions
        # test individual division
        print "Individual division:"
        print divisions[0]

        print ""
        # test tags general fetch
        tags = api.get_tags()
        print "Tags:"
        print tags
        # test individual tag
        print "Tag:"
        print tags[0]

    if __name__ == "__main__":
        self.__main__()
