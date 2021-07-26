import statistics

from feature_extraction.mouse_actions import ActionType


class Session:

    def __init__(self, actions, usertype):
        self.actions = actions
        self.usertype = usertype

        # Session features
        self.num_actions = len(actions)
        self.total_duration = actions[-1].events[-1].time - actions[0].events[0].time
        self.avg_inter_action_time = self.sd_inter_action_time = self.max_inter_action_time = self.min_inter_action_time = 0

        # Mouse Move Action Features
        self.mm_avg_v = self.mm_sd_v = self.mm_max_v = self.mm_min_v = 0
        self.mm_avg_a = self.mm_sd_a = self.mm_max_a = self.mm_min_a = 0
        self.mm_avg_j = self.mm_sd_j = self.mm_max_j = self.mm_min_j = 0
        self.mm_avg_duration = self.mm_sd_duration = self.mm_max_duration = self.mm_min_duration = 0
        self.mm_avg_straightness = self.mm_sd_straightness = self.mm_max_straightness = self.mm_min_straightness = 0
        self.mm_avg_num_points = self.mm_sd_num_points = self.mm_max_num_points = self.mm_min_num_points = 0
        self.mm_avg_curvature = self.mm_sd_curvature = self.mm_max_curvature = self.mm_min_curvature = 0
        self.mm_avg_angle_sum = self.mm_sd_angle_sum = self.mm_max_angle_sum = self.mm_min_angle_sum = 0
        self.mm_avg_max_deviation = self.mm_sd_max_deviation = self.mm_max_max_deviation = self.mm_min_max_deviation = 0

        # Point Click Action Features
        self.pc_avg_v = self.pc_sd_v = self.pc_max_v = self.pc_min_v = 0
        self.pc_avg_a = self.pc_sd_a = self.pc_max_a = self.pc_min_a = 0
        self.pc_avg_j = self.pc_sd_j = self.pc_max_j = self.pc_min_j = 0
        self.pc_avg_duration = self.pc_sd_duration = self.pc_max_duration = self.pc_min_duration = 0
        self.pc_avg_straightness = self.pc_sd_straightness = self.pc_max_straightness = self.pc_min_straightness = 0
        self.pc_avg_num_points = self.pc_sd_num_points = self.pc_max_num_points = self.pc_min_num_points = 0
        self.pc_avg_curvature = self.pc_sd_curvature = self.pc_max_curvature = self.pc_min_curvature = 0
        self.pc_avg_angle_sum = self.pc_sd_angle_sum = self.pc_max_angle_sum = self.pc_min_angle_sum = 0
        self.pc_avg_max_deviation = self.pc_sd_max_deviation = self.pc_max_max_deviation = self.pc_min_max_deviation = 0
        self.pc_avg_click_time = self.pc_sd_click_time = self.pc_max_click_time = self.pc_min_click_time = 0

        # Drag Drop Action Features
        self.dd_avg_v = self.dd_sd_v = self.dd_max_v = self.dd_min_v = 0
        self.dd_avg_a = self.dd_sd_a = self.dd_max_a = self.dd_min_a = 0
        self.dd_avg_j = self.dd_sd_j = self.dd_max_j = self.dd_min_j = 0
        self.dd_avg_duration = self.dd_sd_duration = self.dd_max_duration = self.dd_min_duration = 0
        self.dd_avg_straightness = self.dd_sd_straightness = self.dd_max_straightness = self.dd_min_straightness = 0
        self.dd_avg_num_points = self.dd_sd_num_points = self.dd_max_num_points = self.dd_min_num_points = 0
        self.dd_avg_curvature = self.dd_sd_curvature = self.dd_max_curvature = self.dd_min_curvature = 0
        self.dd_avg_angle_sum = self.dd_sd_angle_sum = self.dd_max_angle_sum = self.dd_min_angle_sum = 0
        self.dd_avg_max_deviation = self.dd_sd_max_deviation = self.dd_max_max_deviation = self.dd_min_max_deviation = 0

    def calculate_features(self, action_type):
        mouse_move_actions = [action for action in self.actions if action.action_type.value == ActionType.MM.value]
        point_click_actions = [action for action in self.actions if action.action_type.value == ActionType.PC.value]
        drag_drop_actions = [action for action in self.actions if action.action_type.value == ActionType.DD.value]

        self.process_mouse_move_actions(mouse_move_actions)
        self.process_point_click_actions(point_click_actions)
        self.process_drag_drop_actions(drag_drop_actions)

        # Times between consecutive actions
        inter_action_times = []
        for i in range(1, len(self.actions)):
            action_start_time = self.actions[i].events[0].time
            num_prev_action_events = len(self.actions[i - 1].events)
            prev_action_end_time = self.actions[i - 1].events[num_prev_action_events - 1].time
            inter_action_times.append(action_start_time - prev_action_end_time)

        self.avg_inter_action_time, self.sd_inter_action_time, self.max_inter_action_time, self.min_inter_action_time = mean_sd_max_min(inter_action_times)

        mm_row = [self.mm_avg_v, self.mm_sd_v, self.mm_max_v, self.mm_min_v,
               self.mm_avg_a, self.mm_sd_a, self.mm_max_a, self.mm_min_a,
               self.mm_avg_j, self.mm_sd_j, self.mm_max_j, self.mm_min_j,
               self.mm_avg_duration, self.mm_sd_duration, self.mm_max_duration, self.mm_min_duration,
               self.mm_avg_straightness, self.mm_sd_straightness, self.mm_max_straightness, self.mm_min_straightness,
               self.mm_avg_num_points, self.mm_sd_num_points, self.mm_max_num_points, self.mm_min_num_points,
               self.mm_avg_curvature, self.mm_sd_curvature, self.mm_max_curvature, self.mm_min_curvature,
               self.mm_avg_angle_sum, self.mm_sd_angle_sum, self.mm_max_angle_sum, self.mm_min_angle_sum,
               self.mm_avg_max_deviation, self.mm_sd_max_deviation, self.mm_max_max_deviation, self.mm_min_max_deviation]

        pc_row = [self.pc_avg_v, self.pc_sd_v, self.pc_max_v, self.pc_min_v,
               self.pc_avg_a, self.pc_sd_a, self.pc_max_a, self.pc_min_a,
               self.pc_avg_j, self.pc_sd_j, self.pc_max_j, self.pc_min_j,
               self.pc_avg_duration, self.pc_sd_duration, self.pc_max_duration, self.pc_min_duration,
               self.pc_avg_straightness, self.pc_sd_straightness, self.pc_max_straightness, self.pc_min_straightness,
               self.pc_avg_num_points, self.pc_sd_num_points, self.pc_max_num_points, self.pc_min_num_points,
               self.pc_avg_curvature, self.pc_sd_curvature, self.pc_max_curvature, self.pc_min_curvature,
               self.pc_avg_angle_sum, self.pc_sd_angle_sum, self.pc_max_angle_sum, self.pc_min_angle_sum,
               self.pc_avg_max_deviation, self.pc_sd_max_deviation, self.pc_max_max_deviation, self.pc_min_max_deviation,
               self.pc_avg_click_time, self.pc_sd_click_time, self.pc_max_click_time, self.pc_min_click_time]

        dd_row = [self.dd_avg_v, self.dd_sd_v, self.dd_max_v, self.dd_min_v,
               self.dd_avg_a, self.dd_sd_a, self.dd_max_a, self.dd_min_a,
               self.pc_avg_j, self.pc_sd_j, self.pc_max_j, self.pc_min_j,
               self.dd_avg_duration, self.dd_sd_duration, self.dd_max_duration, self.dd_min_duration,
               self.dd_avg_straightness, self.dd_sd_straightness, self.dd_max_straightness, self.dd_min_straightness,
               self.dd_avg_num_points, self.dd_sd_num_points, self.dd_max_num_points, self.dd_min_num_points,
               self.dd_avg_curvature, self.dd_sd_curvature, self.dd_max_curvature, self.dd_min_curvature,
               self.dd_avg_angle_sum, self.dd_sd_angle_sum, self.dd_max_angle_sum, self.dd_min_angle_sum,
               self.dd_avg_max_deviation, self.dd_sd_max_deviation, self.dd_max_max_deviation, self.dd_min_max_deviation]

        row = [self.num_actions, self.total_duration]

        if action_type == 'mm':
            row += mm_row
        elif action_type == 'pc':
            row += pc_row
        elif action_type == 'dd':
            row += dd_row
        else:
            row += mm_row + pc_row + dd_row

        return row

    def process_mouse_move_actions(self, mm_actions):
        velocities, accelerations, jerks, durations, straightness, num_points, angle_sums, max_deviations, curvatures = get_action_features(mm_actions)

        [self.mm_avg_v, self.mm_sd_v, self.mm_max_v, self.mm_min_v] = mean_sd_max_min(velocities)
        [self.mm_avg_a, self.mm_sd_a, self.mm_max_a, self.mm_min_a] = mean_sd_max_min(accelerations)
        [self.mm_avg_j, self.mm_sd_j, self.mm_max_j, self.mm_min_j] = mean_sd_max_min(jerks)
        [self.mm_avg_duration, self.mm_sd_duration, self.mm_max_duration, self.mm_min_duration] = mean_sd_max_min(durations)
        [self.mm_avg_straightness, self.mm_sd_straightness, self.mm_max_straightness, self.mm_min_straightness] = mean_sd_max_min(straightness)
        [self.mm_avg_num_points, self.mm_sd_num_points, self.mm_max_num_points, self.mm_min_num_points] = mean_sd_max_min(num_points)
        [self.mm_avg_angle_sum, self.mm_sd_angle_sum, self.mm_max_angle_sum, self.mm_min_angle_sum] = mean_sd_max_min(angle_sums)
        [self.mm_avg_max_deviation, self.mm_sd_max_deviation, self.mm_max_max_deviation, self.mm_min_max_deviation] = mean_sd_max_min(max_deviations)
        [self.mm_avg_curvature, self.mm_sd_curvature, self.mm_max_curvature, self.mm_min_curvature] = mean_sd_max_min(curvatures)

    def process_point_click_actions(self, pc_actions):
        velocities, accelerations, jerks, durations, straightness, num_points, angle_sums, max_deviations, curvatures = get_action_features(pc_actions)

        # Calculate click times
        click_times = []
        for action in pc_actions:
            # Last event is mouse release, second last event is mouse press
            n = len(action.events) - 1
            click_times.append(action.events[n].time - action.events[n - 1].time)

        [self.pc_avg_v, self.pc_sd_v, self.pc_max_v, self.pc_min_v] = mean_sd_max_min(velocities)
        [self.pc_avg_a, self.pc_sd_a, self.pc_max_a, self.pc_min_a] = mean_sd_max_min(accelerations)
        [self.pc_avg_j, self.pc_sd_j, self.pc_max_j, self.pc_min_j] = mean_sd_max_min(jerks)
        [self.pc_avg_duration, self.pc_sd_duration, self.pc_max_duration, self.pc_min_duration] = mean_sd_max_min(durations)
        [self.pc_avg_straightness, self.pc_sd_straightness, self.pc_max_straightness, self.pc_min_straightness] = mean_sd_max_min(straightness)
        [self.pc_avg_num_points, self.pc_sd_num_points, self.pc_max_num_points, self.pc_min_num_points] = mean_sd_max_min(num_points)
        [self.pc_avg_curvature, self.pc_sd_curvature, self.pc_max_curvature, self.pc_min_curvature] = mean_sd_max_min(curvatures)
        [self.pc_avg_angle_sum, self.pc_sd_angle_sum, self.pc_max_angle_sum, self.pc_min_angle_sum] = mean_sd_max_min(angle_sums)
        [self.pc_avg_max_deviation, self.pc_sd_max_deviation, self.pc_max_max_deviation, self.pc_min_max_deviation] = mean_sd_max_min(max_deviations)
        [self.pc_avg_click_time, self.pc_sd_click_time, self.pc_max_click_time, self.pc_min_click_time] = mean_sd_max_min(click_times)

    def process_drag_drop_actions(self, dd_actions):
        velocities, accelerations, jerks, durations, straightness, num_points, angle_sums, max_deviations, curvatures = get_action_features(dd_actions)
        
        [self.dd_avg_v, self.dd_sd_v, self.dd_max_v, self.dd_min_v] = mean_sd_max_min(velocities)
        [self.dd_avg_a, self.dd_sd_a, self.dd_max_a, self.dd_min_a] = mean_sd_max_min(accelerations)
        [self.dd_avg_j, self.dd_sd_j, self.dd_max_j, self.dd_min_j] = mean_sd_max_min(jerks)
        [self.dd_avg_duration, self.dd_sd_duration, self.dd_max_duration, self.dd_min_duration] = mean_sd_max_min(durations)
        [self.dd_avg_straightness, self.dd_sd_straightness, self.dd_max_straightness, self.dd_min_straightness] = mean_sd_max_min(straightness)
        [self.dd_avg_num_points, self.dd_sd_num_points, self.dd_max_num_points, self.dd_min_num_points] = mean_sd_max_min(num_points)
        [self.dd_avg_curvature, self.dd_sd_curvature, self.dd_max_curvature, self.dd_min_curvature] = mean_sd_max_min(curvatures)
        [self.dd_avg_angle_sum, self.dd_sd_angle_sum, self.dd_max_angle_sum, self.dd_min_angle_sum] = mean_sd_max_min(angle_sums)
        [self.dd_avg_max_deviation, self.dd_sd_max_deviation, self.dd_max_max_deviation, self.dd_min_max_deviation] = mean_sd_max_min(max_deviations)


def mean_sd_max_min(array):
    # Check if array is empty
    if not array:
        return [0] * 4
    else:
        # Average
        mean = statistics.mean(array)
        # Standard deviation
        st_dev = 0 if len(array) < 2 else statistics.stdev(array)
        # Maximum value
        max_value = max(array)
        # Minimum value
        min_value = min(array)
        return [mean, st_dev, max_value, min_value]


def get_action_features(actions):
    velocities, accelerations, jerks, durations, straightness, num_points, angle_sums, max_deviations, curvatures = ([] for _ in range(9))

    for action in actions:
        durations.append(action.duration)
        straightness.append(action.straightness)
        num_points.append(action.n)
        velocities.append(action.v)
        accelerations.append(action.a)
        jerks.append(action.j)
        max_deviations.append(action.max_deviation)
        angle_sums.append(action.sum_of_angles)
        curvatures.append(action.curvature)

    return velocities, accelerations, jerks, durations, straightness, num_points, angle_sums, max_deviations, curvatures
