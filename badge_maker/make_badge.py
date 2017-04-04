import yaml
import json
import urllib
import click

@click.command()
@click.argument('name')
@click.option('-f','--settingsfile', default = '.yadage.yml')
@click.option('-u','--url', default = 'http://yadage.cern.ch/submit')
def command(settingsfile,name,url):
    data = yaml.load(open(settingsfile))
    data['pars'] = json.dumps(data['pars'])
    

    print '[![yadage workflow](https://img.shields.io/badge/run_yadage-{name}-4187AD.svg)]({url}?{query})'.format(
        name = name,
        url = url,
        query = urllib.urlencode(data)
    )

if __name__ == '__main__':
    command()
