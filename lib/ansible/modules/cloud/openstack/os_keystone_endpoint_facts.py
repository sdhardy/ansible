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
version_added: "2.7"
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

# Gather facts about all public enabled endpoints
- os_keystone_endpoint_facts:
    filters:
      interface: admin
      enabled: true
- debug:
    var: openstack_endpoints

# Gather facts about all endpoints
- os_keystone_endpoint_facts:

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
            description: Whether the endpoint is enabled or not
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
            description: Region UUID associated with the endpoint
            returned: success
            type: str
        service_id:
            description: Service UUID associated with the endpoint
            returnred: success
            type: str
        service_name:
            description: Name of the service (nova, neutron, cinder, etc)
            returned: success
            type: str
        service_type:
            description: Service type (compute, image, identity, volume, etc)
            returned: success
            type: str
        service_description:
            description: Description of the service
            type: str
        url:
            description: URL for the endpoint
            returned: success
            type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_cloud_from_module

def main():

    argument_spec = openstack_full_argument_spec(
        id=dict(required=False, default=None),
        filters=dict(required=False, type='dict', default=None),
    )

    module = AnsibleModule(argument_spec)
    sdk, cloud = openstack_cloud_from_module(module)
    try:
        id = module.params['id']
        filters = module.params['filters']

        if id:
            endpoints = cloud.get_endpoint(id)
        elif filters:
            endpoints = cloud.search_endpoints(filters=filters)
        else:
            endpoints = cloud.list_endpoints()

        if isinstance(endpoints, list):
            for endpoint in endpoints:
                service = cloud.get_service(endpoint.service_id)
                endpoint.service_name = service.name
                endpoint.service_type = service.type
                endpoint.service_description = service.description
        else:
            service = cloud.get_service(endpoints.service_id)
            endpoints.service_name = service.name
            endpoints.service_type = service.type
            endpoints.service_description = service.description

        module.exit_json(changed=False,ansible_facts=dict(openstack_endpoints=endpoints))
   
    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
