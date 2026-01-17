# Copyright 2017-2018 Akretion (http://www.akretion.com)
# Sebastien BEAU <sebastien.beau@akretion.com>
# Raphael Reverdy <raphael.reverdy@akretion.com>
# Adapted by PowerOn | Wapsol GmbH
# License OPL-1

{
    "name": "JSONifier",
    "summary": "JSON-ify data for all models with optional async support",
    "version": "18.0.2.0.0",
    "category": "Technical",
    "website": "https://simplify-erp.de/apps",
    "author": "PowerOn | Wapsol GmbH, Akretion, ACSONE, Camptocamp",
    "license": "OPL-1",
    "price": "0.0",
    "currency": "EUR",
    "installable": True,
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_exports_view.xml",
        "views/ir_exports_resolver_view.xml",
        "views/jsonify_job_views.xml",
    ],
    "demo": [
        "demo/resolver_demo.xml",
        "demo/export_demo.xml",
        "demo/ir.exports.line.csv",
    ],
    "external_dependencies": {
        "python": [],
    },
    # queue_job is optional - async features require it
    # Install from: https://github.com/euroblaze/queue_job
}
