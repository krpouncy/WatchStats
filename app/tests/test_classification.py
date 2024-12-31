import pytest
from app.core.classification import LogisticRegression, convert_stats_to_int, calculate_team_statuses

@pytest.fixture
def logistic_regression():
    return LogisticRegression()

def test_predicts_probability_correctly(logistic_regression):
    stats = [
        [15, 5, 4, 10369, 0, 11675],
        [14, 0, 7, 10157, 0, 564],
        [8, 0, 10, 10536, 0, 116],
        [5, 7, 10, 3941, 7951, 0],
        [0, 14, 8, 250, 6628, 0],
        [32, 6, 1, 10950, 0, 690],
        [13, 3, 7, 4685, 1022, 0],
        [13, 5, 5, 7421, 1461, 2024],
        [10, 24, 5, 4086, 6573, 0],
        [25, 13, 4, 6567, 5803, 0]
    ]
    # time, player_composition_for_ally_team, player_statuses
    game_details = (9.283, ['tank_name', 'dps_name', 'dps_name', 'supp_name', 'supp_name'], ['good', 'good', 'average'])
    probability = logistic_regression.predict_probability(stats, game_details)
    assert probability is not None
    assert probability < 0.5

def test_handles_missing_stats(logistic_regression):
    stats = []
    game_details = (10, ['player1', 'player2', 'player3', 'player4', 'player5'], ['good', 'average', 'poor'])
    probability = logistic_regression.predict_probability(stats, game_details)
    assert probability is None

def test_handles_insufficient_stats(logistic_regression):
    stats = [[10, 5, 2, 2000, 500, 1000]]
    game_details = (10, ['player1', 'player2', 'player3', 'player4', 'player5'], ['good', 'average', 'poor'])
    probability = logistic_regression.predict_probability(stats, game_details)
    assert probability is None

def test_converts_stats_to_int_correctly():
    stats = [['10', '5', '2', '2000', '500', '1000'], ['', '4', '3', '1800', '400', '900']]
    converted_stats = convert_stats_to_int(stats)
    assert converted_stats == [[10, 5, 2, 2000, 500, 1000], [0, 4, 3, 1800, 400, 900]]

def test_calculates_team_statuses_correctly():
    stats = [
        [15, 5, 4, 10369, 0, 11675],
        [14, 0, 7, 10157, 0, 564],
        [8, 0, 10, 10536, 0, 116],
        [5, 7, 10, 3941, 7951, 0],
        [0, 14, 8, 250, 6628, 0],
        [32, 6, 1, 10950, 0, 690],
        [13, 3, 7, 4685, 1022, 0],
        [13, 5, 5, 7421, 1461, 2024],
        [10, 24, 5, 4086, 6573, 0],
        [25, 13, 4, 6567, 5803, 0]
    ]
    tank_status, dps_status, support_status = calculate_team_statuses(stats)
    assert tank_status == 'good'
    assert dps_status == 'good'
    assert support_status == 'average'