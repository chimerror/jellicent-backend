def test_get_all_players_with_no_records(client):
    response = client.get("/players")
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body == []