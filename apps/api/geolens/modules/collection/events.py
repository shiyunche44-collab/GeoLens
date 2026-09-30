"""Events published by this module. Subscribers import the names via public.py."""

RESPONSE_COLLECTED = "collection.response_collected"  # payload: response_id, project_id
RUN_COMPLETED = "collection.run_completed"  # payload: run_id, project_id
