"""
    Author      : Sujayyendhiren Ramarao Srinivasamurthi
    Description : Preliminary analysis of Kaggle datasets
"""

import os
import json
import traceback
import webbrowser
from glob import glob
from datetime import datetime

import flask
from flask import Flask, render_template, request
import pandas as pd
from nvd3 import multiBarChart
from werkzeug.utils import secure_filename

from library.bose import Bose
from library.aiy  import Aiy
from library.philips import Philips
from library.Utility import Utility
from library.network import HomeNetwork

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
            Bose.change_key_attr(key)

        Bose.discover_boseip()
        return render_template('bosesoundtouch.html', \
                bosehostname=Bose.__HOSTNAME__,\
                boseip=Bose.__IP__,\
                status='' if Bose.__IP__ else "disabled")
    except OSError as err:
        return render_template('failure.html', message="OS error -{0}".format(err))
    except:
        return render_template('failure.html',\
            message="Soundtouch detection failed - {0}".format(traceback.format_exc()))


@application.route('/datanalysis')
def view_datasets():
    """ Welcome screen with a list of datasets to choose from. """
    return render_template('dataanalysis.html', hue={},\
                            datasets=sorted(get_datasets(),\
                            key=lambda s: s.lower()), columns=[])


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
def osdetection():
    """ OS detection is performed here """
    try:
        dataframe = HomeNetwork.read_sqlite3_current()
        jsdata = dataframe.to_json(orient='records')
        return render_template('ostable.html', osdata=json.loads(jsdata))
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        print(traceback.format_exc())
        return render_template('failure.html', message="OS detection failed")


@application.route('/voicekit')
def googlekit(msg=None):
    """ Google AIY kit """
    service = None
    status = None

    aiy = Aiy()
    for service in aiy.available:
        status = aiy.available[service]

    return render_template('aiyvoicekit.html', service=service,\
                status=status, msg=msg)


@application.route('/aiy/<service>/<action>')
def aiycontrols(service=None, action=None):
    """ Control raspberrypi AIY kit """

    msg = None
    aiy = None

    try:
        aiy = Aiy()
        aiy.process_request(service, action)
    except:
        msg = ''
        if aiy and service in aiy.available:
            msg += "{} - {} \n\n".format(service, aiy.available[service])
        msg += traceback.format_exc()

    return googlekit(msg)


@application.route('/d3display')
def d3display():
    """ Discover home network """
    timestamp = str(datetime.now()).replace(" ", "-").replace(":", "-").replace(".","-")
    filename = "networkdata-{}.json".format(timestamp)
    jsonfile = "/static/data/{0}".format(filename)
    HomeNetwork.create_d3json(jsonfile=jsonfile)
    return render_template('d3homedevices.html', jsonfile=jsonfile)

@application.route('/doorbell')
@application.route('/doorbell/<mp3>', methods=['GET', "POST"])
def voicehtml5(mp3 = None):
    """ Voice via html5 """
    
    doorbell = glob("mp3/*")
    doorbell = [bell.replace("mp3/", "") for bell in doorbell]

    if mp3:
        mp3song = 'mp3/{}'.format(mp3)
        os.system('mpg321 {0}'.format(mp3song))
        
    return render_template('doorbell.html', doorbell=doorbell)


@application.route('/')
def welcome():
    """ Welcome screen with a list of datasets to choose from. """
    return render_template('welcome.html')


if __name__ == '__main__':

    #----------------#
    # Initialization #
    #----------------#
    for directory in ['output', 'cache', 'datasets', 'logs', 'static/data', "mp3"]:
        if not os.path.exists(directory):
            os.mkdir(directory)

    HomeNetwork.initializetable()
    application.run(host="0.0.0.0", processes=8)
