import requests


response = requests.post("http://localhost:5000/files/", json={"path": "/Users/nielswarncke/Documents/art/eliza-effect-dresden/gen_theater/output/"})
breakpoint()