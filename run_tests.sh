#!/bin/bash

# Поднимаем тестовые сервисы
docker-compose -f docker-compose.test.yml up -d

# Ждем готовности PostgreSQL
echo "Waiting for PostgreSQL to be ready..."
until docker exec fastapi_test_db pg_isready -U test_user -d test_db; do
  sleep 2
done

# Устанавливаем переменные окружения
export TEST_DATABASE_URL="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
export PYTHONPATH="$PWD"

# Запускаем тесты
pytest app/tests/ -v \
  --tb=short \
  --log-level=INFO

# Сохраняем код завершения
TEST_EXIT_CODE=$?

# Останавливаем контейнеры
docker-compose -f docker-compose.test.yml down

# Возвращаем код завершения тестов
exit $TEST_EXIT_CODE
