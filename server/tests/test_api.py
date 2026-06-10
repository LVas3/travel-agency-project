from uuid import uuid4


def test_register_and_login(api_client):
    login = f"client_{uuid4().hex[:8]}"

    register_response = api_client.post(
        "/auth/register",
        json={"login": login, "password": "Test1234", "role": "client"},
    )
    assert register_response.status_code == 200
    assert register_response.json()["role"] == "client"

    login_response = api_client.post(
        "/auth/login",
        json={"login": login, "password": "Test1234"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["message"] == "login successful"


def test_reject_invalid_role(api_client):
    response = api_client.post(
        "/auth/register",
        json={"login": "bad_role_user", "password": "Test1234", "role": "manager"},
    )
    assert response.status_code in (400, 422)


def test_create_search_update_delete_tour_orm(api_client):
    create_response = api_client.post("/tours?mode=orm", json={
        "name": "Paris Business Tour",
        "type": "business",
        "description": "Business trip to Paris",
        "price": "1500.00",
        "start_date": "2026-07-01",
        "end_date": "2026-07-07",
    })
    assert create_response.status_code == 200
    tour_id = create_response.json()["id"]

    search_response = api_client.get("/tours", params={"name": "Paris", "mode": "orm"})
    assert search_response.status_code == 200
    assert any(tour["id"] == tour_id for tour in search_response.json())

    update_response = api_client.put(f"/tours/{tour_id}?mode=orm", json={
        "name": "Updated Paris Business Tour",
        "type": "business",
        "description": "Updated description",
        "price": "1700.00",
        "start_date": "2026-07-02",
        "end_date": "2026-07-08",
    })
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Paris Business Tour"

    delete_response = api_client.delete(f"/tours/{tour_id}?mode=orm")
    assert delete_response.status_code == 200


def test_create_search_update_delete_tour_sql(api_client):
    create_response = api_client.post("/tours?mode=sql", json={
        "name": "Sea Cruise",
        "type": "cruise",
        "description": "Cruise tour",
        "price": "2000.00",
        "start_date": "2026-08-01",
        "end_date": "2026-08-12",
    })
    assert create_response.status_code == 200
    tour_id = create_response.json()["id"]

    search_response = api_client.get("/tours", params={"type": "cruise", "mode": "sql"})
    assert search_response.status_code == 200
    assert any(tour["id"] == tour_id for tour in search_response.json())

    update_response = api_client.put(f"/tours/{tour_id}?mode=sql", json={
        "name": "Updated Sea Cruise",
        "type": "cruise",
        "description": "Updated cruise tour",
        "price": "2100.00",
        "start_date": "2026-08-02",
        "end_date": "2026-08-13",
    })
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Sea Cruise"

    delete_response = api_client.delete(f"/tours/{tour_id}?mode=sql")
    assert delete_response.status_code == 200


def test_end_to_end_client_booking_review(api_client):
    client_response = api_client.post("/auth/register-client", json={
        "login": f"ivan_{uuid4().hex[:8]}",
        "password": "Test1234",
        "full_name": "Иван Иванов",
        "phone": "+79990000000",
        "email": "ivan@example.com",
        "passport_number": "1234567890",
    })
    assert client_response.status_code == 200
    client_id = client_response.json()["client_id"]

    tour_response = api_client.post("/tours?mode=orm", json={
        "name": "Прага выходного дня",
        "type": "tourist",
        "description": "Экскурсионный тур",
        "price": "500.00",
        "start_date": "2026-09-01",
        "end_date": "2026-09-05",
    })
    assert tour_response.status_code == 200
    tour_id = tour_response.json()["id"]

    booking_response = api_client.post("/bookings", json={
        "client_id": client_id,
        "tour_id": tour_id,
        "status": "created",
    })
    assert booking_response.status_code == 200
    assert booking_response.json()["total_price"] == "500.00"

    client_bookings_response = api_client.get(f"/bookings/client/{client_id}")
    assert client_bookings_response.status_code == 200
    assert len(client_bookings_response.json()) == 1
    assert client_bookings_response.json()[0]["tour_name"] == "Прага выходного дня"

    review_response = api_client.post("/reviews", json={
        "client_id": client_id,
        "tour_id": tour_id,
        "rating": 5,
        "text": "Отличный тур",
    })
    assert review_response.status_code == 200
    assert review_response.json()["rating"] == 5
