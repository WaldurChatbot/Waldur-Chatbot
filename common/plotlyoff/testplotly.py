import plotly.offline as offline
import plotly.graph_objs as go
import json


myinput = """[
  {
    "url": "https://api.etais.ee/api/invoices/b094173f50a848e19d3362c84eabebc4/",
    "uuid": "b094173f50a848e19d3362c84eabebc4",
    "number": 100096,
    "customer": "https://api.etais.ee/api/customers/5991d0c109df4e8cab4f9dd660295517/",
    "price": "87.7300000",
    "tax": "0.0000000",
    "total": "87.7300000",
    "state": "pending",
    "year": 2017,
    "month": 10,
    "issuer_details": {
      "phone": {
        "national_number": "5555555",
        "country_code": "372"
      },
      "account": "123456789",
      "country_code": "EE",
      "address": "Lille 4-205",
      "country": "Estonia",
      "company": "OpenNode",
      "postal": "80041",
      "vat_code": "EE123456789",
      "email": "info@opennodecloud.com",
      "bank": "Estonian Bank"
    },
    "invoice_date": null,
    "due_date": null,
    "customer_details": null,
    "openstack_items": [
      {
        "name": "WaldurChatbot (Small / Generic)",
        "price": 87.73,
        "tax": "0.0000000",
        "total": "87.7300000",
        "unit_price": "2.8300000",
        "unit": "day",
        "start": "2017-10-01T00:00:00Z",
        "end": "2017-10-31T23:59:59.999999Z",
        "product_code": "",
        "article_code": "",
        "project_name": "Waldur Chatbot testbed",
        "project_uuid": "88879e68a4c84f6ea0e05fb9bc59ea8f",
        "scope_type": "OpenStack.Tenant",
        "scope_uuid": "ed505f9ebd8c491b94c6f8dfc30b54b0",
        "package": "https://api.etais.ee/api/openstack-packages/517047bdfefe418899c981663f1ea5f5/",
        "tenant_name": "WaldurChatbot",
        "tenant_uuid": "ed505f9ebd8c491b94c6f8dfc30b54b0",
        "usage_days": 31,
        "template_name": "Generic",
        "template_uuid": "a85daef727d344b3858541e4bc29a274",
        "template_category": "Small"
      }
    ],
    "offering_items": [],
    "generic_items": []
  },
  {
    "url": "https://api.etais.ee/api/invoices/b636ee1236e0486994cdd1ffda4c7e1d/",
    "uuid": "b636ee1236e0486994cdd1ffda4c7e1d",
    "number": 100076,
    "customer": "https://api.etais.ee/api/customers/5991d0c109df4e8cab4f9dd660295517/",
    "price": "11.3200000",
    "tax": "0.0000000",
    "total": "11.3200000",
    "state": "created",
    "year": 2017,
    "month": 9,
    "issuer_details": {
      "phone": {
        "national_number": "5555555",
        "country_code": "372"
      },
      "account": "123456789",
      "country_code": "EE",
      "address": "Lille 4-205",
      "country": "Estonia",
      "company": "OpenNode",
      "postal": "80041",
      "vat_code": "EE123456789",
      "email": "info@opennodecloud.com",
      "bank": "Estonian Bank"
    },
    "invoice_date": "2017-10-01",
    "due_date": "2017-10-31",
    "customer_details": null,
    "openstack_items": [
      {
        "name": "WaldurChatbot (Small / Generic)",
        "price": 11.32,
        "tax": "0.0000000",
        "total": "11.3200000",
        "unit_price": "2.8300000",
        "unit": "day",
        "start": "2017-09-27T13:53:31.425080Z",
        "end": "2017-09-30T23:59:59.999999Z",
        "product_code": "",
        "article_code": "",
        "project_name": "Waldur Chatbot testbed",
        "project_uuid": "88879e68a4c84f6ea0e05fb9bc59ea8f",
        "scope_type": "OpenStack.Tenant",
        "scope_uuid": "ed505f9ebd8c491b94c6f8dfc30b54b0",
        "package": "https://api.etais.ee/api/openstack-packages/517047bdfefe418899c981663f1ea5f5/",
        "tenant_name": "WaldurChatbot",
        "tenant_uuid": "ed505f9ebd8c491b94c6f8dfc30b54b0",
        "usage_days": 4,
        "template_name": "Generic",
        "template_uuid": "a85daef727d344b3858541e4bc29a274",
        "template_category": "Small"
      }
    ],
    "offering_items": [],
    "generic_items": []
  }
]"""

data = json.loads(myinput)


num_to_monthdict = {
    1:'January',
    2:'February',
    3:'March',
    4:'April',
    5:'May',
    6:'June',
    7:'July',
    8:'August',
    9:'September',
    10:'October',
    11:'November',
    12:'December'
    }

plotx = []
ploty = []

for i in range((len(data)-1),-1,-1):
    plotx.append(num_to_monthdict[data[i]['month']] + " " + str(data[i]['year']))
    ploty.append(data[i]['total'])
    print ()
    print ()


print(plotx)
print(ploty)

plotdata = [go.Bar(
                x=plotx,
                y=ploty
    )]

plotdata = [go.Bar(
            x=plotx,
            y=ploty,
            text=ploty,
            textposition = 'auto',
            marker=dict(
                color='rgb(158,202,225)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            ),
            opacity=0.6
        )]

plotlayout = go.Layout(
    title='Total costs for last 6 months',
    width=300,
    height=300
)

plotfigure = go.Figure(data=plotdata, layout=plotlayout)

offline.plot(plotfigure,
             image='png',
             image_width=400,
             image_height=300)
