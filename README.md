# eagle-data-publisher

## Requirements
- **Python 3.8**
    - **FYI**: Change python version; e.g. from `python3.6` into `python3.8`
        - Install python3.8: `$ sudo apt install python3.8`
        - Install venv (optional): `$ apt install python3.8-venv`
        - Install python3.8 dev: `$ sudo apt-get install python3.8-dev`
        - Change alternative: `$ sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1`
            - It will get response as follows:
                ```
                update-alternatives: using /usr/bin/python3.8 to provide /usr/bin/python3 (python3) in auto mode
                ```
        - Set: `$ sudo update-alternatives --config python3`
            - It will get response as follows:
                ```
                There is only one alternative in link group python3 (providing /usr/bin/python3): /usr/bin/python3.8
                Nothing to configure.
                ```
        - Check result: `$ python3 --version`

## Installation
1. Clone project: `$ git clone https://github.com/ardihikaru/eagle-data-publisher.git`
2. Export pycore (can be done later):
    `export PYTHONPATH=:<root-path-to-project>/eagle-data-publisher/pycore`
    - The path may be different. :)
        - In Eaglestitch Server: 
             `export PYTHONPATH=:/home/eagles/devel/eagle-data-publisher/pycore`
        - In Popeye Server: 
             `export PYTHONPATH=:/home/popeye/devel/eagle-data-publisher/pycore`
        - In LittleBoy Server: 
             `export PYTHONPATH=:/home/s010132/devel/eagle-data-publisher/pycore`
3. Install required library
    - Make sure to use latest version of `pip`:
        `$ pip3 install --upgrade pip`
    - Install `Cython`: `$ pip3 install Cython`
    - Install rest of the library: `$ pip3 install -r requirements.txt`
    - OpenCV, it is better to install them manually.
        - For personal use, you may use easy install by running this: `$ pip3 install opencv-python`
        - Especially for `JetsonNano`, you should **NEVER** try to use **pip install**.
            - Follow this [tutorial to do installation in JetsonNano](https://github.com/ardihikaru/eagle-data-publisher/blob/main/Jetson_Nano_Setup_for_ADS) 
4. Finish. you may follow `Testing usage` or `How to use` section.

## Testing usage
1. Prepared two terminals
2. Run Consumer:
    - Add lib (if not added yet), e.g.: 
        `$ export PYTHONPATH=:/home/ardi/devel/nctu/IBM-Lab/eagle-data-publisher/pycore`
    - Run consumer:
        `$ env RUST_LOG=debug python3 data_consumer.py -l tcp/localhost:7446`
            - If you try them in the same PC, you can use `localhost`
            - If you use to test them to PubSub with different PCs, change them to **IP of the Consumer**
3. Run Publisher
    - Add lib (if not added yet), e.g.: 
        `$ export PYTHONPATH=:/home/ardi/devel/nctu/IBM-Lab/eagle-data-publisher/pycore`
    - Run publisher: `$ env RUST_LOG=debug python3 data_publisher.py -e tcp/localhost:7446 --resize`
        - If you try them in the same PC, you can use `localhost`
        - If you use to test them to PubSub with different PCs, change them to **IP of the Consumer**
        - By default, it read your local camera (video0).
        - If you want to extract frames from a video file, use following command:
            `$ env RUST_LOG=debug python3 data_publisher.py -e tcp/localhost:7446 --resize -v >your_video_path>`
        - if you want to resize the video property, let say, to FullHD, follow this steps:
            - Run this to know possible resolution and its FPS (In Linux only):
                `$ v4l2-ctl --list-formats-ext`
            - To apply the config, you can try following command:
              ```
              $ env RUST_LOG=debug python3 data_publisher.py -e tcp/localhost:7446 --resize --pwidth 1920 --pheight 1080 -v >your_video_path>
              ```

## How to use
1. Run Consumer service
2. Run Publisher service (**this project**)
    - Sample script to run in the field trial:
        - Popeye:
            - Default: `$ python3 data_publisher.py -e tcp/192.168.1.11:7446 --resize`
            - Resize Camera's resolution: `$ python3 data_publisher.py -e tcp/192.168.1.11:7446 --resize --pwidth 848 --pheight 480`
    - Run sample: `$ python3 data_publisher.py -e tcp/localhost:7446 --cvout --resize`
        - Possible parameters:
            - `--cvout`: Show the real-time captured images; this can be omitted if you run this script with no monitor capability
            - `--resize`: Force to resize the captured image into **FullHD**; can be omitted
            - `-e <path>`: a protocol to transmit data; **Simply focus to change**:
                - `localhost` into the target Consumer's IP Address, and
                - `7446` into any desired port.
            - `-v <path_to_video>`; Path to extract the video stream; 
            if not provided, it load **video0** (value `0`) from your hardware.
            - `--pwidth <target_width> --pheight <target_height>`: 
            Target width & height to change the OpenCV property. 
            The default value is a FullHD (`1920x1080`)
                - If you have no idea, use this command to show possible resolution (**Linux only**):
                `$ v4l2-ctl --list-formats-ext`, and you will receive response similar like this:
                  ``` 
                  $ v4l2-ctl --list-formats-ext                                                                            ^(*features/experiment-2021-06-23-cont+996) 14:17:59 
                    ioctl: VIDIOC_ENUM_FMT
                        Type: Video Capture
                    
                        [0]: 'MJPG' (Motion-JPEG, compressed)
                            ...
                            Size: Discrete 352x288
                                Interval: Discrete 0.033s (30.000 fps)
                            Size: Discrete 640x480
                                Interval: Discrete 0.033s (30.000 fps)
                        [1]: 'YUYV' (YUYV 4:2:2)  <<<--- Focus here. :)
                            Size: Discrete 1280x720
                                Interval: Discrete 0.100s (10.000 fps)
                            ...
                            Size: Discrete 640x480
                                Interval: Discrete 0.033s (30.000 fps)  
                  ```
                  - Please **ONLY Focus on the format** `YUYV`. :)

## MISC
- Change python version; e.g. from `python3.6` into `python3.8`
    - Install python3.8: `$ sudo apt install python3.8`
    - Install venv (optional): `$ apt install python3.8-venv`
    - Install python3.8 dev: `$ sudo apt-get install python3.8-dev`
    - Change alternative: `$ sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1`
        - It will get response as follows:
            ```
            update-alternatives: using /usr/bin/python3.8 to provide /usr/bin/python3 (python3) in auto mode
            ```
    - Set: `$ sudo update-alternatives --config python3`
        - It will get response as follows:
            ```
            There is only one alternative in link group python3 (providing /usr/bin/python3): /usr/bin/python3.8
            Nothing to configure.
            ```
    - Check result: `$ python3 --version`