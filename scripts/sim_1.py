#!/usr/bin/python3
import random
import simpy


random_seed = 42
mean_order_time = 2
mean_prep_time = 5
mean_collect_time = 2

def example(env):
    event = simpy.events.Timeout(env, delay=5, value=42)
    value = yield event
    print('now=%d, value=%d' % (env.now, value))

#car to go through the line
def car(env, number, orderA, orderB, pickup)
    arrival_time = env.now() #gets arrival time

    #checks if the car leaves or stays
    if(len(orderA.queue) > 3 && len(orderB.queue) > 3) # checks if both order windows are full. 4 people waiting is full.
        print("%7.4f: %s left without ordering" % (env.now, number)); #prints time the car left
    else
        line = orderA if (len(orderA.queue) < len(orderB.queue)) else orderB #assigns the shortest line to the car
        
        #make the car join the line it picked
        yield line.request # wait until it gets to the oder window
        order_time = random.expovariate(1.0 / mean_order_time) 
        line.release(line)

#setup env
env = simpy.Environment()
example_gen = example(env)
#setup resources
orderA = simpy.Resource(env capacity=1)
orderB = simpy.Resource(env capacity=1)
pickup = simpy.Resource(env capacity=1)
#create the process
p = simpy.events.Process(env, example_gen)
#seed the random number gen
random.seed(random_seed)
#run the env
env.run()
