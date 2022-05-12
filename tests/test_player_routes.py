def test_get_all_players_happy_path(client, five_players):
    response = client.get("/players")
    response_body = response.get_json()
    expected_response = []
    current_expected_id = 1
    for player in five_players:
        expected_response.append({
            "id": current_expected_id,
            "user_name": player.user_name,
            "display_name": player.display_name,
        })
        current_expected_id = current_expected_id + 1

    assert response.status_code == 200
    assert response_body == expected_response

def test_get_all_players_no_records(client):
    response = client.get("/players")
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body == []

def test_get_player_by_id_happy_path(client, five_players):
    response = client.get("/players/2")
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body == {
        "id": 2,
        "user_name": five_players[1].user_name,
        "display_name": five_players[1].display_name
    }