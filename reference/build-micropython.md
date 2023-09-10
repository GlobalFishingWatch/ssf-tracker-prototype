## Building micropython for ESP32 S3

### Targeting the ESP32-S3 DevKit C board (Paul's board)

Starting here:

https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/index.html#installation-step-by-step
```
brew install cmake ninja dfu-util
/usr/sbin/softwareupdate --install-rosetta --agree-to-license
mkdir -p ~/esp
cd ~/esp
git clone -b v5.0.2 --recursive https://github.com/espressif/esp-idf.git esp-idf-v5.0.2
ln -s esp-idf-v5.0.2 esp-idf    
cd esp-idf-v5.0.2/
./install.sh esp32,esp32s3
. $HOME/esp/esp-idf-v5.0.2/export.sh
```
Now build the esp32 micropython binary
```console
cd micropython/ports/esp32
make clean
make submodules
make BOARD=GENERIC_S3
```

To flash it to the ESP32, get the port and MAKE SURE the device is in the bootloader state
```commandline
ls /dev/cu*
```
Now write to flash
```console
python \
~/esp/esp-idf-v5.0.2/components/esptool_py/esptool/esptool.py \
-p /dev/cu.usbmodem1101 \
-b 460800 \
--before default_reset \
--after no_reset \
--chip esp32s3  \
write_flash \
--flash_mode dio \
--flash_size 8MB \
--flash_freq 80m \
0x0 build-GENERIC_S3/bootloader/bootloader.bin \
0x8000 build-GENERIC_S3/partition_table/partition-table.bin \
0x10000 build-GENERIC_S3/micropython.bin
 ```

### Targeting OSX

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