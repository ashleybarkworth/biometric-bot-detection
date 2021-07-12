import statistics


def mean_sd_max_min(array):
    # Check if array is empty
    if not array:
        return ['n/a'] * 4
    else:
        # Average
        mean = statistics.mean(array)
        # Standard deviation
        st_dev = 'n/a' if len(array) < 2 else statistics.stdev(array)
        # Maximum value
        max_value = max(array)
        # Minimum value (excluding initial 0 value)
        min_value = 'n/a' if len(array) < 2 else min(array[1:])
        return [mean, st_dev, max_value, min_value]
