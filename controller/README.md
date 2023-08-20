# Micro Controller

The controller runs on an arduino ESP32 running micropython

## Set up the local dev environment
We use micropython to run the code in the arduino, nut we use standard python for development and testing because I haven't figured out how to use unittest properly in micropython.  Ideally we would run all the unitest in micropython on the dev machine so taht we know everything is the same as it will be on the arduino. 

### Python setup for osx - create a python environment if you don't aleady have one
```
conda create -n py311 python=3.11.4 
conda avtivate py311
```

### Create a python virtualenv
```console
pip install virtualenv
cd controller
virtualenv venv
source venv/bin/activate
pip install -r requirements-dev.txt 
```

### Run the unit tests
```console
python app/test.py
```

### install micropython on the ESP32-S3 board

Using [this guide](https://micropython.org/download/GENERIC_S3/)

```
pip install esptool

esptool.py --chip esp32-S3 --port /dev/tty.usbmodem101 erase_flash
esptool.py --chip esp32s3 --port /dev/tty.usbmodem101 write_flash -z 0 ~/Downloads/GENERIC_S3-20230426-v1.20.0.bin 
```

### Install micropython on the dev machine
On OSX, install micropython from source
https://docs.micropython.org/en/latest/develop/gettingstarted.html#building-the-unix-port-of-micropython

```console
git clone https://github.com/micropython/micropython
cd micropython/mpy-cross
make
cd ../ports/unix
make submodules
make
./micropython
```

Now install some packages from micropython-lib
```console
micropython -m mip install unittest
micropython -m mip install tempfile
micropython -m mip install logging
micropython -m mip install shutil
```

Now you should be able to run the unit tests with micropython
```console
micropython app/test.py
```
 
### Install packages to the esp32 device
Use mpremote - [documentation](https://docs.micropython.org/en/latest/reference/mpremote.html)
```console
pip install mpremote

mpremote fs mkdir lib
mpremote mip install unittest
mpremote mip install tempfile
mpremote mip install logging
mpremote mip install shutil
```

### Copy files to the esp32 device
#### Copy with mpremote
```console
mpremote cp app/*.py :
```
Note that this seems to fail intermittently, so here's analternative way

#### Copy files with mpy-upload

Use mpy-upload - [documentation](https://github.com/nickzoic/mpy-utils)

First you need to find the port (mpremote finds it auto-magically)
```console
ls /dev/cu*
```

Then use the usb port to copy all the files
```console
pip install mpy-utils

mpy-upload --port /dev/cu.usbmodem5629254 app/*.py
```

### Open a REPL on the device so you can run things

```console
mpremote repl
```
You may need to hit ctrl-B to get a the `>>>` prompt

### Run the unit tests in the REPL
```python
>>> import test_esp32
>>> test.run_all_tests_esp32()
```

### Now finally, run the App!
From the repl
```python
>>> import main
>>> main.app.run()
```
ctrl-c to break



## SOME RANDOM NOTES BELOW


How to create a virtual env using micropython (not working?)
```
ln -s /Users/paul/github/micropython/ports/unix/build-standard/micropython /usr/local/bin/micropython
micropython -m mip install venv
source venv-mpy/bin/activate 
```


### Using Thonny IDE to run python code on the ESP hardware

### Monitor the serial port directly from OSX

1. Connect the usb cable to the COM port (not the USB port)

2. find the device name
```
ls /dev/cu*
```
3. should look something like this
```
/dev/cu.usbmodem56292549741
```
4. then connect with screen
```
screen /dev/cu.usbmodem56292549741 115200
```
5. To exit screen, do ctrl-a and then k to kill the session


### set up mpy-utils for direct file system access
github: https://github.com/nickzoic/mpy-utils
```
pip install mpy-utils
```


Use mpremote
```console
pip install mpremote
```
To open a shell to the REPL. You may need to hit ctrl-B to get the prompt
```console
mpremote repl
```
It should auto-discover the usb port

To copy files from the host to the device
```console
mpremote cp test.py :tesy.py
mpremote cp test/*.py :
```

List files on the device
```console
mpremote fs ls
```

Install modules using mip onto the device
```console
mpremote fs mkdir lib
mpremote mip install logging
```

#### Copy files with mpy-upload
DEPRECATED - using `mpremote cp` is better

Use mpy-upload - [documentation](https://github.com/nickzoic/mpy-utils)

First you need to find the port (mpremote finds it auto-magically)
```console
ls /dev/cu*
```

Then use the usb port to copy all the files
```console
pip install mpy-utils

mpy-upload --port /dev/cu.usbmodem5629254 app/*.py
```
