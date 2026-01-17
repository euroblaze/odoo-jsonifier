# JSONifier

Odoo 18 JSON serialization for any model - export configurable field mappings to JSON.

## Features

- JSON export for any Odoo model via `jsonify()` method
- Configurable field parsers (simple list or advanced dict format)
- Nested relationship traversal (Many2one, One2many, Many2many)
- Field aliasing with `field_name:json_key` syntax
- Custom resolvers for field transformation
- Multi-language export support
- List marshalling for grouped fields
- Field name injection option

## Requirements

- Odoo 18.0
- base module

## Installation

1. Download and extract to your Odoo addons folder
2. Update apps list in Odoo
3. Install "JSONifier"

## Usage

### Simple Parser

```python
parser = [
    'name',
    'number',
    'create_date',
    ('partner_id', ['id', 'display_name', 'ref']),
    ('line_ids', ['id', ('product_id', ['name']), 'price_unit'])
]

records.jsonify(parser)
```

### Field Aliasing

Use `field_name:json_key` to rename fields in output:

```python
parser = [
    'name',
    'create_date:creationDate',
    ('partner_id:partner', ['id', 'display_name']),
]
```

### Custom Resolvers

Transform field values with methods or lambdas:

```python
parser = [
    ('name', 'jsonify_name'),  # method on model
    ('number', lambda rec, field: rec[field] * 2),  # callable
]
```

### Full Parser (Advanced)

```python
parser = {
    'resolver': resolver_id,  # global resolver
    'fields': [
        {'name': 'description'},
        {'name': 'number', 'resolver': 5},
        ({'name': 'partner_id', 'target': 'partner'}, [{'name': 'display_name'}]),
    ],
}
```

### Multi-Language Export

```python
parser = {
    'language_agnostic': True,
    'langs': {
        False: [{'name': 'description'}],
        'de_DE': [{'name': 'description', 'target': 'description_de'}],
    }
}
```

### List Marshalling

Group multiple fields into a list:

```python
parser = {
    'fields': [
        {'name': 'name'},
        {'name': 'tag_1', 'target': 'tags=list'},
        {'name': 'tag_2', 'target': 'tags=list'},
    ]
}
# Result: {'name': '...', 'tags': ['tag1_value', 'tag2_value']}
```

### Field Name Injection

Include field labels in output:

```python
records.jsonify(parser, with_fieldname=True)
# Result: {'fieldname_name': 'Order Reference', 'name': 'SO001'}
```

## Configuration

Configure JSON exports via Settings > Technical > Exports.

Create `ir.export.resolver` records for custom field transformations using Python code.

## Performance Considerations

The `jsonify()` method runs synchronously. For large datasets:
- Consider batch processing with smaller recordsets
- Use `queue_job` module for background processing (see [Issue #1](https://github.com/euroblaze/odoo-jsonifier/issues/1))
- Limit nested relationship depth when possible

## Credits

Based on OCA server-tools jsonifier module.

Original authors: Akretion, ACSONE, Camptocamp

## License

OPL-1 (Odoo Proprietary License v1.0)

## Support

Contact: https://simplify-erp.de/apps
