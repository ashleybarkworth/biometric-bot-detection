import statistics


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
        # Minimum value (excluding initial 0 value)
        min_value = min(array)
        return [mean, st_dev, max_value, min_value]
