{
    "name": "Fiscal Accounting (Dominican Republic)",
    "summary": """
        This module implements the administration and management of fiscal
        receipt numbers for compliance with norm 06-18 of the Internal
        Tax Directorate in the Dominican Republic.""",
    "author": "iterativo LLC, Indexa, Alytic, TAILORW-SAS",
    "category": "Accounting/Localizations",
    "license": "LGPL-3",
    "website": "https://github.com/tailorw-sas/l10n-dominicana",
    "version": "18.0.1.0.0",
    "countries": ["do"],
    "depends": [
        "l10n_latam_invoice_document",
        "l10n_do",
    ],
    "external_dependencies": {
        "python": ["pyOpenSSL"],
    },
    "data": [
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "data/l10n_latam.document.type.csv",
        "wizard/account_move_reversal_views.xml",
        "wizard/account_move_cancel_views.xml",
        "wizard/account_debit_note_views.xml",
        "views/res_config_settings_view.xml",
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/res_company_views.xml",
        "views/account_dgii_menuitem.xml",
        "views/account_journal_views.xml",
        "views/l10n_latam_document_type_views.xml",
        "views/report_invoice.xml",
        "views/report_templates.xml",
    ],
    "demo": [
        "demo/res_partner_demo.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
