# Wunderground

Make Historical and Forecast weather csv datasets from Wunderground Personal Weather Stations (PWS).

With this python script, we can get historical weather data for any PWS in Wunderground and save them in a csv file.
We can also get weather forecasting data based on the geolocation of the PWS.

We use the history API as defined in https://docs.google.com/document/d/1w8jbqfAk0tfZS5P7hYnar1JiitM0gQZB-clxDfG3aD0/edit
And the hourly forecast API as defined in https://docs.google.com/document/d/1_Zte7-SdOjnzBttb1-Y9e0Wgl0_3tah9dSwXUyEA3-c/edit for 1day, 2day, 3day, 10day and 15day forecasting (5day is not publicly available).

The PWSes for which we will get data, can be defined in the config.py file (see below).

We can get data for any date as long as they are available for the specified PWS. We save only unique data in the csvs based on their . Also, csv files are sorted by observation datetime in ascending order (older to newer).


# Installation

Clone the repository to your working directory

```bash

git clone https://github.com/giannisan/wunderground

```

now we need to configure our API key, default start date for data fetching, PWS groups etc.

## Configuration
Open the **config.py** file and insert the needed values, or change those according to your needs.

### API key

```python
KEY = 'YOUR API KEY'
```

### Default date from which we will start getting data for every station

In YYYY-mm-dd format

You can also specify starting and ending dates from command line arguments (see Usage section)

```python
START_DATE = '2023-03-22'
```

### Default measurement units (--units argument)

'm' for Metric units, 'e' for Imperial (English) units. 

Select from ['m', 'e']

Specify the observations' measurement units

Data is saved in a different file for each measurement unit

You can also specify measument units from command line arguments (see Usage section)

```python
UNITS= ['m', ]
```

### Default history mode (--history argument)

Select from ['hourly', 'daily', 'all']

Historical data is available in 'hourly' (24 observation/day), 'daily' (one summary observation per day), and 'all' (observations every ~5 minutes. ~287 observations/day) resolution. 

More info about history fields is available at: https://docs.google.com/document/d/1w8jbqfAk0tfZS5P7hYnar1JiitM0gQZB-clxDfG3aD0/edit

Leave the array empty for no default history mode.

```python
HISTORY= ['hourly', ]
```

### Default forecast hourly days mode (--forcast-hourly argument)

Select from: ['1day', '2day', '3day', '10day', '15day']

Forecasting data are available for the next Ndays at the requested time in hourly resolution.

More info about forecast fields is availabl at: https://docs.google.com/document/d/1_Zte7-SdOjnzBttb1-Y9e0Wgl0_3tah9dSwXUyEA3-c/edit

Leave the array empty for no default hourly forecasts.

```python
FORECAST_HOURLY= [ ]
```

### Allow new forecast values after N hours of the last request
This helps us avoid unwanted duplicates in our forecast dataset.
```python3
FORECAST_HOURLY_AFTER_N_HOURS= 24
```

### Default storage for downloaded data
For now only csv is available.
```python
STORE_TO= ['csv']
```

### Csv Storage directoy
We will save .csv files in this directory relative to the working directory

```python
DATA_DIR= 'data'
```

### Stations and station Groups
For each station, we need its ID and geolocation. We group stations for better management. We can use only one group if we like. Each group is an array of objects, and each object needs the station's ID and geocode. The geocode is used to get station's forecasting data because the API doesnt provide forecasting data based on station ID.

For all available stations: https://www.wunderground.com/wundermap

```python
stations = {
# Each key must be a group's name e.g. 'my_hood' and each group's value must be an array of Station Objects.
# Each Station Object represents a Wunderground Personal Weather Station with station's 'id' and 'geocode'.

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
}
```

# Usage


## Help
Ptint help message:
```python
python3 wundergroud.py -h
```

```python3
python3 wundergroud.py --help
```

## Default behavior
After we have configured the station(s) and added your api key in config.py, we can just run the wundergroud.py. This will use the default parameters in config.py and fetch data for all stations in all groups, and save them in .csv files.

By default, for each csv file, the latest observation's datetime will be checked, and we will get data from that date untill the runtime date.
If there are no csv files (or if they are empty), the default START_DATE in confing.py will be used.

```python
python3 wundergroud.py
```

Output:
```bash
$ python3 wundergroud.py

osaka I27TSURU2, getting history-hourly-metric data from 2023-03-22, to 2023-04-25, storing to csv
osaka I27TSURU2, 1: 2023-03-22, Observations: 24, Existing: 0, Inserted: 24
osaka I27TSURU2, 2: 2023-03-23, Observations: 24, Existing: 0, Inserted: 24
osaka I27TSURU2, 3: 2023-03-24, Observations: 24, Existing: 0, Inserted: 24
osaka I27TSURU2, 4: 2023-03-25, Observations: 24, Existing: 0, Inserted: 24
osaka I27TSURU2, 5: 2023-03-26, Observations: 24, Existing: 0, Inserted: 24
osaka I27TSURU2, 6: 2023-03-27, Observations: 24, Existing: 0, Inserted: 24
osaka I27TSURU2, 7: 2023-03-28, Observations: 24, Existing: 0, Inserted: 24
osaka I27TSURU2, 8: 2023-03-29, Observations: 24, Existing: 0, Inserted: 24

```

This will create the data directory with a subdirectory for each group and a subdirectory for each station in the group containing all the generated csv files.


## If we want to override the default behavior that is specified in config.py file, we can use the below command line arguments. Those arguments can be used together.


## Get data only for particular group(s)
If we want to get data only for the stations that are in a specific group(s), we can just run the script with the **--groups** (**-g**) argument following by the group(s') name(s). Group names and their stations are defined in config.py

```python
python3 wundergroud.py --groups athens my_group
```


## Get data starting from a particular date
If we want to get data starting from specific a date, we can use the **--start** (**-s**) argument, followed by the date in YYYY-MM-DD format.
The following will fetch data starting from 2023-01-31 (by default, it will end at the runtime date. See below for particulare end date).
This argument will ignore the latest date in csv. Don't worry about getting duplicate data because those will be rejected.

```python
python3 wundergroud.py --start 2023-01-31
```

## Get data until a particular date
If we want to get data until a specific date, we can use the **--end** (**-e**) argument followed by the date in YYYY-MM-DD format.
The following will fetch data only untill 2023-02-28

```python
python3 wundergroud.py --end 2023-02-28
```


## Get data in particular date interval

Use the **--start** and **--end** arguments followed by the interval dates.
The following will fetch data for all groups in config.py:

```python
python3 wundergroud.py --start 2023-01-01 --end 2023-03-31
```


## Get historical data in a particular mode
If we want to get **daily** or **hourly** or **all** (all daily observations) data, we can run with the --history (-hs) argument followed by the wanted mode(s).
The following will get history hourly and all (all daily observations) data for all stations.

```python
python3 wundergroud.py --history all hourly
```


## Get hourly forecasting data
If you want to get hourly forecasting for the next N days(N: 1, 2, 3, 7, 10, 15), run with the **--forecast-hourly** (**-fh**) argument.
We can use this in order to build a dataset with the forecasting values that are provided by Wundergroud.
Forecasting data that we can get, starts from the requested time until 24\*N hours later. We cant get earlier forecasting values (e.g. to compare them with the actual measured ones).
There are six modes available: 1day, 2day, 3day, 7day, 10day and 15day. We can use this to build a dataset if we request forecasting data at the same time each day. To avoid unwanted duplicate data we can use the FORECAST_HOURLY_AFTER_N_HOURS= variable in the config file in order to allow new data entries after N hours from the last request.


```python
python3 wundergroud.py --forecast-hourly 1day
```

## Specify measurment units
We can use the **--units** parameter to retrive observesions in metric or/and imperial units. Choose **m** for metric, **e** for imperial units.
The command below will fetch data both in metric and impetrial units and will save them in seperated csv files for each station.

```python
python3 wundergroud.py --units m e
```



## Usage example

### Get data for a particular date interval and for specific group(s) of stations in metric units

The following will get data for the stations in 'my_group' and 'osaka' groups, from 2021-11-31 to 2022-12-31 in metric units.
Only new observations will be saved in each station's csv file, along with the existing ones (if there are any). No duplicates will be added.

```python
python3 wundergroud.py --groups my_group osaka --start 2021-11-31 --end 2022-12-31 -u m
```


# Schedueling

We can use a cron job to run our script daily in order to get the latest data.


Open crontab

```bash
crontab -e
```

and add the following line at the end of the crontab file. Make sure you leave an empty line at the end.

This job runs daily at 00:01:00 (your machine's time) and gets the latest data for all stations in groups.

This will also create a log file (wu.log) with the output.

Make sure you use absolute paths in your cron job scheduler to run the script.

```bash
1 0 * * * cd /absolute/path/to/wunderground && python3 wunderground.py >> wu.log 2>&1
```

## Job for forecasting data
This job will run every day at 00:01:00 and will get forecasting data along with the default historical mode for all stations.

Output will be saved in wu.log file

```bash
1 0 * * * cd /absolute/path/to/wunderground && python3 wunderground.py --forecast-hourly 1day >> wu.log 2>&1
```
