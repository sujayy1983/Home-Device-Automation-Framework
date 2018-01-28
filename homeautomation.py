"""
    Author      : Sujayyendhiren Ramarao Srinivasamurthi
    Description : Home automation with interesting gadgets at home.
                  Most of them support REST. Some features are based on 
                  a service running on this host (AIY google voice kit)
                  and door bell feature leverages speaker on this device.
"""

import os
import io
import time
import json
import traceback
import subprocess
from glob import glob
from datetime import datetime

import flask
from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename

from library.aiy  import Aiy
from library.bose import Bose
from library.kaggle import Kaggle
from library.philips import Philips
from library.Utility import Utility
from library.network import HomeNetwork
from library.security import Security

UPLOAD_FOLDER = 'datasets'
ALLOWED_EXTENSIONS = set(['csv'])

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@application.route('/filter', methods=['POST'])
@application.route('/filter/<options>', methods=['POST'])
def filter_columns(options=None):
    """" Filters various parameters in a dataset """

    if options != None:
        try:
            result = Kaggle.get_unique_columnelems(request.form['dataset'], \
                       request.form['column'], head=int(request.form['rows']))
            barchart = Kaggle.get_barchart(result)
            formatted = result.values.tolist()
            return render_template('displaystats.html',\
                    columns=result.keys(), rows=formatted, barchart=barchart)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print(traceback.format_exc())

    elif filter == 'withvalue':
        return Kaggle.filter_data(Kaggle.get_dataframe(request.form['dataset']), \
                request.form['column'], request.form['value']).to_html()

    else:
        return "TBD"


@application.route('/getcolumns', methods=['GET', 'POST'])
def retrieve_columns():
    """ Retrieve columns in a dataset """
    dataset = request.form['dataset']
    datasets = sorted(Kaggle.get_datasets(), key=lambda s: s.lower())

    datasets.insert(0, datasets.pop(datasets.index(dataset)))
    return render_template('dataanalysis.html', dataset=dataset,\
                datasets=datasets, columns=Kaggle.get_columns(dataset))


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
                datasets=Kaggle.get_datasets(), columns=[])


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
                            datasets=sorted(Kaggle.get_datasets(),\
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

@application.route('/traceroute')
def traceroute():
    """ Discover home network """

    timestamp = str(datetime.now()).replace(" ", "-").replace(":", "-").replace(".", "-")
    filename = "traceroute-{}.json".format(timestamp)
    jsonfile = "static/data/{0}".format(filename)

    #Security.generate_results('www.facebook.com', filename=jsonfile)
    Security.test_results('www.facebook.com', filename=jsonfile)
    return render_template('networklayout.html', newlayout=jsonfile)

@application.route('/d3display')
def d3display():
    """ Discover home network """
    timestamp = str(datetime.now()).replace(" ", "-").replace(":", "-").replace(".", "-")
    filename = "networkdata-{}.json".format(timestamp)
    jsonfile = "/static/data/{0}".format(filename)
    HomeNetwork.create_d3json(jsonfile=jsonfile)
    return render_template('d3homedevices.html', h2header="Home Network - Discovery", jsonfile=jsonfile)

@application.route('/doorbell')
@application.route('/doorbell/<mp3>', methods=['GET', "POST"])
def voicehtml5(mp3=None):
    """ Voice via html5 """

    doorbell = glob("mp3/*")
    doorbell = sorted([bell.replace("mp3/", "") for bell in doorbell])

    if mp3:
        mp3song = 'mp3/{}'.format(mp3)
        os.system('mpg321 {0}'.format(mp3song))

    return render_template('doorbell.html', doorbell=doorbell)

@application.route('/osupdate', methods=['GET', "POST"])
def osupdate():
    """ os updates """
    def inner():
        proc = subprocess.Popen(
            ["python3 osdetectioncron.py"],
            shell=True,
            stdout=subprocess.PIPE
        )

        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            print(line)
            time.sleep(0.5)
            yield line.rstrip() + '<br/>\n'

    return flask.Response(inner(), mimetype='text/html')

@application.route('/diagnostics/<option>')
def disgnostics(option):
    """ Diagnostics calls are processed here """
    command, results = Utility.diagnostics(option)
    return render_template('diagnostics.html', command=command, results=results)

@application.route('/')
def welcome():
    """ Welcome screen with a list of datasets to choose from. """
    return render_template('welcome.html')


if __name__ == '__main__':

    #----------------------------#
    # Application Initialization #
    #----------------------------#
    appcfg = Utility.read_configuration(config="APPLICATION")

    for directory in appcfg['directories']:
        if not os.path.exists(directory):
            os.mkdir(directory)

    HomeNetwork.initializetable()

    try:
        application.run(host="0.0.0.0", port=appcfg['port'], \
            processes=appcfg['processes'])
    except:
        alternateport = 5000
        print("Starting on {0}".format(alternateport))
        application.run(host="0.0.0.0", port=alternateport,\
            processes=appcfg["processes"])
