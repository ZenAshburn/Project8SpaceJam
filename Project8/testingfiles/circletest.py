import math

placeholder = 0
radius = 10
numDrones = 30

for i in range(numDrones):

    theta = placeholder

    x = (math.cos(theta)) * radius
    y = (math.sin(theta)) * 0
    z = (math.tan(theta)) * radius

    print(x, y, z)

    placeholder += math.radians(360/numDrones)
