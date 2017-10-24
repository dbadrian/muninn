#!/usr/bin/zsh

checkout_latest_tag() {
    # from: https://stackoverflow.com/a/22857288
    # Get new tags from remote
    git fetch --tags

    # Get latest tag name
    latestTag=$(git describe --tags `git rev-list --tags --max-count=1`)

    # Checkout latest tag
    git checkout $latestTag
}

export_bazel_options() {
    # Set appropriate parameters to automate the configure process
    export CC_OPT_FLAGS="-march=native"
    export PYTHON_BIN_PATH=$(which python)
    export PYTHON_LIB_PATH=$(python -c 'import site; print("\\n".join(site.getsitepackages()))')
    export TF_NEED_JEMALLOC=1
    export TF_NEED_GCP=0
    export TF_NEED_HDFS=0
    export TF_ENABLE_XLA=1
    export TF_NEED_GDR=0
    export TF_NEED_VERBS=0
    export TF_NEED_OPENCL=0
    export TF_NEED_MPI=0
    export TF_NEED_S3=0
    export TF_NEED_CUDA=1
    export GCC_HOST_COMPILER_PATH=/usr/bin/gcc-6
    export TF_CUDA_CLANG=0
    export CUDA_TOOLKIT_PATH=/opt/cuda
    export TF_CUDA_VERSION=$($CUDA_TOOLKIT_PATH/bin/nvcc --version | sed -n 's/^.*release \(.*\),.*/\1/p')
    export CUDNN_INSTALL_PATH=/opt/cuda
    export TF_CUDNN_VERSION=$(sed -n 's/^#define CUDNN_MAJOR\s*\(.*\).*/\1/p' $CUDNN_INSTALL_PATH/include/cudnn.h)
    export TF_CUDA_COMPUTE_CAPABILITIES=5.2 #comma separated list otherwise
}

build_tensorflow() {
    ./configure
    bazel build -c opt --config=mkl --copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-mfpmath=both --copt=-msse4.2 --config=cuda //tensorflow/tools/pip_package:build_pip_package
    bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg
}

# Change to tmp dir as defined by cmd arg 1
git clone https://github.com/tensorflow/tensorflow $1
cd $1
source deactivate
checkout_latest_tag
export_bazel_options
build_tensorflow
pip install --upgrade /tmp/tensorflow_pkg/tensorflow-*.whl
source activate muninn