#!/usr/bin/python3
import random
import simpy

##USER VARIABLES:
random_seed = 1024
runtime = 120

pickup_length = 5
order_length = 4

mean_order_time = 1.5
mean_prep_time = 5
mean_collect_time = 1

mean_AR = 5

##CODE:
def cargen(env, time, lineA, lineB, orderA, orderB, lineP, pickup,running,count,left):
    start = env.now
    
    #spool up car gen to get better average:
    #generate cars for user specified time without stats
    while((start + time) >= env.now):
        #make and start car
        running.put(1)
        c = car(env, count.level, lineA, lineB, orderA, orderB,lineP, pickup)
        env.process(c)
        #wait to make another
        t = t = random.expovariate(1.0 / mean_AR)
        yield env.timeout(t)

    #clear left counter if needed
    if(left.level > 0):
        left.get(left.level)

    #generate additional cars for user specified time with stats
    while((start + 2*time) >= env.now):
        #make and start car
        count.put(1)
        running.put(1)
        c = car(env, count.level, lineA, lineB, orderA, orderB,lineP, pickup)
        env.process(c)
        #wait to make another
        t = t = random.expovariate(1.0 / mean_AR)
        yield env.timeout(t)
    
    while(running.level > 0):
        yield env.timeout(1)


#car to go through the line
def car(env, number, lineA, lineB, orderA, orderB,lineP, pickup):
    arrival_time = env.now #gets arrival time

    #checks if the car leaves or stays due to line length.
    if(len(lineA.users) >  order_length and len(lineB.users) > order_length): 
        #print("%7.4f: %s left without ordering" % (env.now, number))
        left.put(1)
        running.get(1)
    else:
        #assigns the shortest line to the car
        aShort = len(lineA.users) < len(lineB.users) 
        
        #make the car join the line it picked and wait until it gets to order
        if aShort:
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
       
        #print("car %s will get its food at %7.4f" % (number, prep_time))

        if aShort:
            orderA.release(order)
        else:
            orderB.release(order)

        #wait to move into pickup line
        pLine = lineP.request()
        yield pLine

        #take a spot in the pickup line and leave the order line
        if aShort:
            lineA.release(line)
        else:
            lineB.release(line)
        line = pickup.request()
        yield line

        #release pLine
        lineP.release(pLine)

        #random number for wait time
        order_time = random.expovariate(1.0 / mean_collect_time) 
        yield env.timeout(order_time)

        #wait for order if needed
        if(env.now < prep_time):            
            yield env.timeout(prep_time - env.now)
        pickup.release(line)
        
        running.get(1)

        #print time taken 
        #print("%7.4f: %s left after %s minutes" % (env.now, number, env.now - arrival_time))



#setup env
env = simpy.Environment()
#setup resources
##lines for ordering (use users instead of queue to get list of cars in line)
lineA = simpy.Resource(env, capacity=5)
lineB = simpy.Resource(env, capacity=5)
##order personel
orderA = simpy.Resource(env, capacity=1)
orderB = simpy.Resource(env, capacity=1)
##pickup window
lineP = simpy.Resource(env, capacity=6)
pickup = simpy.Resource(env, capacity=1)

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
    generator = cargen(env, runtime ,lineA ,lineB, orderA, orderB,lineP, pickup, running, count, left)
    p = simpy.events.Process(env, generator)
    #seed the random number gen
    random.seed(random_seed)
    #run the env
    env.run()
    #print stats
    print(f'%3.5f , %7d , %7d , %1.6f' %(mean_AR, count.level, left.level, left.level/count.level))

    mean_AR = mean_AR - 0.125 
