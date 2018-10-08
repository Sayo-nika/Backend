Understanding the format of mods/mods.json might be difficult to understand, so here it is explained in further detail

Top structure:

```json
{
  "mods": [Mod, ...],
  "reviews": [Review, ...],
  "users": [User, ...],
  "update": 0
}
```
NOTE: the `update` value is only used for triggering saving the json back to disk

A Mod object looks like this:
```json
{
  "title": "Mod Title",
  "path": "local path, usually 8 hex characters",
  "released_at": 0,
  "last_updated": 0,
  "downloads": 0,
  "authors": ["User#name", ...],
  "verified": false
}
```

User:
```json
{
  "name": "Username",
  "bio": "lorem ipsum yadda yadda",
  "mods": ["Mod#title", ...],
  "favorites": ["Mod#title", ...]
}
```

Reviews:
```json
{
  "author": "User#name",
  "mod": "Mod#name",
  "message": "review contents"
}
```