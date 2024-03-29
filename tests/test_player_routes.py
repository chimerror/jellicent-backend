def test_get_all_players_happy_path(client, five_players):
    response = client.get("/players")
    response_body = response.get_json()
    expected_response = []
    current_expected_id = 1
    for player in five_players:
        expected_response.append({
            "id": current_expected_id,
            "user-name": player.user_name,
            "display-name": player.display_name,
        })
        current_expected_id = current_expected_id + 1

    assert response.status_code == 200
    assert response_body == expected_response

def test_get_all_players_no_records(client):
    response = client.get("/players")
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body == []

def test_create_player_happy_path(client):
    EXPECTED_USER_NAME = "latoya82"
    EXPECTED_DISPLAY_NAME = "Latoya Miller"
    post_response = client.post("/players", json = {
        "user-name": EXPECTED_USER_NAME,
        "display-name": EXPECTED_DISPLAY_NAME })
    post_response_body = post_response.text

    assert post_response.status_code == 201
    assert post_response_body == \
        f"Player {EXPECTED_USER_NAME} with ID 1 successfully created"

    get_response = client.get("/players/1")
    get_response_body = get_response.get_json()

    assert get_response.status_code == 200
    assert get_response_body == {
        "id": 1,
        "user-name": EXPECTED_USER_NAME,
        "display-name": EXPECTED_DISPLAY_NAME
    }

def test_create_player_missing_user_name(client):
    response = client.post("/players", json = {
        "display-name": "Missing User Name" })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Missing required field 'user-name'"
    }

def test_create_player_empty_user_name(client):
    response = client.post("/players", json = {
        "user-name": "",
        "display-name": "Empty User Name" })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Field 'user-name' must have one or more alphanumeric characters only"
    }

def test_create_player_user_name_with_non_alphanumeric(client):
    response = client.post("/players", json = {
        "user-name": "latoya 1982!",
        "display-name": "Non-Alphanumeric User Name" })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Field 'user-name' must have one or more alphanumeric characters only"
    }

def test_create_player_already_existing_user_name(client, five_players):
    response = client.post("/players", json = {
        "user-name": "f0c5",
        "display-name": "0xF0C5 duplicate" })
    response_body = response.get_json()

    assert response.status_code == 409
    assert response_body == {
        "message": "A player with user name 'f0c5' already exists"
    }

def test_create_player_already_existing_display_name(client, five_players):
    EXPECTED_USER_NAME = "adag2"
    EXPECTED_DISPLAY_NAME = "Ada Gates"
    post_response = client.post("/players", json = {
        "user-name": EXPECTED_USER_NAME,
        "display-name": EXPECTED_DISPLAY_NAME })
    post_response_body = post_response.text
    
    assert post_response.status_code == 201
    assert post_response_body == \
        f"Player {EXPECTED_USER_NAME} with ID 6 successfully created"

    get_response = client.get("/players/6")
    get_response_body = get_response.get_json()

    assert get_response.status_code == 200
    assert get_response_body == {
        "id": 6,
        "user-name": EXPECTED_USER_NAME,
        "display-name": EXPECTED_DISPLAY_NAME
    }

def test_create_player_missing_display_name(client):
    response = client.post("/players", json = {
        "user-name": "MissingDisplayName" })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Missing required field 'display-name'"
    }

def test_create_player_empty_display_name(client):
    response = client.post("/players", json = {
        "user-name": "EmptyDisplayName",
        "display-name": "" })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Field 'display-name' must have one or more non-whitespace characters"
    }

def test_create_player_whitespace_only_display_name(client):
    response = client.post("/players", json = {
        "user-name": "WhitespaceOnlyDisplayName",
        "display-name": "     " })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Field 'display-name' must have one or more non-whitespace characters"
    }

def test_get_player_by_id_happy_path(client, five_players):
    response = client.get("/players/2")
    response_body = response.get_json()

    assert response.status_code == 200
    assert response_body == {
        "id": 2,
        "user-name": five_players[1].user_name,
        "display-name": five_players[1].display_name
    }

def test_get_player_by_id_invalid_id(client):
    response = client.get("/players/foo")
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "'foo' is not a valid player ID"
    }

def test_get_player_by_id_nonexistent_id(client, five_players):
    response = client.get("/players/7")
    response_body = response.get_json()

    assert response.status_code == 404
    assert response_body == {
        "message": f"No player with ID 7 was found"
    }

def test_delete_player_happy_path(client, five_players):
    delete_response = client.delete("/players/3")
    delete_response_body = delete_response.text

    assert delete_response.status_code == 200
    assert delete_response_body == \
        f"Player {five_players[2].user_name} successfully deleted"

    get_response = client.get("/players/3")
    get_response_body = get_response.get_json()

    assert get_response.status_code == 404
    assert get_response_body == {
        "message": f"No player with ID 3 was found"
    }

def test_delete_player_invalid_id(client):
    response = client.delete("/players/foo")
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "'foo' is not a valid player ID"
    }

def test_delete_player_nonexistent_id(client, five_players):
    response = client.delete("/players/7")
    response_body = response.get_json()

    assert response.status_code == 404
    assert response_body == {
        "message": f"No player with ID 7 was found"
    }

def test_update_player_happy_path(client, five_players):
    EXPECTED_USER_NAME = "chimerror"
    EXPECTED_DISPLAY_NAME = "Chimerelda E. Error"
    put_response = client.put("/players/2", json = {
        "user-name": EXPECTED_USER_NAME,
        "display-name": EXPECTED_DISPLAY_NAME })
    put_response_body = put_response.text

    assert put_response.status_code == 200
    assert put_response_body == \
        f"Player {five_players[1].user_name} successfully updated"

    get_response = client.get("/players/2")
    get_response_body = get_response.get_json()

    assert get_response.status_code == 200
    assert get_response_body == {
        "id": 2,
        "user-name": EXPECTED_USER_NAME,
        "display-name": EXPECTED_DISPLAY_NAME
    }

def test_update_player_invalid_id(client):
    response = client.put("/players/foo", json = {
        "user-name": "InvalidId",
        "display-name": "Invalid ID on Update" })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "'foo' is not a valid player ID"
    }

def test_update_player_nonexistent_id(client, five_players):
    response = client.put("/players/7", json = {
        "user-name": "NonexistentId",
        "display-name": "Nonexistent ID on Update" })
    response_body = response.get_json()

    assert response.status_code == 404
    assert response_body == {
        "message": f"No player with ID 7 was found"
    }