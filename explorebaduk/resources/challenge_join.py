from sanic.views import HTTPMethodView


class ChallengeView(HTTPMethodView):
    def post(self, request, challenge_id: str):
        pass
