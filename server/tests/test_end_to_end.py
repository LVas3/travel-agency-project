from uuid import uuid4


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
        "name": "Тур по Парижу",
        "type": "tourist",
        "description": "Экскурсионный тур",
        "price": 750.00,
        "start_date": "2026-08-01",
        "end_date": "2026-08-07",
    })

    assert tour_response.status_code == 200

    tour_id = tour_response.json()["id"]

    booking_response = api_client.post("/bookings", json={
        "client_id": client_id,
        "tour_id": tour_id,
        "status": "created",
    })

    assert booking_response.status_code == 200

    review_response = api_client.post("/reviews", json={
        "client_id": client_id,
        "tour_id": tour_id,
        "rating": 5,
        "text": "Отличный тур",
    })

    assert review_response.status_code == 200
    
def test_end_to_end_create_tour_with_sql(api_client):
    tour_response = api_client.post("/tours?mode=sql", json={
        "name": "Бизнес-поездка в Берлин",
        "type": "business",
        "description": "Трансфер, отель, конференция",
        "price": 980.00,
        "start_date": "2026-10-02",
        "end_date": "2026-10-05"
    })

    assert tour_response.status_code == 200

    tour_id = tour_response.json()["id"]

    search_response = api_client.get("/tours?mode=sql&name=Берлин")

    assert search_response.status_code == 200

    tours = search_response.json()

    assert len(tours) >= 1
    assert any(tour["id"] == tour_id for tour in tours)