# Knwon Bugs and Issues

1. Carla seems to use a magic frequency of 1/20 in all its code but doesn't mention it in the documentation. Changing this frequency for any local agent update or lidar update causes heavy amounts of jittering.
2. Bounding Boxes are being rendered incorrectly for some vehicle clients when multiple agents run in parallel. Possible fix is to change blueprint filteration code.
3. Only the Carla Simulator runs smoothly. Since the agent is forced to  sync  with the client every pygame loop. So o3d and client windows updates are rough. Possible fix is post processing or vsync lock to 30FPS
4. Would Prefer to run multiple Clients in the same jyupiter file. Possible fix might be explore Tornado for batched multithreading.
5. The Lidar Actor has a known memory leak. Possible fix unknown? Carla side sensor error ?
6. There is a strong coupling of global configurations across functions. Makes customizing placement of sensors difficult. Possible fix use external config file to be imported
7. Currently All data is being sent and recived by the network manager but the dashboard wont update due to high poll rate or jitter . Possible solution? use GRPC? write to SQL? Temporary hot fix works if using a single vehicle



# WIP
1. Move to batch model instead of single user sessions.
2. Get weather up and running. 