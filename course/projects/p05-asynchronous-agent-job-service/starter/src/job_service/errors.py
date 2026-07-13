class JobServiceError(Exception):
    code = "job_service_error"
    public_message = "The job service could not complete the request."


class JobNotFound(JobServiceError):
    code = "job_not_found"
    public_message = "The requested job does not exist."


class IdempotencyConflict(JobServiceError):
    code = "idempotency_conflict"
    public_message = "The idempotency key was already used for another request."


class ResultNotReady(JobServiceError):
    code = "result_not_ready"
    public_message = "The job does not have a successful result."
