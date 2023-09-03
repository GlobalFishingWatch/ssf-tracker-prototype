# GPS Testing

In prior experiments, we have found that the the biggest source of power use is getting a GPS fix.   

We want to try to measure how much power we will need to acquire GPS fixes over time

### Test Questions
1. How long on average does it take to get a GPS fix over a long series of wake/fix/sleep cycles
2. How much power do we consume while getting a fix
3. How do things change when we change the fix interval

### Test setup with the Adafruit Ultimate GPS
Using an arduino feather esp32 for the conroller and AdaFruit Ultimate GPS breakout 

### Test 1

* Power the GPS from the controller 3V3
* Install a button battery in the GPS
* Use the external antenna in an outdoor location with a clear view of the sky
* Set up a sleep/wake cycle in the controller, using deepsleep
* On sleep, disable the GPS with the `EN` pin
* On wake, enable the GPS, wait for it to get a fix
* After the GPS gets a fix, disable it with the `EN` in and send the controller to sleep

#### Measures
* Log the fixed location (so we can check consistency across multiple readings)
* Log the time from wake to fix
* Compute the average and cumulative time the controller spends awake
* Measure total power consumption of the entire system during wake and sleep
* Measure the power consumption of just the GPS with EN on and off

Run this test for a couple of days and see what the timings look like

#### Test 2

* Same setup as test 1, but try to put the controller into light sleep while you wait for the GPS to get a fix. 
* See if there is a way to wake the controller using the `FIX` pin perhaps?
* Or just sleep for a short period like 500ms and then wake and check
* Measure to see if this extra complexity reduces overall power consumption



