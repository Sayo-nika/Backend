# Stdlib
from base64 import b64encode as b64

# External Libraries
import bcrypt
import mmh3
from bs4 import BeautifulSoup
from cachetools import TTLCache
from quart import abort, jsonify
from sqlalchemy import or_, and_, func
from webargs import fields

# Sayonika Internals
from framework.models import Mod, User, ModStatus, EditorsChoice
from framework.objects import SETTINGS, jwt_service
from framework.quart_webargs import use_kwargs
from framework.route import route
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika
from framework.utils import verify_recaptcha


def hash(string: str):
    return b64(str(mmh3.hash(string)).encode("utf8")).decode("utf8")


async def get_latest_medium_post(session):
    """
    Properly gets and parses the latest post from Medium.
    Returns it as a nice simple object with no bs.
    """
    publication = SETTINGS["MEDIUM_PUBLICATION"]

    async with session.get(f"https://medium.com/feed/{publication}") as resp:
        feed = await resp.text()

    soup = BeautifulSoup(feed, "xml")
    post = soup.item
    content = BeautifulSoup(post("content:encoded")[0].string, "html.parser")

    return {
        "title": post.title.string,
        "body": content.p.string,  # First paragraph is the subtitle thing
        "url": post.guid.string,
        "banner": content.img["src"].replace(
            "max/1024", "max/2048"
        ),  # First image is the banner
        "id": hash(post.guid.string),
    }


class Userland(RouteCog):
    news_cache = TTLCache(1, 60 * 60)

    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    @route("/api/v1/login", methods=["POST"])
    @json
    @use_kwargs(
        {
            "username": fields.Str(required=True),
            "password": fields.Str(required=True),
            "recaptcha": fields.Str(required=True),
        },
        locations=("json",),
    )
    async def login(self, username: str, password: str, recaptcha: str):
        score = await verify_recaptcha(recaptcha, self.core.aioh_sess, "login")

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
    @use_kwargs({"token": fields.Str(required=True)}, locations=("query",))
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
    @use_kwargs({"q": fields.Str(required=True)}, locations=("query",))
    async def search(self, q: str):
        like = f"%{q}%"

        mods = (
            await Mod.query.where(
                or_(
                    Mod.title.match(q),
                    Mod.tagline.match(q),
                    Mod.description.match(q),
                    Mod.title.ilike(like),
                    Mod.tagline.ilike(like),
                    Mod.description.ilike(like),
                )
            )
            .limit(5)
            .gino.all()
        )
        users = (
            await User.query.where(
                or_(User.username.match(q), User.username.ilike(like))
            )
            .limit(5)
            .gino.all()
        )

        return jsonify(mods=self.dict_all(mods), users=self.dict_all(users))

    @route("/api/v1/news", methods=["GET"])
    @json
    async def news(self):
        if self.news_cache.get("news"):
            return jsonify(self.news_cache["news"])

        recent = (
            await Mod.query.where(and_(Mod.verified, Mod.status == ModStatus.released))
            .order_by(func.random())
            .limit(10)
            .gino.first()
        )
        featured = (
            await EditorsChoice.load(mod=Mod)
            .where(EditorsChoice.featured)
            .order_by(EditorsChoice.created_at.desc())
            .gino.first()
        )
        blog = await get_latest_medium_post(self.core.aioh_sess)

        recent = (
            {
                "type": 0,
                "title": recent.title,
                "body": recent.tagline,
                "url": f"/mods/{recent.id}",
                "banner": recent.banner,
                "id": hash(recent.id),
            }
            if recent is not None
            else None
        )
        featured = (
            {
                "type": 1,
                "title": featured.mod.title,
                "body": featured.editors_notes,
                "url": featured.article_url,
                "banner": featured.mod.banner,
                "id": hash(featured.mod.id),
            }
            if featured is not None
            else None
        )
        blog = {"type": 2, **blog}

        news = [recent, featured, blog]

        # Featured and recent may be None if there are no EditorsChoices or Mods respectively.
        self.news_cache["news"] = news = [x for x in news if x is not None]

        return jsonify(news)


def setup(core: Sayonika):
    Userland(core).register()
