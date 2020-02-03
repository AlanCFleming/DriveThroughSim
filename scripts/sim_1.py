#!/usr/bin/python3
import random
import simpy

def example(env):
    event = simpy.events.Timeout(env, delay=5, value=42)
    value = yield event
    print('now=%d, value=%d' % (env.now, value))

#setup env
env = simpy.Environment()
example_gen = example(env)
#setup resources
orderA = simpy.Resource(env capacity=1)
orderB = simpy.Resource(env capacity=1)
pickup = simpy.Resource(env capacity=1)
#create the process
p = simpy.events.Process(env, example_gen)
#run the env
env.run()
