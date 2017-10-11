import jq
import json
import jsonpointer
import logging
import subprocess
import shlex

class TypedLeafDecoder(json.JSONDecoder):
    def __init__(self, type_identifiers, type_loader, obj_store, *args, **kwargs):
        self.type_identifiers = type_identifiers
        self.type_loader = type_loader
        self.obj_store = obj_store
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        identifiers = set(self.type_identifiers).intersection(set(obj.keys()))
        if identifiers:
            typed_obj = self.type_loader({k:obj[k] for k in identifiers},obj)
            self.obj_store.append(typed_obj)
            return typed_obj
        return obj

class TypedLeafEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            super(TypedLeafEncoder, self).default(obj)
        except TypeError:
            try:
                return obj.json()
            except AttributeError:
                return None

class File():
    @classmethod
    def from_spec(cls,spec):
        return cls(**spec)

    def json(self):
        return {
            '$type': 'File',
            'public_path': self.public_path,
            'local_path': self.local_path,
            'checksum': self.checksum
        }

    def __init__(self,public_path, local_path, checksum):
        self.local_path = local_path
        self.public_path = public_path
        self.checksum = checksum

    def __repr__(self):
        return '<File: {} from: {}>'.format(self.local_path,self.public_path)

    def __str__(self):
        return self.local_path

# def typeloader(identifiers, spec):
#     if spec.pop('$type',None) == 'File': return str(File.from_spec(spec))
#     return None

def typeloader(identifiers, spec):
    if spec.pop('$type',None) == 'File': return repr(File.from_spec(spec))
    return None

data = {
    'some': {
        'deep': 'structure',
        'anobject': {
            '$type': 'File',
            'path': '/some/other/path',
            'checksum': '0123234134nsa039',
        },
        'with': [
            {
                'a': {
                    '$type': 'File',
                    'path': 1.0,
                    'checksum': '0123234134nsa039'
                },
                'nested': {
                    '$type': 'File',
                    'path': 'here',
                    'checksum': '0123234134nsa039'
                },
                'b': {
                    '$type': 'File',
                    'path': 1.0,
                    'checksum': '0123234134nsa039'
                }
            }
        ]
    }
}


import yadageschemas
import os
import logging

inputdata = {
 'inputfile': {
    '$type': 'File',
    'local_path': '/inputs/input001.dat',
    'public_path': '/Users/lukas/Code/yadagedev/typedleafs/objectstore/public0001.dat',
    'checksum': 'okcool'
 },
 'outputfile': {
    '$type': 'File',
    'local_path': '/outputs/output001.dat',
    'public_path': '/Users/lukas/Code/yadagedev/typedleafs/objectstore/public0002.dat',
    'checksum': 'okcool'
 },
 'message': 'this is a message to the world:'
}

input_objects = []
inputdata = json.loads(json.dumps(inputdata), cls = TypedLeafDecoder,
            type_identifiers = ['$type'],
            type_loader = typeloader,
            obj_store = input_objects
)
print inputdata
raise RuntimeError('..ok..')
logging.basicConfig(level = logging.INFO)
pack = yadageschemas.load('exposing_transform.yml',os.getcwd(),'packtivity/packtivity-schema')

proc = pack['process']
script = proc['script'].format(**inputdata)
env = pack['environment']

mounts = []
for obj in input_objects:
    mounts.append('{}:{}'.format(obj.public_path, obj.local_path))
    if obj.local_path.startswith('/outputs'):
        open(obj.public_path,'w').close() #touch file

dockercmd = 'docker run --rm -i '
for mount in mounts:
    dockercmd += '-v {} '.format(mount)
dockercmd += '{}:{} {}'.format(env['image'],env['imagetag'],proc['interpreter'])

print(script)
print(dockercmd)
p = subprocess.Popen(shlex.split(dockercmd), stdin = subprocess.PIPE)
p.communicate(script)
