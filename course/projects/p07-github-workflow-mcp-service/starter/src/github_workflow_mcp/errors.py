class GitHubWorkflowError(Exception):
    code = "github_workflow_error"


class RepositoryNotFound(GitHubWorkflowError):
    code = "repository_not_found"


class RateLimited(GitHubWorkflowError):
    code = "rate_limited"

    def __init__(self, retry_at: str | None) -> None:
        super().__init__("GitHub rate limit is exhausted")
        self.retry_at = retry_at


class PermissionDenied(GitHubWorkflowError):
    code = "permission_denied"


class ApprovalRequired(GitHubWorkflowError):
    code = "approval_required"


class ProposalNotFound(GitHubWorkflowError):
    code = "proposal_not_found"


class ProposalStale(GitHubWorkflowError):
    code = "proposal_stale"


class DeliveryConflict(GitHubWorkflowError):
    code = "delivery_conflict"


class InvalidWebhookSignature(GitHubWorkflowError):
    code = "invalid_webhook_signature"
