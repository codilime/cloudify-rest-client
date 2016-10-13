########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.


class ClusterView(dict):
    def __init__(self, clusterview):
        self.update(clusterview)

    @property
    def initialized(self):
        return self.get('initialized', False)

    @property
    def consul_encryption_key(self):
        try:
            return self['consul']['encryption_key']
        except KeyError:
            return None


class ClusterClient(object):
    def __init__(self, api):
        self.api = api

    def get(self):
        response = self.api.get('/cluster')
        return ClusterView(response['items'][0])

    def start(self, node_name, consul_key, network_interface=None,
              virtual_ip=None):
        return self.api.post('/cluster', data={
            'event': 'start',
            'config': {
                'node_name': node_name,
                'consul_key': consul_key,
                'network_interface': network_interface,
                'virtual_ip': virtual_ip
            }
        })

    def join(self, join_addrs, node_name, consul_key, network_interface=None,
             virtual_ip=None):
        return self.api.post('/cluster', data={
            'event': 'join',
            'config': {
                'node_name': node_name,
                'consul_key': consul_key,
                'network_interface': network_interface,
                'join': join_addrs
            }
        })
