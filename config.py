##########################################################################
##
##
## wunderground configuration parameters
##
##
##########################################################################
    
# Your API key
KEY = 'YOUR API KEY'

# Default date from which we will start getting data for each station. In YYYY-mm-dd format
START_DATE = '2022-12-31'

# Default response measurements units 'm' for Metric units, 'e' for Imperial (English) units
UNITS = ['m', ]

# Default history mode (--history parameter). Select from ['hourly', 'daily', 'all'].
# Leave the array empty for no default history mode.
# More info about history fields at: https://docs.google.com/document/d/1w8jbqfAk0tfZS5P7hYnar1JiitM0gQZB-clxDfG3aD0/edit
HISTORY = ['hourly', ]

# Default forecast hourly days mode (--forcast-hourly parameter). Select from: ['1day', '2day', '3day', '10day', '15day']. 
# Leave the array empty if you don't want to fetch hourly forcasts by default
# More info about forecast fields at: https://docs.google.com/document/d/1_Zte7-SdOjnzBttb1-Y9e0Wgl0_3tah9dSwXUyEA3-c/edit
FORECAST_HOURLY = [ ]

# Allow new forecast values after N hours of last request. This helps us avoid unwanted dublicates in our forecast dataset
FORECAST_HOURLY_AFTER_N_HOURS = 24

# Default storage for downloaded data. For now only csv is available.
STORE_TO = ['csv']

# The main data storage directory 
DATA_DIR = 'data'


##########################################################################
##
##
## Wunderground Stations
##
##
##########################################################################

# Each key must be a group's name e.g. 'my_hood' and each group's value must be an array of Station Objects.
# Each Station Object represents a Wunderground Personal Weather Station with station's 'id' and 'geocode'.
stations = {

    'athens': [
        {
            'id': 'IATHEN61',
            'geocode': '37.97,23.72'
        },

        {
            'id': 'IATHEN76',
            'geocode': '37.97,23.71'
        },

        {
            'id': 'IATHEN71',
            'geocode': '37.97,23.74'
        },

        # {
        #   'id': 'OtherID',
        #   'geocode': 'XX.XX,YY.YY'
        # },

    ],

    'osaka': [
        {
            'id': 'I27TSURU2',
            'geocode': '34.63,135.42'
        },

    ],

    'my_group': [
        {
            'id': 'KNYNEWYO1421', # NYC
            'geocode': '40.77,-73.95'
        },

        {
            'id': 'IPARIS18204', # Paris
            'geocode': '48.86,2.35'
        },

        {
            'id': 'IJAKAR14', # Jakarta
            'geocode': '-6.19,106.80'
        }
    ],

    # 'other_group' : [
    #     {
    #         'id': '',
    #         'geocode': ''
    #     },
    #
    # ],
}


