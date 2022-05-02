from unittest import mock

import pytest
from opentelemetry.sdk.resources import Resource

from opentelemetry_resourcedetector_kubernetes import KubernetesResourceDetector


@pytest.fixture
def non_kubernetes_cgroups():
    # observed on an Ubuntu laptop, with some tweaks for brevity
    cgroup_lines = [
        '12:memory:/user.slice/user-1000.slice/user@1000.service'
        '11:blkio:/user.slice'
        '10:perf_event:/'
        '9:cpuset:/'
        '8:hugetlb:/'
        '7:freezer:/'
        '6:cpu,cpuacct:/user.slice'
        '5:devices:/user.slice'
        '4:rdma:/'
        '3:pids:/user.slice/user-1000.slice/user@1000.service'
        '2:net_cls,net_prio:/'
        '1:name=systemd:/user.slice/user-1000.slice/user@1000.service/blah-blah-blah'
        '0::/user.slice/user-1000.slice/user@1000.service/apps.slice/blah-blah-blah'
    ]
    opened = mock.mock_open(read_data='\n'.join(cgroup_lines))
    with mock.patch('builtins.open', opened) as mock_file:
        yield mock_file


def test_detecting_in_cgroup_outside_kubernetes(non_kubernetes_cgroups):
    assert not KubernetesResourceDetector().running_in_kubernetes()


def test_in_group_outside_kubernetes_returns_empty_resource(non_kubernetes_cgroups):
    assert KubernetesResourceDetector().detect() == Resource.get_empty()


@pytest.fixture
def no_cgroup():
    with mock.patch('builtins.open', side_effect=FileNotFoundError) as mock_file:
        yield mock_file


def test_detecting_outside_of_cgroup(no_cgroup):
    assert not KubernetesResourceDetector().running_in_kubernetes()


def test_outside_of_cgroup_returns_empty_resource(no_cgroup):
    assert KubernetesResourceDetector().detect() == Resource.get_empty()
