
import click
import requests
from apiclient import APIClient, HeaderAuthentication
import json

token = "1c4690ece19789cc630097f1202dee5e857285ec"
base = "https://ob.nordigen.com/api"

@click.group()
def apis():
    """A CLI wrapper for the API of Public APIs."""


class NordigenClient(APIClient):

    def list_requisitions(self):
        url = "{}/requisitions/".format(base)
        return self.get(url)

    def delete_requisitions(self, id):
        url = "{}/requisitions/{}".format(base, id)
        print("deleting with {} and {}".format(url, id))
        return self.delete(url)

    def list_transactions(self, id):
        url = "{}/accounts/{}/transactions/".format(base, id)
        return self.get(url)

    def list_endusers(self):
        url = "{}/agreements/enduser/".format(base)
        return self.get(url)

    def list_customers(self):
        url = "http://example.com/customers"
        return self.get(url)

    def add_customer(self, customer_info):
        url = "http://example.com/customers"
        return self.post(url, data=customer_info)



client = NordigenClient(
    authentication_method=HeaderAuthentication(
        token=token,
        parameter="Authorization",
        scheme="Token",
    )
)

# @click.option('-a', '--no-auth', is_flag=True, help='Filter out APIs with required auth')
# @click.option('-t', '--title', help='Name of API (matches via substring - i.e. "at" would return "cat" and "atlas".')
# @click.option('-c', '--category', help='Return only APIs from this category')
@apis.command()
def entries():
    """List all cataloged APIs."""
    response = requests.get(url='https://api.publicapis.org/categories')
    print(response.text)


@apis.command()
def requisitions():
    """List all cataloged APIs."""
    response = client.list_requisitions()
    requisitions = json.loads(response.text)
    for requisition in requisitions['results']:
      print("{} : {}".format(requisition['id'], requisition['accounts']))


@click.option('-i', '--id', help='Filter out APIs with required auth')
@apis.command()
def deleterequisition(id):
    """List all cataloged APIs."""
    response = client.delete_requisitions(id)
    # requisitions = json.loads(response.text)
    # for requisition in requisitions['results']:
    #   print("{} : {}".format(requisition['id'], requisition['accounts']))

    # print(json.dumps(requisitions, indent=4))


@click.option('-i', '--id', help='account id')
@apis.command()
def transactions(id):
    """List all cataloged APIs."""
    response = client.list_transactions(id)
    transactions = json.loads(response.text)

    for transaction in transactions['transactions']['booked']:
      #print("{} : {}".format(transaction['id'], transaction['accounts']))
      print(transaction['bookingDate'])
      print("")
    print(json.dumps(transactions, indent=4))


@apis.command()
def endusers():
    
    response = client.list_endusers()
    data = json.loads(response.text)

    # for enduser in endusers['transactions']['booked']:
    #   #print("{} : {}".format(transaction['id'], transaction['accounts']))
    #   print(transaction['bookingDate'])
    #   print("")
    print(json.dumps(data, indent=4))

if __name__ == '__main__':
    apis(prog_name='apis')


