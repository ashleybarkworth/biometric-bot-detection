import math
import statistics
from enum import Enum
from utility.direction import get_bearings

CURV_THRESHOLD = 0.0005


def mean_std_max_min(array):
    # Average
    mean = statistics.mean(array)
    # Standard deviation
    st_dev = statistics.stdev(array)
    # Maximum value
    max_value = max(array)
    # Minimum value (excluding initial 0 value)
    min_value = min(array[1:])
    return [mean, st_dev, max_value, min_value]


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


def compute_direction(theta):
    direction = 0
    if 0 <= theta < math.pi / 4:
        direction = 0
    if math.pi / 4 <= theta < math.pi / 2:
        direction = 1
    if math.pi / 2 <= theta < 3 * math.pi / 4:
        direction = 2
    if 3 * math.pi / 4 <= theta < math.pi:
        direction = 3
    if -math.pi / 4 <= theta < 0:
        direction = 7
    if -math.pi / 2 <= theta < -math.pi / 4:
        direction = 6
    if -3 * math.pi / 4 <= theta < -math.pi / 2:
        direction = 5
    if -math.pi <= theta < -3 * math.pi / 4:
        direction = 4
    return direction


class MouseAction:
    def __init__(self, action_type, events):
        self.action_type = action_type
        self.events = events

    def __str__(self):
        return f'Mouse Action: {self.action_type}\nNumber of Events: {len(self.events)}'

    def calculate_features(self):
        n = len(self.events)
        vx, vy, v, thetas, path = ([0] for i in range(5))
        sum_of_angles = 0
        trajectory = 0

        for i in range(1, n):
            curr_event = self.events[i]
            prev_event = self.events[i - 1]

            dt = curr_event.time - prev_event.time

            # Displacements
            dx = curr_event.x - prev_event.x
            dy = curr_event.y - prev_event.y

            distance = math.sqrt((dx ** 2) + (dy ** 2))
            trajectory += distance
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
        [mean_vx, sd_vx, max_vx, min_vx] = mean_std_max_min(vx)
        [mean_vy, sd_vy, max_vy, min_vy] = mean_std_max_min(vy)
        [mean_v, sd_v, max_v, min_v] = mean_std_max_min(v)

        # Acceleration & Beginning Acceleration Time
        a, beginning_acceleration_time = self.calculate_acceleration(n, v)
        # Mean/St.Dev/Min/Max Acceleration
        [mean_a, sd_a, max_a, min_a] = mean_std_max_min(a)

        # Jerk
        j = self.calculate_jerk(a)
        # Mean/St.Dev/Min/Max Jerk
        [mean_j, sd_j, max_j, min_j] = mean_std_max_min(j)

        # Angular Velocity
        omega = self.calculate_angular_velocity(thetas)
        # Mean/St.Dev/Min/Max Angular Velocity
        [mean_omega, sd_omega, max_omega, min_omega] = mean_std_max_min(omega)

        # Curvature
        curvature = self.calculate_curvature(path, thetas)
        # Mean/St.Dev/Min/Max Curvature
        [mean_curv, sd_curv, max_curv, min_curv] = mean_std_max_min(curvature)

        first_pt = self.events[0]
        last_pt = self.events[-1]

        # Elapsed time
        time = last_pt.time - first_pt.time

        # End-to-End distance
        distance = math.sqrt((last_pt.y - first_pt.y) ** 2 + (last_pt.x - first_pt.x) ** 2)

        # Straightness
        if trajectory == 0:
            straightness = 0
        else:
            straightness = distance / trajectory
        if straightness > 1:
            straightness = 1

        # Largest deviation from the end-to-end line
        max_deviation = self.largest_deviation(n)

        # Direction (-pi,...,pi)
        # theta = math.atan2((last_pt.y - first_pt.y), (last_pt.x - first_pt.x))
        # direction = compute_direction(theta)
        direction = get_bearings(first_pt, last_pt)

        # Generate CSV row
        return map(str, [self.action_type, time, trajectory, direction, straightness, n, max_deviation, sum_of_angles,
                         mean_curv, sd_curv, max_curv, min_curv, mean_omega, sd_omega, max_omega, min_omega,
                         mean_vx, sd_vx, max_vx, min_vx, mean_vy, sd_vy, max_vy, min_vy,
                         mean_v, sd_v, max_v, min_v, mean_a, sd_a, max_a, min_a,
                         mean_j, sd_j, max_j, min_j, distance, beginning_acceleration_time])

    def calculate_acceleration(self, n, v):
        a = [0]
        beginning_acceleration_time = 0
        beginning = True
        for i in range(1, n - 1):
            curr_event = self.events[i]
            prev_event = self.events[i - 1]
            dv = v[i] - v[i - 1]
            dt = curr_event.time - prev_event.time
            a_i = dv / dt
            a.append(a_i)
            if dv > 0 and beginning:
                beginning_acceleration_time += dt
            else:
                beginning = False
        return a, beginning_acceleration_time

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
