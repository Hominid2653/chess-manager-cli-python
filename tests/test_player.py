from models.player import Player


def test_add_result_win():
    player = Player("Alice", "P001", rating=1500)
    player.add_result("win")
    assert player.points == 1.0


def test_add_result_draw():
    player = Player("Bob", "P002", rating=1400)
    player.add_result("draw")
    assert player.points == 0.5


def test_add_result_loss():
    player = Player("Carol", "P003", rating=1300)
    player.add_result("loss")
    assert player.points == 0.0
