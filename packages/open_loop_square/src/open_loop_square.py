#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped, FSMState, WheelEncoderStamped


class ClosedLoopSquareNode:
    def __init__(self):
        rospy.init_node("closed_loop_square_node", anonymous=False)

        # ✅ YOUR BOT NAME (HARDCODED)
        self.vehicle_name = "mybota002417"

        # Topics
        self.cmd_topic = f"/{self.vehicle_name}/car_cmd_switch_node/cmd"
        self.fsm_topic = f"/{self.vehicle_name}/fsm_node/mode"
        self.encoder_topic = f"/{self.vehicle_name}/left_wheel_encoder_node/tick"

        # Publisher
        self.cmd_pub = rospy.Publisher(self.cmd_topic, Twist2DStamped, queue_size=1)

        # Subscribers
        self.fsm_sub = rospy.Subscriber(self.fsm_topic, FSMState, self.fsm_callback)
        self.encoder_sub = rospy.Subscriber(self.encoder_topic, WheelEncoderStamped, self.encoder_callback)

        # Parameters
        self.forward_speed = 0.25
        self.turn_speed = 3.0

        # 🔴 CALIBRATE THESE VALUES
        self.ticks_per_meter = 600     # change after testing
        self.ticks_per_90deg = 300     # change after testing

        # State
        self.current_ticks = 0
        self.start_ticks = 0

        self.current_mode = ""
        self.last_mode = ""
        self.is_executing = False

        rospy.on_shutdown(self.on_shutdown)

        rospy.loginfo("Closed Loop Square Node Started")
        rospy.loginfo(f"Vehicle: {self.vehicle_name}")

    # =========================
    # Callbacks
    # =========================

    def encoder_callback(self, msg):
        self.current_ticks = msg.data

    def fsm_callback(self, msg):
        self.current_mode = msg.state
        rospy.loginfo_throttle(2, f"FSM mode: {self.current_mode}")

        if self.is_executing:
            self.last_mode = self.current_mode
            return

        if self.current_mode == "LANE_FOLLOWING" and self.last_mode != "LANE_FOLLOWING":
            rospy.loginfo("Starting CLOSED-LOOP square motion")
            self.is_executing = True
            self.move_square()
            self.is_executing = False

        self.last_mode = self.current_mode

    # =========================
    # Motion Helpers
    # =========================

    def publish_cmd(self, v, omega):
        msg = Twist2DStamped()
        msg.header.stamp = rospy.Time.now()
        msg.v = v
        msg.omega = omega
        self.cmd_pub.publish(msg)

    def stop_robot(self):
        rospy.loginfo("Stopping robot")
        for _ in range(5):
            self.publish_cmd(0.0, 0.0)
            rospy.sleep(0.05)

    # =========================
    # CLOSED-LOOP FUNCTIONS
    # =========================

    def move_straight(self, distance):
        rospy.loginfo(f"Moving {distance} meters")

        target_ticks = distance * self.ticks_per_meter
        self.start_ticks = self.current_ticks

        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            travelled = self.current_ticks - self.start_ticks

            if travelled >= target_ticks:
                break

            self.publish_cmd(self.forward_speed, 0.0)
            rate.sleep()

        self.stop_robot()

    def rotate_in_place(self, angle_deg):
        rospy.loginfo(f"Rotating {angle_deg} degrees")

        target_ticks = (angle_deg / 90.0) * self.ticks_per_90deg
        self.start_ticks = self.current_ticks

        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            rotated = abs(self.current_ticks - self.start_ticks)

            if rotated >= target_ticks:
                break

            self.publish_cmd(0.0, self.turn_speed)
            rate.sleep()

        self.stop_robot()

    # =========================
    # Square Logic
    # =========================

    def move_square(self):
        rospy.loginfo("Starting square trajectory")

        for i in range(4):
            rospy.loginfo(f"Side {i+1}/4")
            self.move_straight(1.0)
            self.rotate_in_place(90)

        self.stop_robot()
        rospy.loginfo("Square completed")

    # =========================
    # Shutdown
    # =========================

    def on_shutdown(self):
        self.stop_robot()
        rospy.loginfo("Shutdown complete")


# =========================
# Main
# =========================

if __name__ == "__main__":
    try:
        node = ClosedLoopSquareNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
