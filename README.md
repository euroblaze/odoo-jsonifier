# JSONifier

Odoo 18 JSON serialization for any model - export configurable field mappings to JSON.

## Features

- JSON export for any Odoo model via `jsonify()` method
- **Async export** via `jsonify_async()` with queue_job integration
- Configurable field parsers (simple list or advanced dict format)
- Nested relationship traversal (Many2one, One2many, Many2many)
- Field aliasing with `field_name:json_key` syntax
- Custom resolvers for field transformation
- Multi-language export support
- List marshalling for grouped fields
- Field name injection option
- Job tracking with progress monitoring

## Requirements

- Odoo 18.0
- base module
- **Optional:** [queue_job](https://github.com/euroblaze/queue_job) for async exports

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

## Async Export (Large Datasets)

For large datasets, use `jsonify_async()` to process exports in the background without blocking Odoo workers.

### Requirements for Async

Install queue_job module:
```bash
# Clone to your addons folder
git clone https://github.com/euroblaze/queue_job.git

# Start Odoo with queue_job runner
odoo-bin --load=web,queue_job --workers=2
```

### Basic Async Usage

```python
# Export 10,000 partners in background
partners = self.env['res.partner'].search([])
job = partners.jsonify_async(
    parser=['name', 'email', 'phone'],
    name='Partner Export',
    batch_size=500  # process 500 records per batch
)
# Returns jsonify.job record immediately
# job.state: 'pending' -> 'processing' -> 'done'
```

### Using Export Template

```python
export = self.env.ref('my_module.partner_export_template')
job = partners.jsonify_async(export_id=export.id)
```

### With Callback

```python
job = partners.jsonify_async(
    parser=['name', 'email'],
    callback_method='my.model.on_export_done',
    callback_record_id=self.id
)

# In my.model:
def on_export_done(self, job):
    # job.result_attachment_id contains the JSON file
    attachment = job.result_attachment_id
    # Process the result...
```

### Download Result

```python
# After job completes
if job.state == 'done':
    # Get attachment with JSON data
    attachment = job.result_attachment_id
    json_data = base64.b64decode(attachment.datas)
```

### Monitor Jobs

Navigate to Settings > Technical > JSON Export Jobs to view all async export jobs with status, timing, and results.

## Performance Tips

- Use `jsonify_async()` for exports > 1000 records
- Adjust `batch_size` based on record complexity (default: 100)
- Limit nested relationship depth when possible
- Configure queue channels: `ODOO_QUEUE_JOB_CHANNELS=root:4`

## Credits

Based on OCA server-tools jsonifier module.

Original authors: Akretion, ACSONE, Camptocamp

## License

OPL-1 (Odoo Proprietary License v1.0)

## Support

Contact: https://simplify-erp.de/apps
