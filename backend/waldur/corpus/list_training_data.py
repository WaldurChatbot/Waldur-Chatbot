
get_projects = "REQUEST~get_projects"
get_organisations = "REQUEST~get_organisations"
get_team_of_organisation = "REQUEST~get_team_of_organisation"
get_services = "REQUEST~get_services"
get_services_by_organisation = "REQUEST~get_services_by_organisation"
get_services_by_project_and_organisation = "REQUEST~get_services_by_project_and_organisation"
get_vms = "REQUEST~get_vms"
get_vms_by_organisation = "REQUEST~get_vms_by_organisation"
get_vms_by_project_and_organisation = "REQUEST~get_vms_by_project_and_organisation"
get_private_clouds = "REQUEST~get_private_clouds"
get_private_clouds_by_organisation = "REQUEST~get_private_clouds_by_organisation"
get_private_clouds_by_project_and_organisation = "REQUEST~get_private_clouds_by_project_and_organisation"
get_audit_log_by_organisation = "REQUEST~get_audit_log_by_organisation"
get_audit_log_by_project_and_organisation = "REQUEST~get_audit_log_by_project_and_organisation"
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
        'my services of organisation',
        get_services_by_organisation
    ],
    [
        'my services in',
        get_services_by_organisation
    ],
    [
        'my services in project of organisation',
        get_services_by_project_and_organisation
    ],
    [
        'my virtual machines',
        get_vms
    ],
    [
        'my vms',
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
        'my private clouds of organisation',
        get_private_clouds_by_organisation
    ],
    [
        'my private clouds in',
        get_private_clouds_by_organisation
    ],
    [
        'my private clouds in project of organisation',
        get_private_clouds_by_project_and_organisation
    ],
    [
        'my virtual machines of organisation',
        get_vms_by_organisation
    ],
    [
        'my virtual machines in',
        get_vms_by_organisation
    ],
    [
        'my vms of organisation',
        get_vms_by_organisation
    ],
    [
        'my vms in',
        get_vms_by_organisation
    ],
    [
        'my vms in project of organisation',
        get_vms_by_project_and_organisation
    ],
    [
        'my virtual machines in project of organisation',
        get_vms_by_project_and_organisation
    ],
    [
        'my team members of organisation',
        get_team_of_organisation
    ],
    [
        'my team members in',
        get_team_of_organisation
    ],
    [
        'my audit log in',
        get_audit_log_by_organisation
    ],
    [
        'my audit log in project of organisation',
        get_audit_log_by_project_and_organisation
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
