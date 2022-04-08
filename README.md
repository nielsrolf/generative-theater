# Generative Theater

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
