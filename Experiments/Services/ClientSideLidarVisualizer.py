import numpy as np
import open3d as o3d
from matplotlib import cm

VIRIDIS = np.array(cm.get_cmap('plasma').colors)
VID_RANGE = np.linspace(0.0, 1.0, VIRIDIS.shape[0])


# class ClientSideLidarVisualizer(object):
#     """This module is responsible for visualizing the LIDAR input stream from an ego vehicle"""
    
    
    
#     @staticmethod
#     def update_points(point_cloud,point_list):
#         """Prepares a point cloud with intensity colors ready to be consumed by Open3D"""
#         data = np.copy(np.frombuffer(point_cloud.raw_data, dtype=np.dtype('f4')))
#         data = np.reshape(data, (int(data.shape[0] / 4), 4))
#          # Isolate the intensity and compute a color for it
#         intensity = data[:, -1]
#         intensity_col = 1.0 - np.log(intensity) / np.log(np.exp(-0.004 * 100))
#         int_color = np.c_[
#             np.interp(intensity_col, VID_RANGE, VIRIDIS[:, 0]),
#             np.interp(intensity_col, VID_RANGE, VIRIDIS[:, 1]),
#             np.interp(intensity_col, VID_RANGE, VIRIDIS[:, 2])]

#         # Isolate the 3D data
#         points = data[:, :-1]

#         # We're negating the y to correclty visualize a world that matches
#         # what we see in Unreal since Open3D uses a right-handed coordinate system
#         points[:, :1] = -points[:, :1]

#         # # An example of converting points from sensor to vehicle space if we had
#         # # a carla.Transform variable named "tran":
#         # points = np.append(points, np.ones((points.shape[0], 1)), axis=1)
#         # points = np.dot(tran.get_matrix(), points.T).T
#         # points = points[:, :-1]

#         point_list.points = o3d.utility.Vector3dVector(points)
#         point_list.colors = o3d.utility.Vector3dVector(int_color)
        
class ClientSideLidarVisualizer(object):
    """This module is responsible for visualizing the LIDAR input stream from an ego vehicle"""

    @staticmethod
    def update_points(points, point_list):
        """Prepares a point cloud with intensity colors ready to be consumed by Open3D"""

        # We're negating the y to correctly visualize a world that matches
        # what we see in Unreal since Open3D uses a right-handed coordinate system
        points[:, :1] = points[:, :-1]

        # We will assign random colors to the points for visualization purposes
        colors = np.random.rand(len(points), 3)

        point_list.points = o3d.utility.Vector3dVector(points)
        point_list.colors = o3d.utility.Vector3dVector(colors)


    @staticmethod
    def update_points(point_cloud,point_list):
            """Prepares a point cloud with intensity
            colors ready to be consumed by Open3D"""
            data = np.copy(np.frombuffer(point_cloud.raw_data, dtype=np.dtype('f4')))
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

            point_list.points = o3d.utility.Vector3dVector(points)
            point_list.colors = o3d.utility.Vector3dVector(int_color)