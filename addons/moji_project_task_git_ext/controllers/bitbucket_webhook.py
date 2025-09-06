import json
import re

from odoo import http
from odoo.http import request
from odoo.models import BaseModel


class BitbucketWebhookController(http.Controller):
    @http.route(
        "/bitbucket/webhook", type="json", auth="public", methods=["POST"], csrf=False
    )
    def bitbucket_webhook(self, **kw):
        try:
            payload = request.httprequest.get_json(force=True, silent=True)
        except Exception:
            raw = request.httprequest.get_data(as_text=True)
            print("Bitbucket webhook raw body: %s", raw)
            payload = {}
        pull_request = payload.get("pullrequest", {})
        pr_state = pull_request.get("state", "")
        branch_name = pull_request.get("source", {}).get("branch", {}).get("name", "")
        tasks = self._prepare_task_no(pull_request)
        for task_no in tasks:
            state = self._map_state(pr_state)
            if state == "open":
                self._create_pull_request_state(
                    state=state,
                    branch_name=branch_name,
                    task_no=task_no,
                    pull_request_id=pull_request.get("id", 0),
                )
            else:
                self._write_pull_request_state(
                    state=state,
                    pull_request_id=pull_request.get("id", 0),
                )
        return http.Response(
            json.dumps({"status": "ok"}), content_type="application/json"
        )

    def _map_state(self, state: str) -> str:
        mapping = {
            "OPEN": "open",
            "MERGED": "merged",
            "DECLINED": "closed",
        }
        return mapping.get(state, "open")

    def _prepare_task_no(self, pull_request: dict) -> list[str]:
        title = pull_request.get("title", "")
        match = re.search(r"\[([^\]]+)\]", title)
        task_no_list = []
        if match:
            inside = match.group(1)
            task_no_list = [part.strip() for part in inside.split(",") if part.strip()]
        return task_no_list

    def _get_task(self, task_no: str) -> BaseModel:
        return (
            request.env["project.task"]
            .sudo()
            .search([("sequence", "=", task_no)], limit=1)
        )

    def _write_pull_request_state(
        self,
        state: str,
        pull_request_id: int,
    ) -> BaseModel:
        return (
            request.env["project.task.git"]
            .sudo()
            .search([("pull_request_id", "=", pull_request_id)])
            .write({"state": state})
        )

    def _create_pull_request_state(
        self,
        state: str,
        branch_name: str,
        task_no: str,
        pull_request_id: int,
    ) -> BaseModel:
        return (
            request.env["project.task.git"]
            .sudo()
            .create(
                {
                    "name": branch_name,
                    "state": state,
                    "pull_request_id": pull_request_id,
                    "project_task_id": self._get_task(task_no).id,
                }
            )
        )
