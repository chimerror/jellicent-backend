from app.models.card_type import PLAYER_CARDS
from app.models.game import validate_game_id
from app.models.game_status import GameStatus
import re

PLAYER_CARD_VALUES = [pc.value for pc in PLAYER_CARDS]
CREATE_RESPONSE_REGEX = re.compile(
    r"^Game with ID (?P<game_id>[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}) successfully created$")

def test_create_game_happy_path_three_players(client, five_players):
    EXPECTED_PLAYERS = [
        (2, "Chimerelda Error"),
        (3, "Ada Gates"),
        (4, "Glitch")
    ]
    post_response = client.post("/games", json = {
        "player-ids": [player[0] for player in EXPECTED_PLAYERS],
        "use-advanced-scoring": False,
        "assign-wilds-on-take": True
    })
    post_response_body = post_response.text
    post_response_match = CREATE_RESPONSE_REGEX.match(post_response_body)

    assert post_response.status_code == 201
    assert post_response_match

    game_id =  post_response_match.group("game_id")
    get_response = client.get(f"/games/{game_id}")
    get_response_body = get_response.get_json()

    assert get_response.status_code == 200
    assert get_response_body["active-player-index"] == 0
    assert get_response_body["use-advanced-scoring"] == False
    assert get_response_body["assign-wilds-on-take"] == True
    assert get_response_body["cards-left"] == 64
    assert get_response_body["current-state"] == \
        GameStatus.WAITING_FOR_CHOICE.value
    assert get_response_body["choices-allowed"] == ["draw-card"]
    assert get_response_body["last-round"] == False
    assert get_response_body["piles"] == [[], [], []]

    removed_card = get_response_body["removed-card"]
    assert removed_card in PLAYER_CARD_VALUES

    validate_response_body_players(get_response_body, EXPECTED_PLAYERS, removed_card)

def test_create_game_happy_path_four_players(client, five_players):
    EXPECTED_PLAYERS = [
        (2, "Chimerelda Error"),
        (3, "Ada Gates"),
        (1, "Jayce Mitchell"),
        (4, "Glitch")
    ]
    post_response = client.post("/games", json = {
        "player-ids": [player[0] for player in EXPECTED_PLAYERS],
        "use-advanced-scoring": True,
        "assign-wilds-on-take": False
    })
    post_response_body = post_response.text
    post_response_match = CREATE_RESPONSE_REGEX.match(post_response_body)

    assert post_response.status_code == 201
    assert post_response_match

    game_id =  post_response_match.group("game_id")
    get_response = client.get(f"/games/{game_id}")
    get_response_body = get_response.get_json()

    assert get_response.status_code == 200
    assert get_response_body["active-player-index"] == 0
    assert get_response_body["use-advanced-scoring"] == True
    assert get_response_body["assign-wilds-on-take"] == False
    assert get_response_body["cards-left"] == 72
    assert get_response_body["current-state"] == \
        GameStatus.WAITING_FOR_CHOICE.value
    assert get_response_body["choices-allowed"] == ["draw-card"]
    assert get_response_body["last-round"] == False
    assert get_response_body["piles"] == [[], [], [], []]

    validate_response_body_players(get_response_body, EXPECTED_PLAYERS)

def test_create_game_happy_path_five_players(client, five_players):
    EXPECTED_PLAYERS = [
        (2, "Chimerelda Error"),
        (3, "Ada Gates"),
        (1, "Jayce Mitchell"),
        (4, "Glitch"),
        (5, "0xF0C5")
    ]
    post_response = client.post("/games", json = {
        "player-ids": [player[0] for player in EXPECTED_PLAYERS],
        "use-advanced-scoring": True,
        "assign-wilds-on-take": True
    })
    post_response_body = post_response.text
    post_response_match = CREATE_RESPONSE_REGEX.match(post_response_body)

    assert post_response.status_code == 201
    assert post_response_match

    game_id =  post_response_match.group("game_id")
    get_response = client.get(f"/games/{game_id}")
    get_response_body = get_response.get_json()

    assert get_response.status_code == 200
    assert get_response_body["active-player-index"] == 0
    assert get_response_body["use-advanced-scoring"] == True
    assert get_response_body["assign-wilds-on-take"] == True
    assert get_response_body["cards-left"] == 71
    assert get_response_body["current-state"] == \
        GameStatus.WAITING_FOR_CHOICE.value
    assert get_response_body["choices-allowed"] == ["draw-card"]
    assert get_response_body["last-round"] == False
    assert get_response_body["piles"] == [[], [], [], [], []]

    validate_response_body_players(get_response_body, EXPECTED_PLAYERS)

def test_create_game_happy_path_seeding(client, five_players):
    EXPECTED_PLAYER_IDS = [2, 3, 4]
    post1_response = client.post("/games", json = {
        "player-ids": EXPECTED_PLAYER_IDS,
        "use-advanced-scoring": False,
        "assign-wilds-on-take": False,
        "random-seed": 13
    })
    post1_response_body = post1_response.text
    post1_response_match = CREATE_RESPONSE_REGEX.match(post1_response_body)
    game1_id =  post1_response_match.group("game_id")
    assert post1_response.status_code == 201

    post2_response = client.post("/games", json = {
        "player-ids": EXPECTED_PLAYER_IDS,
        "use-advanced-scoring": False,
        "assign-wilds-on-take": False,
        "random-seed": 13
    })
    post2_response_body = post2_response.text
    post2_response_match = CREATE_RESPONSE_REGEX.match(post2_response_body)
    game2_id =  post2_response_match.group("game_id")
    assert post2_response.status_code == 201

    get1_response = client.get(f"/games/{game1_id}")
    get1_response_body = get1_response.get_json()
    assert get1_response.status_code == 200
    get2_response = client.get(f"/games/{game2_id}")
    get2_response_body = get2_response.get_json()
    assert get2_response.status_code == 200

    assert get1_response_body["use-advanced-scoring"] == \
        get2_response_body["use-advanced-scoring"]
    assert get1_response_body["assign-wilds-on-take"] == \
        get2_response_body["assign-wilds-on-take"]
    assert get1_response_body["cards-left"] == get2_response_body["cards-left"]
    assert get1_response_body["current-state"] == \
        get2_response_body["current-state"]
    assert get1_response_body["choices-allowed"] == \
        get2_response_body["choices-allowed"]
    assert get1_response_body["last-round"] == get2_response_body["last-round"]
    assert get1_response_body["piles"] == get2_response_body["piles"]
    assert get1_response_body["removed-card"] == \
        get2_response_body["removed-card"]
    assert get1_response_body["players"] == get2_response_body["players"]

    game1 = validate_game_id(game1_id)
    game2 = validate_game_id(game2_id)
    assert game1.deck == game2.deck

def test_create_game_missing_player_ids(client, five_players):
    response = client.post("/games", json = {
        "use-advanced-scoring": True,
        "assign-wilds-on-take": True
    })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Missing required field 'player-ids'"
    }

def test_create_game_non_list_player_ids(client, five_players):
    response = client.post("/games", json = {
        "player-ids": 13,
        "use-advanced-scoring": True,
        "assign-wilds-on-take": True
    })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Field 'player-ids' must be a list of valid existing player ids with 3 to 5 elements."
    }

def test_create_game_empty_player_ids(client, five_players):
    response = client.post("/games", json = {
        "player-ids": [],
        "use-advanced-scoring": True,
        "assign-wilds-on-take": True
    })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Field 'player-ids' must be a list of valid existing player ids with 3 to 5 elements."
    }

def test_create_game_too_few_player_ids(client, five_players):
    response = client.post("/games", json = {
        "player-ids": [1, 2],
        "use-advanced-scoring": True,
        "assign-wilds-on-take": True
    })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Field 'player-ids' must be a list of valid existing player ids with 3 to 5 elements."
    }

def test_create_game_too_many_player_ids(client, five_players):
    response = client.post("/games", json = {
        "player-ids": [1, 2, 3, 4, 5, 6],
        "use-advanced-scoring": True,
        "assign-wilds-on-take": True
    })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Field 'player-ids' must be a list of valid existing player ids with 3 to 5 elements."
    }

def test_create_game_invalid_player_id(client, five_players):
    response = client.post("/games", json = {
        "player-ids": [1, 2, 3, "foo"],
        "use-advanced-scoring": True,
        "assign-wilds-on-take": True
    })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "'foo' is not a valid player ID"
    }

def test_create_game_nonexistent_player_id(client, five_players):
    response = client.post("/games", json = {
        "player-ids": [1, 7, 3],
        "use-advanced-scoring": True,
        "assign-wilds-on-take": True
    })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "No player with ID 7 was found"
    }

def test_create_game_duplicated_player_id(client, five_players):
    response = client.post("/games", json = {
        "player-ids": [1, 3, 2, 3],
        "use-advanced-scoring": True,
        "assign-wilds-on-take": True
    })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {
        "message": "Player ID 3 was duplicated in field 'player-ids'"
    }

def test_create_game_missing_advanced_scoring(client, five_players):
    post_response = client.post("/games", json = {
        "player-ids": [2, 4, 1],
        "assign-wilds-on-take": True
    })
    post_response_body = post_response.text
    post_response_match = CREATE_RESPONSE_REGEX.match(post_response_body)

    assert post_response.status_code == 201
    game_id =  post_response_match.group("game_id")
    get_response = client.get(f"/games/{game_id}")
    get_response_body = get_response.get_json()

    assert get_response.status_code == 200
    assert get_response_body["use-advanced-scoring"] == False

def test_create_game_missing_assign_wilds_on_take(client, five_players):
    post_response = client.post("/games", json = {
        "player-ids": [2, 4, 1],
        "use-advanced-scoring": True
    })
    post_response_body = post_response.text
    post_response_match = CREATE_RESPONSE_REGEX.match(post_response_body)

    assert post_response.status_code == 201
    game_id =  post_response_match.group("game_id")
    get_response = client.get(f"/games/{game_id}")
    get_response_body = get_response.get_json()

    assert get_response.status_code == 200
    assert get_response_body["assign-wilds-on-take"] == False

def test_get_game_by_id_invalid_id(client, one_game):
    response = client.get(f"/games/foo")
    response_body = response.get_json()
    assert response.status_code == 400
    assert response_body == {
        "message": "'foo' is not a valid game ID"
    }

def test_get_game_by_id_nonexistent_id(client, one_game):
    response = client.get(f"/games/9566f666-b279-4c5e-9983-8f4658e1da78")
    response_body = response.get_json()
    assert response.status_code == 404
    assert response_body == {
        "message": "No game with ID 9566f666-b279-4c5e-9983-8f4658e1da78 was found"
    }

def validate_response_body_players(
    response_body, expected_players, removed_card = None):
    actual_players = response_body["players"]
    assert len(actual_players) == len(expected_players)
    seen_starting_cards = []
    for player in actual_players:
        assert player["took-this-round"] == False
        starting_card = player["starting-card"]
        assert starting_card in PLAYER_CARD_VALUES
        assert starting_card != removed_card
        assert not starting_card in seen_starting_cards
        seen_starting_cards.append(starting_card)
        assert player["hand"] == {
            starting_card: 1
        }
    sorted_actual_players = \
        sorted(actual_players, key=lambda player: player["id"])
    sorted_expected_players = \
        sorted(expected_players, key=lambda player: player[0])
    for current_player_index in range(len(sorted_expected_players)):
        expected_player = sorted_expected_players[current_player_index]
        actual_player = sorted_actual_players[current_player_index]
        assert actual_player["id"] == expected_player[0]
        assert actual_player["display-name"] == expected_player[1]