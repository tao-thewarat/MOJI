from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    sequence = fields.Char(
        string="Sequence",
        readonly=True,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            if rec.project_id.sequence_id:
                rec.sequence = rec.project_id.sequence_id.next_by_id()
        return res
