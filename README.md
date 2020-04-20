# openIMIS Backend Medical Pricelist reference module
This repository holds the files of the openIMIS Backend Medical Pricelist reference module.
It is dedicated to be deployed as a module of [openimis-be_py](https://github.com/openimis/openimis-be_py).

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## Code climat (develop branch)

[![Maintainability](https://img.shields.io/codeclimate/maintainability/openimis/openimis-be-medical_py.svg)](https://codeclimate.com/github/openimis/openimis-be-medical_py/maintainability)
[![Test Coverage](https://img.shields.io/codeclimate/coverage/openimis/openimis-be-medical_py.svg)](https://codeclimate.com/github/openimis/openimis-be-medical_py)

## ORM mapping:
* tblPLItems > ItemsPricelist
* tblPLItemsDetail > ItemsPricelistDetail
* tblPLServices > ServicesPricelist
* tblPLServicesDetail > ServicesPricelistDetail

## Listened Django Signals
None

## Services
None

## Reports (template can be overloaded via report.ReportDefinition)
None

## GraphQL Queries
* pricelists (aggregated items and services prices of a pricelist)

## GraphQL Mutations - each mutation emits default signals and return standard error lists (cfr. openimis-be-core_py)
None

## Configuration options (can be changed via core.ModuleConfiguration)
* gql_query_pricelists_perms: necessary rights to call pricelists (Default: [])

## openIMIS Modules Dependencies
* medical.models.Item
* medical.models.Service