## Jetson Nano Setup for ADS

### Installation Step (v06172021)

---

1. Write the Jetson Nano image to the SD Card
- Follow the guide here: [Getting Started With Jetson Nano Developer Kit | NVIDIA Developer](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit)
2. Update and upgrade the base OS
- ```bash
  sudo apt update
  sudo apt upgrade
  ```
3. Expand swap memory size
- ```bash
  git clone https://github.com/JetsonHacksNano/resizeSwapMemory
  cd resizeSwapMemory
  
  # set swap to 8GB (For 4GB Jetson Nano version)
  ./setSwapMemorySize.sh -g 8 
  ```
4. Install Python 3.8, and Compile OpenCV with CUDA support using the Script below
   
   - Save the following as `filename.sh` and run with `sudo` permission 
     
     ```bash
     echo "** Remove other OpenCV first"
     sudo sudo apt-get purge *libopencv*
     
     echo "** Install requirement"
     sudo apt-get update
     sudo apt-get install -y build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
     sudo apt-get install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
     sudo apt install -y python3.8 python3.8-dev
     sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
     sudo update-alternatives --config python3
     sudo apt install -y python3-pip
     sudo -H python3.8 -m pip uninstall numpy
     sudo apt purge python3-numpy
     sudo -H python3.8 -m pip install --upgrade pip
     sudo apt-get install -y python3-numpy
     sudo apt-get install -y libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev
     sudo apt-get install -y libv4l-dev v4l-utils qv4l2 v4l2ucp
     sudo apt-get install -y curl
     
     version="4.5.0"
     folder="workspace"
     
     echo "** Download opencv-"${version}
     mkdir $folder
     cd ${folder}
     curl -L https://github.com/opencv/opencv/archive/${version}.zip -o opencv-${version}.zip
     curl -L https://github.com/opencv/opencv_contrib/archive/${version}.zip -o opencv_contrib-${version}.zip
     unzip opencv-${version}.zip
     unzip opencv_contrib-${version}.zip
     cd opencv-${version}/
     
     echo "** Building..."
     mkdir release
     cd release/
     cmake -D WITH_CUDA=ON -D WITH_CUDNN=ON -D CUDA_ARCH_BIN="5.3,6.2,7.2" -D CUDA_ARCH_PTX="" -D OPENCV_GENERATE_PKGCONFIG=ON -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-${version}/modules -D WITH_GSTREAMER=ON -D WITH_LIBV4L=ON -D BUILD_opencv_python2=ON -D BUILD_opencv_python3=ON -D BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_EXAMPLES=OFF -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..
     make -j$(nproc)
     sudo make install
     
     echo "** Install opencv-"${version}" successfully"
     echo "** Bye :)"
     ```

5. Install Zenoh

```bash
# Install Rust
sudo apt install curl
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Install Rust toolchain
rustup toolchain install nightly

# Install Zenoh (tested version of eclipse-zenoh 0.5.0b8)
pip3 install eclipse-zenoh==0.5.0-b8 # took around 20 mins
```

6. Install other Python dependencies
- ```bash
  pip3 install -r requirements.txt
  ```

- `requirements.txt`

```bash
asab==20.7.28  # has latest version, instead of `asab`
simplejson==3.17.2
redis==3.5.3

# run command `$ nose2` on the root project directory
nose2==0.10.0
requests==2.25.1
motor==2.4.0
```
