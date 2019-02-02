# External Libraries
from quart import jsonify, request, abort
from sqlalchemy import and_

# Sayonika Internals
from framework.models import Mod, User, ModStatus, UserMods, Review
from framework.route import multiroute, route
from framework.route_wrappers import json, requires_login, requires_supporter
from framework.routecog import RouteCog
from framework.sayonika import Sayonika

mod_attrs = {
    "title": str,
    "tagline": str,
    "description": str,
    "website": str,
    "authors": list
}

mod_patch_attrs = {
    **mod_attrs,
    "icon": str
}

review_attrs = {
    "rating": int,
    "content": str,
    "author": str
}


class Mods(RouteCog):
    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    @multiroute("/api/v1/mods", methods=["GET"], other_methods=["POST"])
    @json
    async def get_mods(self):
        page = request.args.get("page", "")
        limit = request.args.get("limit", "")
        page = int(page) if page.isdigit() else 0
        limit = int(limit) if limit.isdigit() else 50

        if not 1 <= limit <= 100:
            limit = max(1, min(limit, 100))  # Clamp `limit` to 1 or 100, whichever is appropriate

        results = await Mod.paginate(page, limit).where(Mod.verified).gino.all()
        return jsonify(self.dict_all(results))


    @multiroute("/api/v1/mods", methods=["POST"], other_methods=["GET"])
    @requires_login
    @json
    async def post_mods(self):
        body = await request.json

        for attr, type_ in mod_attrs.items():
            val = body.get(attr)

            if val is None:
                abort(400, f"Missing value '{attr}'")
            elif isinstance(val) is not type_:
                abort(400, f"Bad type for '{attr}', should be '{type_.__name__}'")

        mods = await Mod.get_any(True, title=body["title"]).first()

        if mods is not None:
            abort(400, "A mod with that title already exists")

        mod = Mod(title=body["title"], tagline=body["tagline"], description=body["description"],
                  website=body["website"])

        mod.icon = body.get("icon")
        status = body.get("status")

        if status not in ModStatus.__members__:
            abort(400, f"Unknown mod status '{status}'")

        mod.status = ModStatus[status]

        authors = [uid for uid in body["authors"] if await User.exists(uid)]

        await mod.create()
        await UserMods.insert().gino.all(dict(user_id=uid, mod_id=mod.id) for uid in authors)

        print(mod.to_dict())

        return jsonify(mod.to_dict())

    @route("/api/v1/mods/recent_releases")
    @json
    async def get_recent_releases(self):
        mods = await Mod.query.where(Mod.verified).order_by(Mod.released_at.desc()).limit(10).gino.all()
        return jsonify(self.dict_all(mods))

    @route("/api/v1/mods/popular")
    @json
    async def get_popular(self):
        mods = await Mod.query.where(and_(
            Mod.verified,
            Mod.released_at is not None
        )).order_by(Mod.downloads.desc()).limit(10).gino.all()

        return jsonify(self.dict_all(mods))

    @multiroute("/api/v1/mods/<mod_id>", methods=["GET"], other_methods=["PATCH"])
    @json
    async def get_mod(self, mod_id: str):  # pylint: disable=no-self-use
        mod = await Mod.get(mod_id)

        if mod is None:
            abort(404, "Unknown mod")

        return jsonify(mod.to_dict())

    @multiroute("/api/v1/mods/<mod_id>", methods=["PATCH"], other_methods=["GET"])
    @requires_login
    @json
    async def patch_mod(self, mod_id: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        body = await request.json
        mod = await Mod.get(mod_id)
        updates = mod.update()

        for attr, type_ in mod_patch_attrs.items():
            val = body.get(attr)

            if val is None:
                continue
            elif type(val) is not type_:
                abort(400, f"Bad type for '{attr}', should be '{type_.__name__}'")
            elif attr != "authors":
                updates = updates.update(**{attr: val})

        if body.get("authors"):
            authors = [uid for uid in body["authors"] if await User.exists(uid)]
            authors = [uid for uid in authors if not await UserMods.query.where(
                           and_(UserMods.user_id == uid, UserMods.mod_id == mod_id)
                       ).gino.first()]

        status = body.get("status")

        if status is not None and status not in ModStatus.__members__:
            abort(400, f"Unknown mod status '{status}'")
        elif status is not None:
            updates = updates.update(status=ModStatus[status])

        await updates.apply()
        await UserMods.insert().gino.all(dict(user_id=uid, mod_id=mod.id) for uid in authors)

        return jsonify(mod.to_dict())

    @route("/api/v1/mods/<mod_id>/download")
    @json
    async def get_download(self, mod_id: str):  # pylint: disable=no-self-use
        mod = await Mod.get(mod_id)

        if mod is None:
            abort(404, "Unknown mod")
        elif not mod.zip_url:
            abort(404, "Mod has no download")

        # We're using a URL on Upload class. await URL only and let client handle DLs
        return jsonify(url=mod.zip_url)

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["GET"], other_methods=["POST"])
    @json
    async def get_reviews(self, mod_id: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        reviews = await Review.query.where(Review.mod_id == mod_id).gino.all()

        return jsonify(self.dict_all(reviews))

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["POST"], other_methods=["GET"])
    @requires_login
    @json
    async def post_review(self, mod_id: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        body = await request.json

        for attr, type_ in review_attrs.items():
            val = body.get(attr)

            if val is None:
                abort(400, f"Missing value '{attr}'")
            elif isinstance(val) is not type_:
                abort(400, f"Bad type for '{attr}', should be '{type_.__name__}'")

        if not await User.exists(body["author"]):
            abort(404, "Unknown user")

        review = await Review.create(content=body["content"], rating=body["rating"],
                                     author_id=body["author"], mod_id=mod_id)

        print(review.to_dict())

        return jsonify(review.to_json())

    @route("/api/v1/mods/<mod_id>/authors")
    @json
    async def get_authors(self, mod_id: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        author_pairs = await UserMods.query.where(UserMods.mod_id == mod_id).gino.all()
        author_pairs = [x.mod_id for x in author_pairs]
        authors = await User.query.where(User.id.in_(author_pairs)).gino.all()

        return jsonify(self.dict_all(authors))

    # This handles POST requests to add zip_url.
    # Usually this would be done via a whole entry but this
    # is designed for existing content.
    @route("/api/v1/mods/<mod_id>/upload_content", methods=["POST"])
    @json
    @requires_supporter
    @requires_login
    async def upload(self, mod_id: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        abort(501, "Coming soon")


def setup(core: Sayonika):
    Mods(core).register()
