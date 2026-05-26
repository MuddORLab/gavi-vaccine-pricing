from itertools import product
from typing import List

from .types import TrialParams, MultiParam


def create_trials() -> List[TrialParams]:
    """
    Create list of TrailParams from the params.py file, accounting for
    multi-params. Trials are created from the Cartesian product of all supplied
    multi-params.
    """

    # Import mess
    import gavi.params as params

    multi_params = [] 
    multi_param_keys = []
    for trial_param_key in TrialParams.__annotations__.keys():
        param = getattr(params, trial_param_key)
        if type(param) is MultiParam:
            multi_params.append([(trial_param_key, value) for value in param.values])
            multi_param_keys.append(trial_param_key)

    if not multi_params:
        return [params]

    trials = []
    for trial_param_pairs in product(*multi_params):
        trial_dict = {}
        for trial_param_key, trial_param_value in trial_param_pairs:
            trial_dict[trial_param_key] = trial_param_value
        for trial_param_key in TrialParams.__annotations__.keys():
            if trial_param_key not in multi_param_keys:
                trial_dict[trial_param_key] = getattr(params, trial_param_key)
        trials.append(TrialParams(**trial_dict))

    return trials
