import sage as utilities

# Creates a product within Sage
def createproduct(access_token, item_code, description, sales_ledger_name, purchase_ledger_name):
    endpoint = "products"
    method = "POST"
    payload = {
        "product": {
            "description": description,
            "sales_ledger_account_id": utilities.getsalesledger(access_token=access_token, sales_ledger_name=sales_ledger_name),
            "purchase_ledger_account_id": utilities.getpurchaseledger(access_token=access_token, purchase_ledger_name=purchase_ledger_name),
            "item_code": item_code,
            "active": True,
        }
    }

    response = utilities.make_api_request(
        access_token=access_token, endpoint=endpoint, method=method, data=payload
    )
    return response.get("id")


# Checks if product already exists within Sage by item code
def findproductbyitemcode(access_token, item_code, description, sales_ledger_name, purchase_ledger_name):
    endpoint = "products"
    method = "GET"

    params = {"search": item_code, "attributes": "item_code"}

    response = utilities.make_api_request(
        access_token=access_token, endpoint=endpoint, method=method, params=params
    )

    if "$items" in response:
        items = response.get("$items")
        if len(response.get("$items")) < 1:
            productid = createproduct(access_token=access_token, item_code=item_code, description=description, sales_ledger_name=sales_ledger_name, purchase_ledger_name=purchase_ledger_name)
            return productid
        else:
            for item in items:
                if item.get("item_code") == item_code:
                  
                    product_id = item.get("id")

                    return product_id
                else:
                    continue
            productid = createproduct(access_token=access_token, item_code=item_code, description=description, sales_ledger_name=sales_ledger_name, purchase_ledger_name=purchase_ledger_name)
            return productid
    else:
        productid = createproduct(access_token=access_token, item_code=item_code, description=description, sales_ledger_name=sales_ledger_name, purchase_ledger_name=purchase_ledger_name)
        return productid
