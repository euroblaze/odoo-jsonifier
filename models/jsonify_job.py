# Copyright 2025 Euroblaze/PowerOn
# License OPL-1

import json
import logging
import base64
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Check if queue_job is available
try:
    from odoo.addons.queue_job.job import job
    QUEUE_JOB_AVAILABLE = True
except ImportError:
    QUEUE_JOB_AVAILABLE = False
    # Dummy decorator when queue_job not installed
    def job(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class JsonifyJob(models.Model):
    """Track async jsonification jobs and store results."""
    _name = "jsonify.job"
    _description = "Async JSON Export Job"
    _order = "create_date desc"

    name = fields.Char(
        string="Description",
        required=True,
        default=lambda self: f"JSON Export {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    state = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Completed'),
        ('failed', 'Failed'),
    ], string="Status", default='pending', required=True, index=True)

    # Source configuration
    model_name = fields.Char(string="Model", required=True, index=True)
    record_ids = fields.Text(
        string="Record IDs",
        help="JSON list of record IDs to export"
    )
    parser = fields.Text(
        string="Parser Configuration",
        help="JSON parser configuration"
    )
    export_id = fields.Many2one(
        comodel_name="ir.exports",
        string="Export Template",
        ondelete="set null"
    )

    # Processing options
    batch_size = fields.Integer(
        string="Batch Size",
        default=100,
        help="Records per batch for memory management"
    )
    with_fieldname = fields.Boolean(
        string="Include Field Names",
        default=False
    )

    # Results
    result_attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Result File",
        ondelete="cascade"
    )
    result_count = fields.Integer(string="Records Exported", default=0)
    error_message = fields.Text(string="Error Details")

    # Timing
    started_at = fields.Datetime(string="Started At")
    completed_at = fields.Datetime(string="Completed At")

    # Queue job reference
    job_uuid = fields.Char(string="Job UUID", index=True)

    # Callback
    callback_method = fields.Char(
        string="Callback Method",
        help="Method to call on completion (model.method format)"
    )
    callback_record_id = fields.Integer(
        string="Callback Record ID",
        help="Record ID to call callback on"
    )

    @api.model
    def _check_queue_job_available(self):
        """Check if queue_job module is installed."""
        if not QUEUE_JOB_AVAILABLE:
            raise UserError(
                "The queue_job module is required for async exports. "
                "Please install it from: https://github.com/euroblaze/queue_job"
            )

    def action_start(self):
        """Start the async export job."""
        self.ensure_one()
        self._check_queue_job_available()

        if self.state != 'pending':
            raise UserError("Job can only be started from pending state.")

        # Enqueue the job
        delayed = self.with_delay(
            channel='root.jsonify',
            description=f"JSON Export: {self.name}"
        )._execute_export()

        self.write({
            'state': 'processing',
            'started_at': fields.Datetime.now(),
            'job_uuid': delayed.uuid if hasattr(delayed, 'uuid') else None,
        })

        return True

    @job(default_channel='root.jsonify')
    def _execute_export(self):
        """Execute the export job (runs in background)."""
        self.ensure_one()
        try:
            _logger.info("Starting JSON export job %s for model %s", self.id, self.model_name)

            # Get records
            record_ids = json.loads(self.record_ids or '[]')
            records = self.env[self.model_name].browse(record_ids).exists()

            if not records:
                raise UserError("No valid records found for export.")

            # Get parser
            if self.export_id:
                parser = self.export_id.get_json_parser()
            elif self.parser:
                parser = json.loads(self.parser)
            else:
                raise UserError("No parser configuration provided.")

            # Process in batches
            all_results = []
            total = len(records)
            batch_size = self.batch_size or 100

            for i in range(0, total, batch_size):
                batch = records[i:i + batch_size]
                batch_results = batch.jsonify(parser, with_fieldname=self.with_fieldname)
                all_results.extend(batch_results)
                _logger.info("Processed %d/%d records for job %s", min(i + batch_size, total), total, self.id)

            # Store results as attachment
            result_json = json.dumps(all_results, indent=2, ensure_ascii=False, default=str)
            attachment = self.env['ir.attachment'].create({
                'name': f"{self.name}.json",
                'type': 'binary',
                'datas': base64.b64encode(result_json.encode('utf-8')),
                'mimetype': 'application/json',
                'res_model': self._name,
                'res_id': self.id,
            })

            self.write({
                'state': 'done',
                'completed_at': fields.Datetime.now(),
                'result_attachment_id': attachment.id,
                'result_count': len(all_results),
            })

            # Execute callback if configured
            self._execute_callback()

            _logger.info("Completed JSON export job %s: %d records", self.id, len(all_results))

        except Exception as e:
            _logger.exception("Failed JSON export job %s", self.id)
            self.write({
                'state': 'failed',
                'completed_at': fields.Datetime.now(),
                'error_message': str(e),
            })
            raise

    def _execute_callback(self):
        """Execute callback method if configured."""
        self.ensure_one()
        if not self.callback_method:
            return

        try:
            model_name, method_name = self.callback_method.rsplit('.', 1)
            model = self.env[model_name]
            if self.callback_record_id:
                model = model.browse(self.callback_record_id)
            method = getattr(model, method_name, None)
            if callable(method):
                method(self)
        except Exception as e:
            _logger.warning("Callback failed for job %s: %s", self.id, e)

    def action_retry(self):
        """Retry a failed job."""
        self.ensure_one()
        if self.state != 'failed':
            raise UserError("Only failed jobs can be retried.")

        self.write({
            'state': 'pending',
            'error_message': False,
            'started_at': False,
            'completed_at': False,
        })
        return self.action_start()

    def action_cancel(self):
        """Cancel a pending job."""
        self.ensure_one()
        if self.state not in ('pending', 'processing'):
            raise UserError("Only pending or processing jobs can be cancelled.")
        self.state = 'failed'
        self.error_message = "Cancelled by user"

    def action_download(self):
        """Download the result file."""
        self.ensure_one()
        if not self.result_attachment_id:
            raise UserError("No result file available.")
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.result_attachment_id.id}?download=true',
            'target': 'self',
        }
