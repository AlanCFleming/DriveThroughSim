#!/usr/bin/python3
import random
import simpy


random_seed = 5

pickup_length = 5
order_length = 3

mean_order_time = 2
mean_prep_time = 5
mean_collect_time = 2

mean_AR = 2;

#count of cars total and cars left
count = 0
left = 0

def cargen(env, time, orderA, orderB,lineP, pickup):
    
    global count, left
    
    #generate cars during time frame
    while(time >= env.now):
        #make and start a car
        count += 1
        c = car(env, count, orderA, orderB,lineP, pickup)
        env.process(c)
        #wait to make another
        t = t = random.expovariate(1.0 / mean_AR)
        yield env.timeout(t)


#car to go through the line
def car(env, number, orderA, orderB, lineP, pickup):
    arrival_time = env.now #gets arrival time

    #checks if the car leaves or stays due to line length.
    if(len(orderA.queue) >  order_length and len(orderB.queue) > order_length): 
        print("%7.4f: %s left without ordering" % (env.now, number)) 
        left += 1
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

        #print time taken 
        print("%7.4f: %s left after %s minutes" % (env.now, number, env.now - arrival_time))



#setup env
env = simpy.Environment()
#setup resources
##ordering recources
orderA = simpy.Resource(env, capacity=1)
orderB = simpy.Resource(env, capacity=1)
##pickup resources
pickup = simpy.Resource(env, capacity=1)
lineP = simpy.Resource(env, capacity=6)
#create the process
generator = cargen(env,120 ,orderA ,orderB,lineP, pickup)
p = simpy.events.Process(env, generator)
#seed the random number gen
random.seed(random_seed)
#run the env
env.run()
