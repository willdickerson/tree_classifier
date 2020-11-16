# Texas Tree Gazer

Scraped iNaturalist for research-grade images of central Texas trees with `scrape_inat.py`.

Used fast.ai to train a neural network to classify the trees with `inaturalist_trees.ipynb`.

`server.py` is a Starlette API server that accepts tree image URLs and returns the model's prediction as a JSON object.

`TexasTreeGazer.py` is a Twitter bot that looks for mentions containing an image and the keyword "ID" and tweets back a reply with the model's prediction. 

Modelled after [cougar-or-not](https://github.com/simonw/cougar-or-not) and the fast.ai model deployment [example](https://github.com/render-examples/fastai-v3).
