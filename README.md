# ARKR

A simple ARK NAAN resolver service.

ARKR is a minimalist ARK NAAN resolver service that supports redirection to 
registered NAAN targets or introspection (inflection) of a NAAN public record.

Requires a JSON copy of the NAAN public registry information, such as produced 
by `naan_reg_json`.

## Operation

To run ARKR locally, setup your python virtual environment then:

```
pip install -r backend/requirements.txt
```

Retrieve the NAAN records as json (currently requires a local copy of `main_naans`):

```
python ../naan_reg_json/naan_reg_json.py -p -f backend/naans ../naan_reg_priv/main_naans
```

Then run the service:
```
cd backend
uvicorn main:app
```

A [spacefile](https://deta.space/docs/en/introduction/start) is included for deployment on [Deta Space](https://deta.space/). To deploy on Deta Space:

```
space new
space push
```

An example of the service running on Deta is available at: https://arkr-1-v3111276.deta.app/

## Service Endpoints

| Path                                             | Description                                                                                                                                                                                                                                                                                                                                                                                                              |
|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`/docs`](https://arkr-1-v3111276.deta.app/docs) | API documentation                                                                                                                                                                                                                                                                                                                                                                                                        |
| `/diag/{IDENTIFIER}`                             | Presents some diagnostics of request processing. E.g. [diag/ark:/12148/bpt6k10733944](https://arkr-1-v3111276.deta.app/diag/ark:/12148/bpt6k10733944)                                                                                                                                                                                                                                                                    |
| `/{IDENTIFIER}`                                  | Redirects to supplied ARK. <br>* [`/ark:/12148/bpt6k10733944`](https://arkr-1-v3111276.deta.app/ark:/12148/bpt6k10733944) <br>* [`/ark:12148/bpt6k10733944`](https://arkr-1-v3111276.deta.app/ark:12148/bpt6k10733944) <br>* [`/12148/bpt6k10733944`](https://arkr-1-v3111276.deta.app/12148/bpt6k10733944)                                                                                                              |
| `/{NAAN}[/][?? \| ?info]`                        | Returns metadata about the NAAN. Note that if characters beyond a terminating "/" are included then the response is a redirect to the registered location with the provided inflection request. <br>* [`/ark:/12148/?info`](https://arkr-1-v3111276.deta.app/ark:/12148/?info) <br>* [`/ark:12148??`](https://arkr-1-v3111276.deta.app/ark:12148??) <br>* [`/12148/?info`](https://arkr-1-v3111276.deta.app/12148??) |

