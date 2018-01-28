from dvrk_latency_test import dvrk_latency_test as latency_test
import time

latTest = latency_test()
latTest.create_arm_load(6, delay=0.5)
time.sleep(5)
latTest.relieve_arm_load(delay=0.5)
time.sleep(5)
latTest.disconnect()