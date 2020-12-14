from decimal import Decimal, InvalidOperation

from sanic import response
from sanic.views import HTTPMethodView

from explorebaduk.utils.egd import egd_rating


class RatingView(HTTPMethodView):
    async def get(self, request):
        try:
            r1 = Decimal(request.args.get("r1"))
            r2 = Decimal(request.args.get("r2"))
        except InvalidOperation:
            return response.json({"message": "'r1' and 'r2' should be numbers"}, 400)

        if r1 < 100 or r1 > 3000 or r2 < 100 or r2 > 3000:
            return response.json({"message": "'r1' and 'r2' should be from 100 to 3000"}, 400)

        return response.json(
            {
                "win_r1": {
                    "r1": egd_rating(r1, r2, 1),
                    "r2": egd_rating(r2, r1, 0),
                },
                "win_r2": {
                    "r1": egd_rating(r1, r2, 0),
                    "r2": egd_rating(r2, r1, 1),
                },
            },
        )
