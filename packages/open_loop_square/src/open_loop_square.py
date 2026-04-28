#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped


class DriveSquare:
    def __init__(self):

        # Get vehicle name
        self.veh = rospy.get_param("~veh")

        # Initialize ROS node
        rospy.init_node('open_loop_square', anonymous=True)

        # Publisher
        self.pub = rospy.Publisher(
            f'/{self.veh}/car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )

        rospy.loginfo("Open Loop Square Node Initialized")

        # Give ROS time to connect publisher
        rospy.sleep(1.0)

        # Start driving immediately (NO FSM)
        self.move_robot()

    # Stop robot
    def stop_robot(self):

        msg = Twist2DStamped()
        msg.header.stamp = rospy.Time.now()
        msg.v = 0.0
        msg.omega = 0.0

        self.pub.publish(msg)
        rospy.loginfo("Robot Stopped")

    # Drive square pattern
    def move_robot(self):

        rospy.loginfo("Starting Square Movement (NO FSM)")

        msg = Twist2DStamped()

        for i in range(4):

            # Move forward
            msg.header.stamp = rospy.Time.now()
            msg.v = 0.3
            msg.omega = 0.0
            self.pub.publish(msg)

            rospy.loginfo("Forward")
            rospy.sleep(2.0)

            # Turn 90 degrees
            msg.header.stamp = rospy.Time.now()
            msg.v = 0.0
            msg.omega = 2.0
            self.pub.publish(msg)

            rospy.loginfo("Turning")
            rospy.sleep(1.2)

        # Stop at end
        self.stop_robot()

    def run(self):
        rospy.spin()


if __name__ == '__main__':
    try:
        node = DriveSquare()
        node.run()

    except rospy.ROSInterruptException:
        pass
