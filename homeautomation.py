"""
    Author      : Sujayyendhiren Ramarao Srinivasamurthi
    Description : Preliminary analysis of Kaggle datasets
"""

import os
import json
import traceback
from glob import glob
from multiprocessing import Pool

import flask
from flask import Flask, render_template, request
import pandas as pd
from nvd3 import multiBarChart
from werkzeug.utils import secure_filename

from library.bose import Bose
from library.aiy  import Aiy
from library.network import HomeNetwork
from library.philips import Philips
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
    except OSError as err:
        print("OS error: {0}".format(err))
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
        except OSError as err:
            print("OS error: {0}".format(err))
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
    return render_template('welcome.html')


@application.route("/philips", methods=['GET', "POST"])
@application.route("/philips/<light>", methods=['GET', "POST"])
@application.route("/philips/<devid>/<color>", methods=['GET', "POST"])
def toggelelights(light=None, devid=None, color=None):
    """ Philips hue lights are controlled from here """

    try:
        hue = {}
        hue['collapse'] = 'in'
        hue['msghead'] = "Click a button to select desired state"

        Philips.create_dendrogram_input()

        if light:
            Philips.philips_light_switch(int(light), hue)

        if color and devid:
            if color.startswith('hue'):
                color = color.replace("hue", '')
                Philips.philips_light_colors(devid, hue, color=int(color))
            elif color.startswith('bri'):
                bri = color.replace("bri", '')
                Philips.philips_light_colors(devid, hue, bri=int(bri))

        return render_template('philips.html')

    except OSError as err:
        print("OS error: {0}".format(err))
        return render_template('failure.html', message="Phillips hue detection failed")

    except:
        print(traceback.format_exc())
        return render_template('failure.html', message="Phillips hue detection failed")


@application.route('/bosesoundtouch')
@application.route('/bose/<key>')
def bosesoundtouch(key=None):
    """ Welcome screen with a list of datasets to choose from. """

    try:
        if key != None:

            if key == 'PRESETS':
                Bose.check_presets()
            else:
                Bose.change_key_attr(key)

        return render_template('bosesoundtouch.html', \
                display=json.dumps(Bose.get_bose_info(), indent=4),\
                bosehostname=Bose.__HOSTNAME__,\
                boseip=Bose.__IP__)
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        print(traceback.format_exc())
        return render_template('failure.html', message="Soundtouch detection failed")


@application.route('/datanalysis')
def view_datasets():
    """ Welcome screen with a list of datasets to choose from. """
    return render_template('dataanalysis.html', hue={},\
                            datasets=sorted(get_datasets(),\
                            key=lambda s: s.lower()), columns=[])


@application.route('/d3display')
@application.route('/d3display/<option>')
def d3display(option=None):
    """ Discover home network """
    try:
        if not option:
            HomeNetwork.create_tree()
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        print(traceback.format_exc())
        return render_template('failure.html', message="Home network discovery failure")

    return render_template('d3homedevices.html')


@application.route('/appletv')
@application.route('/appletv/<action>')
def appletv(action=None):
    """ Welcome screen with a list of datasets to choose from. """
    try:
        if action != None:
            Utility.appletv_processing(action)
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        return render_template('failure.html', message="Apple TV feature yet to be developed")
    return render_template('appletv.html')


@application.route('/osdetection')
@application.route('/osdetection/<ipaddr>')
def osdetection(ipaddr=None):
    """ OS detection is performed here """
    try:
        osdata = {}
        columns = None

        if ipaddr:
            ipaddr = [(ipaddr, None)]
        else:
            ipaddr = []
            cache = Utility.cache('devices', 'read')

            for hostname in cache:
                ipaddr.append((cache[hostname]['ip'], hostname))

        osdetect = HomeNetwork()

        pool = Pool(processes=len(ipaddr))
        result = pool.map(osdetect.os_detection, ipaddr)
        pool.close()
        pool.join()

        for hostname, osname, _ in result:
            osdata[hostname] = osname

            if not columns:
                columns = osname.keys()

        return render_template('ostable.html', osdata=osdata, columns=columns)
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        print(traceback.format_exc())
        return render_template('failure.html', message="OS detection failed")


@application.route('/voicekit')
def googlekit(msg=None):
    """ Google AIY kit """
    return render_template('aiyvoicekit.html', msg=msg)


@application.route('/aiy/<service>/<action>')
def aiycontrols(service=None, action=None):
    """ Control raspberrypi AIY kit """

    aiy = Aiy(); msg = None

    try:
        aiy.process_request(service, action)
    except:
        msg = ''
        if service in aiy.available:
            msg += "{} - {} \n\n".format(service, aiy.available[service])
        msg += traceback.format_exc()
    return googlekit(msg)


@application.route('/')
def welcome():
    """ Welcome screen with a list of datasets to choose from. """
    return render_template('welcome.html')


if __name__ == '__main__':

    #----------------#
    # Initialization #
    #----------------#
    for directory in ['output', 'cache', 'datasets', 'logs', 'static/data']:
        if not os.path.exists(directory):
            os.mkdir(directory)
    application.run(host="0.0.0.0", processes=8)
