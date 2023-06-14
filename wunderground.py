import config

import argparse
from datetime import datetime, timedelta
import os
import pandas as pd
import requests



DATETIME_NOW = datetime.now().astimezone()
ARGPARSE_DATE_FORMAT = '%Y-%m-%d'
START_DATE   = datetime.strptime(config.START_DATE, ARGPARSE_DATE_FORMAT).date()


class Station:

    def __init__(self, group, station_id, geocode):
        self.group   = group
        self.id      = station_id
        self.geocode = geocode

    def get_history_data(self, date, mode, units):
        try:

            response = requests.get(
                url= HistoryETL.URL.replace(':mode', mode), 
                params={
                    'stationId': self.id, 
                    'format'   : 'json', 
                    'units'    : units, 
                    'date'     : date.strftime(HistoryETL.URL_DATE_FORMAT),
                    'apiKey'   : config.KEY,
                    'numericPrecision': 'decimal'
                }
            )

            response.raise_for_status()
            if response.status_code == 204:
                print("204 No content", sep=', ')
                return None

            return response.json()
            
        except requests.exceptions.RequestException as e:
            print("\nException: ", e.response.text)
            return None

        except Exception as e:
            print("\nException: ", e)
            return None


    def get_forecast_hourly_data(self, mode, units):
        try:

            response = requests.get(
                url= ForecastHourlyETL.URL.replace(':mode', mode), 
                params={
                    'geocode' : self.geocode, 
                    'format'  : 'json', 
                    'units'   : units, 
                    'language': 'en',
                    'apiKey'  : config.KEY,
                }
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print("\nException: ", e.response.text)
            return None

        except Exception as e:
            print("\n", e)
            return None


class HistoryETL:
    
    URL = 'https://api.weather.com/v2/pws/history/:mode'
    URL_DATE_FORMAT = '%Y%m%d' # datetime format. url query parameters must be in YYYYMMDD

    TIMESTAMP_FIELD        = 'obsTimeLocal'
    TIMESTAMP_FIELD_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, station, mode, units, storage, start, end):
        self.station = station
        self.mode    = mode
        self.units   = units
        self.storage = storage
        self.start   = start
        self.end     = end
        self.date    = None
        self.data    = None

        self.observations_len       = 0
        self.observations_len_total = 0
        
        self.observations_existing       = 0
        self.observations_existing_total = 0
        
        self.observations_stored       = 0
        self.observations_stored_total = 0

    def _extract(self):
        self.data = self.station.get_history_data(self.date, self.mode, self.units)
        
        return self

    def _transform(self):
        if self.data is not None:

            self.observations_len = len(self.data['observations'])
            self.observations_len_total += self.observations_len

            # add any data spesific tranformation that will be available for all storages
            # self.data = ...

            # call storage spesific tranformation
            self.data = self.storage.transform(self.data)
            
            self.observations_existing = self.observations_len - len(self.data)
            self.observations_existing_total += self.observations_existing

        return self

    def _load(self):
        if self.data is not None:
            
            self.storage.load(self.data)
            
            self.observations_stored = len(self.data)
            self.observations_stored_total += self.observations_stored

        return self

    def run(self):

        print('\n{} {}, getting history-{}-{} data from {}, to {}, storing to {}'.format(
            self.station.group, 
            self.station.id, 
            self.mode, 
            units_text(self.units), 
            self.start, 
            self.end,
            self.storage.name)
        )

        for i in range( (self.end - self.start).days + 1 ):

            self.date = self.start + timedelta(days=i)
            
            print("{} {}, {}: {}".format(self.station.group, self.station.id, i+1, self.date), end=", ")
            
            self._extract()._transform()._load()
            
            print("Observations: {}, Existing: {}, Inserted: {}".format(self.observations_len, self.observations_existing, self.observations_stored))

        
        print("{} {}, Totals\t Observations: {}, Existing: {}, Inserted: {}".format(self.station.group, self.station.id, self.observations_len_total, self.observations_existing_total, self.observations_stored_total))
        
        self.storage.tidyup()




class ForecastHourlyETL:

    URL = 'https://api.weather.com/v3/wx/forecast/hourly/:mode'
    AFTER_N_HOURS   = config.FORECAST_HOURLY_AFTER_N_HOURS

    TIMESTAMP_FIELD = 'validTimeLocal'
    TIMESTAMP_FIELD_FORMAT =  '%Y-%m-%dT%H:%M:%S%z'


    def __init__(self, station, mode, units, storage):
        self.station = station
        self.mode    = mode
        self.units   = units
        self.storage = storage

        self.data = None


    def _extract(self):
        self.data = station.get_forecast_hourly_data(self.mode, self.units)
        return self

    def _transform(self):
        if self.data is not None:

            # add any data spesific tranformation that will be available for all storages
            # self.data = ...

            # call storage spesific tranformation
            self.data = self.storage.transform(self.data)

        return self


    def _load(self):
        if self.data is not None:
            self.storage.load(self.data)

        return self

    def run(self):
        print('{} {}, {} getting forcast-{}-hourly data'.format(self.station.group, self.station.id, DATETIME_NOW.date(), self.mode, units_text(units)))

        self._extract()._transform()._load()



class Csv:
    
    name = 'csv'

    def __init__(self, station, category, mode, units):
        self.station  = station
        self.category = category
        self.mode     = mode
        self.units    = units
        self.dir      = os.path.join(config.DATA_DIR, self.station.group, self.station.id)
        self.filepath = os.path.join(self.dir, self.station.id + '_' + self.category + '_' + self.mode + '_' + self.units + '.csv')
        self.makedir()
        self.create_file()


    def get_last_date(self, column, datetime_format):
        try:
            df = pd.read_csv(self.filepath, usecols=[column])
            return datetime.strptime(df[column].max(), datetime_format)
            
        except Exception as e:
            return None

    
    def load(self, df, index):
        df.to_csv(self.filepath, mode='a',  index=index, header=self.is_empty())


    def makedir(self):
        os.makedirs(self.dir, exist_ok=True)


    def create_file(self):
        try:
            open(self.filepath, "x")

        except FileExistsError as e:
            pass


    def remove_existing_rows_from_df(self, df, column):
        if self.is_empty():
            return df

        csv_df = pd.read_csv(self.filepath)
        return df[df[column].isin(csv_df[column]) == False]


    def is_empty(self):
        return os.stat(self.filepath).st_size == 0


    def sort(self, column):
        csv_df = pd.read_csv(self.filepath)
        csv_df.sort_values(by=[column], inplace=True)
        csv_df.to_csv(self.filepath, index=False)


class CsvHistory(Csv):

    def get_last_date(self):
        try:
            return super().get_last_date(column=HistoryETL.TIMESTAMP_FIELD, datetime_format=HistoryETL.TIMESTAMP_FIELD_FORMAT).date()
        
        except Exception as e:
            return None
    
    def transform(self, data):
        df = pd.json_normalize(data, 'observations')
                                
        if len(df.index) > 0:
            df.columns = df.columns.str.replace(units_text(self.units) + '.', '', regex=False)
            df         = self.remove_existing_rows_from_df(df, HistoryETL.TIMESTAMP_FIELD)

        return df

    def load(self, data):
        super().load(df=data, index=False)


    def tidyup(self):
        self.sort(column=HistoryETL.TIMESTAMP_FIELD)


class CsvForecastHourly(Csv):

    def get_last_date(self):
        try:
            return super().get_last_date(column=ForecastHourlyETL.TIMESTAMP_FIELD, datetime_format=ForecastHourlyETL.TIMESTAMP_FIELD_FORMAT)
        
        except Exception as e:
            print(e)
            return None

    def transform(self, data):
        return pd.DataFrame.from_dict(data)

    def load(seld, data):
        super().load(df=data, index=True)


def units_text(units):
    if units == 'm' :
        return 'metric'

    elif units == 'e':
        return 'imperial'
    
    else:
        return ''


def datetime_strptime(str_datetime):
    try:
        return datetime.strptime(str_datetime, ARGPARSE_DATE_FORMAT).date()
    
    except ValueError as e:
        raise argparse.ArgumentTypeError(e)


def str_extract_digits_to_int(str):
    return int( ''.join( n for n in str if n.isdigit() ) )


def storage_factory(category, storage, station, mode, units):
    factory = {

        'history': {
            Csv.name: CsvHistory(station, category, mode, units)
        },

        'forecast_hourly':{
            Csv.name: CsvForecastHourly(station, category, mode, units)
        }

    }
    return factory[category][storage]


def argparser():
    parser = argparse.ArgumentParser(
        description="Make Historical and Forecast weather csv datasets from Wunderground Personal Weather Stations (PWS). Please check README file.",
        epilog = "https://github.com/giannisan/wunderground/"
    )
    
    parser.add_argument('-g',  '--groups',
        nargs='+', 
        default=list(config.stations.keys()), 
        choices=list(config.stations.keys()), 
        # metavar='', 
        help="Get data only for stations in specified groups acording to config.py"
    )

    parser.add_argument('-hs', '--history',
        nargs='*', 
        default=config.HISTORY, 
        choices=['hourly', 'daily', 'all'],
        # type=argparse_set,
        # metavar='', 
        help="History data to be obtained. 'hourly': for 60min resulotion, 'daily': for 24h resolution, 'all' for all available measurements in station for each day (about 5min resolution)."
    )

    parser.add_argument('-fh', '--forecast-hourly',
        nargs='*', 
        default=config.FORECAST_HOURLY, 
        choices=['1day', '2day', '3day', '10day', '15day'], 
        # metavar='', 
        help="Forecast hourly data to be obtained. 1day: for the next 24 hours, 2day: for the next 48 hours, 3day for the next 72 hours, etc. Usage: -fh 2day 3day 15day"
    )

    parser.add_argument('-u', '--units',
        nargs='*',
        default=config.UNITS, 
        choices=['m', 'e'], 
        # metavar='', 
        help="The unit of measure for the response. The following values are supported: m = Metric units, e = Imperial (English) units. Usage: -u m"
    )
    
    parser.add_argument('-s', '--start',
        metavar=ARGPARSE_DATE_FORMAT,
        default=None,
        type=datetime_strptime,
        help="Get station's history data starting from the specified date. Format: {}. Usage: --start '{}'".format(ARGPARSE_DATE_FORMAT.replace('%', ''), datetime.strftime(DATETIME_NOW - timedelta(days=120), ARGPARSE_DATE_FORMAT))
    )

    parser.add_argument('-e', '--end',
        metavar=ARGPARSE_DATE_FORMAT,
        default=None,
        type=datetime_strptime,
        help="Get stations's data until the specified date. Format: '{}. Usage: --end {}".format(ARGPARSE_DATE_FORMAT.replace('%', ''), datetime.strftime(DATETIME_NOW.date(), ARGPARSE_DATE_FORMAT))
    )

    parser.add_argument('-st', '--store_to',
        metavar='',
        default=config.STORE_TO,
        choices=config.STORE_TO,
        help=argparse.SUPPRESS
    )

    return parser.parse_args()


if __name__== '__main__':
    args = argparser()

    stations = []
    for group in set(args.groups):
        for station_config in config.stations[group]:
            stations.append(Station(group, station_config['id'], station_config['geocode']))

    for station in stations:
        for history_mode in args.history:
            for units in args.units:
                for arg_storage in args.store_to:
                    
                    storage = storage_factory('history', arg_storage, station, history_mode, units)

                    start = args.start or storage.get_last_date() or START_DATE
                    end   = args.end   or DATETIME_NOW.date() 

                    HistoryETL(station, history_mode, units, storage, start, end).run()


        for forecast_hourly_mode in args.forecast_hourly:
            for units in args.units:
                for arg_storage in args.store_to:

                    storage = storage_factory('forecast_hourly', arg_storage, station, forecast_hourly_mode, units)
                    
                    last_datetime = storage.get_last_date() 
                    if last_datetime:
                        last_req_datetime = last_datetime - timedelta(hours= 24 * str_extract_digits_to_int(forecast_hourly_mode) )

                        if DATETIME_NOW.astimezone(last_req_datetime.tzinfo) <  last_req_datetime + timedelta(hours=ForecastHourlyETL.AFTER_N_HOURS):
                            print("{} {} We already have forecast-hourly-{}-{} for the past {}h".format(station.group, station.id, forecast_hourly_mode, units, ForecastHourlyETL.AFTER_N_HOURS))
                            continue

                    ForecastHourlyETL(station, forecast_hourly_mode, units, storage).run()
    
