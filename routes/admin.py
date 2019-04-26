# Stdlib
import base64

# External Libraries
from Cryptodome.Cipher import AES
from quart import abort, jsonify, request
from sqlalchemy import and_
from webargs import fields

# Sayonika Internals
from framework.models import Mod, Report, ModAuthor, User, AuthorRole
from framework.objects import SETTINGS, db
from framework.quart_webargs import use_kwargs
from framework.route import route
from framework.route_wrappers import json, requires_admin
from framework.routecog import RouteCog
from framework.sayonika import Sayonika
from framework.utils import paginate


# Probably will need to add this to util or smth later
def deep_to_dict(model):
    """
    Turn a model into a dictionary and recurse through any model attributes
    """
    dicted = model.to_dict()

    for attr in dir(model):
        attr_on_model = getattr(model, attr)

        if isinstance(attr_on_model, db.Model) and attr not in dicted:
            dicted[attr] = deep_to_dict(attr_on_model)

    return dicted


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
        "limit": fields.Int(missing=50)
    }, locations=("json",))
    async def get_verify_queue(self, limit: int, page: int):
        if not 1 <= limit <= 100:
            limit = max(1, min(limit, 100))  # Clamp `limit` to 1 or 100, whichever is appropriate

        page = page - 1 if page > 0 else 0

        query = Mod.outerjoin(ModAuthor).outerjoin(User).select().where(and_(
            ModAuthor.role == AuthorRole.owner,
            ModAuthor.mod_id == Mod.id,
            ModAuthor.user_id == User.id
        ))
        query = query.gino.load(Mod.distinct(Mod.id).load(author=User.distinct(User.id))).query
        mods = await paginate(query, page, limit).where(Mod.verified == False).gino.all()

        return jsonify(self.deep_dict_all(mods))

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

    @route("/api/v1/<mod_id>/verify", methods=["POST"])
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


def setup(core: Sayonika):
    Admin(core).register()
