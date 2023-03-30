
cd /workspace
apt update && apt install -y --no-install-recommends \
    wget \
    ninja-build \
    clang \
    python3-dev \
    python3-pip \
    git \
    npm \
    libcudnn8 \
    libcudnn8-dev \
 && rm -rf /var/lib/apt/lists/*

npm install -g @bazel/bazelisk
python3 -mpip install --upgrade pip && pip3 install numpy pybind11

# Install a proper version of cmake.
cmake_ver=3.25.2 && \
    cmake_installer=cmake-${cmake_ver}-linux-x86_64.sh && \
    wget https://github.com/Kitware/CMake/releases/download/v${cmake_ver}/${cmake_installer}  && \
    chmod +x ${cmake_installer} && \
    ./${cmake_installer} --skip-license --prefix=/usr && \
    rm ${cmake_installer}

# Build source.

export CMAKE_BUILD_TYPE=RelWithDebInfo
git clone https://github.com/iree-org/iree.git
cd /workspace/iree
git submodule update --init
# Clang is finicky when it comes to TF. RUN CXX=clang++ CC=clang python3 configure_bazel.py
CXX=g++ CC=gcc python3 configure_bazel.py
cmake -GNinja -B /opt/iree -S . -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE} -DIREE_ENABLE_ASSERTIONS=ON -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DIREE_ENABLE_LLD=OFF -DIREE_BUILD_PYTHON_BINDINGS=ON -DIREE_TARGET_BACKEND_CUDA=ON -DIREE_HAL_DRIVER_CUDA=ON -DPython3_EXECUTABLE=`which python3`
cmake --build /opt/iree

cd /workspace/iree/integrations/tensorflow
bazelisk --output_user_root $HOME/.cache/bazel/_bazel_${USER}/iree build //iree_tf_compiler:importer-binaries
bash symlink_binaries.sh
pip3 install -e python_projects/iree_tf/




