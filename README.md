# opentelemetry-resourcedetector-kubernetes

An OpenTelemetry package to populates Resource attributes for Kubernetes pods.

## Usage

```
from opentelemetry.sdk.resources import get_aggregated_resources
from opentelemetry_resourcedetector_kubernetes import KubernetesResourceDetector

...

resource = get_aggregated_resources([
    KubernetesResourceDetector(),
    SomeOtherResourceDetector()
])

... pass the returned `resource` to a TracerProvder, for example ...
```
