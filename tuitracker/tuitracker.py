# -*- coding: utf-8 -*-
import sys
import time
import logging
import datetime
import traceback
import adage.nodestate as nodestate
import adage.dagstate as dagstate
import networkx as nx

logging.basicConfig(level = logging.INFO)

def relmove(term,n):
    if n < 0:
        for i in range(abs(n)):
            term.stream.write(term.move_up())
    else:
        for i in range(n):
            term.stream.write(term.move_down())

def analyze_progress(adageobj):
    dag, rules, applied = adageobj.dag, adageobj.rules, adageobj.applied_rules
    successful, failed, running, unsubmittable = 0, 0, 0, 0

    nodestates = []
    for node in nx.topological_sort(dag):
        nodeobj = dag.getNode(node)
        if nodeobj.state == nodestate.RUNNING:
            nodestates.append('running')
        elif dagstate.node_status(nodeobj):
            nodestates.append('success')
        elif dagstate.node_ran_and_failed(nodeobj):
            nodestates.append('failed')
        elif dagstate.upstream_failure(dag,nodeobj):
            nodestates.append('unsubmittable')
        else:
            nodestates.append('scheduled')
    return nodestates

def handleevent(term, adageobj):
    relmove(term, 5)
    timestring = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print('Last Update: {}'.format(timestring))

    nodestates = analyze_progress(adageobj)
    perline = 35
    char = u'◼︎'
    colors = {
        'success': term.green(char),
        'running': term.yellow(char),
        'failed': term.red(char),
        'unsubmittable': term.blue(char),
        'scheduled': term.magenta(char),
    }
    chunked = '\n'.join([''.join([colors[ns] for ns in nodestates[x:x+perline]]) for x in range(len(nodestates))[::perline]])
    print('Progress:\n'+chunked)

def ui():
    log = logging.getLogger('yadageui')
    maxheight = 30
    banner = '''\
                __
  __ _____ ____/ /__ ____ ____
 / // / _ `/ _  / _ `/ _ `/ -_)
 \_, /\_,_/\_,_/\_,_/\_, /\__/
/___/               /___/
    '''
    from blessings import Terminal

    rootlogger = logging.getLogger()
    handlers = [x for x in rootlogger.handlers]
    for x in handlers:
        rootlogger.removeHandler(x)
    rootlogger = logging.getLogger()
    rootlogger.addHandler(logging.FileHandler('bkg.log'))

    term = Terminal()

    with term.hidden_cursor():
        for i in range(maxheight):
            print('')
        relmove(term,-maxheight)

        with term.location():
            print(term.bold(banner))

        while True:
            event = yield
            if not event:
                break
            with term.location():
                try:
                    handleevent(term, event)
                except:
                    print('... UI exception ...')
                    traceback.print_exc(file=sys.stdout)
                    print('')
        relmove(term,maxheight)
    print('Workflow done. Good Bye.')
    for x in handlers:
        rootlogger.addHandler(x)


def dummyui():
    while True:
        state = yield
        print('got state', state)

class TUITracker(object):
    def __init__(self):
        self.uicoroutine = ui()
        next(self.uicoroutine)
        pass

    def initialize(self,adageobj):
        self.uicoroutine.send(adageobj)

    def track(self,adageobj):
        self.uicoroutine.send(adageobj)

    def finalize(self,adageobj):
        self.uicoroutine.send(adageobj)
        self.uicoroutine.send(None)
