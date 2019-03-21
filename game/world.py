from math import sin, cos, tan, pi
from random import random
from typing import Tuple

from . import single_frame_actions, physics_object

class Borders:
    LEFT, TOP, RIGHT, BOTTOM = range(4)

class World():
    def __init__(self):
        self._player_maximum_thrust = 0.3

        self._player_base_friction = 0.01
        self._player_thrust_extra_friction = 0.05

        self._player_maximum_turn_thrust = 0.005
        self._thrust_extra_turn_thrust = -0.001
        self._base_rotational_friction = 0.1
        self._thrust_extra_rotational_friction = 0.1
        self._player_ship = physics_object.PhysicsObject(x=50,y=50)
        self._player_controller = None

        self._asteroids = self._create_starting_asteroids()

    def update(self, player_actions : single_frame_actions.SingleFrameActions):
        self._player_ship.rotational_velocity = self._player_ship.rotational_velocity + player_actions.turn_speed * (self._player_maximum_turn_thrust + self._thrust_extra_turn_thrust * player_actions.thrust)
        self._player_ship.friction = self._player_base_friction + self._player_thrust_extra_friction * player_actions.thrust

        player_forward_vector = [sin(self._player_ship.rotation), cos(self._player_ship.rotation)]
        self._player_ship.velocity = [respective_velocity + player_actions.thrust * self._player_maximum_thrust * respective_player_forward_vector for respective_velocity, respective_player_forward_vector in zip(self._player_ship.velocity, player_forward_vector)]
        self._player_ship.rotational_friction = self._base_rotational_friction + self._thrust_extra_rotational_friction * player_actions.thrust
        self._player_ship.update()

        for asteroid in self._asteroids:
            asteroid.update()

    def add_player(self, player_controller):
        self._player_controller = player_controller

    @property
    def player(self):
        return self._player_ship

    @property
    def asteroids(self):
        return self._asteroids

    def _create_starting_asteroids(self):
        return [self._create_single_asteroid() for x in range(5)]

    def _find_border_from_center(self, clockwise_angle_from_right : float) -> Tuple[int, Tuple[float, float]]:
        left_border_x = 0
        right_border_x = 800
        bottom_border_y = 0
        top_border_y = 600

        if clockwise_angle_from_right > pi:
            dydx = tan(clockwise_angle_from_right)
            # line: x = my + c
            # m = dydx
            # c = x - my for x:400, y:300
            c = (right_border_x / 2) - dydx * (top_border_y / 2)

            # resolve upwards
            # target: y = top_border_y
            # x = c + top_border_y * dydx
            x = c + top_border_y * dydx
            if x > left_border_x and x < right_border_x:
                return (Borders.BOTTOM, (x, bottom_border_y))
            elif x <= left_border_x:
                # 0 = dydx * y + c
                # -c / dydx = y
                left_wall_intersect = -c / dydx
                return (Borders.LEFT, (left_border_x, left_wall_intersect))
            else:
                # right_border_x = dydx * y + c
                # (right_border_x - c) / dydx = y
                right_wall_intersect = (right_border_x - c) / dydx
                return (Borders.RIGHT, (right_border_x, right_wall_intersect))
        elif clockwise_angle_from_right < pi and clockwise_angle_from_right > 0:
            dydx = tan(clockwise_angle_from_right)
            # line: x = my + c
            # m = dydx
            # c = x - my for x:400, y:300
            c = (right_border_x / 2) - dydx * (top_border_y / 2)

            # resolve downwards
            # target: y = 0 
            # x = c
            if c > left_border_x and c < right_border_x:
                return (Borders.BOTTOM, (c, bottom_border_y))
            elif c <= left_border_x:
                # 0 = dydx * y + c
                # -c / dydx = y
                left_wall_intersect = -c / dydx
                return (Borders.LEFT, (left_border_x, left_wall_intersect))
            else:
                # right_border_x = dydx * y + c
                # (right_border_x - c) / dydx = y
                right_wall_intersect = (right_border_x - c) / dydx
                return (Borders.RIGHT, (right_border_x, right_wall_intersect))
        elif clockwise_angle_from_right is 0:
            return (Borders.RIGHT, (right_border_x, top_border_y / 2))
        else:
            return (Borders.LEFT, (left_border_x, top_border_y / 2))

    def _create_single_asteroid(self):
        direction = random() * 2 * pi

        border_collided_with, collision_point = self._find_border_from_center(direction)
        
        # place asteroid beyond border
        asteroid_width = 50
        border_offsets = {
            Borders.LEFT: (-asteroid_width, 0),
            Borders.TOP: (0, asteroid_width),
            Borders.RIGHT: (asteroid_width, 0),
            Borders.BOTTOM: (0, -asteroid_width)
        }

        border_offset = border_offsets[border_collided_with]

        asteroid_spawn_location = tuple(collision_coordinate + offset_coordinate for collision_coordinate, offset_coordinate in zip(collision_point, border_offset))

        # make asteroids fly in
        asteroid_speed = 1
        def create_velocity_generator(start_angle, end_angle):
            angle_range = end_angle - start_angle
            def generate_velocity():
                chosen_angle = start_angle + random() * angle_range
                return (sin(chosen_angle) * asteroid_speed, cos(chosen_angle) * asteroid_speed)
            return generate_velocity
        border_velocity_generators = {
            Borders.LEFT: create_velocity_generator    (-1 * pi / 2, 1 * pi / 2),
            Borders.TOP: create_velocity_generator     ( 1 * pi / 2, 3 * pi / 2),
            Borders.RIGHT: create_velocity_generator   ( 3 * pi / 2, 5 * pi / 2),
            Borders.BOTTOM: create_velocity_generator  ( 5 * pi / 2, 7 *pi / 2)
        }
        velocity = border_velocity_generators[border_collided_with]()

        max_rotational_velocity = 0.01
        new_asteroid = physics_object.PhysicsObject(
            x=asteroid_spawn_location[0], y=asteroid_spawn_location[1],
            x_velocity=velocity[0], y_velocity=velocity[1],
            friction=0,
            rotation=random() * pi * 2,
            rotational_velocity= (random() * 2 - 1) * max_rotational_velocity,
            rotational_friction=0
        )
        return new_asteroid