import csv
import os

import core.datetimes.ad_datetime
from core import datetime, filter_validity
from django.core.management.base import BaseCommand
from django.db.models import Q
from location.models import Location, HealthFacility

from insuree.models import Gender, Insuree
from insuree.test_helpers import create_test_insuree, create_test_photo
from medical.models import Service
from medical_pricelist.models import ServicesPricelist, ServicesPricelistDetail


def load_current_hfs():
    hf_dict = {}
    valid_hfs = HealthFacility.objects.filter(*filter_validity())\
                                      .only("id", "code", "name", "location_id")\
                                      .order_by("id")
    for hf in valid_hfs:
        hf_dict[hf.code] = hf
    return hf_dict


def load_current_services():
    service_dict = {}
    valid_services = Service.objects.filter(*filter_validity())\
                                    .only("id", "code")\
                                    .order_by("id")
    for service in valid_services:
        service_dict[service.code] = service.id
    return service_dict

class Command(BaseCommand):
    help = "This command will create Service Pricelists from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_location",
                            nargs=1,
                            type=str,
                            help="Absolute path to the CSV file")

    def handle(self, *args, **options):
        file_location = options["csv_location"][0]
        if not os.path.isfile(file_location):
            print(f"Error - {file_location} is not a correct file path.")
        else:
            with open(file_location, mode='r', encoding='utf-8') as csv_file:

                total_rows = 0
                total_pl_created = 0
                total_pl_details_created = 0
                total_skipped = 0

                print(f"**** Loading Health Facilities ***")
                hf_mapping = load_current_hfs()
                print(f"**** Loading Services ***")
                service_mapping = load_current_services()

                previous_pricelist = None
                previous_hf_code = None

                print(f"**** Starting to import Service Pricelists from {file_location} ***")

                csv_reader = csv.DictReader(csv_file, delimiter=',')
                for row in csv_reader:

                    total_rows += 1
                    hf_code = row["hf_code"]
                    if hf_code not in hf_mapping:
                        total_skipped += 1
                        print(f"Row {total_rows} - Skpping due to non existing Health Facility ({hf_code})")
                        continue

                    service_code = row["service_code"]
                    if service_code not in service_mapping:
                        total_skipped += 1
                        print(f"Row {total_rows} - Skpping due to non existing Service ({service_code})")
                        continue

                    if not row["price"]:
                        total_skipped += 1
                        print(f"Row {total_rows} - Skpping due to not having a price")
                        continue

                    hf = hf_mapping[hf_code]
                    service_id = service_mapping[service_code]

                    if previous_hf_code != hf_code:
                        previous_pricelist = ServicesPricelist.objects.create(
                            name=f"{hf.name} - {row['pl_name']}",
                            pricelist_date=datetime.datetime.today(),
                            audit_user_id=-1,
                            location=hf.location
                        )
                        total_pl_created += 1
                        previous_hf_code = hf_code

                    ServicesPricelistDetail.objects.create(
                        service_id=service_id,
                        price_overrule=row["price"],
                        audit_user_id=-1,
                        services_pricelist=previous_pricelist
                    )
                    total_pl_details_created += 1

                print("**************")
                print(f"Import finished - {total_rows} lines received:")
                print(f"\t- {total_pl_created} Service Pricelists created")
                print(f"\t- {total_pl_details_created} lines in these Pricelists created")
                print(f"\t- {total_skipped} lines skipped")
