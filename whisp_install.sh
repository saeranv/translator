#!/bin//bash

# Install ffmpeg
sudo apt -y update
sudo apt -y install ffmpeg

# Or else stream doesn't work
sudo apt-get -y update
sudo apt-get -y install libsdl2-dev


sudo apt -y install linux-tools-virtual hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip `ls /usr/lib/linux-tools/*/usbip | tail -n1` 20
