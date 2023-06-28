"""ARKR is a minimal ARK NAAN resolver service.
"""
import csv
import glob
import io
import json
import os
import re
import typing
import content_negotiation
import fastapi
import fastapi.middleware.cors

VERSION = "0.0.2"

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


def iter_csv(writer, data, stream):
    yield ()


@app.get("/", summary="List registered NAANs")
async def list_prefixes(
    accept: typing.Optional[str] = fastapi.Header(default="application/json"),
):
    accept = [a.strip() for a in accept.split(",")]
    supported_types = ["application/json", "text/csv", "text/plain"]
    try:
        content_type = content_negotiation.decide_content_type(accept, supported_types)
    except content_negotiation.NoAgreeableContentTypeError:
        content_type = "application/json"
    with open(os.path.join(DATA_DIR, "index.json")) as fsrc:
        data = json.load(fsrc)
        naans = list(data.keys())
    if content_type in ["text/csv", "text/plain"]:
        return fastapi.responses.PlainTextResponse(
            "\n".join(naans), media_type=content_type
        )
    return naans


@app.get("/diag/{identifier:path}")
async def resolve_prefix_diag(request: fastapi.Request, identifier: str = None):
    rurl = str(request.url)
    identifier = identifier.lstrip("/ ")
    matches = ARK_MATCH.fullmatch(identifier)
    arkpid = rurl[rurl.find(identifier) :]
    if not arkpid.startswith("ark:"):
        arkpid = f"ark:/{arkpid}"
    naan = None
    pid = None
    remainder = None
    if matches is not None:
        naan = matches.group(2)
        remainder = matches.group(3)
        pid = arkpid[arkpid.find(naan) :]
    return {
        "url": rurl,
        "url.path": request.url.path,
        "url.query": request.url.query,
        "path": identifier,
        "naan": naan,
        "remainder": remainder,
        "pid": pid,
        "arkpid": arkpid,
    }


@app.get(
    "/{identifier:path}",
    summary="Redirect to the identified resource or present resolver information.",
)
async def resolve_prefix(
    request: fastapi.Request,
    identifier: str = None,
    accept: typing.Optional[str] = fastapi.Header(None),
):
    if identifier is None or len(identifier) < 1:
        # should never reach this, but just in case...
        return fastapi.responses.RedirectResponse("/docs")
    rurl = str(request.url)
    print(rurl)
    identifier = identifier.lstrip("/ ")
    matches = ARK_MATCH.fullmatch(identifier)
    if matches is None:
        raise fastapi.HTTPException(status_code=404, detail=f"Not found.")
    naan = matches.group(2)
    remainder = matches.group(3)
    arkpid = rurl[rurl.find(identifier) :]
    if not arkpid.startswith("ark:"):
        arkpid = f"ark:/{arkpid}"
    pid = arkpid[arkpid.find(naan) :]
    fname = os.path.join(DATA_DIR, f"{naan}.json")
    if not os.path.exists(fname):
        raise fastapi.HTTPException(status_code=404, detail=f"NAAN {naan} not found.")
    with open(fname, "r") as fsrc:
        naan_record = json.load(fsrc)
    if remainder == "" and (
        rurl.endswith("?info")
        or rurl.endswith("?")
        or rurl.endswith("??")
        or rurl.endswith("?%3F")
    ):
        return naan_record
    if "$pid" in naan_record["target"]:
        return fastapi.responses.RedirectResponse(
            naan_record["target"].replace("$pid", pid)
        )
    return fastapi.responses.RedirectResponse(
        naan_record["target"].replace("$arkpid", arkpid)
    )
