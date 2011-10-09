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
        print ""
        
        # test individual deal
        deal = deals[0]
        
        print "Individual Deal: "
        print deal

    if __name__ == "__main__":
        self.__main__()
