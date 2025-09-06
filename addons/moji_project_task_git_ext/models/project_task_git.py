from odoo import fields, models


class ProjectTaskGit(models.Model):
    _name = "project.task.git"
    _description = "Project Task Git"

    name = fields.Char(
        string="Name",
        required=True,
    )
    state = fields.Selection(
        selection=[
            ("open", "Open"),
            ("merged", "Merged"),
            ("closed", "Closed"),
        ],
        default="open",
    )
    project_task_id = fields.Many2one(
        comodel_name="project.task",
        string="Project Task",
        required=True,
    )
    pull_request_id = fields.Integer(
        string="Pull Request",
        requires=True,
        index=True,
    )
