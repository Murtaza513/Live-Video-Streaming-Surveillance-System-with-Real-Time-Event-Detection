# /services

This directory is reserved for standalone microservices or shared utility
containers that are not part of the main backend or frontend.

Examples of what might live here in future iterations:
- `notification-service/`  — push/email alert dispatcher
- `archival-service/`      — event snapshot archival and rotation
- `analytics-service/`     — aggregate stats and ML model retraining pipeline

For v1 the detection and event logic lives inside `/backend/app/services/`.
