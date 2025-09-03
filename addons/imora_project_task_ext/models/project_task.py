from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    reporter_id = fields.Many2one(
        comodel_name="res.users",
        string="Reporter",
        default=lambda self: self.env.user,
    )
    sequence_code = fields.Char(
        string="Task Code",
        readonly=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        vals = super().create(vals_list)
        for rec in vals:
            if rec.project_id and rec.project_id.code:
                project = rec.project_id
                project.task_sequence += 1
                rec.sequence_code = f"{project.code}-{project.task_sequence}"
        return vals
