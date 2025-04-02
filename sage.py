from datetime import datetime
import requests

# API defaults
global base_url
base_url = "https://api.accounting.sage.com"
global api_version
api_version = "v3.1"

# Gets access token from Sage API with authorization code from authorization from a login i.e. OAuth
# Returns the expiration of the access token and the expiration of the refresh token
def getAccessTokenWithAuth(authtoken: str, client_id: str, client_secret: str, redirect_uri: str):
    url = "https://oauth.accounting.sage.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": authtoken,
        "redirect_uri": redirect_uri,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.request("POST", url, headers=headers, data=payload).json()

    access_token = response.get("access_token")
    refresh_token = response.get("refresh_token")
    access_exp = response.get("expires_in")
    access_exp = int(float(access_exp))
    now = datetime.now()
    presentdatetime = datetime.timestamp(now)
    access_exp = presentdatetime + access_exp
    access_exp = str(access_exp)
    refresh_exp = response.get("refresh_token_expires_in")
    refresh_exp = int(float(refresh_exp))
    refresh_exp = presentdatetime + refresh_exp
    refresh_exp = str(refresh_exp)
    return access_token, access_exp, refresh_token, refresh_exp


# Gets access token from Sage API with refresh code
def getAccessTokenWithRefresh(refresh_token: str, client_id: str, client_secret: str):
    url = "https://oauth.accounting.sage.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    header = {
        "Content": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    response = requests.request("POST", url, headers=header, data=payload)
    access_token = response.json().get("access_token")
    access_exp = response.json().get("expires_in")
    access_exp = int(float(access_exp))
    now = datetime.now()
    presentdatetime = datetime.timestamp(now)
    access_exp = presentdatetime + access_exp
    access_exp = str(access_exp)
    refresh_exp = response.json().get("refresh_token_expires_in")
    refresh_token = response.json().get("refresh_token")
    now = datetime.now()
    presentdatetime = datetime.timestamp(now)
    refresh_exp = int(float(refresh_exp))
    refresh_exp = presentdatetime + refresh_exp
    refresh_exp = str(refresh_exp)
    return access_token


# Checks if the access token provided by either of the two above methods needs to be refreshed. You should use this before each API request (as long as the refresh token has not expired)
def needsRefresh(access_exp: float, access_token, client_id, client_secret, refresh_token):
    nowtime = datetime.now()
    nowtimestamp = float(nowtime.timestamp())
    if nowtimestamp >= access_exp:
        return getAccessTokenWithRefresh(
            client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
    else:
        return access_token
    
# Generic api request function called by most functions to help with logging and consistency in requests
    
def make_api_request(access_token, endpoint, method="GET", params=None, data=None, key=None):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    url = f"{base_url}/{api_version}/{endpoint}"

    if key:
        url = f"{url}/{key}"

    response = requests.request(method, url, headers=headers, params=params, json=data)
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    elif endpoint == "stock_items" and response.status_code != 200:
        return response.json()
    else:
        print("---------- ❌ ERROR RAISED ----------")
        print(response.status_code)
        print(response)
        print(response.json())
        raise Exception(
            f"Request failed. Endpoint: {endpoint}. Status Code: {response.status_code}. Error Message/Content: {response.json()}"
        )


# Get the ID of the bank account to search for
def getbankaccount(access_token, bankaccount):
    endpoint = "bank_accounts"
    method = "GET"

    response = make_api_request(access_token=access_token, endpoint=endpoint, method=method)
    bank_accounts = response.get("$items")

    for account in bank_accounts:
        name = account.get("displayed_as")
        if name == bankaccount:
            bank_account_id = account.get("id")
            return bank_account_id
        else:
            continue
    return False


# Gets the ID of a given sales ledger
def getsalesledger(access_token, sales_ledger_name: str):
    endpoint = "ledger_accounts"
    method = "GET"

    params = {"search": sales_ledger_name}

    response = make_api_request(
        access_token=access_token, endpoint=endpoint, method=method, params=params
    )
    id = response.get("$items")[0].get("id")
    return id


# Gets the ID of a given purchase ledger
def getpurchaseledger(access_token, purchase_ledger_name: str):
    endpoint = "ledger_accounts"
    method = "GET"

    params = {"search": purchase_ledger_name}

    response = make_api_request(
        access_token=access_token, endpoint=endpoint, method=method, params=params
    )
    id = response.get("$items")[0].get("id")
    return id

# Creates a stock movement for products at the time of function call
def create_stock_movement(access_token, product_id, quantity_needed, cost_price, details):
    endpoint = "stock_movements"
    method = "POST"

    payload = {
        "stock_movement": {
            "stock_item_id": product_id,
            "date": datetime.today().strftime("%Y-%m-%d"),
            "quantity": quantity_needed,
            "cost_price": cost_price,
            "details": details,
        }
    }

    make_api_request(access_token=access_token, endpoint=endpoint, method=method, data=payload)

# Validates if the quantity of a product is enough for the quantity_needed. Returns True if there is enough, creates a stock movement if False
def quantity_validator(access_token, product_id, quantity_needed):
    endpoint = "stock_items"
    method = "GET"

    response = make_api_request(
        access_token=access_token, endpoint=endpoint, method=method, key=product_id
    )

    if type(response) == list:
        if (
            "$dataCode" in response[0]
            and response[0].get("$dataCode") == "RecordNotFound"
        ):
            return True

    num_in_stock = response.get("quantity_in_stock")
    num_in_stock = float(num_in_stock)
    quantity_needed = float(quantity_needed)
    if num_in_stock >= quantity_needed:
        return True
    else:
        create_stock_movement(access_token=access_token, product_id=product_id, quantity_needed=quantity_needed)

# Gets the net total of an invoice and the tax amount
def gettaxandtotal(access_token, invoice_id):
    endpoint = "sales_invoices"
    method = "GET"

    response = make_api_request(
        access_token=access_token, endpoint=endpoint, method=method, key=invoice_id
    )

    tax_analysis = response.get("tax_analysis")[0]
    netamount = tax_analysis.get("net_amount")
    taxamount = tax_analysis.get("tax_amount")
    total = response.get("total_amount")
    return netamount, taxamount, total


# Adds a payment to the a bank account ledger
def createpayment(
    access_token,
    bank_account_id,
    transaction_type_id,
    contact_id,
    date,
    invoice_id,
    payment_method,
    tax_rate
):
    endpoint = "contact_payments"
    method = "POST"

    net_amount, tax_amount, total = gettaxandtotal(access_token=access_token, invoice_id=invoice_id)
    payload = {
        "contact_payment": {
            "transaction_type_id": transaction_type_id,
            "contact_id": contact_id,
            "bank_account_id": bank_account_id,
            "date": date,
            "total_amount": float(total),
            "payment_method_id": payment_method,
            "net_amount": net_amount,
            "tax_amount": tax_amount,
            "tax_rate_id": tax_rate,
            "allocated_artefacts": [
                {"artefact_id": invoice_id, "amount": float(total)}
            ],
        }
    }
    make_api_request(access_token=access_token, endpoint=endpoint, method=method, data=payload)


# Checks if the length of a response from the API is less than 1 item long
def compareresponse(response):
    length = len(response)
    if length < 1:
        return False
    else:
        return True
