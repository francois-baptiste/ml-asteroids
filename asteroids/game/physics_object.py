import math
import numpy as np

class PhysicsObject():
    def __init__(self, 
            x:float=0,y:float=0,
            x_velocity:float=0,y_velocity:float=0,
            rotation:float=0,
            rotational_velocity:float=0,
            friction:float=0.01,
            rotational_friction:float=0.02
    ):
        self.position = np.array([x,y])
        self.velocity = np.array([x_velocity,y_velocity])
        self.rotation = rotation
        self.rotational_velocity = rotational_velocity
        self.friction = friction
        self.rotational_friction = rotational_friction

    def update(self):
        self.position = self.position + self.velocity
        self.velocity = self.velocity * (1 - self.friction)

        new_rotation = self.rotation + self.rotational_velocity
        self.rotation = new_rotation % (2 * math.pi)

        self.rotational_velocity = self.rotational_velocity * (1 - self.rotational_friction)
