import sys

from src.manager import Manager
from src.models import Parameters


def print_section_header(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def print_subsection_header(title: str):
    """Print a formatted subsection header"""
    print(f"\n  {title}")
    print(f"  {'-' * 40}")


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"{amount:,.2f} PLN"


def display_apartments(manager):
    """Display all apartments with their rooms and bills"""
    print_section_header("APARTMENTS")
    
    for apartment in manager.apartments.values():
        print(f"\n📍 {apartment.name} ({apartment.key})")
        print(f"   Location: {apartment.location}")
        print(f"   Total Area: {apartment.area_m2} m²")
        
        print_subsection_header("Rooms")
        for room in apartment.rooms.values():
            print(f"      • {room.name:<25} {room.area_m2:>6} m²")
        
        # Find bills for this apartment
        apartment_bills = [bill for bill in manager.bills if bill.apartment == apartment.key]
        if apartment_bills:
            print_subsection_header("Bills")
            for bill in apartment_bills:
                month_year = f"{bill.settlement_month}/{bill.settlement_year}" if bill.settlement_month and bill.settlement_year else "N/A"
                print(f"      • {bill.type:<15} {format_currency(bill.amount_pln):>15}  Due: {bill.date_due}  Period: {month_year}")


def display_tenants(manager):
    """Display all tenants with their details and transfers"""
    print_section_header("TENANTS")
    
    for tenant in manager.tenants.values():
        print(f"\n👤 {tenant.name}")
        print(f"   Apartment: {tenant.apartment}")
        print(f"   Room: {tenant.room}")
        print(f"   Rent: {format_currency(tenant.rent_pln)}/month")
        print(f"   Deposit: {format_currency(tenant.deposit_pln)}")
        print(f"   Agreement: {tenant.date_agreement_from} to {tenant.date_agreement_to}")
        
        # Find transfers for this tenant
        tenant_transfers = [transfer for transfer in manager.transfers if transfer.tenant == tenant.name]
        if tenant_transfers:
            print_subsection_header("Transfers")
            for transfer in tenant_transfers:
                month_year = f"{transfer.settlement_month}/{transfer.settlement_year}" if transfer.settlement_month and transfer.settlement_year else "N/A"
                print(f"      • {format_currency(transfer.amount_pln):>15}  Date: {transfer.date}  Period: {month_year}")


def display_monthly_settlement(manager, apartment_key: str, year: int, month: int):
    """Display a full monthly settlement for a given apartment, year and month"""
    if apartment_key not in manager.apartments:
        print(f"\nError: apartment '{apartment_key}' not found.")
        return

    apartment = manager.apartments[apartment_key]
    settlement = manager.get_settlement(apartment_key, year, month)

    print_section_header(f"MONTHLY SETTLEMENT  —  {apartment.name} ({apartment_key})  |  {month:02d}/{year}")

    # --- Bills ---
    apartment_bills = [
        bill for bill in manager.bills
        if bill.apartment == apartment_key
        and bill.settlement_year == year
        and bill.settlement_month == month
    ]

    print_subsection_header("Bills")
    if apartment_bills:
        for bill in apartment_bills:
            print(f"      • {bill.type:<20} {format_currency(bill.amount_pln):>15}  Due: {bill.date_due}")
    else:
        print("      (no bills for this period)")
    print(f"\n      {'TOTAL BILLS':<20} {format_currency(settlement.total_due_pln):>15}")

    # --- Per-tenant breakdown ---
    tenant_settlements = manager.create_tenants_settlements(settlement)
    tenants_in_apt = {
        t.name: t for t in manager.tenants.values() if t.apartment == apartment_key
    }

    print_subsection_header("Tenant Breakdown")
    for ts in tenant_settlements:
        tenant = tenants_in_apt.get(ts.tenant)
        rent = tenant.rent_pln if tenant else 0.0

        transfers = [
            tr for tr in manager.transfers
            if tr.tenant == ts.tenant
            and tr.settlement_year == year
            and tr.settlement_month == month
        ]
        total_paid = sum(tr.amount_pln for tr in transfers)
        total_due = rent + ts.total_due_pln
        balance = total_paid - total_due
        status = "OK" if balance >= 0 else "DEBT"

        print(f"      • {ts.tenant}")
        print(f"          Rent:            {format_currency(rent):>15}")
        print(f"          Bills share:     {format_currency(ts.total_due_pln):>15}")
        print(f"          Total due:       {format_currency(total_due):>15}")
        print(f"          Total paid:      {format_currency(total_paid):>15}")
        print(f"          Balance:         {format_currency(balance):>15}  [{status}]")

    # --- Transfers ---
    all_apt_transfers = [
        tr for tr in manager.transfers
        if tr.tenant in tenants_in_apt
        and tr.settlement_year == year
        and tr.settlement_month == month
    ]

    print_subsection_header("Transfers Received")
    if all_apt_transfers:
        for tr in all_apt_transfers:
            print(f"      • {tr.tenant:<25} {format_currency(tr.amount_pln):>15}  Date: {tr.date}")
    else:
        print("      (no transfers for this period)")

    total_received = sum(tr.amount_pln for tr in all_apt_transfers)
    total_rent = sum(t.rent_pln for t in tenants_in_apt.values())
    total_due_all = total_rent + settlement.total_due_pln
    overall_balance = total_received - total_due_all

    print(f"\n      {'TOTAL RECEIVED':<20} {format_currency(total_received):>15}")
    print(f"      {'TOTAL DUE':<20} {format_currency(total_due_all):>15}")
    print(f"      {'BALANCE':<20} {format_currency(overall_balance):>15}")

    print(f"\n{'=' * 70}\n")


if __name__ == '__main__':
    parameters = Parameters()
    manager = Manager(parameters)

    if len(sys.argv) == 4:
        apartment_key = sys.argv[1]
        year = int(sys.argv[2])
        month = int(sys.argv[3])
        display_monthly_settlement(manager, apartment_key, year, month)
    else:
        display_apartments(manager)
        display_tenants(manager)
        print(f"\n{'=' * 70}\n")