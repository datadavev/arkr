"""ARKR is a minimal ARK NAAN resolver service.
"""
import json
import os
import re
import typing
import fastapi
import fastapi.middleware.cors

VERSION = "0.0.1"

app = fastapi.FastAPI(
    title="ARKR",
    description=__doc__,
    version=VERSION,
    contact={"name": "Dave Vieglais", "url": "https://github.com/datadavev/"},
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Enables CORS for UIs on different domains
app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "HEAD",
    ],
    allow_headers=[
        "*",
    ],
)

ARK_MATCH = re.compile("(^|ark\:|ark\:\/)([0-9]{4,64})\/?(.*)", re.IGNORECASE)
DATA_DIR = "naans/"

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    raise fastapi.HTTPException(status_code=404)


@app.get("/diag/{identifier:path}")
async def resolve_prefix_diag(request:fastapi.Request, identifier:str=None):
    rurl = str(request.url)
    identifier = identifier.lstrip("/ ")
    matches = ARK_MATCH.fullmatch(identifier)
    arkpid = rurl[rurl.find(identifier):]
    if not arkpid.startswith("ark:"):
        arkpid = f"ark:/{arkpid}"
    naan = None
    pid = None
    if matches is not None:
        naan = matches.group(2)
        pid = arkpid[arkpid.find(naan):]
    return {
        "url":rurl,
        "url.path": request.url.path,
        "url.query": request.url.query,
        "path": identifier,
        "naan": naan,
        "pid": pid,
        "arkpid": arkpid,
    }


@app.get(
    "/{identifier:path}",
    summary="Redirect to the identified resource or present resolver information.",
)
async def resolve_prefix(
    request:fastapi.Request,
    identifier: str=None,
    accept:typing.Optional[str]=fastapi.Header(None)
):
    if identifier is None or len(identifier) < 1:
        # should never reach this, but just in case...
        return fastapi.responses.RedirectResponse("/docs")
    rurl = str(request.url)
    identifier = identifier.lstrip("/ ")
    matches = ARK_MATCH.fullmatch(identifier)
    if matches is None:
        raise fastapi.HTTPException(status_code=404, detail=f"Not found.")
    naan = matches.group(2)
    arkpid = rurl[rurl.find(identifier):]
    if not arkpid.startswith("ark:"):
        arkpid = f"ark:/{arkpid}"
    pid = arkpid[arkpid.find(naan):]
    fname = os.path.join(DATA_DIR,f"{naan}.json")
    if not os.path.exists(fname):
        raise fastapi.HTTPException(status_code=404, detail=f"NAAN {naan} not found.")
    with open(fname, "r") as fsrc:
        naan_record = json.load(fsrc)
    if rurl.endswith("?info") or rurl.endswith("?") or rurl.endswith("??"):
        return naan_record
    if "$pid" in naan_record["target"]:
        return fastapi.responses.RedirectResponse(naan_record["target"].replace("$pid", pid))
    return fastapi.responses.RedirectResponse(naan_record["target"].replace("$arkpid", arkpid))

