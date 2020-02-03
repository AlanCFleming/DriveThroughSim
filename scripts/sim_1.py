#!/usr/bin/python3
import random
import simpy


random_seed = 42

pickup_length = 5
order_length = 3

mean_order_time = 2
mean_prep_time = 5
mean_collect_time = 2

mean_AR = 5;

def example(env):
    event = simpy.events.Timeout(env, delay=5, value=42)
    value = yield event
    print('now=%d, value=%d' % (env.now, value))

#car to go through the line
def car(env, number, orderA, orderB, pickup):
    arrival_time = env.now #gets arrival time

    #checks if the car leaves or stays due to line length.
    if(len(orderA.queue > order_length) and len(orderB.queue) order_length): 
        print("%7.4f: %s left without ordering" % (env.now, number)) 
    else:
        #assigns the shortest line to the car
        line = orderA if (len(orderA.queue) < len(orderB.queue)) else orderB 
        
        #make the car join the line it picked and wait until it gets to order
        yield line.request 
        #random number for wait time
        order_time = random.expovariate(1.0 / mean_order_time)
        yield env.timeout(order_time)

        #get time order is done
        prep_time = (env.now() + random.expovariate(1.0 / mean_prep_time) )
        

        #check to see if you can move up
        while(len(pickup) > pickup_length):
            pass

        #take a spot in the pickup line and leave the order line
        pickup.release(line)
        yield pickup.request

        #random number for wait time
        order_time = random.expovariate(1.0 / mean_collect_time) 
        yield env.timeout(oder_time)

        #wait for order if needed
        while(env.now() < perp_time):
            pass
        pickup.release(pickup)

        #print time taken 
        print("%7.4f: %s left after %s minutes" % (env.now, number, env.now - arrival_time))

#setup env
env = simpy.Environment()
example_gen = example(env)
#setup resources
orderA = simpy.Resource(env, capacity=1)
orderB = simpy.Resource(env, capacity=1)
pickup = simpy.Resource(env, capacity=1)
#create the process
p = simpy.events.Process(env, example_gen)
#seed the random number gen
random.seed(random_seed)
#run the env
env.run()
