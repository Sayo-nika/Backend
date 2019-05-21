# Stdlib
import base64
from enum import Enum
import inspect
from typing import List

# External Libraries
from Cryptodome.Cipher import AES
from marshmallow_enum import EnumField
from quart import abort, jsonify, request
from sqlalchemy import and_
from webargs import fields

# Sayonika Internals
from framework.authentication import Authenticator
from framework.models import Mod, User, Report, ModAuthor, AuthorRole
from framework.objects import SETTINGS, db, jwt_service
from framework.quart_webargs import use_kwargs
from framework.route import route, multiroute
from framework.route_wrappers import json, requires_admin, requires_developer
from framework.routecog import RouteCog
from framework.sayonika import Sayonika
from framework.utils import paginate


def get_members(type_) -> List[str]:
    non_routines = inspect.getmembers(type_, lambda x: not inspect.isroutine(x))
    return [x[0] for x in non_routines if not (x[0].startswith("_") or x[0].endswith("_"))]


# Probably will need to add this to util or smth later
def deep_to_dict(model):
    """
    Turn a model into a dictionary and recurse through any model attributes
    """
    dicted = model.to_dict()

    for attr in get_members(model):
        attr_on_model = getattr(model, attr)

        if attr not in dicted or dicted[attr] == attr_on_model:
            if isinstance(attr_on_model, db.Model):
                dicted[attr] = deep_to_dict(attr_on_model)
            elif isinstance(attr_on_model, list):
                dicted[attr] = [deep_to_dict(x) for x in attr_on_model]

    return dicted


class VerifyQueueSorting(Enum):
    date_submitted = 0
    name = 1


queue_sorting = {
    VerifyQueueSorting.date_submitted: Mod.created_at,
    VerifyQueueSorting.name: Mod.title
}


class Admin(RouteCog):
    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    @staticmethod
    def deep_dict_all(models):
        return [deep_to_dict(m) for m in models]

    @route("/api/v1/mods/verify_queue", methods=["GET"])
    @requires_admin
    @json
    @use_kwargs({
        "page": fields.Int(missing=0),
        "limit": fields.Int(missing=50),
        "sort": EnumField(VerifyQueueSorting, missing="date_submitted"),
        "ascending": fields.Bool(missing=False),
        "get_all_authors": fields.Bool(missing=False)
    })
    async def get_verify_queue(self, limit: int, page: int, sort: VerifyQueueSorting, ascending: bool,
                               get_all_authors: bool):
        if not 1 <= limit <= 100:
            limit = max(1, min(limit, 100))  # Clamp `limit` to 1 or 100, whichever is appropriate

        page = page - 1 if page > 0 else 0
        sort_by = queue_sorting[sort]

        query = Mod.outerjoin(ModAuthor).outerjoin(User).select()

        loader = Mod.distinct(Mod.id).load(
            authors=User.load(
                role=ModAuthor.distinct(ModAuthor.id)
            )
        )
        query = query.gino.load(loader).query

        query = query.where(Mod.verified == False).order_by(  # noqa: E712
            sort_by.asc() if ascending else sort_by.desc()
        )

        results = await paginate(query, page, limit).gino.all()
        total = await Mod.query.where(Mod.verified == False).alias().count().gino.scalar()  # noqa: E712
        results = self.deep_dict_all(results)

        return jsonify(total=total, page=page, limit=limit, results=results)

    @route("/api/v1/mods/report_queue", methods=["GET"])
    @requires_admin
    @json
    @use_kwargs({
        "page": fields.Int(missing=0),
        "limit": fields.Int(missing=50)
    }, locations=("json",))
    async def get_report_queue(self, limit: int, page: int):
        if not 1 <= limit <= 100:
            limit = max(1, min(limit, 100))  # Clamp `limit` to 1 or 100, whichever is appropriate

        page = page - 1 if page > 0 else 0
        reports = await paginate(Report.query.order_by("mod_id"), page, limit).gino.all()

        return jsonify(self.dict_all(reports))

    @route("/api/v1/mods/<mod_id>/verify", methods=["POST"])
    @requires_admin
    @json
    async def post_verify(self, mod_id: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        await Mod.update.values(verified=True).where(Mod.id == mod_id).gino.status()

        return jsonify(True)

    @route("/api/v1/admin/decrypt_tb", methods=["POST"])
    @requires_admin
    @json
    async def post_decrypt_tb(self):
        data = await request.get_data()
        data = data.strip()

        if b"." not in data or data.count(b".") != 1:
            abort(400, "Bad data")

        nonce, digest = data.split(b".")
        nonce = base64.b64decode(nonce)
        digest = base64.decodebytes(digest.replace(rb"\n", b"\n"))

        c = AES.new(SETTINGS["AES_KEY"], AES.MODE_CTR, nonce=nonce)
        parsed = c.decrypt(digest).decode()

        return jsonify(parsed)

    @multiroute("/api/v1/admin/users/<user_id>", methods=["PATCH"], other_methods=["DELETE"])
    @requires_developer
    @json
    @use_kwargs({
        "supporter": fields.Boolean(allow_none=True),
        "editor": fields.Boolean(allow_none=True),
        "moderator": fields.Boolean(allow_none=True),
        "developer": fields.Boolean(allow_none=True),
        "password": fields.Str(required=True)
    }, locations=("json",))
    async def patch_user_roles(self, user_id: str, password: str, **kwargs):
        # TODO: audit log stuff
        if not await User.exists(user_id):
            abort(404, "Unknown user")

        token = request.headers.get("Authorization", request.cookies.get("token"))
        parsed_token = await jwt_service.verify_login_token(token, True)
        admin_user_id = parsed_token["id"]

        user = await User.get(admin_user_id)

        if not Authenticator.compare_password(password, user.password):
            abort(401, "Invalid password")

        if not kwargs:
            return jsonify(True)

        await User.update.values(**{
            k: v for k, v in kwargs.items() if v is not None
        }).where(User.id == user_id).gino.status()

        return jsonify(True)

    @multiroute("/api/v1/admin/users/<user_id>", methods=["DELETE"], other_methods=["PATCH"])
    @requires_developer
    @json
    @use_kwargs({
        "password": fields.Str(required=True)
    }, locations=("json",))
    async def delete_user(self, user_id: str, password: str):
        # TODO: audit log stuff
        if not await User.exists(user_id):
            abort(404, "Unknown user")

        token = request.headers.get("Authorization", request.cookies.get("token"))
        parsed_token = await jwt_service.verify_login_token(token, True)
        admin_user_id = parsed_token["id"]

        user = await User.get(admin_user_id)

        if not Authenticator.compare_password(password, user.password):
            abort(401, "Invalid password")

        await Mod.delete.where(and_(
            ModAuthor.user_id == user_id,
            ModAuthor.mod_id == Mod.id,
            ModAuthor.role == AuthorRole.owner
        )).gino.status()
        await User.delete.where(User.id == user_id).gino.status()

        return jsonify(True)


def setup(core: Sayonika):
    Admin(core).register()
