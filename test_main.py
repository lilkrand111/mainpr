import pytest
from fastapi.testclient import TestClient
import main
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Автоматически очищает словарь и сбрасывает счетчик перед каждым тестом."""
    main.notesDB.clear()
    main.next_id = 1


# --- Тесты POST /notes ---


def test_create_note_success():
    """Успешное создание заметки."""
    payload = {"title": "Покупки", "content": "Купить молоко"}
    response = client.post("/notes", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert "created_at" in data
    assert "updated_at" in data


def test_create_note_validation_empty_title():
    """Ошибка валидации при пустом заголовке (min_length=1)."""
    response = client.post("/notes", json={"title": "", "content": "Текст"})
    assert response.status_code == 422


def test_create_note_validation_missing_field():
    """Ошибка валидации при отсутствии поля content."""
    response = client.post("/notes", json={"title": "Заголовок"})
    assert response.status_code == 422


# --- Тесты GET /notes ---


def test_get_notes_empty():
    """Получение списка заметок, когда база пуста."""
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_get_notes_list():
    """Получение списка из нескольких заметок."""
    client.post("/notes", json={"title": "Заметка 1", "content": "Текст 1"})
    client.post("/notes", json={"title": "Заметка 2", "content": "Текст 2"})

    response = client.get("/notes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[1]["id"] == 2


# --- Тесты GET /notes/{note_id} ---


def test_get_note_by_id_success():
    """Успешное получение конкретной заметки по ID."""
    client.post("/notes", json={"title": "Тест", "content": "Описание"})

    response = client.get("/notes/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Тест"


def test_get_note_by_id_not_found():
    """Запрос несуществующей заметки (404)."""
    response = client.get("/notes/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Заметка с 999 ID не найдена!"}


def test_get_note_invalid_path_param():
    """Передача ID меньше 1 (ge=1)."""
    response = client.get("/notes/0")
    assert response.status_code == 422


# --- Тесты PUT /notes/{note_id} ---


def test_edit_note_success():
    """Успешное обновление заметки."""
    client.post("/notes", json={"title": "Старый заголовок", "content": "Старый текст"})

    payload = {"title": "Новый заголовок", "content": "Новый текст"}
    response = client.put("/notes/1", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]


def test_edit_note_not_found():
    """Обновление несуществующей заметки (404)."""
    payload = {"title": "Заголовок", "content": "Текст"}
    response = client.put("/notes/999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Заметка с 999 ID не найдена!"}


# --- Тесты DELETE /notes/{note_id} ---


def test_delete_note_success():
    """Успешное удаление заметки."""
    client.post("/notes", json={"title": "Заметка", "content": "Текст"})

    # В текущей реализации метод возвращает 200 OK без явного status_code
    response = client.delete("/notes/1")
    assert response.status_code == 200

    # Проверяем, что заметка удалена
    get_response = client.get("/notes/1")
    assert get_response.status_code == 404


def test_delete_note_not_found():
    """Удаление несуществующей заметки (404)."""
    response = client.delete("/notes/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Заметка с 999 ID не найдена!"}