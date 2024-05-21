# Commit message: Implement process_frame method to detect colored cubes

import cv2
import pyrealsense2 as rs
import numpy as np

class RealSenseCubeDetector:
    def __init__(self, min_area=100):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(self.config)

        self.color_ranges = self.define_color_ranges()
        self.min_area = min_area  # Minimum area of the contour to be considered as a cube
        self.kernel = np.ones((5, 5), np.uint8)  # Morphological kernel

    def define_color_ranges(self):
        return {
            'red': ((0, 120, 70), (10, 255, 255)),
            'green': ((40, 40, 40), (80, 255, 255)),
            'blue': ((100, 150, 150), (140, 255, 255)),
            'yellow': ((20, 100, 100), (30, 255, 255)),
            'cyan': ((80, 100, 100), (100, 255, 255)),
            'orange': ((10, 100, 100), (25, 255, 255)),
            'pink': ((145, 60, 65), (165, 255, 255))
        }

    def process_frame(self, color_image):
        detected_cubes = []
        blurred_image = cv2.GaussianBlur(color_image, (5, 5), 0)
        hsv = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2HSV)

        for color, (lower, upper) in self.color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            mask = cv2.dilate(mask, self.kernel, iterations=1)
            mask = cv2.erode(mask, self.kernel, iterations=1)
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) > self.min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    center = (x + w // 2, y + h // 2)
                    detected_cubes.append({
                        'color': color,
                        'position': center
                    })
        return detected_cubes

    def detect_cubes(self):
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            return []

        color_image = np.asanyarray(color_frame.get_data())
        return self.process_frame(color_image)

    def stop(self):
        self.pipeline.stop()
        cv2.destroyAllWindows()