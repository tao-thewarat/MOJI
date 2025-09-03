from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    code = fields.Char(
        string="Project Code",
    )
    task_sequence = fields.Integer(
        string="Task Sequence Counter",
        default=0,
    )
