"""Event type string constants for the in-process event bus."""

MOZO_DEPARTURE = "mozo.departure"
MOZO_RETURN = "mozo.return"
TRANSCRIPT_SEGMENT_READY = "transcript.segment_ready"
CALENDAR_SYNC_COMPLETE = "calendar.sync_complete"
CALENDAR_CONFLICT = "calendar.conflict"
SCHEDULE_CONFIRMATION_NEEDED = "schedule.confirmation_needed"
SCHEDULE_CONFIRMED = "schedule.confirmed"
SCHEDULE_DENIED = "schedule.denied"

ALL_EVENT_TYPES = (
    MOZO_DEPARTURE,
    MOZO_RETURN,
    TRANSCRIPT_SEGMENT_READY,
    CALENDAR_SYNC_COMPLETE,
    CALENDAR_CONFLICT,
    SCHEDULE_CONFIRMATION_NEEDED,
    SCHEDULE_CONFIRMED,
    SCHEDULE_DENIED,
)
