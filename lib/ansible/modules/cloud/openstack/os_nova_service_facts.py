#!/usr/bin/python
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: os_nova_service_facts
short_description: Retrieve facts about one or more Nova services.
version_added: "2.8"
author: "Skyler Hardy (@sdhardy)"
description:
    - Retrieve facts about one or more Nova services.
requirements:
    - "python >= 2.7"
    - "openstacksdk"
options:
    id:
      description:
        - ID of the nova service.
      required: false
    filters:
      description:
        - A dictionary of meta data to use for filtering services.
      required: false
    availability_zone:
      description:
        - Ignored. Present for backwards compatibility
      required: false
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
# Gather facts about all nova services
- os_nova_service_facts:
- debug:
    var: openstack_nova_services

# Gather facts about a nova service by id
- os_nova_service_facts:
    id: 1
- debug:
    var: openstack_nova_services

# Gather facts about nova services with a state of down and status of enabled
- os_nova_service_facts:
    filters:
      state: down
      status: enabled
- debug:
    var: openstack_nova_services
'''

RETURN = '''
openstack_nova_services:
    description: has all the openstack facts about nova services
    returned: always, but can be null
    type: complex
    contains:
        id:
            description: Unique ID
            returned: success
            type: str
        status:
            description: Whether the service is enabled or disabled
            returned: success
            type: str
        state:
            description: The current state of the service (up, down)
            returned: success
            type: str
        disabled_reason:
            description: The reason the service is disabled.
            returned: success
            type: str
        binary:
            description: Name of the service (nova-compute, nova-scheduler, etc)
            returned: success
            type: str
        host:
            description: The host the service resides on.
            returned: success
            type: str
        zone:
            description: The zone for the service (internal, nova, etc)
            returned: success
            type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module


def filter_services(services, filters):
    for key, value in filters.iteritems():
        for service in [x for x in services if x[key] != value]:
            services.remove(service)
    return services

def fetch_services(c):
    results = []
    for service in c.compute.services():
        results.append({
            'id': service.id,
            'binary': service.binary,
            'host': service.host,
            'zone': service.zone,
            'status': service.status,
            'state': service.state,
            'disabled_reason': service.disables_reason
        })
    return results

def main():

    argument_spec = openstack_full_argument_spec(
        id=dict(required=False, type=int, default=None),
        filters=dict(required=False, type=dict, default=None),
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

        if id:
            services = filter_services(fetch_services(cloud), {'id': id})
        elif filters:
            services = filter_services(fetch_services(cloud), filters)
        else:
            services = fetch_services(cloud)
        
        module.exit_json(changed=False, ansible_facts=dict(openstack_nova_services=services))

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
