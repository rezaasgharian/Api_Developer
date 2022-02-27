import jwt
from test_plus import APITestCase
from django.conf import settings

class AuthTestCase(APITestCase):
    def test_auth(self):
        # check password length
        self.post(
            "/auth/signup",
            data=dict(loginId="bepro", password="pwd1234", name="user name"),
        )
        self.response_400()
        json_data = self.last_response.json()
        self.assertEqual(
            json_data["message"], "password should have at least 8 characters"
        )

        # successful sign-up
        self.post(
            "/auth/signup",
            data=dict(loginId="bepro", password="password1234", name="user name"),
        )
        self.response_201()

        # respond with user data
        user_data = self.last_response.json()["data"]
        self.assertEqual(user_data["loginId"], "bepro")
        self.assertEqual(user_data["name"], "user name")
        self.assertNotIn("password", user_data)

        # sign-in with wrong password
        self.post("/auth/signin", data=dict(loginId="bepro", password="pwd"))
        self.response_404()

        # successful sign-in
        self.post("/auth/signin", data=dict(loginId="bepro", password="password1234"))
        self.response_200()

        # login response should contain a token
        json_data = self.last_response.json()
        token = json_data["token"]

        # jwt payload should contain the user's id
        jwt_payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        self.assertEqual(jwt_payload["id"], json_data["data"]["id"])

        # should provide /users/me API
        self.client.credentials(HTTP_AUTHORIZATION=token)
        self.get("/users/me")
        user_id = self.last_response.json()["data"]["id"]
        self.assertEqual(user_data["id"], user_id)


class APITestCaseWithUserData(APITestCase):
    def setUp(self):
        self.user_data = self.post(
            "/auth/signup",
            data=dict(loginId="bepro1", password="password1234", name="user1"),
        ).json()["data"]

        self.user2_data = self.post(
            "/auth/signup",
            data=dict(loginId="bepro2", password="password1234", name="user2"),
        ).json()["data"]

        self.token = self.post(
            "/auth/signin",
            data=dict(loginId="bepro1", password="password1234"),
        ).json()["token"]

        self.token2 = self.post(
            "/auth/signin",
            data=dict(loginId="bepro2", password="password1234"),
        ).json()["token"]


class TeamTestCase(APITestCaseWithUserData):
    def test_team_api(self):
        # only signed in user can create a team
        self.post("/teams", data=dict(name="FC Bepro"))
        self.response_401()

        # successful team creation
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.post("/teams", data=dict(name="FC Bepro"))
        self.response_201()
        team_data = self.last_response.json()["data"]
        self.assertEqual(team_data["userId"], self.user_data["id"])
        self.assertEqual(team_data["name"], "FC Bepro")

        # a player should be created automatically
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.get("/players", data=dict(teamId=team_data["id"]))
        players = self.last_response.json()["data"]
        self.assertEqual(len(players), 1)
        self.assertEqual(players[0]["userId"], self.user_data["id"])
        self.assertEqual(players[0]["teamId"], team_data["id"])
        self.assertEqual(players[0]["joinStatus"], "APPROVED")

        # team list api
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.get("/teams")
        self.assertEqual(len(self.last_response.json()["data"]), 1)

        # only team creator can delete their team
        self.client.credentials(HTTP_AUTHORIZATION=self.token2)
        self.delete(f"/teams/{team_data['id']}")
        self.response_403()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.delete(f"/teams/{team_data['id']}")
        self.response_204()


class PlayerTestCase(APITestCaseWithUserData):
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.team_data = self.post("/teams", data=dict(name="FC Bepro")).json()["data"]

    def test_player_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.token2)
        self.post("/players", data=dict(teamId=self.team_data["id"]))
        self.response_201()
        player_data = self.last_response.json()["data"]
        self.assertEqual(player_data["userId"], self.user2_data["id"])
        self.assertEqual(player_data["teamId"], self.team_data["id"])

        # initial join status should be "REQUESTED"
        self.assertEqual(player_data["joinStatus"], "REQUESTED")

        # only approved players should be included to player count
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.get("/teams")
        team = self.last_response.json()["data"][0]
        self.assertEqual(team["playerCount"], 1)

        # only "APPROVED" players can see players list. otherwise the API has to respond with an empty list
        self.client.credentials(HTTP_AUTHORIZATION=self.token2)
        self.get("/players", data=dict(teamId=self.team_data["id"]))
        self.assertEqual(len(self.last_response.json()["data"]), 0)

        # only team creator can approve the join request
        self.client.credentials(HTTP_AUTHORIZATION=self.token2)
        self.put(
            f"/players/{player_data['id']}",
            data=dict(joinStatus="APPROVED"),
        )
        self.response_403()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.put(
            f"/players/{player_data['id']}",
            data=dict(joinStatus="APPROVED"),
        )
        self.response_200()

        # now join status is "APPROVED" - able to see players list
        self.client.credentials(HTTP_AUTHORIZATION=self.token2)
        self.get("/players", data=dict(teamId=self.team_data["id"]))
        self.assertEqual(len(self.last_response.json()["data"]), 2)

        # leave the team
        self.delete(
            f"/players/{player_data['id']}",
            data=dict(teamId=self.team_data["id"]),
            Authorization=self.token2,
        )
        self.response_204()

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.get("/players", data=dict(teamId=self.team_data["id"]))
        self.assertEqual(len(self.last_response.json()["data"]), 1)
