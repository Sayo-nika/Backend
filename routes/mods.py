# External Libraries
from quart import abort, jsonify, request
from sqlalchemy import and_, func

# Sayonika Internals
from framework.models import (AuthorRoles, Mod, ModAuthors, ModCategory,
                              ModStatus, Review, User)
from framework.objects import db, jwt_service
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
        # Get page and limit from qs, or set defaults.
        page = request.args.get("page", "")
        limit = request.args.get("limit", "")
        page = int(page) if page.isdigit() else 0
        limit = int(limit) if limit.isdigit() else 50

        if not 1 <= limit <= 100:
            limit = max(1, min(limit, 100))  # Clamp `limit` to 1 or 100, whichever is appropriate

        filters = []
        sort = None
        query = Mod.paginate(page, limit)

        if request.args.get("category"):
            category = request.args["category"].lower()
            valid_categories = [x.name.lower() for x in ModCategory]

            if category not in valid_categories:
                abort(400, f"Invalid category. Must be one of: '{', '.join(valid_categories)}'")
            else:
                category = [x for x in ModCategory][valid_categories.index(category)]
                filters.append(Mod.status == category)

        if request.args.get("rating"):
            rating = request.args["rating"]
            valid_ratings = [str(x) for x in range(1, 6)]

            if rating not in valid_ratings:
                abort(400, "Invalid rating. Must be between 1 and 5 inclusive")
            else:
                int_rating = int(rating)

                filters.append(int_rating + 1 > db.select([
                    func.avg(Review.select('rating').where(Review.mod_id == Mod.id))
                ]) >= int_rating)

        if request.args.get("status"):
            status = request.args["status"].lower()
            valid_statuses = [x.name.lower() for x in ModStatus]

            if category not in valid_statuses:
                abort(400, f"Invalid status. Must be one of: '{', '.join(valid_statuses)}'")
            else:
                status = [x for x in ModStatus][valid_statuses.index(status)]
                filters.append(Mod.status == status)

        results = await query.where(and_(
            Mod.verified,
            *filters
        )).gino.all()
        total = await db.func.count(Mod.id).gino.scalar()

        return jsonify(total=total, page=page, limit=limit, results=self.dict_all(results))

    @multiroute("/api/v1/mods", methods=["POST"], other_methods=["GET"])
    @requires_login
    @json
    async def post_mods(self):
        body = await request.json
        token = request.headers.get("Authorization", request.cookies.get("token"))
        parsed_token = await jwt_service.verify_login_token(token, True)
        user_id = parsed_token["id"]

        for attr, type_ in mod_attrs.items():
            val = body.get(attr)

            if val is None:
                abort(400, f"Missing value '{attr}'")
            elif not isinstance(val, type_):
                abort(400, f"Bad type for '{attr}', should be '{type_.__name__}'")

        mods = await Mod.get_any(True, title=body["title"]).first()

        if mods is not None:
            abort(400, "A mod with that title already exists")

        lowered_roles = [x.name.lower() for x in AuthorRoles]

        for author in body["authors"]:
            if not isinstance(author, dict) or list(author.keys()) != ['id', 'role']:
                abort(400, "`authors` should be a list of {'id', 'role'}")
            elif not await User.exists(author["id"]):
                abort(400, f"Author '{author['id']}' doesn't exist")
            elif author["role"].lower() not in lowered_roles:
                abort(400, f"Unknown role '{author['role']}'")

        authors = body["authors"]
        authors = [{**author, "role": [x for x in AuthorRoles][lowered_roles.index(author["role"].lower())]} for author
                   in authors]

        authors.append({"id": user_id, "role": AuthorRoles.Owner})

        mod = Mod(title=body["title"], tagline=body["tagline"], description=body["description"],
                  website=body["website"])

        mod.icon = body.get("icon")
        status = body.get("status")

        if status not in ModStatus.__members__ and status:
            abort(400, f"Unknown mod status '{status}'")

        mod.status = ModStatus[status]

        authors = [x for x in body["authors"] if await User.exists(x["id"])]

        await mod.create()
        await ModAuthors.insert().gino.all(*[dict(user_id=author["id"], mod_id=mod.id, role=author["role"]) for author in authors])

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
            authors = [uid for uid in authors if not await ModAuthors.query.where(
                           and_(ModAuthors.user_id == uid, ModAuthors.mod_id == mod_id)
                       ).gino.first()]

        status = body.get("status")

        if status is not None and status not in ModStatus.__members__:
            abort(400, f"Unknown mod status '{status}'")
        elif status is not None:
            updates = updates.update(status=ModStatus[status])

        await updates.apply()
        await ModAuthors.insert().gino.all(dict(user_id=uid, mod_id=mod.id) for uid in authors)

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
            elif isinstance(val, type_):
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

        author_pairs = await ModAuthors.query.where(ModAuthors.mod_id == mod_id).gino.all()
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
