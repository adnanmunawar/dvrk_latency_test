# Adnan Munawar
# Testing Robot IO Loading with varying ROS Communication Load

from dvrk import arm, psm, mtm, ecm
import rospy
from geometry_msgs.msg import PoseStamped
import time
from threading import Thread
from cisst_msgs.msg import mtsIntervalStatistics as StatsMsg


class stats(object):
    def __init__(self):
        rospy.init_node('dvrk_load_test')
        self._rate = rospy.Rate(1000)
        self._userDataScale = 10
        self._active = True

        self._stat_msg = StatsMsg
        self._statsTopicPubStr = '/dvrk/rosBridge/period_statistics/user'
        self._statsTopicSubStr = '/dvrk/rosBridge/period_statistics'

        self._pub = rospy.Publisher(self._statsTopicPubStr, StatsMsg, queue_size=10)
        self._sub = rospy.Subscriber(self._statsTopicSubStr, StatsMsg, self._ros_cb, queue_size=10, tcp_nodelay=True)

        self._pubThread = Thread(target=self._run_pub)
        self._pubThread.daemon = True
        self._pubThread.start()

    def set_user_data(self, n_arms):
        self._stat_msg.UserData = n_arms * self._userDataScale
        pass

    def clear_user_data(self):
        self._stat_msg.UserData = 0
        pass

    def disconnect(self):
        self._active = False

    def _ros_cb(self, data):
        self._stat_msg = data
        pass

    def _run_pub(self):
        while not rospy.is_shutdown() and self._active:
            self._pub.publish(self._stat_msg)
            self._rate.sleep()


class dvrk_latency_test(stats):
    def __init__(self):
        super(dvrk_latency_test, self).__init__()
        self.psmInterface = psm
        self.mtmInterface = mtm
        self.ecmInterface = ecm
        self.arm_dict = {'PSM1': self.psmInterface,
                         'PSM2': self.psmInterface,
                         'PSM3': self.psmInterface,
                         'MTMR': self.mtmInterface,
                         'MTML': self.mtmInterface,
                         'ECM' : self.ecmInterface}
        self.activeArms = []

    def create_arm_load(self, n_arms, delay = 0.0):
        self._is_narm_valid(n_arms, self.arm_dict.__len__(), 1)
        indx = 0
        for armStr, armIrce in self.arm_dict.iteritems():
            armIrce = armIrce(armStr)
            self.activeArms.append(armIrce)
            indx += 1
            self.set_user_data(self.activeArms.__len__())
            print 'Connecting ROS Client for {}'.format(armIrce.name())
            time.sleep(delay)
            if indx == n_arms:
                break

    def relieve_arm_load(self, n_arms=None, delay = 0.0):
        n_active_arms = self.activeArms.__len__()

        if n_arms is None:
            n_arms = n_active_arms

        self._is_narm_valid(n_arms, n_active_arms)
        for i in range(n_arms):
            armIrfc = self.activeArms.pop()
            armIrfc.unregister()
            self.set_user_data(self.activeArms.__len__())
            print 'Disconnecting ROS Client for {}'.format(armIrfc.name())
            time.sleep(delay)

    def _is_narm_valid(self, n_arms, max_num=6, min_num=0):
        if n_arms < min_num or n_arms > max_num:
            raise ValueError('num_arms cannot be negative or greater than {}'.format(max_num))
