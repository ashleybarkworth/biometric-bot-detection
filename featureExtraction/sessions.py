from featureExtraction.actions import ActionType
from utility.stats import mean_sd_max_min


class Session:

    def __init__(self, filename, actions, usertype):
        self.filename = filename
        self.actions = actions
        self.usertype = usertype

        # Session features
        self.num_actions = len(actions)
        self.mean_inter_action_time = self.sd_inter_action_time = self.max_inter_action_time = self.min_inter_action_time = 0

        self.pc_mean_inter_action_time = self.pc_sd_inter_action_time = 0
        self.mm_mean_inter_action_time = self.mm_sd_inter_action_time = 0
        self.dd_mean_inter_action_time = self.dd_sd_inter_action_time = 0

        # Mouse Move Action Features
        self.mm_mean_v = self.mm_sd_v = self.mm_max_v = self.mm_min_v = 0
        self.mm_mean_a = self.mm_sd_a = self.mm_max_a = self.mm_min_a = 0
        self.mm_mean_j = self.mm_sd_j = self.mm_max_j = self.mm_min_j = 0
        self.mm_mean_duration = self.mm_sd_duration = self.mm_max_duration = self.mm_min_duration = 0
        self.mm_mean_trajectory = self.mm_sd_trajectory = self.mm_max_trajectory = self.mm_min_trajectory = 0
        self.mm_mean_distance = self.mm_sd_distance = self.mm_max_distance = self.mm_min_distance = 0
        self.mm_mean_straightness = self.mm_sd_straightness = self.mm_max_straightness = self.mm_min_straightness = 0
        self.mm_mean_num_points = self.mm_sd_num_points = self.mm_max_num_points = self.mm_min_num_points = 0
        self.mm_mean_angle_sum = self.mm_sd_angle_sum = self.mm_max_angle_sum = self.mm_min_angle_sum = 0
        self.mm_mean_max_deviation = self.mm_sd_max_deviation = 0
        self.mm_mean_curvature = self.mm_sd_curvature = 0

        # Point Click Action Features
        self.pc_mean_v = self.pc_sd_v = self.pc_max_v = self.pc_min_v = 0
        self.pc_mean_a = self.pc_sd_a = self.pc_max_a = self.pc_min_a = 0
        self.pc_mean_j = self.pc_sd_j = self.pc_max_j = self.pc_min_j = 0
        self.pc_mean_duration = self.pc_sd_duration = self.pc_max_duration = self.pc_min_duration = 0
        self.pc_mean_trajectory = self.pc_sd_trajectory = self.pc_max_trajectory = self.pc_min_trajectory = 0
        self.pc_mean_distance = self.pc_sd_distance = self.pc_max_distance = self.pc_min_distance = 0
        self.pc_mean_straightness = self.pc_sd_straightness = self.pc_max_straightness = self.pc_min_straightness = 0
        self.pc_mean_num_points = self.pc_sd_num_points = self.pc_max_num_points = self.pc_min_num_points = 0
        self.pc_mean_angle_sum = self.pc_sd_angle_sum = self.pc_max_angle_sum = self.pc_min_angle_sum = 0
        self.pc_mean_click_time = self.pc_sd_click_time = self.max_click_time = self.min_click_time = 0
        self.pc_mean_approach_time = self.pc_sd_approach_time = self.max_approach_time = self.min_approach_time = 0
        self.pc_mean_max_deviation = self.pc_sd_max_deviation = 0
        self.pc_mean_curvature = self.pc_sd_curvature = 0

        # Drag Drop Action Features
        self.dd_mean_v = self.dd_sd_v = self.dd_max_v = self.dd_min_v = 0
        self.dd_mean_a = self.dd_sd_a = self.dd_max_a = self.dd_min_a = 0
        self.dd_mean_j = self.dd_sd_j = self.dd_max_j = self.dd_min_j = 0
        self.dd_mean_duration = self.dd_sd_duration = self.dd_max_duration = self.dd_min_duration = 0
        self.dd_mean_trajectory = self.dd_sd_trajectory = self.dd_max_trajectory = self.dd_min_trajectory = 0
        self.dd_mean_distance = self.dd_sd_distance = self.dd_max_distance = self.dd_min_distance = 0
        self.dd_mean_straightness = self.dd_sd_straightness = self.dd_max_straightness = self.dd_min_straightness = 0
        self.dd_mean_num_points = self.dd_sd_num_points = self.dd_max_num_points = self.dd_min_num_points = 0
        self.dd_mean_angle_sum = self.dd_sd_angle_sum = self.dd_max_angle_sum = self.dd_min_angle_sum = 0
        self.dd_mean_max_deviation = self.dd_sd_max_deviation = 0
        self.dd_mean_curvature = self.dd_sd_curvature = 0


    def calculate_features(self):
        mouse_move_actions = [action for action in self.actions if action.action_type.value == ActionType.MM.value]
        point_click_actions = [action for action in self.actions if action.action_type.value == ActionType.PC.value]
        drag_drop_actions = [action for action in self.actions if action.action_type.value == ActionType.DD.value]

        self.process_mouse_move_actions(mouse_move_actions)
        self.process_point_click_actions(point_click_actions)
        self.process_drag_drop_actions(drag_drop_actions)

        return map(str, [self.num_actions, self.pc_mean_inter_action_time, # self.pc_sd_inter_action_time,
                         self.mm_mean_inter_action_time, # self.mm_sd_inter_action_time,
                         self.dd_mean_inter_action_time, # self.dd_sd_inter_action_time,
                         self.mm_mean_v,  # self.mm_sd_v,  # self.mm_max_v, self.mm_min_v,
                         # self.mm_mean_a, self.mm_sd_a,  # self.mm_max_a, self.mm_min_a,
                         self.mm_mean_j,  # self.mm_sd_j,  # self.mm_max_j, self.mm_min_j,
                         self.mm_mean_duration,  # self.mm_sd_duration,  # self.mm_max_duration, self.mm_min_duration,
                         # self.mm_mean_trajectory, self.mm_sd_trajectory, self.mm_max_trajectory, self.mm_min_trajectory,
                         # self.mm_mean_distance, self.mm_sd_distance, self.mm_max_distance, self.mm_min_distance,
                         self.mm_mean_straightness,  # self.mm_sd_straightness,
                         # self.mm_max_straightness, self.mm_min_straightness,
                         # self.mm_mean_num_points, self.mm_sd_num_points,
                         # self.mm_max_num_points, self.mm_min_num_points,
                         # self.mm_mean_curvature, self.mm_sd_curvature,
                         # self.mm_mean_angle_sum, self.mm_sd_angle_sum,  # self.mm_max_angle_sum, self.mm_min_angle_sum,
                         # self.mm_mean_max_deviation, self.mm_sd_max_deviation,
                         # self.pc_mean_v, self.pc_sd_v,  # self.pc_max_v, self.pc_min_v,
                         # self.pc_mean_a, self.pc_sd_a,  # self.pc_max_a, self.pc_min_a,
                         # self.pc_mean_j, self.pc_sd_j,  # self.pc_max_j, self.pc_min_j,
                         self.pc_mean_duration, # self.pc_sd_duration,  # self.pc_max_duration, self.pc_min_duration,
                         # self.pc_mean_distance, self.pc_sd_distance, self.pc_max_distance, self.pc_min_distance,
                         self.pc_mean_straightness, # self.pc_sd_straightness,
                         # self.pc_max_straightness, self.pc_min_straightness,
                         # self.pc_mean_num_points, self.pc_sd_num_points,
                         # self.pc_max_num_points, self.pc_min_num_points,
                         # self.pc_mean_curvature, self.pc_sd_curvature,
                         # self.pc_mean_angle_sum, self.pc_sd_angle_sum,  # self.pc_max_angle_sum, self.pc_min_angle_sum,
                         # self.pc_mean_max_deviation, self.pc_sd_max_deviation,
                         self.pc_mean_click_time, # self.pc_sd_click_time,  # self.max_click_time, self.min_click_time,
                         self.pc_mean_approach_time,#  self.pc_sd_approach_time,
                         # self.max_approach_time, self.min_approach_time,
                         # self.dd_mean_v, self.dd_sd_v,  # self.dd_max_v, self.dd_min_v,
                         # self.dd_mean_a, self.dd_sd_a,  # self.dd_max_a, self.dd_min_a,
                         # self.pc_mean_j, self.pc_sd_j,  # self.pc_max_j, self.pc_min_j,
                         self.dd_mean_duration, # self.dd_sd_duration,  # self.dd_max_duration, self.dd_min_duration,
                         # self.dd_mean_trajectory, self.dd_sd_trajectory, self.dd_max_trajectory, self.dd_min_trajectory,
                         # self.dd_mean_distance, self.dd_sd_distance, self.dd_max_distance, self.dd_min_distance,
                         self.dd_mean_straightness]) #  self.dd_sd_straightness])
                         # self.dd_max_straightness, self.dd_min_straightness,
                         # self.dd_mean_num_points, self.dd_sd_num_points,
                         # self.dd_max_num_points, self.dd_min_num_points,
                         # self.dd_mean_curvature, self.dd_sd_curvature])
                         # self.dd_mean_angle_sum, self.dd_sd_angle_sum,  # self.dd_max_angle_sum, self.dd_min_angle_sum])
                         # self.dd_mean_max_deviation, self.dd_sd_max_deviation])

    def process_mouse_move_actions(self, actions):
        durations, velocities, accelerations, jerks, straightness, num_points, angle_sums, deviations = \
            ([] for _ in range(8))
        curvatures = []

        for action in actions:
            durations.append(action.duration)
            # trajectories.append(action.trajectory)
            # distances.append(action.distance)
            straightness.append(action.straightness)
            num_points.append(action.n)
            velocities.append(action.v)
            accelerations.append(action.a)
            jerks.append(action.j)
            angle_sums.append(action.sum_of_angles)
            deviations.append(action.max_deviation)
            curvatures.append(action.curvature)

        [self.mm_mean_v, self.mm_sd_v, self.mm_max_v, self.mm_min_v] = mean_sd_max_min(velocities)
        [self.mm_mean_a, self.mm_sd_a, self.mm_max_a, self.mm_min_a] = mean_sd_max_min(accelerations)
        [self.mm_mean_j, self.mm_sd_j, self.mm_max_j, self.mm_min_j] = mean_sd_max_min(jerks)

        [self.mm_mean_duration, self.mm_sd_duration, self.mm_max_duration, self.mm_min_duration] \
            = mean_sd_max_min(durations)
        # [self.mm_mean_trajectory, self.mm_sd_trajectory, self.mm_max_trajectory, self.mm_min_trajectory] \
        #     = mean_sd_max_min(trajectories)
        # [self.mm_mean_distance, self.mm_sd_distance, self.mm_max_distance, self.mm_min_distance] = mean_sd_max_min(
        #     distances)
        [self.mm_mean_straightness, self.mm_sd_straightness, self.mm_max_straightness, self.mm_min_straightness] \
            = mean_sd_max_min(straightness)
        [self.mm_mean_num_points, self.mm_sd_num_points, self.mm_max_num_points, self.mm_min_num_points] \
            = mean_sd_max_min(num_points)
        [self.mm_mean_angle_sum, self.mm_sd_angle_sum, self.mm_max_angle_sum, self.mm_min_angle_sum] \
            = mean_sd_max_min(angle_sums)
        [self.mm_mean_max_deviation, self.mm_sd_max_deviation, _, _] = mean_sd_max_min(angle_sums)
        [self.mm_mean_curvature, self.mm_sd_curvature, _, _] = mean_sd_max_min(curvatures)

        # Times between consecutive actions
        inter_action_times = []
        for i in range(1, len(actions)):
            action_start_time = actions[i].events[0].time
            num_prev_action_events = len(actions[i - 1].events)
            prev_action_end_time = actions[i - 1].events[num_prev_action_events - 1].time
            inter_action_times.append(action_start_time - prev_action_end_time)

        self.mm_mean_inter_action_time, self.mm_sd_inter_action_time, _, _ = mean_sd_max_min(inter_action_times)

    def process_point_click_actions(self, actions):
        durations, velocities, accelerations, jerks, straightness, num_points, angle_sums, deviations, click_times,\
        approach_times = ([] for _ in range(10))
        curvatures = []

        for action in actions:
            durations.append(action.duration)
            # trajectories.append(action.trajectory)
            # distances.append(action.distance)
            straightness.append(action.straightness)
            num_points.append(action.n)
            velocities.append(action.v)
            accelerations.append(action.a)
            jerks.append(action.j)
            angle_sums.append(action.sum_of_angles)
            # Last event is mouse release, second last event is mouse press
            n = len(action.events) - 1
            click_times.append(action.events[n].time - action.events[n - 1].time)
            approach_times.append(action.events[n - 1].time - action.events[n - 2].time)
            curvatures.append(action.curvature)

        [self.pc_mean_v, self.pc_sd_v, self.pc_max_v, self.pc_min_v] = mean_sd_max_min(velocities)
        [self.pc_mean_a, self.pc_sd_a, self.pc_max_a, self.pc_min_a] = mean_sd_max_min(accelerations)
        [self.pc_mean_j, self.pc_sd_j, self.pc_max_j, self.pc_min_j] = mean_sd_max_min(jerks)

        [self.pc_mean_duration, self.pc_sd_duration, self.pc_max_duration, self.pc_min_duration] \
            = mean_sd_max_min(durations)
        # [self.pc_mean_trajectory, self.pc_sd_trajectory, self.pc_max_trajectory, self.pc_min_trajectory] \
        #     = mean_sd_max_min(trajectories)
        # [self.pc_mean_distance, self.pc_sd_distance, self.pc_max_distance, self.pc_min_distance] = mean_sd_max_min(
        #     distances)
        [self.pc_mean_straightness, self.pc_sd_straightness, self.pc_max_straightness, self.pc_min_straightness] \
            = mean_sd_max_min(straightness)
        [self.pc_mean_num_points, self.pc_sd_num_points, self.pc_max_num_points, self.pc_min_num_points] \
            = mean_sd_max_min(num_points)
        [self.pc_mean_angle_sum, self.pc_sd_angle_sum, self.pc_max_angle_sum, self.pc_min_angle_sum] \
            = mean_sd_max_min(angle_sums)

        [self.pc_mean_click_time, self.pc_sd_click_time, self.max_click_time, self.min_click_time] \
            = mean_sd_max_min(click_times)

        [self.pc_mean_approach_time, self.pc_sd_approach_time, self.max_approach_time, self.min_approach_time] \
            = mean_sd_max_min(approach_times)
        [self.pc_mean_max_deviation, self.pc_sd_max_deviation, _, _] = mean_sd_max_min(deviations)
        [self.pc_mean_curvature, self.pc_sd_curvature, _, _] = mean_sd_max_min(curvatures)

        # Times between consecutive actions
        inter_action_times = []
        for i in range(1, len(actions)):
            action_start_time = actions[i].events[0].time
            num_prev_action_events = len(actions[i - 1].events)
            prev_action_end_time = actions[i - 1].events[num_prev_action_events - 1].time
            inter_action_times.append(action_start_time - prev_action_end_time)

        self.pc_mean_inter_action_time, self.pc_sd_inter_action_time, _, _ = mean_sd_max_min(inter_action_times)

    def process_drag_drop_actions(self, actions):
        durations, velocities, accelerations, jerks, straightness, num_points, angle_sums, deviations \
            = ([] for _ in range(8))
        curvatures = []

        for action in actions:
            durations.append(action.duration)
            # trajectories.append(action.trajectory)
            # distances.append(action.distance)
            straightness.append(action.straightness)
            num_points.append(action.n)
            velocities.append(action.v)
            accelerations.append(action.a)
            jerks.append(action.j)
            angle_sums.append(action.sum_of_angles)
            deviations.append(action.max_deviation)
            curvatures.append(action.curvature)

        [self.dd_mean_v, self.dd_sd_v, self.dd_max_v, self.dd_min_v] = mean_sd_max_min(velocities)
        [self.dd_mean_a, self.dd_sd_a, self.dd_max_a, self.dd_min_a] = mean_sd_max_min(accelerations)
        [self.dd_mean_j, self.dd_sd_j, self.dd_max_j, self.dd_min_j] = mean_sd_max_min(jerks)

        [self.dd_mean_duration, self.dd_sd_duration, self.dd_max_duration, self.dd_min_duration] \
            = mean_sd_max_min(durations)
        # [self.dd_mean_trajectory, self.dd_sd_trajectory, self.dd_max_trajectory, self.dd_min_trajectory] \
        #     = mean_sd_max_min(trajectories)
        # [self.dd_mean_distance, self.dd_sd_distance, self.dd_max_distance, self.dd_min_distance] = mean_sd_max_min(
        #     distances)
        [self.dd_mean_straightness, self.dd_sd_straightness, self.dd_max_straightness, self.dd_min_straightness] \
            = mean_sd_max_min(straightness)
        [self.dd_mean_num_points, self.dd_sd_num_points, self.dd_max_num_points, self.dd_min_num_points] \
            = mean_sd_max_min(num_points)
        [self.dd_mean_angle_sum, self.dd_sd_angle_sum, self.dd_max_angle_sum, self.dd_min_angle_sum] \
            = mean_sd_max_min(angle_sums)
        [self.dd_mean_max_deviation, self.dd_sd_max_deviation, _, _] = mean_sd_max_min(deviations)
        [self.dd_mean_curvature, self.dd_sd_curvature, _, _] = mean_sd_max_min(curvatures)

        # Times between consecutive actions
        inter_action_times = []
        for i in range(1, len(actions)):
            action_start_time = actions[i].events[0].time
            num_prev_action_events = len(actions[i - 1].events)
            prev_action_end_time = actions[i - 1].events[num_prev_action_events - 1].time
            inter_action_times.append(action_start_time - prev_action_end_time)

        self.dd_mean_inter_action_time, self.dd_sd_inter_action_time, _, _ = mean_sd_max_min(inter_action_times)
