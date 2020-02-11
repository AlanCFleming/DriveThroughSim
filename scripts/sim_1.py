#!/usr/bin/python3
import random
import simpy

#USER VARIABLES:
random_seed = 1024
runtime = 120

pickup_length = 5
order_length = 3

mean_order_time = 2
mean_prep_time = 5
mean_collect_time = 2

mean_AR = 5

##CODE:

def cargen(env, time, orderA, orderB,lineP, pickup, running, count, left):
    #offset for starting time time
    start = env.now

    #spin up generator
    #generate cars for user specified time without stats
    while((start + time) >= env.now):
        #make and start a car
        running.put(1)
        c = car(env, 0, orderA, orderB,lineP, pickup, running, left)
        env.process(c)
        #wait to make another
        t = t = random.expovariate(1.0 / mean_AR)
        yield env.timeout(t)
    #clear left statistics
    if(left.level < 0):
        left.get(left.level)

    #generate additional cars for user specified time with stats
    while((start + 2*time) >= env.now):
        #make and start a car
        count.put(1)
        running.put(1)
        c = car(env, count.level, orderA, orderB,lineP, pickup, running, left)
        env.process(c)
        #wait to make another
        t = t = random.expovariate(1.0 / mean_AR)
        yield env.timeout(t)
    
    while(running.level>  0):
        yield env.timeout(1)


#car to go through the line
def car(env, number, orderA, orderB, lineP, pickup, running, left):
    #gets arrival time
    arrival_time = env.now

    #checks if the car leaves or stays due to line length.
    if(len(orderA.queue) >  order_length and len(orderB.queue) > order_length): 
        #print("%7.4f: %s left without ordering" % (env.now, number)) 
        left.put(1)
        running.get(1)
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
        

        #grab a spot in line to pickup
        pLine = lineP.request()
        yield pLine

        
        #leave order line and wait to pickup order
        if lineA:
            orderA.release(line)
        else:
            orderB.release(line)
        line = pickup.request()
        yield line

        #leave pickup line to pickup order
        lineP.release(pLine)

        #random number for wait time
        order_time = random.expovariate(1.0 / mean_collect_time) 
        yield env.timeout(order_time)

        #wait for order if needed
        if(env.now < prep_time):
            yield env.timeout(prep_time - env.now)
        pickup.release(line)

        #take running resource
        running.get(1)

        #print time taken 
        #print("%7.4f: %s left after %s minutes" % (env.now, number, env.now - arrival_time))

#setup environment
env = simpy.Environment()
#setup resources
##ordering recources
orderA = simpy.Resource(env, capacity=1)
orderB = simpy.Resource(env, capacity=1)
##pickup resources
pickup = simpy.Resource(env, capacity=1)
lineP = simpy.Resource(env, capacity=6)
#setup counting resources
running = simpy.Container(env)
count = simpy.Container(env)
left = simpy.Container(env)
#first run boolean
first = True

#print table headers
print(f'%7s , %7s , %7s , %7s' % ( "AR","Count","Left","Left/Count"))

#Run until more than 50% of cars leave
while(first or (left.level/count.level < .5)):
    #clear the first run boolean 
    first = False

    #clear counting resources
    running = simpy.Container(env)
    count = simpy.Container(env)
    left = simpy.Container(env)

    #create the process
    generator = cargen(env, runtime ,orderA ,orderB,lineP, pickup, running, count, left)
    p = simpy.events.Process(env, generator)
    #seed the random number gen
    random.seed(random_seed)
    #run the env
    env.run()
    #print stats
    print(f'%3.5f , %7d , %7d , %1.6f' %(mean_AR, count.level, left.level, left.level/count.level))
    #lower AR
    mean_AR = mean_AR - 0.125
