import sage as utilities

# Creates a sales invoice on the user's Sage account - must use reference to use searchsalesinvoicesbyreference function
def createsalesinvoice(access_token, contact_id, date, products, reference):
    endpoint = "sales_invoices"
    method = "POST"
    payload = {
        "sales_invoice": {
            "contact_id": contact_id,
            "date": date,
            "due_date": date,
            "reference": reference,
            "invoice_lines": products,
        }
    }

    response = utilities.make_api_request(access_token=access_token, endpoint=endpoint, method=method, data=payload)
    id = response.get("id")
    return id


# Searches existing sales invoices within Sage by reference
def searchsalesinvoicesbyreference(access_token, reference):
    endpoint = "sales_invoices"
    method = "GET"

    params = {
        "search": reference,
    }

    response = utilities.make_api_request(access_token=access_token, endpoint=endpoint, method=method, params=params)
    return utilities.compareresponse(response.get("$items"))
