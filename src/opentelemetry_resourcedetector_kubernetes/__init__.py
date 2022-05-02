import functools
import re
import sys
from typing import Dict, Tuple, Union

from opentelemetry.sdk.resources import Resource, ResourceDetector
from opentelemetry.semconv.resource import ResourceAttributes

Attributes = Dict[str, Union[str, bool, int, float]]


class NotInKubernetes(Exception):
    pass


class KubernetesResourceDetector(ResourceDetector):
    """Detects OpenTelemetry Resource attributes for a Kubernetes Pod, providing the
    `container.*` and `k8s.*` attributes"""

    cgroup_pattern = re.compile(
        r'\d+:[\w=]+:/kubepods/.+'
        r'/pod(?P<pod_uid>[a-f0-9\-]+)'
        r'/(?P<container_id>[a-f0-9\-]+)'
    )
    cgroup_file = '/proc/self/cgroup'

    @functools.lru_cache(maxsize=1)
    def _pod_and_container_ids(self) -> Tuple[str, str]:
        for line in self.cgroup_lines():
            if match := self.cgroup_pattern.match(line):
                return match.group('pod_uid'), match.group('container_id')
        raise NotInKubernetes()

    def pod_uid(self) -> str:
        return self._pod_and_container_ids()[0]

    def container_id(self) -> str:
        return self._pod_and_container_ids()[1]

    @functools.lru_cache(maxsize=1)
    def cgroup_lines(self):
        with open(self.cgroup_file, 'r', encoding='utf-8') as cgroups:
            return list(cgroups)

    @functools.lru_cache(maxsize=1)
    def running_in_kubernetes(self) -> bool:
        try:
            return bool(self.pod_uid() and self.container_id())
        except FileNotFoundError:
            pass
        except NotInKubernetes:
            pass
        return False

    def detect(self) -> Resource:
        if not self.running_in_kubernetes():
            return Resource.get_empty()

        attributes: Attributes = {
            ResourceAttributes.CONTAINER_RUNTIME: 'kubernetes',
            ResourceAttributes.K8S_POD_UID: self.pod_uid(),
            ResourceAttributes.CONTAINER_ID: self.container_id(),
        }
        return Resource.create(attributes)

        # TODO: more attributes to gather through elevated access or Downward API
        # CONTAINER_NAME = "container.name"
        # CONTAINER_IMAGE_NAME = "container.image.name"
        # CONTAINER_IMAGE_TAG = "container.image.tag"

        # K8S_CLUSTER_NAME = "k8s.cluster.name"
        # K8S_NODE_NAME = "k8s.node.name"
        # K8S_NODE_UID = "k8s.node.uid"
        # K8S_NAMESPACE_NAME = "k8s.namespace.name"
        # K8S_POD_UID = "k8s.pod.uid"
        # K8S_POD_NAME = "k8s.pod.name"
        # K8S_CONTAINER_NAME = "k8s.container.name"
        # K8S_CONTAINER_RESTART_COUNT = "k8s.container.restart_count"
        # K8S_REPLICASET_UID = "k8s.replicaset.uid"
        # K8S_REPLICASET_NAME = "k8s.replicaset.name"
        # K8S_DEPLOYMENT_UID = "k8s.deployment.uid"
        # K8S_DEPLOYMENT_NAME = "k8s.deployment.name"
        # K8S_STATEFULSET_UID = "k8s.statefulset.uid"
        # K8S_STATEFULSET_NAME = "k8s.statefulset.name"
        # K8S_DAEMONSET_UID = "k8s.daemonset.uid"
        # K8S_DAEMONSET_NAME = "k8s.daemonset.name"
        # K8S_JOB_UID = "k8s.job.uid"
        # K8S_JOB_NAME = "k8s.job.name"
        # K8S_CRONJOB_UID = "k8s.cronjob.uid"
        # K8S_CRONJOB_NAME = "k8s.cronjob.name"
