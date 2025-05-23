from django.test import TestCase
from heltour.tournament.models import Player
from heltour.tournament.workflows import ApproveRegistrationWorkflow
from heltour.tournament.tests.testutils import createCommonLeagueData, create_reg, get_season, set_rating, Shush


class TestLJPCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        createCommonLeagueData(round_count=7)

    def test_ljp_none_rating(self, *args):
        new_player = Player.objects.create(lichess_username="newplayer", profile={"perfs": {"bullet": {"games": 50, "rating": 1650, "rd": 45, "prog": 10}}})
        season = get_season("lone")
        # creating a reg writes to the log, disable that temporarily for nicer test output
        with Shush():
            reg = create_reg(season, "newplayer")
        arw = ApproveRegistrationWorkflow(reg, 4)
        self.assertEqual(arw.default_byes, 2)
        self.assertEqual(arw.active_round_count, 3)
        self.assertEqual(arw.default_ljp, 0)
