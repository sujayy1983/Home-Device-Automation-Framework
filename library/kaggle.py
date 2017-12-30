"""
Author: Sujayyendhiren Ramarao Srinivasamurthi
Description: Kaggle Processing shall be moved here and enhanced
"""

import traceback
from glob import glob

import pandas as pd
from nvd3 import multiBarChart


class Kaggle(object):
    """ Kaggle dataset minimal processing """

    __DATASET__ = "datasets/{0}"

    @staticmethod
    def filter_data(dataframe, column, value):
        """ Process csv data """
        ##Loop over filters
        return dataframe[dataframe[column].str.contains(value)]

    @staticmethod
    def get_datasets():
        """ Get datasets """
        return [elem.split('/')[-1] for elem in glob('datasets/*.csv')]

    @staticmethod
    def get_dataframe(dataset):
        """ Get dataframe from a csv file name"""
        return pd.read_csv(Kaggle.__DATASET__.format(dataset), low_memory=False, \
        encoding="latin1", skipinitialspace=True, error_bad_lines=False)

    @staticmethod
    def get_columns(dataset):
        """ Get columns in a dataset """
        return Kaggle.get_dataframe(dataset).keys()

    @staticmethod
    def get_unique_columnelems(dataset, column, head=15):
        """ Get a list of column names from a csv file """
        try:
            analyze = pd.read_csv(Kaggle.__DATASET__.format(dataset), \
                    skipinitialspace=True)[column].value_counts(\
                                            ).head(head).to_frame()
            analyze.reset_index(inplace=True)
            analyze.columns = [column, 'OccurrenceCnt']
            return analyze
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print(traceback.format_exc())
            return None
    
    @staticmethod
    def get_barchart(formatted):
        """ Create a bar chart and return html content """

        chart = multiBarChart(width=1200, height=500, x_axis_format=None)
        xdata = formatted[formatted.keys()[0]].values.tolist()
        ydata1 = formatted[formatted.keys()[1]].values.tolist()
        chart.add_serie(name=formatted.keys()[0], y=ydata1, x=xdata)
        chart.buildhtml()

        with open("test.html", 'w') as fil:
            fil.write(chart.htmlcontent)

        return chart.htmlcontent