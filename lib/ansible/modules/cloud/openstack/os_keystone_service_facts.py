#!/usr/bin/python

#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: os_keystone_service_facts
short_description: Retrieve facts about one or more OpenStack services
version_added: "2.7"
author: "Skyler Hardy (@sdhardy)"
description:
    - Retrieve facts about one or more OpenStack services.
requirements:
    - "python >= 2.7"
    - "openstacksdk"
options:
    service:
      description:
        - Name or id of the service.
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
- debug:
    var: openstack_services
'''

RETURN = '''
openstack_services:
    description: has all the openstack facts about services
    returned: always, but can be null
    type: complex
    contains:
        id:
            description: Unique UUID
            returned: success
            type: str
        enabled:
            description: Whether the service is enabled
            returned: success
            type: bool 
        name:
            description: Name of the service (nova, neutron, cinder, etc)
            returned: success
            type: str
        type:
            description: Service type (compute, image, identity, volume, etc)
            returned: success
            type: str
        description:
            description: Description of the service
            type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_cloud_from_module

def main():

    argument_spec = openstack_full_argument_spec(
        service=dict(required=False, default=None),
        filters=dict(required=False, type='dict', default=None),
    )

    module = AnsibleModule(argument_spec)
    sdk, cloud = openstack_cloud_from_module(module)
    try:
        service = module.params['service']
        filters = module.params['filters']

        if service:
            services = cloud.search_services(service)
        elif filters:
            services = cloud.search_services(filters=filters)
        else:
            services = cloud.list_services()

        module.exit_json(changed=False,ansible_facts=dict(openstack_services=services))

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()
