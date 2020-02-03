#!/usr/bin/python3
import random
import simpy

def example(env):
    event = simpy.events.Timeout(env, delay=5, value=42)
    value = yield event
    print('now=%d, value=%d' % (env.now, value))

env = simpy.Environment()
example_gen = example(env)
p = simpy.events.Process(env, example_gen)

env.run()
