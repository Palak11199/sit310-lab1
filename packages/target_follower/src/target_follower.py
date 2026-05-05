#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import AprilTagDetectionArray


class Target_Follower:
    def __init__(self):

        # Initialize ROS node
        rospy.init_node('target_follower_node', anonymous=True)

        # Shutdown hook
        rospy.on_shutdown(self.clean_shutdown)

        # ===== PARAMETERS (TUNABLE) =====
        self.search_speed = 0.5        # rotation speed when searching
        self.turn_speed = 0.3          # rotation speed when tracking
        self.center_threshold = 0.05   # how close to center is "aligned"

        # ===== PUBLISHER =====
        self.cmd_vel_pub = rospy.Publisher(
            '/akandb/car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )

        # ===== SUBSCRIBER =====
        rospy.Subscriber(
            '/akandb/apriltag_detector_node/detections',
            AprilTagDetectionArray,
            self.tag_callback,
            queue_size=1
        )

        rospy.loginfo("Target Follower Node Started")
        rospy.spin()

    # ================= CALLBACK =================
    def tag_callback(self, msg):
        self.move_robot(msg.detections)

    # ================= MAIN LOGIC =================
    def move_robot(self, detections):

        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()

        # ===== FEATURE 1: SEEK OBJECT =====
        if len(detections) == 0:
            rospy.loginfo("No tag detected → SEEKING")

            cmd_msg.v = 0.0
            cmd_msg.omega = self.search_speed   # rotate to find object

            self.cmd_vel_pub.publish(cmd_msg)
            return

        # ===== FEATURE 2: LOOK AT OBJECT =====
        tag = detections[0]

        x = tag.transform.translation.x
        y = tag.transform.translation.y
        z = tag.transform.translation.z

        rospy.loginfo("Tag detected | x: %.3f y: %.3f z: %.3f", x, y, z)

        cmd_msg.v = 0.0   # IMPORTANT: no forward movement

        # Rotate based on horizontal offset
        if x > self.center_threshold:
            rospy.loginfo("Turning RIGHT")
            cmd_msg.omega = -self.turn_speed

        elif x < -self.center_threshold:
            rospy.loginfo("Turning LEFT")
            cmd_msg.omega = self.turn_speed

        else:
            rospy.loginfo("Object CENTERED")
            cmd_msg.omega = 0.0

        self.cmd_vel_pub.publish(cmd_msg)

    # ================= SHUTDOWN =================
    def clean_shutdown(self):
        rospy.loginfo("Shutting down → stopping robot")
        self.stop_robot()

    def stop_robot(self):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        cmd_msg.omega = 0.0
        self.cmd_vel_pub.publish(cmd_msg)


# ================= MAIN =================
if __name__ == '__main__':
    try:
        Target_Follower()
    except rospy.ROSInterruptException:
        pass
