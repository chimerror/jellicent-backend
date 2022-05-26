from app.models.card_type import PLAYER_CARDS
from app.models.game_status import GameStatus
import re

PLAYER_CARD_VALUES = [pc.value for pc in PLAYER_CARDS]
CREATE_RESPONSE_REGEX = re.compile(
    r"^Game with ID (?P<game_id>[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}) successfully created$")

def test_create_game_happy_path_three_players(client, five_players):
    EXPECTED_PLAYER_IDS = [2, 3, 4]
    post_response = client.post("/games", json = {
        "player-ids": EXPECTED_PLAYER_IDS,
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
    assert get_response_body["last-round"] == False
    assert get_response_body["piles"] == [[], [], []]

    validate_response_body_players(get_response_body, EXPECTED_PLAYER_IDS)

def test_create_game_happy_path_four_players(client, five_players):
    EXPECTED_PLAYER_IDS = [2, 3, 1, 4]
    post_response = client.post("/games", json = {
        "player-ids": EXPECTED_PLAYER_IDS,
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
    assert get_response_body["last-round"] == False
    assert get_response_body["piles"] == [[], [], [], []]

    validate_response_body_players(get_response_body, EXPECTED_PLAYER_IDS)

def test_create_game_happy_path_five_players(client, five_players):
    EXPECTED_PLAYER_IDS = [2, 3, 1, 4, 5]
    post_response = client.post("/games", json = {
        "player-ids": EXPECTED_PLAYER_IDS,
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
    assert get_response_body["last-round"] == False
    assert get_response_body["piles"] == [[], [], [], [], []]

    validate_response_body_players(get_response_body, EXPECTED_PLAYER_IDS)

def validate_response_body_players(response_body, expected_player_ids):
    actual_players = response_body["players"]
    assert len(actual_players) == len(expected_player_ids)
    actual_player_ids = []
    seen_starting_cards = []
    for player in actual_players:
        actual_player_ids.append(player["id"])
        assert player["took-this-round"] == False
        starting_card = player["starting-card"]
        assert starting_card in PLAYER_CARD_VALUES
        assert not starting_card in seen_starting_cards
        seen_starting_cards.append(starting_card)
        assert player["hand"] == {
            starting_card: 1
        }
    assert sorted(actual_player_ids) == sorted(expected_player_ids)