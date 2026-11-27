from oak9 import Robot

robot = Robot("172.20.10.12")

print([m for m in dir(robot.motor) if not m.startswith("_")])
print([m for m in dir(robot) if not m.startswith("_")])

robot.close()