# fingrid-py
[![PyPI](https://img.shields.io/pypi/v/fingrid-py.svg)](https://pypi.org/project/fingrid-py/)
[![CI](https://github.com/hoofir/fingrid-py/actions/workflows/ci.yml/badge.svg)](https://github.com/hoofir/fingrid-py/actions/workflows/ci.yml)
![Repo Size](https://img.shields.io/github/repo-size/hoofir/fingrid-py.svg)
[![Downloads](https://img.shields.io/pypi/dm/fingrid-py.svg)](https://pypistats.org/packages/fingrid-py)
[![License](https://img.shields.io/github/license/hoofir/fingrid-py.svg)](https://github.com/hoofir/fingrid-py/blob/main/LICENSE)

Python package to provide access to Fingrid (Finnish TSO) datasets through open **REST API** interface.

## How to Get Started
1. Make sure you have an active email address.
2. Do [register](https://fingridavoindata.b2clogin.com/fingridavoindata.onmicrosoft.com/B2C_1A_signup_signin/api/CombinedSigninAndSignup/unified?local=signup&csrf_token=TzBZTGVyNjJSZUVsT3dJQjQvc2dCeGpJc2twM0h3N1c0WmsrMUFBUkF0VU00cUNvQ0tFR0E3c2pGVlF6SklzOXNxMTZlQllYZVFuellKUnlYVlFJY2c9PTsyMDI1LTA5LTI2VDE0OjUwOjA1LjY2NTM5MTNaO3FadS9DNS8vRGJhVmZ1NGpaTk1GY3c9PTt7Ik9yY2hlc3RyYXRpb25TdGVwIjoxfQ==&tx=StateProperties=eyJUSUQiOiI4ZTcyMmNiMS1jYjMyLTQzY2ItYTE2My1iMzA5NDBhMmI0NjcifQ&p=B2C_1A_signup_signin) and approve the license and terms of use. 
3. You will receive a personal API-key right away. If you don't receive the email, please check your Junk/Spam folder.
4. Registered users may opt-in to receive email maintenance breaks or other important changes about API.
5. If you want, you can also [delete your account](https://fingridavoindata.b2clogin.com/fingridavoindata.onmicrosoft.com/b2c_1a_signup_signin/oauth2/v2.0/authorize?client_id=a226de5e-0083-4ae3-8054-b0a65498f1d9&scope=openid%20profile%20offline_access&redirect_uri=https%3A%2F%2Fdata.fingrid.fi%2F&client-request-id=b4058e9e-28ed-431d-a83f-41646e648e41&response_mode=fragment&response_type=code&x-client-SKU=msal.js.browser&x-client-VER=2.38.4&client_info=1&code_challenge=bHfbRl36HXkYHpZM3CchqRP1SLJTDoaO2wPBloOYZEA&code_challenge_method=S256&nonce=e9cf8dd3-1939-4065-bc6c-2d57c4f5dc03&state=eyJpZCI6IjkyNDljODY5LWJhZGYtNDcyNi04YWJlLWUzMTI1ZWM4NzIyZCIsIm1ldGEiOnsiaW50ZXJhY3Rpb25UeXBlIjoicmVkaXJlY3QifX0%3D&ui_locales=en) and the related API-key.

## Installation
```bash
pip install fingrid-py
```

## Usage
### Fetch data using utility functions

```python
api_key = "<your own API key>"

from fingrid import get_data, get_series_metadata

# Get datasets' metadata:
metadata_dict = get_series_metadata(api_key)                    # as json dict
metadata_df = get_series_metadata(api_key, to_dataframe=True)   # as Pandas.DataFrame

# Get datasets' timeseries data:
data_df = get_data(
  api_key,
  [277, 317, 347],
  "2025-09-01 01:00",
  "2025-09-10 01:00",
)
```

### Call directly API endpoints
There are 9 different endpoints provided by API. All endpoints work in the same way with the same methods. \
You can easily import and instantiate the endpoint's class and call the `get()` method to get the raw data in json format.

```python
# Example

from fingrid import GetHealthStatus

health = GetHealthStatus(api_key).get()
```

Check out the parameters of each endpoint [here](https://developer-data.fingrid.fi/api-details#api=avoindata-api&operation=GetActiveNotifications).\
Alternatively, you can call the `get()` method and the system will complain if any required parameter is missing.

## Information for Developers
Technical API documentation for developers is available [here](https://data.fingrid.fi/en/instructions).

- You can access data in JSON and DataFrame formats.
- Each dataset has a unique `datasetId` number that you need to use in API requests. Find about available datasets [here](https://data.fingrid.fi/en/datasets).
- You can make 10,000 requests in 24h period and 10 requests per 1 minute with one API-key. Please contact the [admin](mailto:avoindata@fingrid.fi) if you need more.
- Timestamps are by default presented in `UTC` time zone.
- If you request frequently updated data from an extended date range, you may receive an error message that results from exceeding the maximum allowed API payload. 
