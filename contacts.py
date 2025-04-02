import sage as utilities

# Creates a contact in the user's Sage account to assign to an invoice
def createcontact(access_token, name, mainaddress, deliveryaddress, mainperson, contact_types):
    endpoint = "contacts"
    method = "POST"

    payload = {
        "contact": {
            "name": name,
            "contact_type_ids": contact_types,
            "main_address": mainaddress,
            "delivery_address": deliveryaddress,
            "main_contact_person": mainperson,
        }
    }

    response = utilities.make_api_request(access_token=access_token, endpoint=endpoint, method=method, data=payload)
    id = response.get("id")
    return id


# Checks if the customer already exists in contacts by email
def customerexistsbyemail(access_token, name, email):
    endpoint = "contacts"
    method = "GET"

    params = {"email": email}

    response = utilities.make_api_request(access_token=access_token, endpoint=endpoint, method=method, params=params)

    if not utilities.compareresponse(response.get("$items")):
        return False
    else:
        # Checks if multiple contacts exists with email address
        if len(response.get("$items")) > 1:
            raise Exception(
                f"Request failed. Multiple contacts exist, who use this email address: {email}"
            )
        # Checks if the name doesn't mathc the found contact
        elif name != response.get("$items")[0].get("displayed_as"):
            return False
        # Returns the id of the contact
        else:
            return response.get("$items")[0].get("id")
        
