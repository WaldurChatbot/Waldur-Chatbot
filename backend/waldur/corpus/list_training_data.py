
get_projects = "REQUEST~get_projects"
get_services = "REQUEST~get_services"
get_vms = "REQUEST~get_vms"
get_organisations = "REQUEST~get_organisations"
get_private_clouds = "REQUEST~get_private_clouds"
get_services_by_organisation = "REQUEST~get_services_by_organisation"
get_vms_by_organisation = "REQUEST~get_vms_by_organisation"
get_total_costs = "REQUEST~get_totalcosts"
create_vm = "REQUEST~create_vm"

waldur_list_corpus = [
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
        'my private clouds',
        get_private_clouds
    ],
    [
        'my services of organisation',
        get_services_by_organisation
    ],
    [
        'my virtual machines of organisation',
        get_vms_by_organisation
    ],
    [
        'createvm',
        create_vm
    ]
]

buffer = []
for s in ["please", "please give", "give",
          "i want", "give me", "can i have"]:
    for ss in waldur_list_corpus:
        ss = ss
        buffer.append([
            s + " " + ss[0],
            ss[1]
        ])

waldur_list_corpus.extend(buffer)

