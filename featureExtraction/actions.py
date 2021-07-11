import math
from enum import Enum
from utility.direction import get_bearings
from utility.stats import mean_sd_max_min

CURV_THRESHOLD = 0.0005


class ActionType(Enum):
    MM = "Mouse Move"
    PC = "Point and Click"
    DD = "Drag and Drop"


class MouseState(Enum):
    MOVED = "Move"
    DRAGGED = "Drag"
    PRESSED = "Pressed"
    RELEASED = "Released"


class MouseEvent:
    def __init__(self, time, x, y, button, state):
        self.time = float(time)
        self.x = float(x)
        self.y = float(y)
        self.button = button
        self.state = MouseState(state)

    def __str__(self):
        return f'Event occurred at time {self.time}s at ({self.x}, {self.y}), button {self.button} was {self.state}'


class MouseAction:
    def __init__(self, action_type, events):
        self.action_type = action_type
        self.events = events

        self.direction = None
        self.duration = self.trajectory = self.distance = self.straightness = self.n = self.sum_of_angles = self.max_deviation = 0
        self.mean_vx = self.sd_vx = self.max_vx = self.min_vx = 0
        self.mean_vy = self.sd_vy = self.max_vy = self.min_vy = 0
        self.mean_v = self.sd_v = self.max_v = self.min_v = 0
        self.mean_a = self.sd_a = self.max_a = self.min_a = 0
        self.mean_j = self.sd_j = self.max_j = self.min_j = 0
        self.mean_omega = self.sd_omega = self.max_omega = self.min_omega = 0
        self.mean_curv = self.sd_curv = self.max_curv = self.min_curv = 0

    def __str__(self):
        return f'Mouse Action: {self.action_type}\nNumber of Events: {len(self.events)}'

    def calculate_features(self):
        self.n = len(self.events)
        vx, vy, v, thetas, path = ([0] for _ in range(5))
        sum_of_angles = 0
        trajectory = 0

        for i in range(1, self.n):
            curr_event = self.events[i]
            prev_event = self.events[i - 1]

            dt = curr_event.time - prev_event.time

            # Displacements
            dx = curr_event.x - prev_event.x
            dy = curr_event.y - prev_event.y

            self.distance = math.sqrt((dx ** 2) + (dy ** 2))
            trajectory += self.distance
            path.append(trajectory)

            # Velocities
            vx_i = dx / dt
            vy_i = dy / dt
            v_i = math.sqrt((vx_i ** 2) + (vy_i ** 2))

            vx.append(vx_i)
            vy.append(vy_i)
            v.append(v_i)

            # Angles
            theta_i = math.atan2(dy, dx)
            thetas.append(theta_i)
            sum_of_angles += theta_i

        # Mean/St.Dev/Min/Max Velocities
        [self.mean_vx, self.sd_vx, self.max_vx, self.min_vx] = mean_sd_max_min(vx)
        [self.mean_vy, self.sd_vy, self.max_vy, self.min_vy] = mean_sd_max_min(vy)
        [self.mean_v, self.sd_v, self.max_v, self.min_v] = mean_sd_max_min(v)

        # Acceleration & Beginning Acceleration Time
        a = self.calculate_acceleration(self.n, v)
        # Mean/St.Dev/Min/Max Acceleration
        [self.mean_a, self.sd_a, self.max_a, self.min_a] = mean_sd_max_min(a)

        # Jerk
        j = self.calculate_jerk(a)
        # Mean/St.Dev/Min/Max Jerk
        [self.mean_j, self.sd_j, self.max_j, self.min_j] = mean_sd_max_min(j)

        # Angular Velocity
        omega = self.calculate_angular_velocity(thetas)
        # Mean/St.Dev/Min/Max Angular Velocity
        [self.mean_omega, self.sd_omega, self.max_omega, self.min_omega] = mean_sd_max_min(omega)

        # Curvature
        curvature = self.calculate_curvature(path, thetas)
        # Mean/St.Dev/Min/Max Curvature
        [self.mean_curv, self.sd_curv, self.max_curv, self.min_curv] = mean_sd_max_min(curvature)

        first_pt = self.events[0]
        last_pt = self.events[-1]

        # Duration
        self.duration = last_pt.time - first_pt.time

        # End-to-End distance
        self.distance = math.sqrt((last_pt.y - first_pt.y) ** 2 + (last_pt.x - first_pt.x) ** 2)

        # Straightness
        if self.trajectory == 0:
            self.straightness = 0
        else:
            self.straightness = self.distance / self.trajectory
        if self.straightness > 1:
            self.straightness = 1

        # Largest deviation from the end-to-end line
        self.max_deviation = self.largest_deviation(self.n)

        # Direction (-pi,...,pi)
        # theta = math.atan2((last_pt.y - first_pt.y), (last_pt.x - first_pt.x))
        # direction = compute_direction(theta)
        self.direction = get_bearings(first_pt, last_pt)

        # Generate CSV row
        return map(str, [self.action_type, self.duration, self.direction, self.trajectory, self.distance,
                         self.straightness, self.n, self.max_deviation, self.sum_of_angles,
                         self.mean_curv, self.sd_curv, self.max_curv, self.min_curv,
                         self.mean_omega, self.sd_omega, self.max_omega, self.min_omega,
                         self.mean_vx, self.sd_vx, self.max_vx, self.min_vx,
                         self.mean_vy, self.sd_vy, self.max_vy, self.min_vy,
                         self.mean_v, self.sd_v, self.max_v, self.min_v,
                         self.mean_a, self.sd_a, self.max_a, self.min_a,
                         self.mean_j, self.sd_j, self.max_j, self.min_j])

    def calculate_acceleration(self, n, v):
        a = [0]

        for i in range(1, n - 1):
            curr_event = self.events[i]
            prev_event = self.events[i - 1]
            dv = v[i] - v[i - 1]
            dt = curr_event.time - prev_event.time
            a_i = dv / dt
            a.append(a_i)
        return a

    def calculate_jerk(self, a):
        j = [0]
        for i in range(1, len(a)):
            curr_event = self.events[i]
            prev_event = self.events[i - 1]
            j_i = a[i] - a[i - 1] / (curr_event.time - prev_event.time)
            j.append(j_i)
        return j

    def calculate_angular_velocity(self, theta):
        omega = [0]
        for i in range(1, len(theta)):
            curr_event = self.events[i]
            prev_event = self.events[i - 1]
            dtheta = theta[i] - theta[i - 1]
            dt = curr_event.time - prev_event.time
            omega_i = dtheta / dt
            omega.append(omega_i)
        return omega

    def calculate_curvature(self, path, theta):
        curvature = [0]
        num_critical_points = 0
        for i in range(1, len(path)):
            dp = path[i] - path[i - 1]
            if dp == 0:
                continue
            dtheta = theta[i] - theta[i - 1]
            curv_i = dtheta / dp
            curvature.append(curv_i)
            if abs(curv_i) < CURV_THRESHOLD:
                num_critical_points += 1
        return curvature

    def largest_deviation(self, n):
        first_pt = self.events[0]
        last_pt = self.events[-1]

        # Form equation of a line ax + by + c = 0
        a = first_pt.y - last_pt.y
        b = last_pt.x - first_pt.x
        c = (first_pt.x * last_pt.y) - (last_pt.x * first_pt.y)

        max_distance = 0
        denominator = math.sqrt((a ** 2) + (b ** 2))
        for i in range(1, n - 1):
            pt = self.events[i]
            # distance from point to line (ax+by+c)/(a^2+b^2)
            distance = math.fabs((a * pt.x) + (b * pt.y) + c)
            if distance > max_distance:
                max_distance = distance
            if denominator > 0:
                max_distance /= denominator

        return max_distance
