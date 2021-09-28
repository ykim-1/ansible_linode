#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module contains all of the functionality for Linode Domain records."""

from __future__ import absolute_import, division, print_function

# pylint: disable=unused-import
from typing import List, Any, Optional

from linode_api4 import Domain, DomainRecord

from ansible_collections.linode.cloud.plugins.module_utils.linode_common import LinodeModuleBase
from ansible_collections.linode.cloud.plugins.module_utils.linode_helper import create_filter_and, \
    paginated_list_to_json

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'supported_by': 'Linode'
}

DOCUMENTATION = '''
author:
- Luke Murphy (@decentral1se)
- Charles Kenney (@charliekenney23)
- Phillip Campbell (@phillc)
- Lena Garber (@lbgarber)
description:
- Get info about a Linode Domain Records.
module: domain_record_info
options:
  domain:
    description: The name of the parent Domain.
    required: false
    type: str
  domain_id:
    description: The ID of the parent Domain.
    required: false
    type: int
  id:
    description: The unique id of the subdomain.
    required: false
    type: int
  name:
    description: The name of the subdomain.
    required: false
    type: str
requirements:
- python >= 3.0
'''

EXAMPLES = '''
- name: Get info about a domain record by name
  linode.cloud.domain_record_info:
    domain: my-domain.com
    name: my-subdomain

- name: Get info about a domain record by id
  linode.cloud.domain_info:
    domain: my-domain.com
    id: 12345
'''

RETURN = '''
record:
  description: The domain record in JSON serialized form.
  linode_api_docs: "https://www.linode.com/docs/api/domains/#domain-record-view"
  returned: always
  type: dict
  sample: {
   "created":"xxxxx",
   "id":xxxxx,
   "name":"xxxx",
   "port":0,
   "priority":0,
   "protocol":null,
   "service":null,
   "tag":null,
   "target":"127.0.0.1",
   "ttl_sec":3600,
   "type":"A",
   "updated":"xxxxx",
   "weight":55
}
'''

linode_domain_record_info_spec = dict(
    # We need to overwrite attributes to exclude them as requirements
    state=dict(type='str', required=False, doc_hide=True),
    label=dict(type='str', required=False, doc_hide=True),

    domain_id=dict(type='int',
                   description='The ID of the parent Domain.'),
    domain=dict(type='str',
                description='The name of the parent Domain.'),

    id=dict(type='int',
            description='The unique id of the subdomain.'),
    name=dict(type='str',
              description='The name of the subdomain.'),
)

specdoc_meta = dict(
    description=[
        'Get info about a Linode Domain Records.'
    ],
    requirements=[
        'python >= 3.0'
    ],
    author=[
        'Luke Murphy (@decentral1se)',
        'Charles Kenney (@charliekenney23)',
        'Phillip Campbell (@phillc)',
        'Lena Garber (@lbgarber)'
    ],
    spec=linode_domain_record_info_spec
)


class LinodeDomainRecordInfo(LinodeModuleBase):
    """Module for getting info about a Linode Domain record"""

    def __init__(self) -> None:
        self.module_arg_spec = linode_domain_record_info_spec
        self.required_one_of: List[List[str]] = [['domain_id', 'domain'], ['id', 'name']]
        self.results = dict(
            record=None
        )

        super().__init__(module_arg_spec=self.module_arg_spec,
                         required_one_of=self.required_one_of)

    def _get_domain_by_name(self, name: str) -> Optional[Domain]:
        try:
            domain = self.client.domains(Domain.domain == name)[0]
            return domain
        except IndexError:
            return None
        except Exception as exception:
            return self.fail(msg='failed to get domain {0}: {1}'.format(name, exception))

    def _get_domain_from_params(self) -> Optional[Domain]:
        domain_id = self.module.params.get('domain_id')
        domain = self.module.params.get('domain')

        if domain is not None:
            return self._get_domain_by_name(domain)

        if domain_id is not None:
            result = Domain(self.client, domain_id)
            result._api_get()
            return result

        return None

    def _get_record_by_name(self, domain: Domain, name: str) -> Optional[DomainRecord]:
        try:
            for record in domain.records:
                if record.name == name:
                    return record

            return None
        except IndexError:
            return None
        except Exception as exception:
            return self.fail(msg='failed to get domain record {0}: {1}'.format(name, exception))

    def _get_record_from_params(self, domain: Domain) -> Optional[DomainRecord]:
        record_id = self.module.params.get('id')
        record_name = self.module.params.get('name')

        if record_name is not None:
            return self._get_record_by_name(domain, record_name)

        if record_id is not None:
            result = DomainRecord(self.client, record_id, domain.id)
            result._api_get()
            return result

        return None

    def exec_module(self, **kwargs: Any) -> Optional[dict]:
        """Entrypoint for domain record info module"""

        domain = self._get_domain_from_params()
        if domain is None:
            return self.fail('failed to get domain')

        record = self._get_record_from_params(domain)
        if record is None:
            return self.fail('failed to get record')

        self.results['record'] = record._raw_json

        return self.results


def main() -> None:
    """Constructs and calls the Linode Domain Record info module"""
    LinodeDomainRecordInfo()


if __name__ == '__main__':
    main()