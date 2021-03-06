import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

export_file_url = 'https://drive.google.com/uc?export=download&id=1C6OCxi6u5aYNq_Ffu9T9X7cYmNCbGNs6'
export_file_name = 'export.pkl'

classes = ['american_elm','american_sycamore','bald_cypress', 'bigtooth_maple', 'black_cherry', 'cedar_elm', 'green_ash', 'live_oak', 'magnolia', 'mexican_white_oak', 'pecan', 'red_oak', 'shumard_oak', 'texas_ash', 'texas_walnut', 'yaupon']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

async def get_bytes(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = await (img_data['file'].read())
    img = open_image(BytesIO(img_bytes))
    prediction = learn.predict(img)[0]
    return JSONResponse({'result': str(prediction)})

@app.route("/classify-url", methods=["GET"])
async def classify_url(request):
    img_bytes = await get_bytes(request.query_params["url"])
    img = open_image(BytesIO(img_bytes))
    prediction = learn.predict(img)[0]
    return JSONResponse({'result': str(prediction)})


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")

# @app.route("/upload", methods=["POST"])
# async def upload(request):
#     data = await request.form()
#     bytes = await (data["file"].read())
#     return predict_image_from_bytes(bytes)


# @app.route("/classify-url", methods=["GET"])
# async def classify_url(request):
#     bytes = await get_bytes(request.query_params["url"])
#     return predict_image_from_bytes(bytes)


# def predict_image_from_bytes(bytes):
#     img = open_image(BytesIO(bytes))
#     prediction = learn.predict(img)[0]
#     return JSONResponse({'result': str(prediction)})


# @app.route("/")
# def form(request):
#     return HTMLResponse(
#         """
#         <form action="/upload" method="post" enctype="multipart/form-data">
#             Select image to upload:
#             <input type="file" name="file">
#             <input type="submit" value="Upload Image">
#         </form>
#         Or submit a URL:
#         <form action="/classify-url" method="get">
#             <input type="url" name="url">
#             <input type="submit" value="Fetch and analyze image">
#         </form>
#     """)


# @app.route("/form")
# def redirect_to_homepage(request):
#     return RedirectResponse("/")


# if __name__ == "__main__":
#     if "serve" in sys.argv:
#         uvicorn.run(app, host="0.0.0.0", port=8008)
