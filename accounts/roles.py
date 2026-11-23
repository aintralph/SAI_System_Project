"""
Centralized Role Definitions and Configuration for Nissin Indirect Materials System.

This module defines the ten confirmed internal system roles, their operational
responsibilities, authorized modules, permissions, and navigation items.

Important architectural constraints:
- 'enduser-maintenance-lead' is a single combined role with identical permissions.
- 'Supplier' is reserved for potential future external access; not implemented here.
- Groups and Permissions utilize Django's standard auth framework.
"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


ROLE_DEFINITIONS = {
    'system-administrator': {
        'slug': 'system-administrator',
        'display': 'System Administrator',
        'short_name': 'SysAdmin',
        'badge_class': 'green',
        'description': 'Manage authorized employee accounts, assign roles, activate/deactivate accounts, and manage system permissions.',
        'phase_status': 'Active — user and role management available via Django Admin.',
        'permissions': [
            ('can_manage_accounts', 'Can manage authorized employee accounts'),
            ('can_assign_roles', 'Can assign system roles to users'),
            ('can_manage_permissions', 'Can manage access permissions'),
            ('can_view_audit_trail', 'Can view security audit trail logs'),
        ],
        'nav_items': [
            {'title': 'Account Management', 'icon': '&#9881;'},
            {'title': 'Role Assignments', 'icon': '&#9671;'},
            {'title': 'Access Permissions', 'icon': '&#9670;'},
            {'title': 'Audit Log Records', 'icon': '&#128196;'},
        ],
        'modules': [
            {
                'title': 'Authorized Employee Accounts',
                'description': 'Create, review, update, and manage verified employee profiles in the system.',
                'scope': 'User Lifecycle Management',
                'icon': '&#128100;',
                'status': 'Operational Scope',
                'actions': ['Create Account', 'View Directory', 'Update Profile'],
            },
            {
                'title': 'System Role Assignment',
                'description': 'Assign and maintain internal operational roles across the 10 authorized system designations.',
                'scope': 'RBAC Group Control',
                'icon': '&#9671;',
                'status': 'Operational Scope',
                'actions': ['Manage Role Groups', 'Audit Assignments', 'Revoke Roles'],
            },
            {
                'title': 'Account Activation & Deactivation',
                'description': 'Safely activate authorized personnel and deactivate separated or transferred employee accounts.',
                'scope': 'Access Revocation',
                'icon': '&#128274;',
                'status': 'Operational Scope',
                'actions': ['Toggle Active State', 'Deactivation History', 'Security Review'],
            },
            {
                'title': 'Access Permission Governance',
                'description': 'Enforce least-privilege security policies and server-side authorization boundaries.',
                'scope': 'Permission Matrices',
                'icon': '&#9670;',
                'status': 'Operational Scope',
                'actions': ['Inspect Permissions', 'Model Grants', 'Verify Restrictions'],
            },
        ],
    },

    'enduser-maintenance-lead': {
        'slug': 'enduser-maintenance-lead',
        'display': 'End-user / Maintenance Lead',
        'short_name': 'EU / ML',
        'badge_class': 'blue',
        'description': 'Submit indirect material requests, track request progression, and acknowledge issued stock.',
        'phase_status': 'Active — indirect material request lifecycle and tracking.',
        'permissions': [
            ('can_submit_material_request', 'Can submit indirect material requests'),
            ('can_track_own_requests', 'Can view and track own requests'),
            ('can_acknowledge_materials', 'Can acknowledge issued materials'),
        ],
        'nav_items': [
            {'title': 'Submit Request', 'icon': '&#9998;'},
            {'title': 'My Requests Queue', 'icon': '&#128221;'},
            {'title': 'Material Acknowledgments', 'icon': '&#9989;'},
            {'title': 'Request History', 'icon': '&#128340;'},
        ],
        'modules': [
            {
                'title': 'Submit Material Request',
                'description': 'Initiate requisitions for indirect materials specifying clear item descriptions, quantities, and operational purpose.',
                'scope': 'Requisition Intake',
                'icon': '&#9998;',
                'status': 'Operational Scope',
                'actions': ['New Material Request', 'Draft Requests', 'Submission Rules'],
            },
            {
                'title': 'Track Own Requests',
                'description': 'Monitor real-time approval, PR generation, procurement canvassing, and fulfillment milestones for submitted requests.',
                'scope': 'Status Visibility',
                'icon': '&#128221;',
                'status': 'Operational Scope',
                'actions': ['View Active Queue', 'Filter by Urgency', 'Track Status'],
            },
            {
                'title': 'Material Specifications & Purpose',
                'description': 'Provide required technical notes, machine references, department allocation, and justification.',
                'scope': 'Specification Detail',
                'icon': '&#128203;',
                'status': 'Operational Scope',
                'actions': ['Attach Specs', 'Edit Purpose Details', 'Review Quantities'],
            },
            {
                'title': 'Acknowledge Issued Materials',
                'description': 'Confirm physical receipt of indirect materials released by the SIC / Stockroom team upon issuance.',
                'scope': 'Fulfillment Sign-off',
                'icon': '&#9989;',
                'status': 'Operational Scope',
                'actions': ['Pending Sign-offs', 'Acknowledge Batch', 'Issuance Receipts'],
            },
        ],
    },

    'pr-creator': {
        'slug': 'pr-creator',
        'display': 'PR Creator',
        'short_name': 'PR Creator',
        'badge_class': 'green',
        'description': 'Process assigned material requests, prepare Purchase Requisitions, record SAP PR numbers, and log revisions.',
        'phase_status': 'Active — purchase requisition preparation and SAP synchronization logging.',
        'permissions': [
            ('can_view_assigned_requests', 'Can view assigned material requests'),
            ('can_prepare_pr', 'Can prepare Purchase Requisitions'),
            ('can_record_sap_pr', 'Can record SAP PR references'),
            ('can_track_pr_history', 'Can track PR revisions and history'),
        ],
        'nav_items': [
            {'title': 'Assigned Requests', 'icon': '&#128229;'},
            {'title': 'Prepare PR', 'icon': '&#128221;'},
            {'title': 'SAP PR References', 'icon': '&#128279;'},
            {'title': 'PR Revision History', 'icon': '&#128337;'},
        ],
        'modules': [
            {
                'title': 'Assigned Material Requests Queue',
                'description': 'Review incoming material requisitions assigned from maintenance leads for requisition drafting.',
                'scope': 'Request Processing',
                'icon': '&#128229;',
                'status': 'Operational Scope',
                'actions': ['View Pending Queue', 'Inspect Items', 'Validate Quantities'],
            },
            {
                'title': 'Purchase Requisition Preparation',
                'description': 'Prepare standardized indirect material Purchase Requisitions aligned with procurement policy.',
                'scope': 'PR Assembly',
                'icon': '&#128221;',
                'status': 'Operational Scope',
                'actions': ['Create Draft PR', 'Group Request Items', 'Compile Dossier'],
            },
            {
                'title': 'SAP PR Reference Recording',
                'description': 'Record and verify official SAP Purchase Requisition reference numbers for cross-system tracking.',
                'scope': 'ERP Reference Synchronization',
                'icon': '&#128279;',
                'status': 'Operational Scope',
                'actions': ['Log SAP PR Number', 'Verify System Code', 'Audit References'],
            },
            {
                'title': 'PR Revision & History Tracking',
                'description': 'Maintain comprehensive change logs, version histories, and remarks for revised requisitions.',
                'scope': 'Version Audit',
                'icon': '&#128337;',
                'status': 'Operational Scope',
                'actions': ['View Version Log', 'Record Modification Note', 'Compare Revisions'],
            },
        ],
    },

    'odm': {
        'slug': 'odm',
        'display': 'ODM',
        'short_name': 'ODM',
        'badge_class': 'amber',
        'description': 'Review department PRs in SAP, record official decision outcomes, and archive supporting evidence.',
        'phase_status': 'Active — department PR review and decision recording.',
        'permissions': [
            ('can_review_sap_prs', 'Can review applicable PRs in SAP'),
            ('can_record_odm_decisions', 'Can record ODM decision outcomes and evidence'),
        ],
        'nav_items': [
            {'title': 'PR Review Queue', 'icon': '&#128065;'},
            {'title': 'SAP Verification', 'icon': '&#128279;'},
            {'title': 'Decision Records', 'icon': '&#128203;'},
            {'title': 'Evidence Archives', 'icon': '&#128193;'},
        ],
        'modules': [
            {
                'title': 'Applicable SAP PR Review Queue',
                'description': 'Inspect pending indirect material Purchase Requisitions within the department operational scope.',
                'scope': 'Departmental PR Review',
                'icon': '&#128065;',
                'status': 'Operational Scope',
                'actions': ['Review Queue', 'Check Operational Justification', 'Verify Line Items'],
            },
            {
                'title': 'Decision Outcome Recording',
                'description': 'Record verified decision outcomes (Approved, Rejected, Requires Revision) with official remarks.',
                'scope': 'Decision Audit',
                'icon': '&#128203;',
                'status': 'Operational Scope',
                'actions': ['Record Approval', 'Document Revision Notes', 'Log Rejection Basis'],
            },
            {
                'title': 'Supporting Evidence Documentation',
                'description': 'Log external SAP transaction codes, screenshots, and supporting documentary evidence.',
                'scope': 'Evidence Management',
                'icon': '&#128193;',
                'status': 'Operational Scope',
                'actions': ['Archive SAP Code', 'Upload Supporting Notes', 'Review History'],
            },
        ],
    },

    'procurement-specialist': {
        'slug': 'procurement-specialist',
        'display': 'Procurement Specialist',
        'short_name': 'Procurement Spec.',
        'badge_class': 'green',
        'description': 'Source suppliers, record and compare quotations, prepare recommendations, record PO references, and follow up.',
        'phase_status': 'Active — quotation canvassing, supplier comparison, and PO tracking.',
        'permissions': [
            ('can_source_suppliers', 'Can handle supplier sourcing'),
            ('can_record_quotations', 'Can record supplier quotations'),
            ('can_compare_quotations', 'Can compare quotations'),
            ('can_recommend_suppliers', 'Can prepare supplier recommendations'),
            ('can_record_po_references', 'Can record applicable PO references'),
            ('can_followup_suppliers', 'Can follow up with suppliers'),
        ],
        'nav_items': [
            {'title': 'Supplier Sourcing', 'icon': '&#127970;'},
            {'title': 'Quotations Intake', 'icon': '&#128181;'},
            {'title': 'Quotation Comparison', 'icon': '&#9878;'},
            {'title': 'Supplier Recommendations', 'icon': '&#128221;'},
            {'title': 'PO References & Follow-up', 'icon': '&#128230;'},
        ],
        'modules': [
            {
                'title': 'Supplier Sourcing & Canvassing',
                'description': 'Identify accredited suppliers, solicit formal bids, and coordinate indirect material procurement specs.',
                'scope': 'Supplier Sourcing',
                'icon': '&#127970;',
                'status': 'Operational Scope',
                'actions': ['Browse Accredited Vendors', 'Send RFP', 'Track Inquiries'],
            },
            {
                'title': 'Quotation Recording & Management',
                'description': 'Record itemized vendor pricing, lead times, warranty conditions, and commercial terms.',
                'scope': 'Quotation Intake',
                'icon': '&#128181;',
                'status': 'Operational Scope',
                'actions': ['Record Quote', 'Upload Quotation Sheet', 'Verify Validity Date'],
            },
            {
                'title': 'Quotation Canvass Comparison',
                'description': 'Conduct objective side-by-side comparative analysis of supplier bids against budget and delivery parameters.',
                'scope': 'Comparative Analysis',
                'icon': '&#9878;',
                'status': 'Operational Scope',
                'actions': ['Generate Comparison Table', 'Rank Value Proposals', 'Flag Outliers'],
            },
            {
                'title': 'Supplier Recommendation',
                'description': 'Prepare formal supplier selection recommendations detailing technical compliance and commercial rationale.',
                'scope': 'Award Justification',
                'icon': '&#128221;',
                'status': 'Operational Scope',
                'actions': ['Draft Recommendation', 'Attach Canvass Summary', 'Submit for Lead Review'],
            },
            {
                'title': 'PO References & Supplier Follow-up',
                'description': 'Record generated SAP PO numbers, confirm order receipt with chosen vendors, and follow up delivery dates.',
                'scope': 'Order Execution',
                'icon': '&#128230;',
                'status': 'Operational Scope',
                'actions': ['Log SAP PO Number', 'Update Delivery ETA', 'Record Vendor Follow-ups'],
            },
        ],
    },

    'procurement-site-lead': {
        'slug': 'procurement-site-lead',
        'display': 'Procurement Site Lead',
        'short_name': 'Site Lead',
        'badge_class': 'amber',
        'description': 'Review PO approval information, verify supplier awards, and record external SAP review evidence.',
        'phase_status': 'Active — PO approval review and external SAP verification.',
        'permissions': [
            ('can_review_po_approvals', 'Can review applicable PO approval information'),
            ('can_record_sap_review_evidence', 'Can record external SAP review evidence'),
        ],
        'nav_items': [
            {'title': 'PO Approval Queue', 'icon': '&#128065;'},
            {'title': 'Canvass Review', 'icon': '&#9878;'},
            {'title': 'SAP Review Evidence', 'icon': '&#128279;'},
            {'title': 'Lead Endorsement Log', 'icon': '&#128203;'},
        ],
        'modules': [
            {
                'title': 'PO Approval Information Review',
                'description': 'Review purchase order packages, vendor canvass comparisons, and cost justifications prior to site endorsement.',
                'scope': 'Procurement Review',
                'icon': '&#128065;',
                'status': 'Operational Scope',
                'actions': ['Review Open Packages', 'Inspect Canvass Results', 'Verify Commercial Terms'],
            },
            {
                'title': 'External SAP Review Evidence',
                'description': 'Record external SAP transaction approvals, verification reference codes, and review timestamps.',
                'scope': 'ERP Review Verification',
                'icon': '&#128279;',
                'status': 'Operational Scope',
                'actions': ['Log SAP Review Reference', 'Record Endorsement Status', 'Archive Review Stamp'],
            },
            {
                'title': 'Procurement Compliance Oversight',
                'description': 'Ensure indirect material requisitions adhere to Nissin procurement thresholds and audit guidelines.',
                'scope': 'Governance & Policy',
                'icon': '&#128203;',
                'status': 'Operational Scope',
                'actions': ['Check Threshold Compliance', 'Review Sole Source Flags', 'Audit Records'],
            },
        ],
    },

    'laguna-manager': {
        'slug': 'laguna-manager',
        'display': 'Laguna Manager',
        'short_name': 'Laguna Mgr',
        'badge_class': 'amber',
        'description': 'Review management-level PO approvals for the Laguna site and record external SAP approval evidence.',
        'phase_status': 'Active — Laguna management-level approvals and SAP sign-off logging.',
        'permissions': [
            ('can_review_mgmt_po_approvals', 'Can review applicable management-level PO approvals'),
            ('can_record_mgmt_sap_evidence', 'Can record external SAP approval evidence'),
        ],
        'nav_items': [
            {'title': 'Management PO Queue', 'icon': '&#128202;'},
            {'title': 'SAP Approval Verification', 'icon': '&#128279;'},
            {'title': 'Laguna Plant Authorizations', 'icon': '&#128196;'},
            {'title': 'Executive Audit Log', 'icon': '&#128340;'},
        ],
        'modules': [
            {
                'title': 'Management-Level PO Approval Queue',
                'description': 'Review high-value, plant-critical indirect material procurement orders for the Laguna manufacturing plant.',
                'scope': 'Executive Approval',
                'icon': '&#128202;',
                'status': 'Operational Scope',
                'actions': ['Review High-Value POs', 'Examine Budget Line', 'Evaluate Site Impact'],
            },
            {
                'title': 'External SAP Approval Evidence',
                'description': 'Record management-level SAP approval release codes and verification timestamps for audited commitments.',
                'scope': 'SAP Release Audit',
                'icon': '&#128279;',
                'status': 'Operational Scope',
                'actions': ['Record Release Code', 'Log Management Approval', 'Archive Evidence'],
            },
            {
                'title': 'Laguna Plant Expenditure Governance',
                'description': 'Monitor site-wide indirect material procurement spend against operating budgets and planned maintenance.',
                'scope': 'Budget Governance',
                'icon': '&#128196;',
                'status': 'Operational Scope',
                'actions': ['Review Site Spend', 'Quarterly Commitments', 'Expenditure Summary'],
            },
        ],
    },

    'sic-stockroom-gr-creator': {
        'slug': 'sic-stockroom-gr-creator',
        'display': 'SIC / Stockroom / GR Creator',
        'short_name': 'SIC / GR Creator',
        'badge_class': 'blue',
        'description': 'Handle receiving records, record SAP GR references, manage authorized inventory, record stock issuance, and maintain MIS.',
        'phase_status': 'Active — receiving, goods receipt logging, inventory, and issuance records.',
        'permissions': [
            ('can_handle_receiving', 'Can handle receiving records'),
            ('can_record_gr_references', 'Can record applicable GR references'),
            ('can_manage_inventory', 'Can manage authorized inventory activities'),
            ('can_record_stock_issuance', 'Can record stock issuance'),
            ('can_maintain_mis_docs', 'Can maintain applicable MIS documentation'),
        ],
        'nav_items': [
            {'title': 'Receiving Records', 'icon': '&#128230;'},
            {'title': 'SAP GR References', 'icon': '&#128279;'},
            {'title': 'Stockroom Inventory', 'icon': '&#128190;'},
            {'title': 'Stock Issuance', 'icon': '&#128228;'},
            {'title': 'MIS Documentation', 'icon': '&#128196;'},
        ],
        'modules': [
            {
                'title': 'Material Receiving Records',
                'description': 'Record physical shipments received at the plant, verify quantities against delivery receipts and PO items.',
                'scope': 'Inbound Receiving',
                'icon': '&#128230;',
                'status': 'Operational Scope',
                'actions': ['Log Inbound Shipment', 'Record Packing Slip', 'Flag Discrepancies'],
            },
            {
                'title': 'SAP Goods Receipt (GR) References',
                'description': 'Record and link official SAP Goods Receipt (GR) document numbers for accepted physical deliveries.',
                'scope': 'SAP GR Synchronization',
                'icon': '&#128279;',
                'status': 'Operational Scope',
                'actions': ['Record SAP GR Number', 'Validate PO Line Match', 'Archive GR Stamp'],
            },
            {
                'title': 'Authorized Stockroom Inventory',
                'description': 'Manage indirect material stockroom bins, storage locations, stock balances, and authorized cycle counts.',
                'scope': 'Stockroom Control',
                'icon': '&#128190;',
                'status': 'Operational Scope',
                'actions': ['Inspect Stockroom Bins', 'View Stock Balances', 'Log Inventory Adjustments'],
            },
            {
                'title': 'Stock Issuance Records',
                'description': 'Record the physical transfer of stored materials to requesting maintenance leads and operating units.',
                'scope': 'Material Issuance',
                'icon': '&#128228;',
                'status': 'Operational Scope',
                'actions': ['Issue Materials to User', 'Generate Issuance Record', 'Track Pending Pickup'],
            },
            {
                'title': 'MIS Documentation Management',
                'description': 'Maintain authorized Material Issuance Slips (MIS) and receiving documentation archives for internal audit.',
                'scope': 'MIS Archival',
                'icon': '&#128196;',
                'status': 'Operational Scope',
                'actions': ['File MIS Slips', 'Search MIS Numbers', 'Export Log Summary'],
            },
        ],
    },

    'dct': {
        'slug': 'dct',
        'display': 'DCT',
        'short_name': 'DCT (Doc Control)',
        'badge_class': 'blue',
        'description': 'Handle invoice documentation, record invoice handoffs to Finance, and record applicable SAP upload evidence.',
        'phase_status': 'Active — invoice documentation, handoff logging, and SAP upload tracking.',
        'permissions': [
            ('can_handle_invoice_docs', 'Can handle invoice documentation'),
            ('can_record_invoice_handoff', 'Can record invoice handoffs'),
            ('can_record_sap_upload_evidence', 'Can record applicable SAP upload evidence'),
        ],
        'nav_items': [
            {'title': 'Invoice Documentation', 'icon': '&#128196;'},
            {'title': 'Invoice Handoff Records', 'icon': '&#128257;'},
            {'title': 'SAP Upload Evidence', 'icon': '&#128279;'},
            {'title': 'Document Tracking Log', 'icon': '&#128340;'},
        ],
        'modules': [
            {
                'title': 'Invoice Documentation Management',
                'description': 'Verify completeness of supplier commercial invoices, billing statements, and attached delivery documents.',
                'scope': 'Document Ingestion',
                'icon': '&#128196;',
                'status': 'Operational Scope',
                'actions': ['Log Vendor Invoice', 'Verify Complete Attachments', 'Match with PO/GR'],
            },
            {
                'title': 'Invoice Handoff Records',
                'description': 'Record formal physical and electronic handoffs of verified invoice packages to Accounting & Finance.',
                'scope': 'Custody Transmittal',
                'icon': '&#128257;',
                'status': 'Operational Scope',
                'actions': ['Create Handoff Transmittal', 'Record Finance Recipient', 'Track In-Transit Docs'],
            },
            {
                'title': 'SAP Upload Evidence Records',
                'description': 'Record external SAP invoice verification entry status, upload references, and digital document stamps.',
                'scope': 'SAP Upload Verification',
                'icon': '&#128279;',
                'status': 'Operational Scope',
                'actions': ['Log SAP Upload Number', 'Verify Entry Status', 'Archive Digital Proof'],
            },
        ],
    },

    'accounting-finance': {
        'slug': 'accounting-finance',
        'display': 'Accounting & Finance',
        'short_name': 'Acctg & Finance',
        'badge_class': 'green',
        'description': 'Review financial documentation, record authorized Finance status, and maintain payment-related references.',
        'phase_status': 'Active — financial review, status approval, and payment settlement records.',
        'permissions': [
            ('can_review_financial_docs', 'Can review financial documentation'),
            ('can_record_finance_status', 'Can record authorized Finance status'),
            ('can_maintain_payment_refs', 'Can maintain payment-related references'),
        ],
        'nav_items': [
            {'title': 'Financial Doc Review', 'icon': '&#128181;'},
            {'title': 'Finance Status Queue', 'icon': '&#9989;'},
            {'title': 'Payment References', 'icon': '&#128279;'},
            {'title': 'Disbursement Audit', 'icon': '&#128203;'},
        ],
        'modules': [
            {
                'title': 'Financial Documentation Review',
                'description': 'Perform three-way match auditing against PO, GR, and vendor invoice prior to disbursement authorization.',
                'scope': '3-Way Match Audit',
                'icon': '&#128181;',
                'status': 'Operational Scope',
                'actions': ['Perform 3-Way Match', 'Verify Tax Computations', 'Review Cost Center'],
            },
            {
                'title': 'Authorized Finance Status Recording',
                'description': 'Record official finance processing status (Verified, Scheduled, Approved for Payment, On Hold).',
                'scope': 'Disbursement Status',
                'icon': '&#9989;',
                'status': 'Operational Scope',
                'actions': ['Update Finance Status', 'Log Approval Sign-off', 'Record Payment Hold Reason'],
            },
            {
                'title': 'Payment-Related Reference Maintenance',
                'description': 'Record and maintain check numbers, EFT disbursement references, payment voucher codes, and clearance dates.',
                'scope': 'Settlement Tracking',
                'icon': '&#128279;',
                'status': 'Operational Scope',
                'actions': ['Log Payment Voucher', 'Record Check / EFT Number', 'Record Settlement Date'],
            },
        ],
    },
}


def setup_system_roles():
    """
    Ensure all 10 internal system roles exist as Django Groups with their
    appropriate permissions.

    Idempotent: safe to run multiple times without duplicating groups or permissions.
    Preserves existing users, groups, and permissions.
    """
    content_type = ContentType.objects.get_for_model(User)
    created_groups_count = 0
    existing_groups_count = 0
    created_perms_count = 0

    for slug, role_data in ROLE_DEFINITIONS.items():
        group, created = Group.objects.get_or_create(name=slug)
        if created:
            created_groups_count += 1
        else:
            existing_groups_count += 1

        # Create and assign permissions
        for codename, name in role_data.get('permissions', []):
            perm, p_created = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )
            if p_created:
                created_perms_count += 1
            if not group.permissions.filter(pk=perm.pk).exists():
                group.permissions.add(perm)

    return {
        'created_groups': created_groups_count,
        'existing_groups': existing_groups_count,
        'created_permissions': created_perms_count,
        'total_roles': len(ROLE_DEFINITIONS),
    }


def get_user_operational_roles(user):
    """
    Return a list of role definitions for all roles assigned to the given user.
    """
    if not user.is_authenticated:
        return []
    user_groups = set(user.groups.values_list('name', flat=True))
    assigned = []
    for slug, info in ROLE_DEFINITIONS.items():
        if slug in user_groups:
            assigned.append(info)
    return assigned


def get_post_login_redirect_url(user):
    """
    Determine the post-login destination based on user roles:
    - Superusers / staff / system-administrator -> Overview/Superadmin dashboard ('accounts:home')
    - Users with exactly 1 operational role -> Direct to role's dashboard ('accounts:dashboard')
    - Users with multiple operational roles -> Overview ('accounts:home')
    - Users without an operational role -> Safe landing on Overview ('accounts:home')
    """
    if not user.is_authenticated:
        return '/accounts/login/'

    # Superadmin or Staff always goes to the Superadmin dashboard
    if user.is_superuser or user.is_staff:
        return '/accounts/home/'

    operational_roles = get_user_operational_roles(user)

    # System administrator role goes to accounts:home
    has_sysadmin = any(r['slug'] == 'system-administrator' for r in operational_roles)
    if has_sysadmin:
        return '/accounts/home/'

    # Exactly one operational role redirects directly to their dashboard
    if len(operational_roles) == 1:
        return f"/accounts/dashboard/{operational_roles[0]['slug']}/"

    # Multiple roles or 0 roles redirect to accounts:home
    return '/accounts/home/'
