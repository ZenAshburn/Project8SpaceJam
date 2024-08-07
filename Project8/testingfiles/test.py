import random

def PlanetPicker():
    planet = "Planet" + str(random.randint(1, 7))

    print(planet)

randomObject = PlanetPicker()