Краткое описание проекта Order Service (FastAPI) с чистой архитектурой.
Запуск: использовать docker-compose.yml (Postgres, Redis, RabbitMQ).
- docker-compose up

Swagger
http://localhost:8000/docs

Требования: посмотреть requirements.txt.

Запуск тестов из корня проекта
- sh run_tests.sh

В ручках убрал в конце слеш
- /register/ -> /register
- /orders/{order_id}/ -> /orders/{order_id}
- и тд
