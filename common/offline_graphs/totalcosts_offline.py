import json
import collections
import matplotlib.pyplot as plt
import numpy as np

myinput = """[
  {
    "url": "https://api.etais.ee/api/invoices/bb6f38e908e7493791c65b26e88e1619/",
    "uuid": "bb6f38e908e7493791c65b26e88e1619",
    "number": 100121,
    "customer": "https://api.etais.ee/api/customers/5991d0c109df4e8cab4f9dd660295517/",
    "price": "84.9000000",
    "tax": "0.0000000",
    "total": "84.9000000",
    "state": "pending",
    "year": 2017,
    "month": 11,
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
        "price": 84.9,
        "tax": "0.0000000",
        "total": "84.9000000",
        "unit_price": "2.8300000",
        "unit": "day",
        "start": "2017-11-01T00:00:00Z",
        "end": "2017-11-30T23:59:59.999999Z",
        "product_code": "",
        "article_code": "",
        "project_name": "Waldur Chatbot testbed",
        "project_uuid": "88879e68a4c84f6ea0e05fb9bc59ea8f",
        "scope_type": "OpenStack.Tenant",
        "scope_uuid": "ed505f9ebd8c491b94c6f8dfc30b54b0",
        "package": "https://api.etais.ee/api/openstack-packages/517047bdfefe418899c981663f1ea5f5/",
        "tenant_name": "WaldurChatbot",
        "tenant_uuid": "ed505f9ebd8c491b94c6f8dfc30b54b0",
        "usage_days": 30,
        "template_name": "Generic",
        "template_uuid": "a85daef727d344b3858541e4bc29a274",
        "template_category": "Small"
      }
    ],
    "offering_items": [],
    "generic_items": []
  },
  {
    "url": "https://api.etais.ee/api/invoices/b094173f50a848e19d3362c84eabebc4/",
    "uuid": "b094173f50a848e19d3362c84eabebc4",
    "number": 100096,
    "customer": "https://api.etais.ee/api/customers/5991d0c109df4e8cab4f9dd660295517/",
    "price": "87.7300000",
    "tax": "0.0000000",
    "total": "87.7300000",
    "state": "created",
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
    "invoice_date": "2017-11-01",
    "due_date": "2017-12-01",
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
    1:'Jan',
    2:'Feb',
    3:'Mar',
    4:'Apr',
    5:'May',
    6:'Jun',
    7:'Jul',
    8:'Aug',
    9:'Sep',
    10:'Oct',
    11:'Nov',
    12:'Dec'
    }

plotx = []
ploty = []

for i in range((len(data)-1),-1,-1):
    plotx.append(num_to_monthdict[data[i]['month']] + " " + str(data[i]['year']))
    ploty.append(float(data[i]['total']))
    print ()
    print ()

'''
result = collections.OrderedDict()

for i in range(len(plotx)):
    result[plotx[i]] = float(ploty[i])
'''

print(plotx)
print(ploty)

N = len(ploty)

ind = np.arange(N)
width = 0.35
fig, ax = plt.subplots()

rects1 = ax.bar(ind, ploty, width, color='#2388d6')

ax.set_xlabel('Months')
ax.set_ylabel('Total costs')
ax.set_xticks(ind + width / 2)
ax.set_xticklabels(plotx)
ax.set_title('Last ' + str(N) + 'month total costs')

def autolabel(rects, ax):
    # Get y-axis height to calculate label position from.
    (y_bottom, y_top) = ax.get_ylim()
    y_height = y_top - y_bottom

    for rect in rects:
        height = rect.get_height()
        label_position = height + (y_height * 0.01)

        ax.text(rect.get_x() + rect.get_width()/2., label_position,
                '%d' % int(height),
                ha='center', va='bottom')

autolabel(rects1, ax)

#plt.show()
fig.savefig('foo.png')
