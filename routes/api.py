# External Libraries
import aiohttp
import bcrypt
from quart import abort, jsonify
from sqlalchemy import or_
from webargs import fields

# Sayonika Internals
from framework.models import Mod, User
from framework.objects import jwt_service, SETTINGS
from framework.quart_webargs import use_kwargs
from framework.route import route
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Userland(RouteCog):
    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    @route("/api/v1/login", methods=["POST"])
    @json
    @use_kwargs({
        "username": fields.Str(required=True),
        "password": fields.Str(required=True),
        # "recaptcha": fields.Str(required=True)
    }, locations=("json",))
    async def login(self, username: str, password: str, recaptcha: str=None):
        """async with aiohttp.ClientSession(raise_for_status=True) as sess:
            params = {
                # TODO: switch to invisible v3 captcha when vue-recaptcha-v3 gets fixed.
                "secret": SETTINGS["RECAPTCHA_CHECKBOX_SECRET_KEY"],
                "response": recaptcha
            }

            async with sess.post("https://www.google.com/recaptcha/api/siteverify", params=params) as resp:
                data = await resp.json()

                if data["success"] is False:
                    abort(400, "Invalid captcha")

                if data["action"] != "login":
                    abort(400, "Invalid captcha action")

                # if data["score"] < 0.5:
                #     # TODO: send verification email when score is too low
                #     abort(400, "Possibly a bot")"""

        user = await User.get_any(True, username=username, email=username).first()

        if not user:
            abort(400, "Invalid username or email")

        if not bcrypt.checkpw(password.encode(), user.password):
            abort(400, "Invalid password")

        if not user.email_verified:
            abort(401, "Email needs to be verified")

        token = jwt_service.make_login_token(user.id, user.last_pass_reset)

        return jsonify(token=token)

    @route("/api/v1/verify", methods=["GET"])
    @json
    @use_kwargs({
        "token": fields.Str(required=True)
    }, locations=("query",))
    async def verify_email(self, token):
        parsed_token = await jwt_service.verify_email_token(token, True)

        if parsed_token is False:
            abort(400, "Invalid token")

        user = await User.get(parsed_token["id"])

        if user.email_verified:
            return jsonify("Email already verified")

        await user.update(email_verified=True).apply()

        return jsonify("Email verified")

    @route("/api/v1/search", methods=["GET"])
    @json
    @use_kwargs({
        "q": fields.Str(required=True)
    }, locations=("query",))
    async def search(self, q: str):
        like = f"%{q}%"

        mods = await Mod.query.where(or_(
            Mod.title.match(q),
            Mod.tagline.match(q),
            Mod.description.match(q),

            Mod.title.ilike(like),
            Mod.tagline.ilike(like),
            Mod.description.ilike(like)
        )).limit(5).gino.all()
        users = await User.query.where(or_(
            User.username.match(q),
            User.username.ilike(like)
        )).limit(5).gino.all()

        return jsonify(mods=self.dict_all(mods), users=self.dict_all(users))


def setup(core: Sayonika):
    Userland(core).register()
