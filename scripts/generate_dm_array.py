import os
import numpy as np
import math

def generate_dm_array(start_DM, end_DM, dm_step):
    """Prepare DM array based on start, end, and step."""
    N0 = int(math.floor((end_DM - start_DM) / dm_step))
    dm1 = ["{:.2f}".format(start_DM + i * dm_step) for i in range(N0)]
    DM_array = np.array(dm1, dtype=str)
    return DM_array