#!/usr/bin/env bash

# TODO(gp): Move all the PATH and PYTHONPATH to the entrypoint.

set -e
source ~/.bash_profile

devops/docker_build/entrypoint/aws_credentials.sh

source devops/docker_build/entrypoint/patch_environment_variables.sh

mount -a || true

# Allow working with files outside a container.
umask 000

./devops/docker_build/test/test_mount_fsx.sh
./devops/docker_build/test/test_mount_s3.sh
./devops/docker_build/test/test_volumes.sh

echo "which python: " $(which python)
echo "check pandas package: " $(python -c "import pandas; print(pandas)")

#echo "PATH=$PATH"
#echo "PYTHONPATH=$PYTHONPATH"
#echo "entrypoint.sh: '$@'"
# TODO(gp): eval seems to be more general, but it creates a new executable.
eval "$@"