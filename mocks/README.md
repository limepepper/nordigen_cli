# Banking Data mock endpoint

This package mocks the endpoints that the tool uses for testing purposes

## Usage

1. create or modify a mock user in the mock data

    user one of the existing users in the user database
    
      
        mocks/api/user_database.py



2. add a mock profile to the user config file

  ```yaml
  {
    "verbose": 1,
    "output_format": "rich",
    "active_profile": "default",
    "profiles": {
                  ...
      "mock": {
        "api": "http://localhost:8000/api/v2",
        "secret_id": "<your-id-here>",
        "secret_key": "<your-key-here",
      }
    },
  }
  ```

3. start a mock server with the following command:

```bash
fastapi dev mocks/api/main.py
```

will output something like:

```console
INFO     Using import string api.main:app

 ╭────────── FastAPI CLI - Development mode ───────────╮
 │                                                     │
 │  Serving at: http://127.0.0.1:8000                  │
 │                                                     │
 │  API docs: http://127.0.0.1:8000/docs               │
 │                                                     │
 │  Running in development mode, for production use:   │
 │                                                     │
 │  fastapi run                                        │
 │                                                     │
 ╰─────────────────────────────────────────────────────╯

```


4. use the mock profile when running the nordctl command

```bash
nordctl --profile mock --format rich bank list GB
```

```console
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ mymeta ┃ id                 ┃ name               ┃ bic  ┃ transaction_total_… ┃ max_access_valid_… ┃ countries ┃ logo                ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ None   │ griffin-thompson-… │ Griffin-Thompson   │ None │ 90                  │ 180                │ CA        │ https://placekitte… │
│        │                    │ National Bank      │      │                     │                    │ MV        │                     │
│        │                    │                    │      │                     │                    │ MN        │                     │
│        │                    │                    │      │                     │                    │ MG        │                     │
│        │                    │                    │      │                     │                    │ TJ        │                     │
│ None   │ cox-group-bank     │ Cox Group Bank     │ None │ 90                  │ 180                │ BE        │ https://picsum.pho… │
│        │                    │                    │      │                     │                    │ LU        │                     │
│        │                    │                    │      │                     │                    │ ES        │                     │
│        │                    │                    │      │                     │                    │ CL        │                     │
│        │                    │                    │      │                     │                    │ CH        │                     │
│ None   │ jones-boyd-bank    │ Jones-Boyd Bank    │ None │ 90                  │ 180                │ BR        │ https://picsum.pho… │
│        │                    │                    │      │                     │                    │ SR        │                     │
│        │                    │                    │      │                     │                    │ EG        │                     │
│        │                    │                    │      │                     │                    │ GW        │                     │
│        │                    │                    │      │                     │                    │ DJ        │                     │
│ None   │ mccann-li-and-boy… │ Mccann, Li and     │ None │ 90                  │ 180                │ NE        │ https://dummyimage… │
│        │                    │ Boyer Credit Union │      │                     │                    │ MG        │                     │
│        │                    │                    │      │                     │                    │ LV        │                     │
│        │                    │                    │      │                     │                    │ BN        │                     │
│        │                    │                    │      │                     │                    │ BG        │                     │
│ None   │ frederick-fischer… │ Frederick, Fischer │ None │ 90                  │ 180                │ LB        │ https://dummyimage… │
│        │                    │ and Perez Credit   │      │                     │                    │ ME        │                     │
│        │                    │ Union              │      │                     │                    │ TJ        │                     │
│        │                    │                    │      │                     │                    │ GY        │                     │
│        │                    │                    │      │                     │                    │ SM        │                     │
│ None   │ daugherty-perez-a… │ Daugherty, Perez   │ None │ 90                  │ 180                │ EG        │ https://picsum.pho… │
│        │                    │ and Huffman Credit │      │                     │                    │ ZA        │                     │
│        │                    │ Union              │      │                     │                    │ TT        │                     │
│        │                    │                    │      │                     │                    │ MR        │                     │
│        │                    │                    │      │                     │                    │ YE        │                     │
│ None   │ ramirez-inc-credi… │ Ramirez Inc Credit │ None │ 90                  │ 180                │ TM        │ https://picsum.pho… │
│        │                    │ Union              │      │                     │                    │ DZ        │                     │
│        │                    │                    │      │                     │                    │ SV        │                     │
│        │                    │                    │      │                     │                    │ PS        │                     │
│        │                    │                    │      │                     │                    │ US        │                     │
│ None   │ cameron-williams-… │ Cameron, Williams  │ None │ 90                  │ 180                │ CY        │ https://placekitte… │
│        │                    │ and Reed Bank      │      │                     │                    │ QA        │                     │
│        │                    │                    │      │                     │                    │ QA        │                     │
│        │                    │                    │      │                     │                    │ BO        │                     │
│        │                    │                    │      │                     │                    │ TL        │                     │
│ None   │ thomas-plc-saving… │ Thomas PLC Savings │ None │ 90                  │ 180                │ MK        │ https://placekitte… │
│        │                    │ and Loans          │      │                     │                    │ MY        │                     │
│        │                    │                    │      │                     │                    │ BT        │                     │
│        │                    │                    │      │                     │                    │ RS        │                     │
│        │                    │                    │      │                     │                    │ KE        │                     │
│ None   │ thomas-brown-and-… │ Thomas, Brown and  │ None │ 90                  │ 180                │ LA        │ https://dummyimage… │
│        │                    │ Hawkins Credit     │      │                     │                    │ AU        │                     │
│        │                    │ Union              │      │                     │                    │ AG        │                     │
│        │                    │                    │      │                     │                    │ VN        │                     │
│        │                    │                    │      │                     │                    │ BD        │                     │
└────────┴────────────────────┴────────────────────┴──────┴─────────────────────┴────────────────────┴───────────┴─────────────────────┘
```

