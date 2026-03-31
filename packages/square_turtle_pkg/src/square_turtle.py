#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import time
import math

# -------- Callback function --------
def pose_callback(msg):
    rospy.loginfo("X: %.2f | Y: %.2f | Theta: %.2f", msg.x, msg.y, msg.theta)


def move_turtle_square():
    rospy.init_node('turtlesim_square_node', anonymous=True)

    velocity_publisher = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
    rospy.Subscriber('/turtle1/pose', Pose, pose_callback)

    rospy.loginfo("Turtles are great at drawing squares!")

    rate = rospy.Rate(20)

    while not rospy.is_shutdown():

        for i in range(4):

            # -------- Move forward --------
            move_cmd = Twist()
            move_cmd.linear.x = 2.0

            t0 = rospy.Time.now().to_sec()
            duration = 2  # adjust for side length

            while (rospy.Time.now().to_sec() - t0) < duration:
                velocity_publisher.publish(move_cmd)
                rate.sleep()

            # Stop
            velocity_publisher.publish(Twist())
            time.sleep(0.5)

            # -------- Rotate 90 degrees --------
            turn_cmd = Twist()
            angular_speed = math.radians(90)   # 90 deg/sec → 1.57 rad/s
            angle = math.radians(90)           # target angle

            turn_cmd.angular.z = angular_speed

            t0 = rospy.Time.now().to_sec()
            current_angle = 0

            while current_angle < angle:
                velocity_publisher.publish(turn_cmd)
                t1 = rospy.Time.now().to_sec()
                current_angle = angular_speed * (t1 - t0)
                rate.sleep()

            # Stop rotation
            velocity_publisher.publish(Twist())
            time.sleep(0.5)


if __name__ == '__main__':
    try:
        move_turtle_square()
    except rospy.ROSInterruptException:
        pass
