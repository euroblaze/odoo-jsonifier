# Copyright 2017-2018 Akretion (http://www.akretion.com)
# Sebastien BEAU <sebastien.beau@akretion.com>
# Raphael Reverdy <raphael.reverdy@akretion.com>
# Adapted by PowerOn | Wapsol GmbH
# License OPL-1

{
    "name": "JSONifier",
    "summary": "JSON-ify data for all models",
    "version": "18.0.1.1.0",
    "category": "Technical",
    "website": "https://simplify-erp.de/apps",
    "author": "PowerOn | Wapsol GmbH, Akretion, ACSONE, Camptocamp",
    "license": "OPL-1",
    "price": "0.0",
    "currency": "EUR",
    "installable": True,
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_exports_view.xml",
        "views/ir_exports_resolver_view.xml",
    ],
    "demo": [
        "demo/resolver_demo.xml",
        "demo/export_demo.xml",
        "demo/ir.exports.line.csv",
    ],
}
