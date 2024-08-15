import random
import hashlib
import math
#from math import sqrt


def consistent_color_generator(text: str) -> str: # pseudo-randomization function
    h = hashlib.md5(text.encode()).hexdigest()
    rand_gen = random.Random(h) # create random generator object

    r = rand_gen.randint(0, 255) # generate random RGB values
    g = rand_gen.randint(0, 255)
    b = rand_gen.randint(0, 255)

    return f'#{r:02x}{b:02x}{g:02x}'

def consistent_blue_generator(text: str, factor=0.5) -> str: # pseudo-randomization function
    h = hashlib.md5((text + "_insp").encode()).hexdigest()
    rand_gen = random.Random(h) # create random generator object
    
    f = lambda x: 1 / (1 + math.exp(-(x-255/2)/50))

    rand_list = [rand_gen.randint(0, 255)]
    rand_list.append(255*(1-f(sum(rand_list))) + rand_gen.randint(0, 255)*f(sum(rand_list)))
    rand_list.append(255*(1-f(sum(rand_list))) + rand_gen.randint(0, 255)*f(sum(rand_list)))

    rand_gen.shuffle(rand_list)

    r = 255*factor + rand_list[0]*(1-factor)
    b = 255*f(r) + rand_list[1]*(1-f(r))
    g = 255*f(b) + rand_list[2]*(1-f(b))

    return f'#{int(r):02x}{int(b):02x}{int(g):02x}'

def consistent_pastel_color_generator(text: str, factor=0.5) -> str: # pseudo-randomization function
    h = hashlib.md5((text + "_insp").encode()).hexdigest()
    rand_gen = random.Random(h) # create random generator object
    f = lambda x: 1 / (1 + math.exp(-(x-255/2)/50))

    rand_list = [rand_gen.randint(0, 255)]
    rand_list.append(255*(1-f(sum(rand_list))) + rand_gen.randint(0, 255)*f(sum(rand_list)))
    rand_list.append(255*(1-f(sum(rand_list))) + rand_gen.randint(0, 255)*f(sum(rand_list)))

    rand_gen.shuffle(rand_list)

    r = 255*factor + rand_list[0]*(1-factor)
    b = 255*factor + rand_list[1]*(1-factor)
    g = 255*factor + rand_list[2]*(1-factor)

    return f'#{int(r):02x}{int(b):02x}{int(g):02x}'