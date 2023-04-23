import Carla

try:
    client_1 = BasicSynchronousClient()
    client_1.game_loop()
finally:
        print('EXIT')