# CLAUDE.md - JSONifier

## Module Purpose

JSON serialization for Odoo 18 models with configurable field mappings.

## Key Models

- `ir.exports`: Export configuration
- `ir.exports.line`: Field mappings
- `ir.exports.resolver`: Custom field resolvers

## Extension Points

- Create custom resolvers by inheriting `ir.exports.resolver`
- Extend export configs for new models

## Testing

Test via Settings > Technical > Exports. Create export config, add fields, call `jsonify()` method.
