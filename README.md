<div align="center">

<h1>Hub Connector</h1>

Connecting ERPNext users to Hub Marketplace

</div>

## Introduction

-  Hub Marketplace (hubmarket.place) has been conceptualised to extend the scope of an ERP to a network of e-commerce industry, as we know how powerful networks are compared to single nodes.
-  The Hub Marketplace will evolve into a data-driven marketplace. The goal of Hub Marketplace is to offer ERPNext users a centralized marketplace where they can list products, improving lead generation, discoverability, and transact with convenience.

This app helps ERPNext users connect and list their products/services on the Hub Marketplace. It is built on top of [ERPNext](https://github.com/frappe/erpnext) and the [Frappe Framework](https://github.com/frappe/frappe) - incredible FOSS projects built and maintained by the incredible folks at Frappe. Go check these out if you haven't already!

## Key Features

-   Create an account on hubmarket.place as a seller
-   Publish items on hubmarket.place
-   Generate leads from hubmarket.place in the ERPNext's CRM module

For a detailed overview of these features and setup guidelines, please refer to the documentation (link to be provided).

## Installation

1. [Install bench/frappe](https://github.com/frappe/bench).
2. [Install ERPNext](https://github.com/frappe/erpnext#installation).
3. Once ERPNext is installed, add the Hub Connector app to your bench by running

	```sh
	$ bench get-app git@github.com:mytra-money/hub-connector.git
	```
4. After that, you can install the Hub Connector app on the required site by running
	```sh
	$ bench --site sitename install-app hub_marketplace_connector
	```

## Planned Features

-   Providing an e-commerce section in the seller's ERPNext instance which shall navigate from the Material Request Doc to send enquiry to the sellers listed on Hub Marketplace and receive Supplier Quotations
-   Providing complete e-commerce features by enabling buyers on Hub Marketplace to place orders and sellers to fulfill the orders
-   Building a connector to ONDC to help the sellers listed on Hub Marketplace get registered on ONDC as well

## Contributing

-   [Issue Guidelines](https://github.com/frappe/erpnext/wiki/Issue-Guidelines)
-   [Pull Request Requirements](https://github.com/frappe/erpnext/wiki/Contribution-Guidelines)

## License

[GNU General Public License (v3)](https://github.com/resilient-tech/india-compliance/blob/develop/license.txt)
