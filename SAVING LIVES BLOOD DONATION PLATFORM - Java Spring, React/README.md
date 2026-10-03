# SavingLives: blood donation platform (Spring Boot, React)

Project for the Software Systems Development course (TUCN, year IV).

- `backend/`: Spring Boot REST + WebSocket API. JWT auth, donor / doctor / admin roles, donation centers, donation requests with location-based notifications, analysis results, QR codes, statistics. `diagnosis_service.py` is a small Flask service that calls the OpenAI API for a symptom check.
- `frontend/`: React app with dashboards per role, a Google Maps view of donation centers, registration and password reset.

Configuration comes from the environment: `JWT_SECRET`, `OPENAI_API_KEY`, `REACT_APP_GOOGLE_MAPS_API_KEY`, and the database settings in `backend/src/main/resources/application.properties`.
