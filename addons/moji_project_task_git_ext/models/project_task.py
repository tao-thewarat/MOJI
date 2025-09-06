from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    git_task_ids = fields.One2many(
        comodel_name="project.task.git",
        inverse_name="project_task_id",
        string="Git State",
    )
