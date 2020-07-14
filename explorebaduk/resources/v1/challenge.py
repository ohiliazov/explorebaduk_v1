import uuid

from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request

from explorebaduk.helpers import validate_json
from explorebaduk.validation import challenge_create_schema


class ChallengeView(HTTPMethodView):
    """View to get challenge"""

    @validate_json(challenge_create_schema, clean=True)
    async def post(self, request: Request, valid_json: dict):
        """
        Create challenge
        :param request:
        :param valid_json:
        :return:
        """
        challenge_id = str(uuid.uuid4())
        request.app.challenges[challenge_id] = valid_json

        return response.json({"challenge_id": challenge_id, "challenge_data": valid_json})
