"""
    Author      : Sujayyendhiren Ramarao Srinivasamurthi
    Description : Preliminary analysis of Kaggle datasets
"""

import os
import json
import traceback

from glob import glob

import nmap
import flask

from   flask import Flask, render_template, request
import pandas as pd
from werkzeug.utils import secure_filename
from nvd3 import multiBarChart

import library.bose as bose
from library.Utility import Utility



DATASET = "datasets/{0}"
UPLOAD_FOLDER = 'datasets'
ALLOWED_EXTENSIONS = set(['csv'])

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def filter_data(dataframe, column, value):
    """ Process csv data """
    ##Loop over filters
    return dataframe[dataframe[column].str.contains(value)]


def get_datasets():
    """ Get datasets """
    return [elem.split('/')[-1] for elem in glob('datasets/*.csv')]


def get_dataframe(dataset):
    """ Get dataframe from a csv file name"""
    return pd.read_csv(DATASET.format(dataset), low_memory=False, \
    encoding="latin1", skipinitialspace=True, error_bad_lines=False)


def get_columns(dataset):
    """ Get columns in a dataset """
    return get_dataframe(dataset).keys()


def get_unique_columnelems(dataset, column, head=15):
    """ Get a list of column names from a csv file """
    try:
        analyze = pd.read_csv(DATASET.format(dataset), \
                  skipinitialspace=True)[column].value_counts(\
                                        ).head(head).to_frame()
        analyze.reset_index(inplace=True)
        analyze.columns = [column, 'OccurrenceCnt']
        return analyze
    except:
        print(traceback.format_exc())
        return None


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


@application.route('/filter', methods=['POST'])
@application.route('/filter/<options>', methods=['POST'])
def filter_columns(options=None):
    """" Filters various parameters in a dataset """
    if options != None:

        try:
            result = get_unique_columnelems(request.form['dataset'], \
                       request.form['column'], head=int(request.form['rows']))
            barchart = get_barchart(result)
            formatted = result.values.tolist()
            return render_template('displaystats.html',\
                    columns=result.keys(), rows=formatted, barchart=barchart)

        except:
            print(traceback.format_exc())

    elif filter == 'withvalue':
        return filter_data(get_dataframe(request.form['dataset']), \
                request.form['column'], request.form['value']).to_html()

    else:
        return "TBD"


@application.route('/getcolumns', methods=['GET', 'POST'])
def retrieve_columns():
    """ Retrieve columns in a dataset """
    dataset = request.form['dataset']
    datasets = sorted(get_datasets(), key=lambda s: s.lower())

    datasets.insert(0, datasets.pop(datasets.index(dataset)))
    return render_template('dataanalysis.html', dataset=dataset,\
                datasets=datasets, columns=get_columns(dataset))


@application.route("/upload", methods=["POST"])
def upload():
    """ Upload a dataset that needs to be analyzed """
    if request.method == 'POST':
        uploaded_files = flask.request.files.getlist("file[]")

        for afile in uploaded_files:
            if not afile.filename.endswith('.csv'): 
                continue
            afile.save(os.path.join(application.config['UPLOAD_FOLDER'],\
                                    secure_filename(afile.filename)))
    return render_template('welcome.html', hue={},\
                datasets=get_datasets(), columns=[])


@application.route('/test')
def test():
    """ test a new feature  before standardizing as part of the tool. """
    return render_template('test.html')


@application.route("/philips", methods=['GET', "POST"])
@application.route("/philips/<light>", methods=['GET', "POST"])
def toggelelights(light=None):
    """ Phillips hue lights are controlled from here """

    hue= {}; hue['collapse'] = 'in'; 
    hue['msghead'] = "Click a button to select desired state"

    if light:
        print("Light: {0}".format(light))
        Utility.phillips_light_switch(int(light), hue)

    lightsinfo = Utility.get_basic_info()
    return render_template('philips.html', lights=lightsinfo,\
                           hue=hue)


@application.route('/bosesoundtouch')
@application.route('/bose/<key>')
def bosesoundtouch(key=None):
    """ Welcome screen with a list of datasets to choose from. """
    if key != None:

        if key == 'PRESETS':
            bose.check_presets(key)
        else:
            bose.change_key_attr(key)

    return render_template('bosesoundtouch.html', \
            display=json.dumps(bose.get_bose_info(), indent=4))


@application.route('/datanalysis')
def view_datasets():
    """ Welcome screen with a list of datasets to choose from. """
    return render_template('dataanalysis.html', hue={},\
                            datasets=sorted(get_datasets(),\
                            key=lambda s: s.lower()), columns=[])


@application.route('/discovery/<ip>')
def device_description(ip):
    """ Discover all the devices in home network """

    devices = []
    nm = nmap.PortScanner()
    nm.scan(hosts=ip, arguments='-O') 
    scanned = nm.all_hosts()

    for host in scanned:
        print(json.dumps(nm[host], indent=4))
        devices.append({'ip': host})

    return render_template('devicediscovery.html',\
                            columns=['ip'],\
                            rows=devices)


@application.route('/d3display')
@application.route('/d3display/<option>')
def d3display(option=None):
    """ Welcome screen with a list of datasets to choose from. """
    if not option:
        Utility.create_tree()
    return render_template('d3homedevices.html')


@application.route('/appletv')
@application.route('/appletv/<action>')
def appletv(action=None):
    """ Welcome screen with a list of datasets to choose from. """
    if action != None:
        Utility.appletv_processing(action)
        
    return render_template('appletv.html')


@application.route('/')
def welcome():
    """ Welcome screen with a list of datasets to choose from. """
    return render_template('welcome.html')


if __name__ == '__main__':

    #----------------#
    # Initialization #
    #----------------#
    for directory in ['output', 'cache', 'datasets', 'logs', 'static/data']:
        if not os.path.exists(directory): os.mkdir(directory)

    application.run(host="0.0.0.0", threaded=True)
