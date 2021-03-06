# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run datastore system tests locally with the datastore emulator.

First makes system calls to spawn the datastore emulator and get
the local environment variables needed for it. Then calls the
datastore system tests.
"""


import os
import subprocess

from gcloud.environment_vars import GCD_DATASET
from gcloud.environment_vars import GCD_HOST
from system_tests.run_system_test import run_module_tests


_START_CMD = ('gcloud', 'beta', 'emulators', 'datastore', 'start')
_ENV_INIT_CMD = ('gcloud', 'beta', 'emulators', 'datastore', 'env-init')
_DATASET_PREFIX = 'export ' + GCD_DATASET + '='
_HOST_LINE_PREFIX = 'export ' + GCD_HOST + '='


def main():
    """Spawn an emulator instance and run the datastore system tests."""
    # Ignore stdin and stdout, don't pollute the user's output with them.
    proc_start = subprocess.Popen(_START_CMD, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    try:
        env_lines = subprocess.check_output(
            _ENV_INIT_CMD).strip().split('\n')
        dataset, = [line.split(_DATASET_PREFIX, 1)[1] for line in env_lines
                    if line.startswith(_DATASET_PREFIX)]
        host, = [line.split(_HOST_LINE_PREFIX, 1)[1] for line in env_lines
                 if line.startswith(_HOST_LINE_PREFIX)]
        # Set environment variables before running the system tests.
        os.environ[GCD_DATASET] = dataset
        os.environ[GCD_HOST] = host
        os.environ['GCLOUD_NO_PRINT'] = 'true'
        run_module_tests('datastore',
                         ignore_requirements=True)
    finally:
        # NOTE: This is mostly defensive. Since ``proc_start`` will be spawned
        #       by this current process, it should be killed when this process
        #       exits whether or not we kill it.
        proc_start.kill()


if __name__ == '__main__':
    main()
