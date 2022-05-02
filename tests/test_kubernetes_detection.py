from unittest import mock

import pytest
from opentelemetry.sdk.resources import Resource

from opentelemetry_resourcedetector_kubernetes import (
    Attributes,
    KubernetesResourceDetector,
)


@pytest.fixture(scope='module')
def pod_uid():
    return '345781c1-c512-4bc4-9667-f0cf07848486'


@pytest.fixture(scope='module')
def container_id():
    return 'ca0ff160f5136a5929d56cdbed62fac14073edda70452c3001a31fa7917ff15d'


@pytest.fixture(scope='module')
def kubernetes_cgroups(pod_uid, container_id):
    # observed on a k3s cluster running v1.23.5+k3s1
    cgroup_lines = [
        f'12:blkio:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        f'11:perf_event:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        f'10:devices:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        f'9:pids:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        f'8:cpuset:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        f'7:freezer:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        f'6:net_cls,net_prio:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        f'5:memory:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        f'4:cpu,cpuacct:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        f'3:hugetlb:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        '2:rdma:/',
        f'1:name=systemd:/kubepods/besteffort/pod{pod_uid}/{container_id}',
        '0::/system.slice/k3s-agent.service',
    ]
    opened = mock.mock_open(read_data='\n'.join(cgroup_lines))
    with mock.patch('builtins.open', opened) as mock_file:
        yield mock_file


def test_getting_ids(kubernetes_cgroups, pod_uid, container_id):
    detector = KubernetesResourceDetector()
    assert detector.pod_uid() == pod_uid
    assert detector.container_id() == container_id


def test_detecting_within_kubernetes(kubernetes_cgroups):
    assert KubernetesResourceDetector().running_in_kubernetes()


@pytest.fixture(scope='module')
def resource(kubernetes_cgroups) -> Resource:
    return KubernetesResourceDetector().detect()


@pytest.fixture(scope='module')
def attributes(resource: Resource) -> Attributes:
    return dict(resource.attributes)


def test_container_id(attributes, container_id):
    assert attributes['container.id'] == container_id


def test_container_runtime(attributes):
    assert attributes['container.runtime'] == 'kubernetes'


def test_pod_uid(attributes, pod_uid):
    assert attributes['k8s.pod.uid'] == pod_uid
