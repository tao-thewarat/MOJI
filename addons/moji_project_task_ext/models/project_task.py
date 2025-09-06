from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    reporter_id = fields.Many2one(
        comodel_name="res.users",
        string="Reporter",
        index=True,
        default=lambda self: self.env.user,
    )
    task_category = fields.Selection(
        selection=[
            ("issue", "Issue"),
            ("process", "Process"),
            ("view", "View"),
            ("input", "Input"),
            ("migrate", "Migrate"),
            ("defect", "Defect"),
            ("report", "Report"),
        ],
        string="Categories",
        index=True,
    )
    is_defect = fields.Boolean(
        string="Is Defect",
        index=True,
    )
    parent_defect_id = fields.Many2one(
        comodel_name="project.task",
        string="Defect from",
        domain="[('project_id','=',project_id)]",
    )
    defect_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="parent_defect_id",
        string="Defects",
        domain=[("is_defect", "=", True)],
    )
    defect_count = fields.Integer(
        string="Defect Count",
        compute="_compute_defect_count",
        store=True,
    )
    child_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="parent_id",
        string="Sub-tasks",
        domain=[
            ("recurring_task", "=", False),
            ("is_defect", "=", False),
        ],
        export_string_translation=False,
    )

    @api.depends("defect_ids")
    def _compute_defect_count(self):
        for record in self:
            record.defect_count = len(record.defect_ids)

    @api.depends("child_ids")
    def _compute_subtask_count(self):
        Task = self.env["project.task"]

        if not any(self._ids):
            for rec in self:
                task_defect = len(rec.child_ids.filtered(lambda x: not x.is_defect))
                rec.subtask_count = task_defect
                rec.closed_subtask_count = 0
                Task |= rec

            return super(__class__, self - Task)._compute_subtask_count()

        query = """
            SELECT parent_id,
                COUNT(*) as total
            FROM project_task
            WHERE parent_id = ANY(%s)
            AND (is_defect IS NULL OR is_defect = FALSE)
            GROUP BY parent_id
        """
        self.env.cr.execute(query, (self.ids,))
        results = dict(self.env.cr.fetchall())

        for rec in self:
            rec.subtask_count = results.get(rec.id, 0)
            rec.closed_subtask_count = 0
            Task |= rec

        return super(__class__, self - Task)._compute_subtask_count()

    def action_open_defect_task(self):
        return self.defect_ids._get_records_action(
            name=self.env._("Defect Task"),
        )
