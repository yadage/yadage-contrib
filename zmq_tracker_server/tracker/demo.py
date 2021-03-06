from yadage.steering_api import steering_ctx
from yadage.clihelpers import setupbackend_fromstring
from zeromq_tracker import ZeroMQTracker
import shutil
import os
import time
import click
import zmq
ctx = zmq.Context()


@click.command()
@click.argument('workdir')
@click.argument('identifier')
def cli(workdir, identifier):
	if os.path.exists(workdir):
		shutil.rmtree(workdir)


	ctx = zmq.Context()

	socket = ctx.socket(zmq.PUB)
	socket.connect('ipc://backend.sock')

	with steering_ctx(
		workdir, 'workflow.yml',
		loadtoplevel = 'from-github/testing/dynamic_glob',
		initdata = {'sourcefile': 'https://github.com/lukasheinrich/yadage-workflows/raw/master/testing/dynamic_glob/inputs/three_files.zip'},
		updateinterval = 5,
		loginterval = 5,
		backend = setupbackend_fromstring('multiproc:auto')	) as ys:
			
			ys.adage_argument(
				additional_trackers = [ ZeroMQTracker(socket = socket, identifier = identifier) ]
		)

if __name__ == '__main__':
	cli()