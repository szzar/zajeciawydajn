import time
import pytest

from src.models import Apartment, Parameters
from src.manager import Manager


def _create_n_apartments(n: int) -> dict:
    """Return a dict of n apartments with keys 'apart-0', 'apart-1', ..., 'apart-(n-1)'."""
    return {f"apart-{i}": Apartment(key=f"apart-{i}", name=f"Apart {i}", area_m2=100.0, location=f"{i} Main St", rooms={}) for i in range(n)}


def test_search_for_apartment_large_dataset():
    """Searching for an apartment in a dataset of 10 000 apartments should complete within the time limit."""
    ALLOWED_SEARCH_TIME_MS = 10
    N = 100_000
    manager = Manager(Parameters())
    manager.apartments = _create_n_apartments(N)

    exisitng_apartment_key = "apart-80901"
    non_existent_apartment_key = "apart-1000000"


    ok_search_time = time.perf_counter()
    result_ok = manager.get_apartment(exisitng_apartment_key)
    ok_search_time = (time.perf_counter() - ok_search_time) * 1e3  # convert to milliseconds

    fail_search_time = time.perf_counter()
    result_fail = manager.get_apartment(non_existent_apartment_key)
    fail_search_time = (time.perf_counter() - fail_search_time) * 1e3  # convert to milliseconds

    assert type(result_ok) is Apartment
    assert result_fail is None
    assert ok_search_time < ALLOWED_SEARCH_TIME_MS, (
        f"Searching for existing apartment in {N} apartments took {ok_search_time:.3f}ms, limit {ALLOWED_SEARCH_TIME_MS}ms"
    )
    assert fail_search_time < ALLOWED_SEARCH_TIME_MS, (
        f"Searching for non-existing apartment in {N} apartments took {fail_search_time:.3f}ms, limit {ALLOWED_SEARCH_TIME_MS}ms"
    )

