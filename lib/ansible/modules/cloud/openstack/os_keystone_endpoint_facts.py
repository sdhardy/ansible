#!/usr/bin/python
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: os_keystone_endpoint_facts
short_description: Retrieve facts about one or more OpenStack endpoints
version_added: "2.8"
author: "Skyler Hardy (@sdhardy)"
description:
    - Retrieve facts about one or more OpenStack endpoints.
requirements:
    - "python >= 2.7"
    - "openstacksdk"
options:
    id:
      description:
        - ID of the endpoint
      required: false
    filters:
      description:
        - A dictionary of meta data to use for further filtering.  Elements of
          this dictionary may be additional dictionaries.
      required: false
    include_services:
      description:
        - Boolean option to include keystone service data
      required: false
    availability_zone:
      description:
        - Ignored. Present for backwards compatibility
      required: false
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
# Gather facts about an endpoint
- os_keystone_endpoint_facts:
    id: endpoint_id
- debug:
    var: openstack_endpoints

# Gather facts about all endpoints
- os_keystone_endpoint_facts:
- debug:
    var: openstack_endpoints

# Gather facts about all enabled endpoints with the network service type
- os_keystone_endpoint_facts:
    filters:
      enabled: true
      service: network
- debug:
    var: openstack_endpoints
'''

RETURN = '''
openstack_endpoints:
    description: has all the openstack facts about endpoints
    returned: always, but can be null
    type: complex
    contains:
        id:
            description: Unique UUID
            returned: success
            type: str
        enabled:
            description: True endpoint is enabled
            returned: success
            type: bool
        interface:
            description: Endpoint interface type (admin, public or internal)
            returned: success
            type: str
        region:
            description: Region name associated with the endpoint
            returned: success
            type: str
        region_id:
            description: Region ID associated with the endpoint
            returned: success
            type: str
        service_id:
            description: Service ID associated with the endpoint
            returnred: success
            type: str
        url:
            description: URL for the endpoint
            returned: success
            type: str
        service_name:
            description: Name of the service (nova, neutron, cinder, etc). Only if include_services is true
            returned: success
            type: str
        service_type:
            description: Service type (compute, image, identity, volume, etc). Only if include_services is true
            returned: success
            type: str
        service_description:
            description: Description of the service. Only if include_services is true.
            type: str
        service_enabled:
            description: True if the service is enabled. Only if include_services is true.
            type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module


def main():

    argument_spec = openstack_full_argument_spec(
        id=dict(required=False, aliases=['name'], default=None),
        filters=dict(required=False, type='dict', default=None),
        include_services=dict(type=bool)
    )
    module_kwargs = openstack_module_kwargs(
        mutually_exclusive=[
            ['id', 'filters'],
        ]
    )
    module = AnsibleModule(argument_spec, **module_kwargs)
    sdk, cloud = openstack_cloud_from_module(module)
    try:
        id = module.params['id']
        filters = module.params['filters']
        include = module.params['include_services']
        endpoints = []
        services = []

        if id:
            endpoints.append(cloud.get_endpoint(id))
        elif filters:
            if include and 'service' in filters:
                # Assume ID or Name is given
                services = cloud.search_services(filters['service'])
                if len(services) == 0:
                    # Otherwise attempt to search by type
                    services = cloud.search_services(filters={'type': filters['service']})
                # remove service from filters
                filters.pop('service')
                # If we found a service, use it's ID as a filter for the endpoint search
                if len(services) > 0:
                    filters['service_id'] = services[0].id
            # finally search for endpoints using our filters
            endpoints = cloud.search_endpoints(filters=filters)
        else:
            # list all endpoints if no id or filter was given
            endpoints = cloud.list_endpoints()

        if include:
            if len(endpoints) >= 1:
                if len(services) == 0:
                    # Rather than make a request for each endpoint in
                    # our list, use a single request to get them all
                    services = cloud.list_services()
                for endpoint in endpoints:
                    # Grab the service data by service_id
                    si = next((index for (index, d) in enumerate(services) 
                        if d['id'] == endpoint.service_id), None)
                    endpoint.service_name = services[si].name
                    endpoint.service_type = services[si].type
                    endpoint.service_enabled = services[si].enabled
                    endpoint.service_description = services[si].description

        module.exit_json(changed=False, ansible_facts=dict(openstack_endpoints=endpoints))

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
