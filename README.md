# Generative Theater


Steps to do an update:
- open the `generative-theater` folder in a terminal
- run `git stash && git pull` - it will delete your changes to the story template so save that somewhere else, then it will update the code

Steps to generate:
- open the `generative-theater` folder in a terminal
- write the story template in the `/story` folder
- run `python3 gen_theater/main.py story/ media/ --generate_all --play`

How it works:
- template story is in `/story`
- when a new version is generated, the gaps are filled by GPT-J 20B
- then it is translated by deepl
- then audios are created
- then videos are created

```sh
# Install dependencies
pip install -e ".[test]"
```
