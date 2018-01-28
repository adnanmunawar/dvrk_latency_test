# Adnan Munawar
# Testing Robot IO Loading with varying ROS Communication Load

from dvrk import arm, psm, mtm, ecm
import rospy
from geometry_msgs.msg import PoseStamped
import time
import thread


class dvrk_latency_test():
    def __init__(self):
        self.psmInterface = psm
        self.mtmInterface = mtm
        self.ecmInterface = ecm
        self.statsTopicStr = '/dvrk/Statistics/'
        self.psmTopicStr = '/dvrk/PSM1/cartesian_position_current'
        self.pub = None
        self.poseData = PoseStamped()
        self.threadPub = None
        self.arm_dict = {'PSM1': self.psmInterface,
                         'PSM2': self.psmInterface,
                         'PSM3': self.psmInterface,
                         'MTMR': self.mtmInterface,
                         'MTML': self.mtmInterface,
                         'ECM' : self.ecmInterface}
        self.activeArms = []

        self.sub = rospy.Subscriber(self.psmTopicStr, PoseStamped, self.ros_cb, 10)

    def create_arm_load(self, n_arms):
        self._is_narm_valid(n_arms, self.arm_dict.__len__(), 1)
        indx = 0
        for armStr, armIrce in self.arm_dict.iteritems():
            armIrce(armStr)
            self.activeArms.append(armIrce)
            indx += 1
            print 'Activating ROS Client for {}'.format(armStr)
            if indx == n_arms:
                break

    def relieve_arm_load(self, n_arms=None):
        n_active_arms = self.activeArms.__len__()

        if n_arms is None:
            n_arms = n_active_arms

        self._is_narm_valid(n_arms, n_active_arms)
        for i in range(n_arms):
            armIrfc = self.activeArms.pop()
            print 'Removing ROS Client for {}'.format(armIrfc)
            armIrfc = None # clearing arm interface handle

    def _is_narm_valid(self, n_arms, max_num=5, min_num=0):
        if n_arms < min_num or n_arms > max_num:
            raise ValueError('num_arms cannot be negative or greater than {}'.format(max_num))

    def ros_cb(self, data):

        pass


latTest = dvrk_latency_test()
latTest.create_arm_load(3)
time.sleep(3)
latTest.relieve_arm_load(2)
