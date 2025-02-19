"""Cloud provision interface.

This module provides a standard low-level interface that all
providers supported by SkyPilot need to follow.
"""
import functools
import importlib
import inspect
from typing import Any, Dict, List, Optional

from sky import sky_logging
from sky import status_lib
from sky.provision import common

logger = sky_logging.init_logger(__name__)


def _route_to_cloud_impl(func):

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        # check the signature to fail early
        inspect.signature(func).bind(*args, **kwargs)
        if args:
            provider_name = args[0]
            args = args[1:]
        else:
            provider_name = kwargs.pop('provider_name')

        module_name = provider_name
        module = importlib.import_module(f'sky.provision.{module_name.lower()}')

        impl = getattr(module, func.__name__)
        return impl(*args, **kwargs)

    return _wrapper


# pylint: disable=unused-argument


@_route_to_cloud_impl
def query_instances(
    provider_name: str,
    cluster_name_on_cloud: str,
    provider_config: Optional[Dict[str, Any]] = None,
    non_terminated_only: bool = True,
) -> Dict[str, Optional[status_lib.ClusterStatus]]:
    """Query instances.

    Returns a dictionary of instance IDs and status.

    A None status means the instance is marked as "terminated"
    or "terminating".
    """
    raise NotImplementedError


@_route_to_cloud_impl
def bootstrap_instances(
        provider_name: str, region: str, cluster_name: str,
        config: common.ProvisionConfig) -> common.ProvisionConfig:
    """Bootstrap configurations for a cluster.

    This function sets up auxiliary resources for a specified cluster
    with the provided configuration,
    and returns an InstanceConfig object with updated configuration.
    These auxiliary resources could include security policies, network
    configurations etc. These resources tend to be free or very cheap,
    but it takes time to set them up from scratch. So we generally
    cache or reuse them when possible.
    """
    raise NotImplementedError


@_route_to_cloud_impl
def run_instances(provider_name: str, region: str, cluster_name: str,
                  config: common.ProvisionConfig) -> common.ProvisionRecord:
    """Start instances with bootstrapped configuration."""
    raise NotImplementedError


@_route_to_cloud_impl
def stop_instances(
    provider_name: str,
    cluster_name_on_cloud: str,
    provider_config: Optional[Dict[str, Any]] = None,
    worker_only: bool = False,
) -> None:
    """Stop running instances."""
    raise NotImplementedError


@_route_to_cloud_impl
def terminate_instances(
    provider_name: str,
    cluster_name_on_cloud: str,
    provider_config: Optional[Dict[str, Any]] = None,
    worker_only: bool = False,
) -> None:
    """Terminate running or stopped instances."""
    raise NotImplementedError


@_route_to_cloud_impl
def open_ports(
    provider_name: str,
    cluster_name_on_cloud: str,
    ports: List[str],
    provider_config: Optional[Dict[str, Any]] = None,
) -> None:
    """Open ports for inbound traffic."""
    raise NotImplementedError


@_route_to_cloud_impl
def cleanup_ports(
    provider_name: str,
    cluster_name_on_cloud: str,
    provider_config: Optional[Dict[str, Any]] = None,
) -> None:
    """Delete any opened ports."""


@_route_to_cloud_impl
def wait_instances(provider_name: str, region: str, cluster_name: str,
                   state: Optional[status_lib.ClusterStatus]) -> None:
    """Wait instances until they ends up in the given state."""
    raise NotImplementedError


@_route_to_cloud_impl
def get_cluster_info(provider_name: str, region: str,
                     cluster_name: str) -> common.ClusterInfo:
    """Get the metadata of instances in a cluster."""
    raise NotImplementedError
