from kubernetes import client,config
from packtivity.asyncbackends import PacktivityProxyBase
from packtivity.syncbackends import packconfig, build_job, publish
from packtivity.statecontexts import load_state
import logging
import uuid
import os

log = logging.getLogger(__name__)

class KubeProxy(PacktivityProxyBase):
    def __init__(self, job_id, spec, pars, state):
        self.job_id = job_id
        self.spec = spec
        self.pars = pars
        self.state = state

    def proxyname(self):
        return 'KubeProxy'

    def details(self):
        return {
            'job_id': self.job_id,
            'spec': self.spec,
            'pars':self.pars,
            'state':self.state.json()
        }

    @classmethod
    def fromJSON(cls,data):
        return cls(
            data['proxydetails']['job_id'],
            data['proxydetails']['spec'],
            data['proxydetails']['pars'],
            load_state(data['proxydetails']['state'])
        )

class KubeBackend(object):
    def __init__(self,kubeconfigloc = None):
        config.load_kube_config(kubeconfigloc or os.path.join(os.environ['HOME'],'.kube/config'))
        self.config = packconfig()

    def prepublish(self, spec, parameters, state):
        return None

    def submit(self, spec, parameters, state, metadata = None):
        job = build_job(spec['process'], parameters, self.config)

        image   = spec['environment']['image']
        tag     = spec['environment']['imagetag']

        interpreter = 'sh' if 'command' in job else job['interpreter']
        script = job['command'] if 'command' in job else job['script']
        jobspec = job_spec(interpreter, script, image, tag, state)

        jobid = jobspec['metadata']['name']
        
        thejob = client.V1Job(
            api_version = jobspec['apiVersion'],
            kind = jobspec['kind'],
            metadata = jobspec['metadata'],
            spec = jobspec['spec']
        )

        client.BatchV1Api().create_namespaced_job('default',thejob)                                                               

        log.info('submitted job: %s', jobid)
        return KubeProxy(
            job_id = jobid,
            spec = spec,
            pars = parameters,
            state = state
        )

    def result(self, resultproxy):
        return publish(
            resultproxy.spec['publisher'],
            resultproxy.pars, resultproxy.state, self.config
        )

    def ready(self, resultproxy):
        jobstatus = client.BatchV1Api().read_namespaced_job(resultproxy.job_id,'default').status
        return jobstatus.failed or jobstatus.succeeded

    def successful(self, resultproxy):
        jobstatus = client.BatchV1Api().read_namespaced_job(resultproxy.job_id,'default').status
        return jobstatus.succeeded

    def fail_info(self, resultproxy):
        pass


def state_binds(state):
    container_mounts = []
    volumes = []

    for i,path in enumerate(state.readwrite + state.readonly):
        container_mounts.append({
            "name": "state{}".format(i),
            "mountPath": path
        })
        volumes.append({
            "name": "state{}".format(i),
            "hostPath": {
                "path": path
            }
        })
    return container_mounts, volumes    


def job_spec(interpreter,script,image,imagetag,state):
    wrapped_script = '''cat << EOF | {interpreter}\n{script}\nEOF'''.format(
        interpreter = interpreter,
        script = script)

    job_uuid = str(uuid.uuid4())

    container_mounts, volumes = state_binds(state)

    spec = {
      "apiVersion": "batch/v1",
      "kind": "Job",
      "spec": {
        "template": {
          "spec": {
            "restartPolicy": "Never",
            "containers": [
              {
                "image": ':'.join([image,imagetag]),
                "command": [
                  "sh",
                  "-c",
                  wrapped_script
                ],
                "volumeMounts": container_mounts,
                "name": job_uuid
              }
            ],
            "volumes": volumes
          },
          "metadata": {
            "name": job_uuid
          }
        }
      },
      "metadata": {
        "name": job_uuid
      }
    }
    return spec
