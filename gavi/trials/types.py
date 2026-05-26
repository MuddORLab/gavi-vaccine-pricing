from dataclasses import dataclass
from typing import Callable, Generic, List, TypeVar, Union

import numpy as np


T = TypeVar("T")
S = TypeVar("S")

# Let a vector be either a Python list or a numpy array
Vector = Union[List[float], np.ndarray]
Matrix = np.ndarray


@dataclass
class TrialParams:
    vaccine_names: List[str]
    antigen_names: List[str]
    excluded_vaccines: List[int]
    M: int
    T: int
    hex_proportion: float
    mu: Vector
    opv_frac: float
    demand_coeff_a: Matrix
    demand_coeff_b: Matrix
    demand_coeff_c: Matrix
    dist_cost: float
    N: int
    N1: int
    N2: int
    profit_threshold: Vector
    capacity: Vector
    hex_cost: Vector
    hex_cap: Vector
    year_index: Vector
    mfr_index: Vector
    demand_projection: Matrix
    upper_demand: Vector
    historical_upper_price_limit: Vector
    vaccine_composition: Matrix
    mfr_resources: Matrix
    mfr_resources2: Matrix
    num_antigens: Vector


@dataclass
class MultiParam(Generic[T]):
    values: List[T]


def lambda_multi_param(fn: Callable[[T], S], param: Union[T, MultiParam[T]]) -> Union[S, MultiParam[S]]:
    if type(param) is MultiParam:
        return MultiParam(values=[fn(value) for value in param.values])
    return fn(param)
