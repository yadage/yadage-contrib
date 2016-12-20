from yadage.steering_api import steering_ctx
from yadage.clihelpers import setupbackend_fromstring
from zeromq_tracker import ZeroMQTracker
import shutil
import os
import time

workdir = 'work'
if os.path.exists(workdir):
	shutil.rmtree(workdir)

with steering_ctx(
	workdir, 'madgraph_delphes.yml',
	loadtoplevel = 'from-github/phenochain',
	initdata = {'nevents': 100},
	updateinterval = 5,
	loginterval = 5,
	backend = setupbackend_fromstring('multiproc:auto')	) as ys:
	
		ys.adage_argument(
			additional_trackers = [ ZeroMQTracker(connect_string = 'ipc://../what.sock', sleep = 1) ]
		)
