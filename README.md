# Sage-Py
A Python implementation of some endpoints from the [Sage Accounting API](https://developer.sage.com/accounting/reference/).

## Table of Contents
* [General Info](#General-Info)
* [Technologies](#Technologies)
* [Author Info](#Author-Info)

## General Info
Version: 2.0, 02/04/2025<br>
Sage-py was used in a project used for integrating Sage into other platforms. This repo provides correct formatting to be accepted by the [Sage Accounting API](https://developer.sage.com/accounting/reference/). Due to this being used in another project, not all of the functions are implemented as not all of the endpoints from the API were used. It does cover basic areas such as authentication and token management.

Files in Repository:

-sage.py: This is the base file for the project. This includes functions of various sizes, which are either a base requirement to be able to interact with the API or cannot be categorised into another python file.

-contacts.py: Stores functions used for interacting with the contacts endpoint of the Sage API.

-products.py: Stores functions used for interacting with the products endpoint of the Sage API.

-invoices.py: Stores functions used for interacting with the sales_invoices endpoint of the Sage API.


## Technologies
Created in Python 3.10
## Author Info
Name: Morgan Firkins<br>
GitHub: https://github.com/mfirkins<br>
