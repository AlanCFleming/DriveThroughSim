#!/usr/bin/python3
import random
import simpy


random_seed = 42

pickup_length = 5
order_length = 3

mean_order_time = 2
mean_prep_time = 5
mean_collect_time = 2

mean_AR = 2;

def cargen(env, number, orderA, orderB, pickup):
    #for loop to generate "number" cars
    for i in range(number):
        #make and start car
        c = car(env, i, orderA, orderB, pickup)
        env.process(c)
        #wait to make another
        t = t = random.expovariate(1.0 / mean_AR)
        yield env.timeout(t)


#car to go through the line
def car(env, number, orderA, orderB, pickup):
    arrival_time = env.now #gets arrival time

    #checks if the car leaves or stays due to line length.
    if(len(orderA.queue) >  order_length and len(orderB.queue) > order_length): 
        print("%7.4f: %s left without ordering" % (env.now, number)) 
    else:
        #assigns the shortest line to the car
        lineA = len(orderA.queue) < len(orderB.queue) 
        
        #make the car join the line it picked and wait until it gets to order
        if lineA:
            line = orderA.request()
        else:
            line =orderB.request()
        yield line
        #random number for wait time
        order_time = random.expovariate(1.0 / mean_order_time)
        yield env.timeout(order_time)

        #get time order is done
        prep_time = (env.now + random.expovariate(1.0 / mean_prep_time) )
        

        #check to see if you can move up
        while(len(pickup.queue) > pickup_length):
            #if the line is full, check again later
            yield env.timeout(1)

        #take a spot in the pickup line and leave the order line
        if lineA:
            orderA.release(line)
        else:
            orderB.release(line)
        line = pickup.request()
        yield line

        #random number for wait time
        order_time = random.expovariate(1.0 / mean_collect_time) 
        yield env.timeout(order_time)

        #wait for order if needed
        if(env.now < prep_time):
            env.timeout(prep_time - env.now)
        pickup.release(line)

        #print time taken 
        print("%7.4f: %s left after %s minutes" % (env.now, number, env.now - arrival_time))



#setup env
env = simpy.Environment()
#setup resources
orderA = simpy.Resource(env, capacity=1)
orderB = simpy.Resource(env, capacity=1)
pickup = simpy.Resource(env, capacity=1)
#create the process
generator = cargen(env,100 ,orderA ,orderB, pickup)
p = simpy.events.Process(env, generator)
#seed the random number gen
random.seed(random_seed)
#run the env
env.run()
