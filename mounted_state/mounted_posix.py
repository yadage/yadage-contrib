import hashlib
import itertools
import os
import shutil
import json
import logging
import checksumdir
import yaml
import packtivity.utils as utils
log = logging.getLogger(__name__)

class MountedFSState(object):
    '''
    Local Filesyste State consisting of a number of readwrite and readonly directories
    '''
    def __init__(self,readwrite = None,readonly = None, dependencies = None, identifier = 'unidentified_state', mountspec = None):
        self._identifier = identifier
        self.readwrite = list(readwrite if readwrite else  [])
        self.readonly  = list(readonly if readonly else  [])
        self.dependencies = dependencies or []
        self.mountspec = mountspec

    @property
    def metadir(self):
        return '{}/_packtivity'.format(self.readwrite[0])

    def identifier(self):
        return self._identifier

    def add_dependency(self,depstate):
        pass

    def reset(self):
        raise NotImplementedError('reset not implemented')

    def state_hash(self):
        raise NotImplementedError('hash not implemented')

    def contextualize_data(self,data):
        '''
        contextualizes string data by string interpolation.
        replaces '{workdir}' placeholder with first readwrite directory
        '''
        try: 
            workdir = self.readwrite[0]
            return data.format(workdir = workdir)
        except AttributeError:
            return data


    def json(self):
        return {
            'state_type': 'mountedfs',
            'identifier': self.identifier(),
            'readwrite':  self.readwrite,
            'readonly':   self.readonly,
            'dependencies': [x.json() for x in self.dependencies],
            'mountspec':  self.mountspec

        }

    @classmethod
    def fromJSON(cls,jsondata):
        return cls(
            readwrite    = jsondata['readwrite'],
            readonly     = jsondata['readonly'],
            identifier   = jsondata['identifier'],
            dependencies = [MountedFSState.fromJSON(x) for x in jsondata['dependencies']],
            mountspec    = jsondata['mountspec']
        )

def _merge_states(lhs,rhs):
    return MountedFSState(lhs.readwrite + rhs.readwrite,lhs.readonly + rhs.readonly, mountspec = lhs.mountspec)

class MountedFSProvider(object):
    def __init__(self, mountspec, *base_states, **kwargs):
        self.mountspec = mountspec
        base_states = list(base_states)
        self.nest = kwargs.get('nest', True)

        first = base_states.pop()
        assert first

        self.base = first

        while base_states:
            next_state = base_states.pop()
            if not next_state:
                continue
            self.base = _merge_states(self.base,next_state)

    def new_provider(self,name):
        new_base_ro = self.base.readwrite + self.base.readonly
        new_base_rw = [os.path.join(self.base.readwrite[0],name)]
        return MountedFSProvider(self.mountspec,MountedFSState(new_base_rw,new_base_ro, mountspec = self.mountspec), nest = self.nest)


    def new_state(self,name):
        '''
        creates a new context from an existing context.

        if subdir is True it declares a new read-write nested under the old
        context's read-write and adds all read-write and read-only locations
        of the old context as read-only. This is recommended as it makes rolling
        back changes to the global state made in this context easy.

        else the same readwrite/readonly configuration as the parent context is used

        '''

        if self.base is None:
            new_readwrites = [os.path.abspath(name)]
        else:
            new_readwrites = ['{}/{}'.format(self.base.readwrite[0],name)] if self.nest else self.base.readwrite

        if self.nest:
            # for nested directories, we want to have at lease read access to all data in parent context
            new_readonlies = [ro for ro in itertools.chain(self.base.readonly,self.base.readwrite)] if self.base else []
        else:
            new_readonlies = self.base.readonly if self.base else []

        log.debug('new context is: rw: %s, ro: ', new_readwrites, new_readonlies)
        new_identifier = name.replace('/','_') # replace in case name is nested path
        newstate = MountedFSState(readwrite = new_readwrites, readonly = new_readonlies, identifier = new_identifier, mountspec = self.mountspec)

        return newstate

    def json(self):
        return {
            'state_provider_type': 'mountedfs_provider',
            'base_state': self.base.json(),
            'nest': self.nest,
            'mountspec': self.mountspec
        }

    @classmethod
    def fromJSON(cls,jsondata):
        return cls(MountedFSState.fromJSON(jsondata['mountspec'],jsondata['base_state']), nest = jsondata['nest'])

def setup_provider(dataarg,dataopts):
    mountspec = dataopts.get('mountspec',None)
    if mountspec:
        mountspec = yaml.load(open(mountspec))
    return MountedFSProvider(mountspec, MountedFSState([os.path.join('/',dataarg)]))
