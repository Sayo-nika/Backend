# Stdlib
import base64
from enum import Enum
import imghdr
import re
from typing import List, Tuple, Union, Optional

# External Libraries
from marshmallow import Schema
from marshmallow_enum import EnumField
from quart import abort, jsonify, request
from sqlalchemy import and_, func, select
from webargs import fields, validate

# Sayonika Internals
from framework.models import (Mod, User, Report, Review, ModColor, ModAuthor, ModStatus, AuthorRole, ReportType,
                              ModCategory, ReactionType, UserFavorite, ModPlaytester, ReviewReaction)
from framework.objects import db, owo, limiter, jwt_service
from framework.quart_webargs import use_kwargs
from framework.route import route, multiroute
from framework.route_wrappers import json, requires_login, requires_supporter
from framework.routecog import RouteCog
from framework.sayonika import Sayonika
from framework.utils import NamedBytes, paginate, generalize_text, verify_recaptcha


class AuthorSchema(Schema):
    id = fields.Str()
    role = EnumField(AuthorRole)


class ModSorting(Enum):
    title = 0
    rating = 1
    last_updated = 2
    release_date = 3
    downloads = 4


class ReviewSorting(Enum):
    best = 0
    newest = 1
    oldest = 2
    highest = 3
    lowest = 4
    funniest = 5


def data_is_acceptable_img(data: str) -> bool:
    """Check if a given file data is a PNG or JPEG."""
    return imghdr.test_png(data, None) or imghdr.test_jpeg(data, None)


def get_b64_size(data: bytes) -> int:
    """Get the size of data encoded in base64."""
    return (len(data) * 3) / 4 - data.count(b"=", -2)


def validate_img(uri: str, name: str, *, return_data: bool = True) -> Optional[Tuple[str, str]]:
    """Validates an image to be used for banner or icon."""
    # Pre-requirements for uri (determine proper type and size).
    mimetype, data = DATA_URI_RE.match(uri).groups()

    if mimetype not in ACCEPTED_MIMETYPES:
        abort(400, f"`{name}` mimetype should either be 'image/png', 'image/jpeg', or 'image/webp'")

    # Get first 33 bytes of icon data and decode. See: https://stackoverflow.com/a/34287968/8778928
    sample = base64.b64decode(data[:44])
    type_ = data_is_acceptable_img(sample)

    if type_ is None:
        abort(400, f"`{name}` data is not PNG, JPEG, or WEBP")
    elif type_ != mimetype.split("/")[1]:  # Compare type from mimetype and actual image data type
        abort(400, f"`{name}` mimetype and data mismatch")

    size = get_b64_size(data.encode("utf-8"))

    if size > (5 * 1000 * 1000):  # Check if image is larger than 5MB
        abort(400, f"`{name}` should be less than 5MB")

    return (mimetype, data) if return_data else None


ACCEPTED_MIMETYPES = ("image/png", "image/jpeg", "image/webp")
DATA_URI_RE = re.compile(r"data:([a-z]+/[a-z-.+]+);base64,([a-zA-Z0-9/+]+=*)")
mod_sorters = {
    ModSorting.title: Mod.title,
    # ModSorting.rating: lambda ascending:
    ModSorting.last_updated: Mod.last_updated,
    ModSorting.release_date: Mod.released_at,
    ModSorting.downloads: Mod.downloads
}

review_sorters = {
    ReviewSorting.newest: Review.created_at,
    ReviewSorting.oldest: Review.created_at.asc(),
    ReviewSorting.highest: Review.rating,
    ReviewSorting.lowest: Review.rating.asc()
}


class Mods(RouteCog):
    @staticmethod
    def dict_all(models):
        return [m.to_dict() for m in models]

    @multiroute("/api/v1/mods", methods=["GET"], other_methods=["POST"])
    @json
    @use_kwargs({
        "q": fields.Str(),
        "page": fields.Int(missing=0),
        "limit": fields.Int(missing=50),
        "category": EnumField(ModCategory),
        "rating": fields.Int(validate=validate.OneOf([1, 2, 3, 4, 5])),
        "status": EnumField(ModStatus),
        "sort": EnumField(ModSorting),
        "ascending": fields.Bool(missing=False)
    }, locations=("query",))
    async def get_mods(self, q: str = None, page: int = None, limit: int = None, category: ModCategory = None,
                       rating: int = None, status: ModStatus = None, sort: ModSorting = None, ascending: bool = None):
        if not 1 <= limit <= 100:
            limit = max(1, min(limit, 100))  # Clamp `limit` to 1 or 100, whichever is appropriate

        page = page - 1 if page > 0 else 0
        query = Mod.query.where(Mod.verified)

        if q is not None:
            like = f"%{q}%"

            query = query.where(and_(
                Mod.title.match(q),
                Mod.tagline.match(q),
                Mod.description.match(q),

                Mod.title.ilike(like),
                Mod.tagline.ilike(like),
                Mod.description.ilike(like)
            ))

        if category is not None:
            query = query.where(Mod.status == category)

        if rating is not None:
            query = query.where(rating + 1 > db.select([
                func.avg(Review.select("rating").where(Review.mod_id == Mod.id))
            ]) >= rating)

        if status is not None:
            query = query.where(Mod.status == status)

        if sort is not None:
            sort_by = mod_sorters[sort]
            query = query.order_by(sort_by.asc() if ascending else sort_by.desc())

        results = await paginate(query, page, limit).gino.all()
        total = await query.alias().count().gino.scalar()

        return jsonify(total=total, page=page, limit=limit, results=self.dict_all(results))

    @multiroute("/api/v1/mods", methods=["POST"], other_methods=["GET"])
    @requires_login
    @json
    @use_kwargs({
        "title": fields.Str(required=True, validate=validate.Length(max=64)),
        "tagline": fields.Str(required=True, validate=validate.Length(max=100)),
        "description": fields.Str(required=True, validate=validate.Length(min=100, max=10000)),
        "website": fields.Url(required=True),
        "status": EnumField(ModStatus, required=True),
        "category": EnumField(ModCategory, required=True),
        "authors": fields.List(fields.Nested(AuthorSchema), required=True),
        "icon": fields.Str(
            validate=validate.Regexp(
                DATA_URI_RE,
                error=("`icon` should be a data uri like 'data:image/png;base64,<data>' or "
                       "'data:image/jpeg;base64,<data>'")
            ),
            required=True
        ),
        "banner": fields.Str(
            validate=validate.Regexp(
                DATA_URI_RE,
                error=("`banner` should be a data uri like 'data:image/png;base64,<data>' or "
                       "'data:image/jpeg;base64,<data>'"),
            ),
            required=True
        ),
        "is_private_beta": fields.Bool(missing=False),
        "mod_playtester": fields.List(fields.Str()),
        "color": EnumField(ModColor, missing=ModColor.default),
        "recaptcha": fields.Str(required=True)
    }, locations=("json",))
    async def post_mods(self, title: str, tagline: str, description: str, website: str, authors: List[dict],
                        status: ModStatus, category: ModCategory, icon: str, banner: str, recaptcha: str,
                        color: ModColor, is_private_beta: bool = None, mod_playtester: List[str] = None):
        score = await verify_recaptcha(recaptcha, self.core.aioh_sess, "create_mod")

        if score < 0.5:
            # TODO: discuss what to do here
            abort(400, "Possibly a bot")

        token = request.headers.get("Authorization", request.cookies.get("token"))
        parsed_token = await jwt_service.verify_login_token(token, True)
        user_id = parsed_token["id"]

        # Check if any mod with a similar enough name exists already.
        generalized_title = generalize_text(title)
        mods = await Mod.get_any(True, generalized_title=generalized_title).first()

        if mods is not None:
            abort(400, "A mod with that title already exists")

        if status is ModStatus.archived:
            abort(400, "Can't create a new archived mod")

        mod = Mod(title=title, tagline=tagline, description=description, website=website, status=status,
                  category=category, theme_color=color)

        icon_mimetype, icon_data = validate_img(icon, "icon")
        banner_mimetype, banner_data = validate_img(banner, "banner")

        for i, author in enumerate(authors):
            if author["id"] == user_id:
                authors.pop(i)
                continue
            elif not await User.exists(author["id"]):
                abort(400, f"Unknown user '{author['id']}'")

        authors.append({"id": user_id, "role": AuthorRole.owner})

        if is_private_beta is not None:
            mod.is_private_beta = is_private_beta

        if mod_playtester is not None:
            if not is_private_beta:
                abort(400, "No need for `ModPlaytester` if open beta")

            for playtester in mod_playtester:
                if not await User.exists(playtester):
                    abort(400, f"Unknown user '{playtester}'")

        # Decode images and add name for mimetypes
        icon_data = base64.b64decode(icon_data)
        banner_data = base64.b64decode(banner_data)
        icon_ext = icon_mimetype.split("/")[1]
        banner_ext = banner_mimetype.split("/")[1]

        icon_data = NamedBytes(icon_data, name=f"icon.{icon_ext}")
        banner_data = NamedBytes(banner_data, name=f"banner.{banner_ext}")

        img_urls = await owo.async_upload_files(icon_data, banner_data)

        mod.icon = img_urls[icon_data.name]
        mod.banner = img_urls[banner_data.name]

        await mod.create()
        await ModAuthor.insert().gino.all(*[dict(user_id=author["id"], mod_id=mod.id, role=author["role"]) for author
                                            in authors])

        if ModPlaytester is not None:
            await ModPlaytester.insert().gino.all(*[dict(user_id=user, mod_id=mod.id) for user in mod_playtester])

        return jsonify(mod.to_dict())

    @route("/api/v1/mods/recent_releases")
    @json
    async def get_recent_releases(self):
        mods = await Mod.query.where(and_(
            Mod.verified,
            Mod.status == ModStatus.released
        )).order_by(Mod.released_at.desc()).limit(10).gino.all()

        return jsonify(self.dict_all(mods))

    @route("/api/v1/mods/most_loved")
    @json
    async def get_most_loved(self):
        love_counts = select([func.count()]).where(UserFavorite.mod_id == Mod.id).as_scalar()
        mods = await Mod.query.order_by(love_counts.desc()).limit(10).gino.all()

        return jsonify(self.dict_all(mods))

    @route("/api/v1/mods/most_downloads")
    @json
    async def get_most_downloads(self):
        mods = await Mod.query.where(and_(
            Mod.verified,
            Mod.released_at is not None
        )).order_by(Mod.downloads.desc()).limit(10).gino.all()

        return jsonify(self.dict_all(mods))

    @route("/api/v1/mods/trending")
    @json
    async def get_trending(self):
        # TODO: implement
        return jsonify([])

    @multiroute("/api/v1/mods/<mod_id>", methods=["GET"], other_methods=["PATCH", "DELETE"])
    @json
    async def get_mod(self, mod_id: str):
        mod = await Mod.get(mod_id)

        if mod is None:
            abort(404, "Unknown mod")

        return jsonify(mod.to_dict())

    @multiroute("/api/v1/mods/<mod_id>", methods=["PATCH"], other_methods=["GET", "DELETE"])
    @requires_login
    @json
    @use_kwargs({
        "title": fields.Str(validate=validate.Length(max=64)),
        "tagline": fields.Str(validate=validate.Length(max=100)),
        "description": fields.Str(validate=validate.Length(min=100, max=10000)),
        "website": fields.Url(),
        "status": EnumField(ModStatus),
        "category": EnumField(ModCategory),
        "authors": fields.List(fields.Nested(AuthorSchema)),
        "icon": fields.Str(
            validate=validate.Regexp(
                DATA_URI_RE,
                error=("`icon` should be a data uri like 'data:image/png;base64,<data>' or "
                       "'data:image/jpeg;base64,<data>'")
            )
        ),
        "banner": fields.Str(
            validate=validate.Regexp(
                DATA_URI_RE,
                error=("`banner` should be a data uri like 'data:image/png;base64,<data>' or "
                       "'data:image/jpeg;base64,<data>'"),
            )
        ),
        "color": EnumField(ModColor),
        "is_private_beta": fields.Bool(),
        "mod_playtester": fields.List(fields.Str())
    }, locations=("json",))
    async def patch_mod(self, mod_id: str = None, authors: List[dict] = None, mod_playtester: List[str] = None,
                        icon: str = None, banner: str = None, **kwargs):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        mod = await Mod.get(mod_id)
        updates = mod.update(**kwargs)

        if authors is not None:
            authors = [author for author in authors if await User.exists(author["id"])]
            # TODO: if user is owner or co-owner, allow them to change the role of others to ones below them.
            authors = [author for author in authors if not await ModAuthor.query.where(
                and_(ModAuthor.user_id == author["id"], ModAuthor.mod_id == mod_id)
            ).gino.first()]

        if mod_playtester is not None:
            for playtester in mod_playtester:
                if not await User.exists(playtester):
                    abort(400, f"Unknown user '{playtester}'")
                elif await ModPlaytester.query.where(
                        and_(ModPlaytester.user_id == playtester, ModPlaytester.mod_id == mod.id)).gino.all():
                    abort(400, f"{playtester} is already enrolled.")

        to_upload = []

        if icon is not None:
            icon_mimetype, icon_data = validate_img(icon, "icon")
            icon_data = base64.b64decode(icon_data)

            icon_ext = icon_mimetype.split("/")[1]
            icon_data = NamedBytes(icon_data, name=f"icon.{icon_ext}")

            to_upload.append(icon_data)

        if banner is not None:
            banner_mimetype, banner_data = validate_img(banner, "banner")
            banner_data = base64.b64decode(banner_data)

            banner_ext = banner_mimetype.split("/")[1]
            banner_data = NamedBytes(banner_data, name=f"banner.{banner_ext}")

            to_upload.append(banner_data)

        img_urls = await owo.async_upload_files(*to_upload)
        img_updates = {}

        if icon is not None:
            img_updates["icon"] = img_urls[icon_data.name]

        if banner is not None:
            img_updates["banner"] = img_urls[banner_data.name]

        # Lump together image updates because lessening operations or some shit.
        updates = updates.update(**img_updates)

        await updates.apply()
        await ModAuthor.insert().gino.all(*[
            dict(user_id=author["id"], mod_id=mod.id, role=author["role"]) for author in authors
        ])
        await ModPlaytester.insert().gino.all(*[dict(user_id=user, mod_id=mod.id) for user in ModPlaytester])

        return jsonify(mod.to_dict())

    # TODO: decline route with reason, maybe doesn't 100% delete it? idk
    @multiroute("/api/v1/mods/<mod_id>", methods=["DELETE"], other_methods=["GET", "PATCH"])
    @requires_login
    @json
    async def delete_mod(self, mod_id: str):
        await Mod.delete.where(Mod.id == mod_id).gino.status()

        return jsonify(True)

    @route("/api/v1/mods/<mod_id>/download")
    @json
    async def get_download(self, mod_id: str):
        token = request.headers.get("Authorization", request.cookies.get("token"))
        parsed_token = await jwt_service.verify_login_token(token, True)
        user_id = parsed_token["id"]

        mod = await Mod.get(mod_id)

        if mod is None:
            abort(404, "Unknown mod")
        if user_id is None and mod.is_private_beta:
            abort(403, "Private beta mods requires authentication.")
        if not await ModPlaytester.query.where(and_(ModPlaytester.user_id == user_id, ModPlaytester.mod_id == mod.id))\
                .gino.all():
            abort(403, "You are not enrolled to the private beta.")
        elif not mod.zip_url:
            abort(404, "Mod has no download")

        return jsonify(url=mod.zip_url)

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["GET"], other_methods=["POST"])
    @json
    @use_kwargs({
        "page": fields.Int(missing=0),
        "limit": fields.Int(missing=10),
        # Probably won't work right now, will need union field.
        "rating": fields.Int(validate=validate.OneOf([1, 2, 3, 4, 5, "all"]), missing="all"),
        "sort": EnumField(ReviewSorting, missing=ReviewSorting.best)
    }, locations=("query",))
    async def get_reviews(self, mod_id: str, page: int, limit: int, rating: Union[int, str],
                          sort: ReviewSorting):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        if not 1 <= limit <= 25:
            limit = max(1, min(limit, 25))  # Clamp `limit` to 1 or 100, whichever is appropriate

        page = page - 1 if page > 0 else 0
        query = Review.query.where(Review.mod_id == mod_id)

        if review_sorters[sort]:
            query = query.order_by(review_sorters[sort])
        elif sort == ReviewSorting.best:
            upvoters_count = select([func.count()]).where(and_(
                ReviewReaction.review_id == Review.id,
                ReviewReaction.reaction == ReactionType.upvote
            )).as_scalar()

            downvoters_count = select([func.count()]).where(and_(
                ReviewReaction.review_id == Review.id,
                ReviewReaction.reaction == ReactionType.downvote
            )).as_scalar()

            query = query.order_by(upvoters_count - downvoters_count)
        elif sort == ReviewSorting.funniest:
            # Get count of all funny ratings by review.
            sub_order = select([func.count()]).where(and_(
                ReviewReaction.review_id == Review.id,
                ReviewReaction.reaction == ReactionType.funny
            )).as_scalar()
            query = query.order_by(sub_order.desc())

        if isinstance(rating, int):
            values = [rating, rating + 0.5]

            if rating == 1:
                # Also get reviews with a 0.5 star rating, otherwise they'll never appear.
                values.append(0.5)

            query = query.where(Review.rating.in_(values))

        reviews = await query.gino.all()

        return jsonify(self.dict_all(reviews))

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["POST"], other_methods=["GET"])
    @requires_login
    @json
    @use_kwargs({
        "rating": fields.Int(required=True, validate=[
            # Only allow increments of 0.5, up to 5.
            lambda x: 5 >= x >= 1,
            lambda x: x % 0.5 == 0
        ]),
        "content": fields.Str(required=True, validate=validate.Length(max=2000)),
        "title": fields.Str(required=True, validate=validate.Length(max=32))
    })
    async def post_review(self, mod_id: str, rating: int, content: str, title: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        token = request.headers.get("Authorization", request.cookies.get("token"))
        parsed_token = await jwt_service.verify_login_token(token, True)
        user_id = parsed_token["id"]

        if await Review.query.where(and_(Review.author_id == user_id, Review.mod_id == mod_id)).gino.first():
            abort(400, "Review already exists")

        review = await Review.create(title=title, content=content, rating=rating, author_id=user_id, mod_id=mod_id)

        return jsonify(review.to_json())

    @route("/api/v1/mods/<mod_id>/authors")
    @json
    async def get_authors(self, mod_id: str):
        if not await Mod.exists(mod_id):
            abort(404, "Unknown mod")

        author_pairs = await ModAuthor.query.where(ModAuthor.mod_id == mod_id).gino.all()
        author_pairs = [x.user_id for x in author_pairs]
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

    @route("/api/v1/mods/<mod_id>/report", methods=["POST"])
    @json
    @use_kwargs({
        "content": fields.Str(required=True, validate=validate.Length(min=100, max=1000)),
        "type_": EnumField(ReportType, required=True),
        "recaptcha": fields.Str(required=True)
    }, locations=("json",))
    @requires_login
    @limiter.limit("2 per hour")
    async def report_mod(self, mod_id: str, content: str, type_: ReportType, recaptcha: str):
        await verify_recaptcha(recaptcha, self.core.aioh_sess)

        token = request.headers.get("Authorization", request.cookies.get("token"))
        parsed_token = await jwt_service.verify_login_token(token, True)
        user_id = parsed_token["id"]

        report = await Report.create(content=content, author_id=user_id, mod_id=mod_id, type=type_)
        return jsonify(report.to_dict())


def setup(core: Sayonika):
    Mods(core).register()
