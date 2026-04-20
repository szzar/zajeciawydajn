import time
import pytest

from src.models import Apartment, Parameters, Tenant
from src.manager import Manager


def _create_n_apartments(n: int) -> dict:
    """Return a dict of n apartments with keys 'apart-0', 'apart-1', ..., 'apart-(n-1)'."""
    return {f"apart-{i}": Apartment(key=f"apart-{i}", name=f"Apart {i}", area_m2=100.0, location=f"{i} Main St", rooms={}) for i in range(n)}

def _create_n_tenants(n: int, num_apartments: int) -> dict:
    """Return a dict of n tenant with keys 'tenant-0', 'tenant-1', ..., 'tenant-(n-1)'."""
    return{f"tenant-{i}": Tenant(name=f"Tenant {i}",apartment=f"apart-{i % num_apartments}",room="Room A",
    rent_pln=2500.0,deposit_pln=3000.0,date_agreement_from="2026-05-01",date_agreement_to="2027-05-01") for i in range(n)}


def test_creating_n_apartments_and_validation():
    """Tests the performance of (1) creating 100 000 apartments and 1 000 000 tenants (2) tenant-apartment assignment validation."""
    manager = Manager(Parameters())
    
    ALLOWED_CREATION_TIME_S = 10
    ALLOWED_CHECK_TIME_MS = 10
    N_APARTMENTS = 100_000
    N_TENANTS = 1_000_000

    creation_start_time = time.perf_counter()
    creation_time_s = time.perf_counter() - creation_start_time
    
    apartments_data = _create_n_apartments(N_APARTMENTS)
    tenants_data = _create_n_tenants(N_TENANTS, N_APARTMENTS)
    
    

    manager.apartments = apartments_data
    manager.tenants = tenants_data 

    assert creation_time_s < ALLOWED_CREATION_TIME_S, (
        f"Creating {N_APARTMENTS} apartments and {N_TENANTS} tenants took {creation_time_s:.3f}s, whereas the limit is {ALLOWED_CREATION_TIME_S}s")

   #(2) 
    check_start_time = time.perf_counter()
    validation_result = manager.check_tenants_apartment_keys()
    
    check_time_ms = (time.perf_counter() - check_start_time) * 1e3

    assert check_time_ms < ALLOWED_CHECK_TIME_MS, (
        f"Validating apartment keys for {N_TENANTS} tenants took {check_time_ms:.3f}ms, whereas the limit is {ALLOWED_CHECK_TIME_MS}ms")

    #validation
    assert validation_result is True, ("Expected true - every tenant has a valid apartment.")



def test_search_for_apartment_large_dataset():
    """Searching for an apartment in a dataset of 10 000 apartments should complete within the time limit."""
    ALLOWED_SEARCH_TIME_MS = 10
    N = 100_000
    manager = Manager(Parameters())
    manager.apartments = _create_n_apartments(N)

    exisitng_apartment_key = "apart-8090454321"
    non_existent_apartment_key = "apart-1005340000"


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

