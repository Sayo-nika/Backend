# Stdlib
from datetime import datetime

# External Libraries
from quart import abort, jsonify, request
from sqlalchemy import and_

# Sayonika Internals
from framework.authentication import Authenticator
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

user_attrs = {
    "username": str,
    "password": str,
    "email": str
}

user_patch_attrs = {
    **user_attrs,
    "bio": str,
    "avatar": str
}


class Mods(RouteCog):
    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    # === Mods ===
    @multiroute("/api/v1/mods", methods=["POST"], other_methods=["GET"])
    @requires_login
    @json
    async def post_mods(self):
        body = await request.json

        for attr, type_ in mod_attrs:
            val = body.get(attr)

            if val is None:
                abort(400, f"Missing value '{attr}'")
            elif type(val) is not type_:
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

        print(mod)

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

        for attr, type_ in mod_patch_attrs:
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

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["POST"], other_methods=["GET"])
    @requires_login
    @json
    async def post_review(self, mod_id: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        body = await request.json

        for attr, type_ in review_attrs:
            val = body.get(attr)

            if val is None:
                abort(400, f"Missing value '{attr}'")
            elif type(val) is not type_:
                abort(400, f"Bad type for '{attr}', should be '{type_.__name__}'")

        if not await User.exists(body["author"]):
            abort(404, "Unknown user")

        review = await Review.create(content=body["content"], rating=body["rating"],
                                     author_id=body["author"], mod_id=mod_id)

        print(review)

        return jsonify(review.to_json())

    @multiroute("/api/v1/users", methods=["POST"], other_methods=["GET"])
    @json
    async def post_users(self):
        body = await request.json
        user = User()

        for attr, type_ in user_attrs:
            val = body.get(attr)

            if val is None:
                abort(400, f"Missing value '{attr}'")
            elif type(val) is not type_:
                abort(400, f"Bad type for '{attr}', should be '{type_.__name__}'")

            setattr(user, attr, val)

        users = await User.get_any(True, username=user["username"], email=user["email"]).first()

        if users is not None:
            return abort(400, "Username and/or email already in use")

        user.avatar = body.get("avatar")
        user.bio = body.get("bio")
        user.password = Authenticator.hash_password(user.password)
        user.last_pass_reset = datetime.now()

        await user.create()

        print(user)

        return jsonify(user.to_dict())

    @multiroute("/api/v1/users/<user_id>", methods=["PATCH"], other_methods=["GET"])
    @requires_login
    @json
    async def patch_user(self, user_id: str):
        if not await User.exists(user_id):
            abort(404, "Unknown user")

        body = await request.json
        user = await User.get(user_id)
        updates = user.update()

        for attr, type_ in user_patch_attrs:
            val = body.get(attr)

            if val is None:
                continue
            elif type(val) is not type_:
                abort(400, f"Bad type for '{attr}', should be '{type_.__name__}'")
            elif attr != "password":
                updates = updates.update(**{attr: val})

        if body.get("password"):
            password = Authenticator.hash_password(body["password"])
            updates = updates.update(password=password, last_pass_reset=datetime.now())

        await updates.apply()

        return jsonify(user.to_dict())

    # This handles POST requests to add zip_url.
    # Usually this would be done via a whole entry but this
    # is designed for existing content.
    @route("/api/v1/mods/<mod_id>/upload_content", methods=["POST"])
    @json
    @requires_supporter
    @requires_login
    async def upload(self, mod_id: str):
        if not await Mod.exists(mod_id):
            return abort(404, "Unknown mod")

        return abort(501, "Coming soon")


def setup(core: Sayonika):
    Mods(core).register()
