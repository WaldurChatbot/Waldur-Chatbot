
get_projects = "REQUEST~get_projects"
get_services = "REQUEST~get_services"
get_vms = "REQUEST~get_vms"
get_organisations = "REQUEST~get_organisations"
get_projects_by_organisation = "REQUEST~get_projects_by_organisation"
get_total_costs = "REQUEST~get_totalcosts"

data = [
    [
        'my projects',
        get_projects
    ],
    [
        'my services',
        get_services
    ],
    [
        'my virtual machines',
        get_vms
    ],
    [
        'my organisations',
        get_organisations
    ],
    [
        'my total costs',
        get_total_costs
    ],
    [
        'my projects of organisation',
        get_projects_by_organisation
    ]
]

buffer = []
for s in ["please", "please give", "give",
          "i want", "give me", "can i have"]:
    for ss in data:
        ss = ss
        buffer.append([
            s + " " + ss[0],
            ss[1]
        ])

data.extend(buffer)

