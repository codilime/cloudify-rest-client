########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
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

import os
import urlparse
import contextlib

from cloudify_rest_client import bytes_stream_utils


class Snapshot(dict):
    """
    Cloudify snapshot.
    """

    def __init__(self, snapshot):
        self.update(snapshot)

    @property
    def id(self):
        """
        :return: The identifier of the snapshot.
        """
        return self.get('id')

    @property
    def created_at(self):
        """
        :return: Timestamp of snapshot creation.
        """
        return self.get('created_at')


class SnapshotsClient(object):
    """
    Cloudify's snapshot management client.
    """

    def __init__(self, api):
        self.api = api

    def list(self, _include=None):
        """
        Returns a list of currently stored snapshots.

        :param _include: List of fields to include in responce.
        :return: Snapshots list.
        """
        response = self.api.get('/snapshots', _include=_include)
        return [Snapshot(item) for item in response]

    def create(self, snapshot_id):
        """
        Creates a new snapshot.

        :param snapshot_id: Snapshot id of the new created deployment.
        :return: The created snapshot.
        """
        assert snapshot_id
        uri = '/snapshots/{0}'.format(snapshot_id)
        response = self.api.put(uri, expected_status_code=201)
        return Snapshot(response)

    def delete(self, snapshot_id):
        """
        Deletes the snapshot whose id matches the provided snapshot id.

        :param snapshot_id: The id of the snapshot to be deleted.
        :return: Deleted snapshot.
        """
        assert snapshot_id
        response = self.api.delete('/snapshots/{0}'.format(snapshot_id))
        return Snapshot(response)

    def restore(self, snapshot_id):
        """
        Restores the snapshot whose id matches the provided snapshot id.

        :param snapshot_id: The id of the snapshot to be restored.
        """
        assert snapshot_id
        uri = '/snapshots/{0}'.format(snapshot_id)
        self.api.post(uri, expected_status_code=201)

    def upload(self, snapshot_path, snapshot_id):
        """
        Uploads snapshot archive to Cloudify's manager.

        :param snapshot_path: Path to snapshot archive.
        :param snapshot_id: Id of the uploaded snapshot.
        :return: Uploaded snapshot.

        Snapshot archive should be this which was created and downloaded
        from Cloudify's manager in process of create snapshot / download
        snapshot commands.
        """
        assert snapshot_path
        assert snapshot_id

        uri = '/snapshots/{0}/upload'.format(snapshot_id)
        query_params = {}

        if urlparse.urlparse(snapshot_path).scheme and \
                not os.path.exists(snapshot_path):
            query_params['snapshot_archive_url'] = snapshot_path
            data = None
        else:
            data = bytes_stream_utils.request_data_file_stream_gen(
                snapshot_path)

        response = self.api.put(uri, params=query_params, data=data,
                                expected_status_code=201)
        return Snapshot(response)

    def download(self, snapshot_id, output_file):
        """
        Downloads a previously created/uploaded snapshot archive from
        Cloudify's manager.

        :param snapshot_id: The id of the snapshot to be downloaded.
        :param output_file: The file path of the downloaded snapshot file
         (optional)
        :return: The file path of the downloaded snapshot.
        """
        uri = '/snapshots/{0}/download'.format(snapshot_id)

        with contextlib.closing(self.api.get(uri, stream=True)) as response:
            output_file = bytes_stream_utils.write_response_stream_to_file(
                response, output_file)

            return output_file