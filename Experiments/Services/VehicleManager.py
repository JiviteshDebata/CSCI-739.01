
import carla
import weakref
import random
import numpy as np

import pygame
from pygame.locals import K_ESCAPE
from pygame.locals import K_SPACE
from pygame.locals import K_a
from pygame.locals import K_d
from pygame.locals import K_s
from pygame.locals import K_w

import time
from datetime import datetime

##Bounding Box from here
from ClientSideBoundingBox import ClientSideBoundingBoxes

##Lidar from here
import open3d as o3d
from matplotlib import cm
from ClientSideLidarVisualizer import ClientSideLidarVisualizer

##Network from here
import requests
import threading
import uuid

class VehicleManager(object):
    """
    A vehicle class that opens up a client connection to the simulator and shows the live visualizations.
    """

    def __init__(self):
        self.client = None
        self.world = None
        self.car = None
        self.viz=None
        self.vehicle_id = uuid.uuid4()
        
        
        self.camera = None
        self.display = None
        self.image = None
        self.capture = True

        self.lidar=None
        self.point_list=o3d.geometry.PointCloud()
        self.point_capture=True
        

    def camera_blueprint(self):
        """
        Returns camera blueprint.
        """
        VIEW_WIDTH = 1920//2
        VIEW_HEIGHT = 1080//2
        VIEW_FOV = 90
        
        camera_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
        
        camera_bp.set_attribute('image_size_x', str(VIEW_WIDTH))
        camera_bp.set_attribute('image_size_y', str(VIEW_HEIGHT))
        camera_bp.set_attribute('fov', str(VIEW_FOV))
        return camera_bp
    
    def lidar_blueprint(self):
        """
        Returns the liodar blueprint. Vehicle Class doesnt use semantic lidar by design.
        """
        DELTA = 0.05# magic Carla number
        ADDED_NOISE=0.2
        UPPER_FOV=15.0
        LOWER_FOV=25.0
        CHANNELS=64.0
        RANGE=100.0
        ROTATION_FREQUENCY=1.0 / DELTA
        POINTS_PER_SECOND=50000
        
        lidar_bp=self.world.get_blueprint_library().find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('noise_stddev', str(ADDED_NOISE))
        lidar_bp.set_attribute('upper_fov', str(UPPER_FOV))
        lidar_bp.set_attribute('lower_fov', str(LOWER_FOV))
        lidar_bp.set_attribute('channels', str(CHANNELS))
        lidar_bp.set_attribute('range', str(RANGE))#in meters
        lidar_bp.set_attribute('rotation_frequency', str(ROTATION_FREQUENCY))
        lidar_bp.set_attribute('points_per_second', str(POINTS_PER_SECOND))
        return lidar_bp
        

    def set_synchronous_mode(self, synchronous_mode):
        """
        Sets synchronous mode.
        """

        settings = self.world.get_settings()
        settings.synchronous_mode = synchronous_mode
        self.world.apply_settings(settings)
    
    #TODO  setup async to fix Lidar
    

    def setup_car(self):
        """
        Spawns actor-vehicle to be controled.
        """

        car_bp = self.world.get_blueprint_library().filter('vehicle.*')[0]
        # car_bp.set_attribute('role_name', f'vehicle_{self.unique_id}') #WIP? Explore BP Classes
        location = random.choice(self.world.get_map().get_spawn_points())
        self.car = self.world.spawn_actor(car_bp, location)

    def setup_camera(self):
        """
        Spawns actor-camera to be used to render view.
        Sets calibration for client-side boxes rendering.
        """
        VIEW_WIDTH = 1920//2
        VIEW_HEIGHT = 1080//2
        VIEW_FOV = 90

        camera_transform = carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15))
        self.camera = self.world.spawn_actor(self.camera_blueprint(), camera_transform, attach_to=self.car)
        weak_self = weakref.ref(self)
        self.camera.listen(lambda image: weak_self().set_image(weak_self, image))

        calibration = np.identity(3)
        calibration[0, 2] = VIEW_WIDTH / 2.0
        calibration[1, 2] = VIEW_HEIGHT / 2.0
        calibration[0, 0] = calibration[1, 1] = VIEW_WIDTH / (2.0 * np.tan(VIEW_FOV * np.pi / 360.0))
        self.camera.calibration = calibration
        
    def setup_lidar(self):
        """spawns actor-lidar to be used to render lidar data"""
        
        VIRIDIS = np.array(cm.get_cmap('plasma').colors)
        VID_RANGE = np.linspace(0.0, 1.0, VIRIDIS.shape[0])
        LABEL_COLORS = np.array([
        (255, 255, 255), # None
        (70, 70, 70),    # Building
        (100, 40, 40),   # Fences
        (55, 90, 80),    # Other
        (220, 20, 60),   # Pedestrian
        (153, 153, 153), # Pole
        (157, 234, 50),  # RoadLines
        (128, 64, 128),  # Road
        (244, 35, 232),  # Sidewalk
        (107, 142, 35),  # Vegetation
        (0, 0, 142),     # Vehicle
        (102, 102, 156), # Wall
        (220, 220, 0),   # TrafficSign
        (70, 130, 180),  # Sky
        (81, 0, 81),     # Ground
        (150, 100, 100), # Bridge
        (230, 150, 140), # RailTrack
        (180, 165, 180), # GuardRail
        (250, 170, 30),  # TrafficLight
        (110, 190, 160), # Static
        (170, 120, 50),  # Dynamic
        (45, 60, 150),   # Water
        (145, 170, 100), # Terrain
        ]) / 255.0 # normalize each channel [0-1] since is what Open3D uses
        
        lidar_transform=carla.Transform(carla.Location(x=-0.5, z=1.8))
        self.lidar=self.world.spawn_actor(self.lidar_blueprint(),lidar_transform,attach_to=self.car)
        weak_self=weakref.ref(self)
        self.lidar.listen(lambda data: weak_self().update_points(weak_self,data))
        

    def control(self, car):
        """
        Applies control to main car based on pygame pressed keys.
        Will return True If ESCAPE is hit, otherwise False to end main loop.
        """

        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            return True

        control = car.get_control()
        control.throttle = 0
        if keys[K_w]:
            control.throttle = 1
            control.reverse = False
        elif keys[K_s]:
            control.throttle = 1
            control.reverse = True
        if keys[K_a]:
            control.steer = max(-1., min(control.steer - 0.05, 0))
        elif keys[K_d]:
            control.steer = min(1., max(control.steer + 0.05, 0))
        else:
            control.steer = 0
        control.hand_brake = keys[K_SPACE]

        car.apply_control(control)
        return False
    
    def update_network(self, points_size):
        def send_request():
            data = {
                "vehicle_id": self.vehicle_id,
                "points_size": points_size
            }
            try:
                requests.post("http://127.0.0.1:5001/update", data=data)
            except requests.exceptions.RequestException as e:
                print(f"Error updating dashboard: {e}")

        update_thread = threading.Thread(target=send_request)
        update_thread.start()



    @staticmethod
    def set_image(weak_self, img):
        """
        Sets image coming from camera sensor.
        The self.capture flag is a mean of synchronization - once the flag is
        set, next coming image will be stored.
        """
        self = weak_self()
        if self.capture:
            self.image = img
            self.capture = False

            
    @staticmethod
    def update_points(weak_self, points):
        VIRIDIS = np.array(cm.get_cmap('plasma').colors)
        VID_RANGE = np.linspace(0.0, 1.0, VIRIDIS.shape[0])
        """Updates the points captured to be visualizes

        Args:
            weak_self (_type_): _description_
            points (_type_): _description_
        """
        self = weak_self()
        if self.point_capture:
            data = np.copy(np.frombuffer(points.raw_data, dtype=np.dtype('f4')))
            data = np.reshape(data, (int(data.shape[0] / 4), 4))

            # Isolate the intensity and compute a color for it
            intensity = data[:, -1]
            intensity_col = 1.0 - np.log(intensity) / np.log(np.exp(-0.004 * 100))
            int_color = np.c_[
                np.interp(intensity_col, VID_RANGE, VIRIDIS[:, 0]),
                np.interp(intensity_col, VID_RANGE, VIRIDIS[:, 1]),
                np.interp(intensity_col, VID_RANGE, VIRIDIS[:, 2])]

            # Isolate the 3D data
            points = data[:, :-1]

            # We're negating the y to correclty visualize a world that matches
            # what we see in Unreal since Open3D uses a right-handed coordinate system
            points[:, :1] = -points[:, :1]

            # # An example of converting points from sensor to vehicle space if we had
            # # a carla.Transform variable named "tran":
            # points = np.append(points, np.ones((points.shape[0], 1)), axis=1)
            # points = np.dot(tran.get_matrix(), points.T).T
            # points = points[:, :-1]

            self.point_list.points = o3d.utility.Vector3dVector(points)
            self.point_list.colors = o3d.utility.Vector3dVector(int_color)  
            

            self.point_capture = False

  
    def render(self, display):
        """
        Transforms image from camera sensor and blits it to main pygame display.
        """

        if self.image is not None:
            array = np.frombuffer(self.image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (self.image.height, self.image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
            display.blit(surface, (0, 0))

    def game_loop(self):
        """
        Main program loop.
        """
        VIEW_WIDTH = 1920//2
        VIEW_HEIGHT = 1080//2
        VIEW_FOV = 90

        try:
            pygame.init()
            
   
            self.client = carla.Client('127.0.0.1', 2000)
            self.client.set_timeout(2.0)
            self.world = self.client.get_world()

            self.setup_car()
            self.setup_camera()
            self.setup_lidar()
            
            
            self.display = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
            pygame_clock = pygame.time.Clock()

            self.set_synchronous_mode(True)
            vehicles = self.world.get_actors().filter('vehicle.*')
            
            self.vis = o3d.visualization.Visualizer()
            self.vis.create_window(
            window_name='Carla Lidar',
            width=960,
            height=540,
            left=480,
            top=270)
            self.vis.get_render_option().background_color = [0.05, 0.05, 0.05]
            self.vis.get_render_option().point_size = 1
            self.vis.get_render_option().show_coordinate_frame = True
            
            frame = 0
            while True:
                self.world.tick()
                self.capture = True
                self.point_capture=True
              
                
                
                pygame_clock.tick_busy_loop(20) #Should be 100?what is this? CARLA magic frequency is 1/20
                
                
                
                
                self.render(self.display)
                bounding_boxes = ClientSideBoundingBoxes.get_bounding_boxes(vehicles, self.camera)
                ClientSideBoundingBoxes.draw_bounding_boxes(self.display, bounding_boxes)
                # self.point_list=ClientSideLidarVisualizer.update_points(self.lidar,self.point_list)
                # self.point_list = ClientSideLidarVisualizer.update_points(np.array([p.location for p in self.point_list.points]), self.point_list)
                # self.point_list = ClientSideLidarVisualizer.update_points(np.array(self.point_list.points), self.point_list)
                # point_list = ClientSideLidarVisualizer.update_points(self.point_list, self.point_list)

               
                
                pygame.display.flip()
                
                if frame%2!=0:
                    self.vis.add_geometry(self.point_list)
                self.vis.update_geometry(self.point_list)
                self.vis.poll_events()
                self.vis.update_renderer()
                
                frame += 1
                
                pygame.event.pump()
                
                points_size = len(self.point_list.points)

                # Update the dashboard with the size of the self.points list
                self.update_network(points_size)
                
                
                
                if self.control(self.car):
                    return

        finally:
            self.set_synchronous_mode(False)
            self.camera.destroy()
            self.car.destroy()
            self.lidar.destroy()
            self.vis.destroy_window()
            pygame.quit()
            



# def main():
#     """
#     Initializes the client-side bounding box demo.
#     """

#     try:
#         client = VehicleManager()
#         client.game_loop()
#     finally:
#         print('EXIT')


# if __name__ == '__main__':
#     main()
