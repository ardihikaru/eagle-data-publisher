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
- Export pycore:
    `export PYTHONPATH=:<root-path-to-project>/eagle-data-publisher/pycore`
    - The path may be different. :)
        - In Eaglestitch Server: 
             `export PYTHONPATH=:/home/eagles/devel/eagle-data-publisher/pycore`
        - In Popeye Server: 
             `export PYTHONPATH=:/home/popeye/devel/eagle-data-publisher/pycore`
        - In LittleBoy Server: 
             `export PYTHONPATH=:/home/s010132/devel/eagle-data-publisher/pycore`
2. Install required library
    - Make sure to use latest version of `pip`:
        `$ pip3 install --upgrade pip`
    - Install lib: `$ pip3 install -r requirements.txt`

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
