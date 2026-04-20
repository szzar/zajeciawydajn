import time
import pytest

from src.models import Apartment, Tenant, Parameters
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
def _create_n_tenants(n: int, apart_count: int) -> dict:
    """Tworzy słownik najemców szybciej dzięki model_construct."""
    tenants = {}
    for i in range(n):
        t = Tenant.model_construct(
            name=f"Tenant {i}",
            apartment=f"apart-{i % apart_count}",
            room="Room 1",
            rent_pln=0.0,
            deposit_pln=0.0,
            date_agreement_from="",
            date_agreement_to=""
        )
        tenants[f"t-{i}"] = t
    return tenants
def test_performance_bulk_creation_and_validation():
    N_APARTMENTS = 100_000
    N_TENANTS = 1_000_000
    MAX_CREATION_TIME_S = 10.0
    MAX_VALIDATION_TIME_MS = 1000.0

    manager = Manager(Parameters())

    start_creation = time.perf_counter()
    
    manager.apartments = _create_n_apartments(N_APARTMENTS)
    manager.tenants = _create_n_tenants(N_TENANTS, N_APARTMENTS)
    
    total_creation_time = time.perf_counter() - start_creation

    start_validation = time.perf_counter()
    
    is_valid = manager.check_tenants_apartment_keys()
    
    validation_time_ms = (time.perf_counter() - start_validation) * 1000

    assert total_creation_time < MAX_CREATION_TIME_S, \
        f"Tworzenie danych zajęło {total_creation_time:.2f}s, przekraczając limit {MAX_CREATION_TIME_S}s"
    
    assert is_valid is True, "Walidacja powiązań zwróciła False, a powinna True"
    
    assert validation_time_ms < MAX_VALIDATION_TIME_MS, \
        f"Walidacja powiązań zajęła {validation_time_ms:.2f}ms, przekraczając limit {MAX_VALIDATION_TIME_MS}ms"