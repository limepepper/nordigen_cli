
import click
import requests
from apiclient import APIClient, HeaderAuthentication
import json
from os import environ
import sys
from flask import Flask, request
import webbrowser

from nordigenclient import NordigenClient
from output_formatting import formatter

token = environ.get('NORDIGEN_TOKEN')
if not token:
    print("please set NORDIGEN_TOKEN environment variable")
    sys.exit(1)


@click.group()
@click.option('--output', default="text", help='output format. one of json, text')
@click.pass_context
def apis(ctx, output):
    """A CLI wrapper for Nordigen open banking APIs."""
    ctx.ensure_object(dict)
    ctx.obj['output'] = output


client = NordigenClient(
    authentication_method=HeaderAuthentication(
        token=token,
        parameter="Authorization",
        scheme="Token",
    )
)

# flask app to handle redirect from approval browser process
app = Flask("redirect")
# app.debug = True


@apis.command("list-banks")
@click.argument('country')
@click.pass_context
def list_banks(ctx, country):
    """list banks by country code, COUNTRY is 'GB', 'US' etc"""
    data = client.list_banks(country)
    # print(json.dumps(data, indent=4))
    formatter.pr_banks(data, ctx.obj['output'])


@apis.command("show-bank")
@click.argument('id')
def list_banks(id):
    """show bank by id"""
    data = client.show_bank(id)
    print(json.dumps(data, indent=4))


@apis.command("list-requisitions")
def requisitions():
    """List all the requisitions associated with the token"""
    data = client.list_requisitions()
    # for requisition in requisitions['results']:
    #   print("{} : {}".format(requisition['id'], requisition['accounts']))
    print(json.dumps(data, indent=4))


@apis.command("delete-requisition")
@click.argument('id')
def deleterequisition(id):
    """Delete requisition based on its uuid"""
    response = client.delete_requisitions(id)


@apis.command("list-endusers")
def list_endusers():
    data = client.list_requisitions()["results"]
    results = [d['enduser_id'] for d in data]
    data = list(set(results))
    print(json.dumps(data, indent=4))


@apis.command("list-account-transactions")
@click.argument('account_id')
@click.pass_context
def transactions(ctx, account_id):
    """List all transactions for account"""
    data = client.list_transactions(account_id)
    formatter.pr_transactions(data, ctx.obj['output'])

    # for transaction in data['transactions']['booked']:
    #     #print("{} : {}".format(transaction['id'], transaction['accounts']))
    #     print(transaction['bookingDate'] + " " +
    #           transaction['remittanceInformationUnstructured'])
        # print("")
    # print(json.dumps(transactions, indent=4))


@apis.command("show-account-balance")
@click.argument('id')
def show_balance(id):
    """show balance for account"""
    response = client.show_balance(id)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))


@apis.command("show-account-detail")
@click.argument('account_id')
def show_account_detail(account_id):
    """show detail for account"""
    response = client.show_account_detail(account_id)
    data = json.loads(response.text)
    print(json.dumps(data, indent=4))


@apis.command("list-agreements")
@click.argument('user_id')
def list_agreements(user_id):
    """end user agreements"""
    data = client.list_agreements(user_id)
    print(json.dumps(data, indent=4))


@apis.command("delete-agreement")
@click.argument('agreement_id')
def deleterequisition(agreement_id):
    """Delete agreement based on its id"""
    response = client.delete_agreement(agreement_id)


@apis.command("create-requisition")
@click.argument('bank_id')
@click.argument('user_id')
def create_requisition(bank_id, user_id):
    """create a bank requition by bank ID and user ID"""
    data = client.create_requisition(bank_id, user_id)
    print(json.dumps(data, indent=4))


@apis.command("show-requisition")
@click.argument('requisition_id')
def show_requisition(requisition_id):
    """ show the details relating to a requisition """
    data = client.show_requisition(requisition_id)
    print(json.dumps(data, indent=4))


@apis.command("show-requisition-links")
@click.argument('requisition_id')
@click.argument('bank_id')
def show_requisition_links(requisition_id, bank_id):
    """get approval links for requisition"""
    data = client.show_requisition_links(requisition_id, bank_id)
    print(json.dumps(data, indent=4))


@apis.command("create-approval")
@click.argument('bank_id')
@click.argument('user_id')
def create_approval(bank_id, user_id):
    """create a bank approval, including agreement and requisition
    present the approval user interface to the user via flask App"""

    # create a default agreement for 90 days access
    data = client.create_end_user_agreement(bank_id, user_id)
    # print("agreement data")
    # print(json.dumps(data, indent=4))
    agreement_id = data['id']
    print("agreement id: {}".format(agreement_id))

    # create a requsition for the previously created agreement
    data = client.create_requisition(user_id, agreements=[agreement_id])
    # print("requisition data")
    # print(json.dumps(data, indent=4))
    requisition_id = data['id']
    print("requisition_id: {}".format(requisition_id))

    # get the approval links for the previously created requisition
    data = client.show_requisition_links(requisition_id, bank_id)
    # print("initiate link for authorization")
    # print(json.dumps(data, indent=4))
    initiate = data["initiate"]
    print("initiate link: {}".format(initiate))

    # open the approval links in the default browser in a tab (if possible)
    webbrowser.open_new_tab(initiate)

    # run flask to handle the return redirect from the approval process
    app.run()

    # now the approval has been accepted, the accounts field is populated
    data = client.show_requisition(requisition_id)
    print("requisition should now have account information")
    # print(json.dumps(data, indent=4))

    print("""you are now linked to the following accounts""")
    for account in data["accounts"]:
        print("account id: {}".format(account))


@apis.command("test-approval")
def test_approval():
    app.run()


@app.route("/redirect")
def handle_redirect():
    return "you have been redirected back after approval process"


@app.after_request
def after_request_func(response):
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        raise RuntimeError('Not running werkzeug')
    shutdown_func()
    return response


if __name__ == '__main__':
    apis(obj={}, prog_name='nordctl')
