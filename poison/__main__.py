'''

- https://maurycyz.com/misc/the_cost_of_trash/
- https://iocaine.madhouse-project.org/
- https://www.theregister.com/2024/07/30/taming_ai_content_crawlers/
- https://drewdevault.com/2025/03/17/2025-03-17-Stop-externalizing-your-costs-on-me.html


'''

import uvicorn
import textwrap
from itertools import islice
import fastapi
from pathlib import Path
from io import BytesIO
from fastapi import Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from .variable_chain import WordCounts

from .hilbert_image import Creator
PROJECT_ROOT = Path(__file__).resolve().parent

TEXTS = PROJECT_ROOT.parent / "texts"
IMAGES = PROJECT_ROOT.parent/"images"
WORD_COUNTS = WordCounts.from_paths(*TEXTS.iterdir())


TEMPLATES = PROJECT_ROOT / "templates"

assert TEMPLATES.is_dir()

templates = Jinja2Templates(directory=TEMPLATES)


app = fastapi.FastAPI()

IMAGE_CREATOR = Creator(IMAGES/"swim.512.png")


def seed_page(request: Request, seed: str,show_image:bool) -> HTMLResponse:
    chain = WORD_COUNTS.chain(seed)
    long = list(islice(chain, 400))
    text = textwrap.fill(" ".join(long), width=88, replace_whitespace=True)
    links = chain.random_words(10)

     
    return templates.TemplateResponse(
        request=request,
        name='page.html', 
        context=dict(text=text, links=links, seed=seed, show_image=show_image),
    )

@app.get("/image/{seed}", response_class=StreamingResponse)
async def get_image(request:Request, seed:str):

    image = IMAGE_CREATOR.create(seed)

    io=BytesIO()
    image.save(io,"png")
    io.seek(0)
    return StreamingResponse(io, media_type="image/png")

@app.get("/{seed}", response_class=HTMLResponse)
async def page(request: Request,  seed: str, show_image:bool=False) -> HTMLResponse:
    return seed_page(request, seed,show_image)


@app.get("/",  response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return seed_page(request, "Main",False )


if __name__ == "__main__":
    server = uvicorn.Server(config=uvicorn.Config(app, host="0.0.0.0"))
    server.run()
