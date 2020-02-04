#!/usr/bin/python3
import random
import simpy


random_seed = 42

pickup_length = 5
order_length = 4

mean_order_time = 2
mean_prep_time = 5
mean_collect_time = 2

mean_AR = 2;

def cargen(env, number, lineA, lineB, pickup):
    #for loop to generate "number" cars
    for i in range(number):
        #make and start car
        c = car(env, i, lineA, lineB, pickup)
        env.process(c)
        #wait to make another
        t = t = random.expovariate(1.0 / mean_AR)
        yield env.timeout(t)


#car to go through the line
def car(env, number, lineA, lineB, pickup):
    arrival_time = env.now #gets arrival time

    #checks if the car leaves or stays due to line length.
    if(len(lineA.users) >  order_length and len(lineB.users) > order_length): 
        print("%7.4f: %s left without ordering" % (env.now, number)) 
    else:
        #assigns the shortest line to the car
        lineA = len(lineA.users) < len(lineB.users) 
        
        #make the car join the line it picked and wait until it gets to order
        if lineA:
            line = lineA.request()
            order = orderA.request()
        else:
            line = lineB.request()
            order = orderB.request()
        yield line
        yield order
        #random number for wait time
        order_time = random.expovariate(1.0 / mean_order_time)
        yield env.timeout(order_time)

        #get time order is done
        prep_time = (env.now + random.expovariate(1.0 / mean_prep_time) )
        
        if lineA:
            orderA.release(order)
        else:
            orderB.release(order)

        #check to see if you can move up
        while(len(pickup.queue) > pickup_length):
            #if the line is full, check again later
            yield env.timeout(1)

        #take a spot in the pickup line and leave the order line
        if lineA:
            lineA.release(line)
        else:
            lineB.release(line
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
##lines for ordering (use users instead of queue to get list of cars in line)
lineA = simpy.Resource(env, capacity=5)
lineB = simpy.Resource(env, capacity=5)
##order personel
orderA = simpy.Resource(env, capacity=1)
orderA = simpy.Resource(env, capacity=1)
##pickup window line
pickup = simpy.Resource(env, capacity=1)
#create the process
generator = cargen(env,100 ,lineA ,lineB, pickup)
p = simpy.events.Process(env, generator)
#seed the random number gen
random.seed(random_seed)
#run the env
env.run()
