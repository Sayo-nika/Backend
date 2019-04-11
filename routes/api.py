# External Libraries
import bcrypt
from cachetools import TTLCache
import json as json_
from quart import abort, jsonify
from sqlalchemy import or_, func, and_
from webargs import fields

# Sayonika Internals
from framework.models import Mod, User, EditorsChoice, ModStatus
from framework.objects import jwt_service, SETTINGS
from framework.quart_webargs import use_kwargs
from framework.route import route
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika
from framework.utils import verify_recaptcha


async def get_latest_medium_post(session):
    """
    Properly gets and parses the latest post from Medium.
    Returns it as a nice simple object with no bs.
    """
    publication = SETTINGS["MEDIUM_PUBLICATION"]

    async with session.get(f"https://medium.com/{publication}/latest?format=json") as resp:
        # Have to get the response body as text instead of json, because Medium prepends "])}while(1);</x>" to the
        # start of responses from this "endpoint" because it's unofficial I guess, and there's no "official" endpoint
        # we can use. Thanks, Medium.
        data = await resp.text()

    # Replace the first instance of the shitty string (may be present in the article), and then parse.
    data = data.replace("])}while(1);</x>", "", 1)
    data = json_.loads(data)

    post = data["payload"]["posts"][0]

    # Make nice object :) (one that can be simply expanded with `**` for news).
    return {
        "title": post["title"],
        "body": post["previewContent"]["subtitle"],
        "url": f"https://medium.com/{publication}/{post['uniqueSlug']}"
    }


class Userland(RouteCog):
    news_cache = TTLCache(1, 60 * 60)

    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    @route("/api/v1/login", methods=["POST"])
    @json
    @use_kwargs({
        "username": fields.Str(required=True),
        "password": fields.Str(required=True),
        "recaptcha": fields.Str(required=True)
    }, locations=("json",))
    async def login(self, username: str, password: str, recaptcha: str):
        score = await verify_recaptcha(recaptcha, self.core.aioh_sess, 3, "login")

        if score < 0.5:
            # TODO: send email/other 2FA when below 0.5
            abort(400, "Possibly a bot")

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

    @route("/api/v1/news", methods=["GET"])
    @json
    async def news(self):
        if self.news_cache.get("news"):
            return jsonify(self.news_cache["news"])

        recent = await Mod.query.where(and_(
            Mod.verified,
            Mod.status == ModStatus.released
        )).order_by(func.random()).limit(10).gino.first()
        featured = await EditorsChoice.load(mod=Mod).where(EditorsChoice.featured).order_by(
            EditorsChoice.created_at.desc()
        ).gino.first()
        blog = await get_latest_medium_post(self.core.aioh_sess)

        recent = {
            "type": 0,
            "title": recent.title,
            "body": recent.tagline,
            "url": f"/mods/{recent.id}"
        }
        featured = {
            "type": 1,
            "title": featured.mod.title,
            "body": featured.editors_notes,
            "url": featured.article_url
        }
        blog = {
            "type": 2,
            **blog
        }

        self.news_cache["news"] = news = [
            recent,
            featured,
            blog
        ]

        return jsonify(news)


def setup(core: Sayonika):
    Userland(core).register()
