# a simple cli for nordigen open banking API

## You will first need to sign up with nordigen, and create a token:

https://nordigen.com/en/


## install the package from github using the following syntax

    $ pip install --user git+https://github.com/limepepper/nordigen_cli.git#egg=nordigen_cli

The tool will then be available as `nordctl`

export your nordigen private token as environment variable:

    $ export NORDIGEN_TOKEN=xxxxxxxx

You can then list the banks that nordigen supports. There is a list [here](https://airtable.com/shrX4uBtNLnsPxSih/tblyRj2FTQoXq9Qmu) by country.

You need the country code. e.g. GB

    $ nordctl list-banks GB

    name: ABN AMRO Bank Commercial             id: ABNAMRO_ABNAGB2LXXX
    name: American Express                     id: AMERICAN_EXPRESS_AESUGB21
    name: Bank of Scotland Business            id: BANK_OF_SCOTLAND_BUSINESS_BOFSGBS1
    name: Bank of Scotland Commercial          id: BANK_OF_SCOTLAND_COMMERCIAL_BOFSGBS1
    name: Bank of Scotland Personal            id: BANK_OF_SCOTLAND_BOFSGBS1
    name: Barclaycard Commercial Payments      id: BARCLAYCARD_COMMERCIAL_BUKBGB22
    ...


or you can use Nordigens sandbox box, which has `aspsp_id` SANDBOXFINANCE_SFIN0000

The `aspsp_id` is referred to as `bank_id` by the nordctl for legacy reasons

    $ nordctl show-bank SANDBOXFINANCE_SFIN0000

    {
        "id": "SANDBOXFINANCE_SFIN0000",
        "name": "Sandbox Finance",
        "bic": "SFIN0000",
        "transaction_total_days": "90",
        "countries": [
            "XX"
        ],
        "logo": "https://cdn.nordigen.com/ais/SANDBOXFINANCE_SFIN0000.png"
    }

The API requires an `enduser_id` which is an arbitrary value used to identify
individual users in approvals. Create an enduser_id and store it safely locally

    $ enduser_id=$(uuid)
    $ echo $enduser_id

    17c1859e-1f09-12ec-b03f-2c56dc3a9c74

* uuid is available in the `uuid` package on fedora, alternatively you can install
utils-linux which has a similar command `uuidgen`

You can then link the enduser_id to the bank's open banking API by creating an
approval. A browser will open to handle the open banking approval process.

    $ nordctl create-approval SANDBOXFINANCE_SFIN0000  17c1859e-1f09-12ec-b03f-2c56dc3a9c74

    agreement id: 6d5bbb57-c43c-41e1-a174-5fc80452b3c1
    requisition_id: 5f725a38-72c2-4173-99f3-476de90de915
    initiate link: https://ob.nordigen.com/psd2/start/5f725a38-72c2-4173-99f3-476de90de915/SANDBOXFINANCE_SFIN0000
    * Serving Flask app 'redirect' (lazy loading)
    * Environment: production
      WARNING: This is a development server. Do not use it in a production deployment.
      Use a production WSGI server instead.
    * Debug mode: off
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

after you have approved the access request, it will display the available accounts

    requisition should now have account information
    you are now linked to the following accounts
    account id: 1048f194-cb13-4cee-a55c-5ef6d8662341
    account id: 582a6ea9-81c7-4def-952d-85709d9432c7

you can then get information on balances, details and list all the transactions
on the account

    $ nordctl show-account-detail 1048f194-cb13-4cee-a55c-5ef6d8661341
    {
        "account": {
            "resourceId": "01F3NS4YV94RA29YCH8R0F6BMF",
            "iban": "GL11SAFI05510125815",
            "currency": "EUR",
            "ownerName": "John Doe",
            "name": "Main Account",
            "product": "Checkings",
            "cashAccountType": "CACC"
        }
    }

balances:

    $ nordctl show-account-balance 1048f194-cb13-4cee-a55c-5ef6d8661341
    {
        "balances": [
            {
                "balanceAmount": {
                    "amount": "1913.12",
                    "currency": "EUR"
                },
                "balanceType": "authorised",
                "referenceDate": "2021-09-26"
            },
            {
                "balanceAmount": {
                    "amount": "1913.12",
                    "currency": "EUR"
                },
                "balanceType": "interimAvailable",
                "referenceDate": "2021-09-26"
            }
        ]
    }


transactions:

    $ nordctl list-account-transactions 1048f194-cb13-4cee-a55c-5ef6d8661341
    2021-09-25:  -15.00 EUR : 2021092502698008-1 PAYMENT Alderaan Coffe
    2021-09-25:   45.00 EUR : 2021092502698007-1 For the support of Restoration of the Republic foundation
    2021-09-25:   45.00 EUR : 2021092502698004-1 For the support of Restoration of the Republic foundation
    2021-09-25:   45.00 EUR : 2021092502698001-1 For the support of Restoration of the Republic foundation
    2021-09-25:  -15.00 EUR : 2021092502698005-1 PAYMENT Alderaan Coffe
    2021-09-25:  -15.00 EUR : 2021092502698002-1 PAYMENT Alderaan Coffe
