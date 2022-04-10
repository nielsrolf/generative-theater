from glob import glob
import os
from typing import List
import nlpcloud
import deepl 
import click

from gen_theater import secrets



class Part:
    """Class for one part of the story - i.e. one line of the script
    
    Attributes:
        - raw: the raw text of the part
        - actor: the actor of the part, or 'room' if it's the narrator
        - media: one of ['audio', 'video', 'text']
        - text: the text of the part
    """
    def __init__(self, raw: str):
        self.raw = raw
        self.actor, raw = raw.split(" (", 1)
        self.media, self.text = raw.split("): ", 1)
        self.text = self.text.strip()
    
    def __str__(self):
        return f"{self.actor}: {self.text}"


def fill_template_gpt(parts: List[Part]) -> List[Part]:
    """Replace <generate> with generated text from GPT"""
    client = nlpcloud.Client("gpt-neox-20b", secrets.NLPCLOUD, True)
    for i, part in enumerate(parts):
        if part.text == "<generate>":
            prompt = create_prompt(parts[:i + 1])
            print(f"PROMPT: {prompt}", end="\n" + "-" * 80 + "\n")
            part.text = client.generation(prompt,
                min_length=10,
                max_length=50,
                length_no_input=True,
                remove_input=True,
                end_sequence="\n",
                top_p=1,
                temperature=1,
                top_k=50,
                repetition_penalty=2,
                length_penalty=1,
                do_sample=True,
                early_stopping=False,
                num_beams=1,
                no_repeat_ngram_size=3,
                num_return_sequences=1,
                bad_words=None,
                remove_end_sequence=False
            )['generated_text'].strip()
    return parts


def create_prompt(parts: List[Part]) -> str:
    """Create a prompt for GPT to generate text
    
    Arguments:
        parts {List[Part]} -- list of parts of the script
    
    Returns:
        prompt -- the concatenated text of the parts
    """
    prompt = ""
    for part in parts[:-1]:
        prompt += str(part) + "\n"
    prompt += f"{parts[-1].actor}:"
    return prompt


def generate_chapter(story_file, output):
    """Open the story file and generate all media channels.

    Format of the story_file:
    `
        Luzia (audio): Hi
        Context: something happens
        Marin (audio): Hey what's up?
        Kriemhild (audio): <generate>
        Room (video): bla
        Room (audio): bla
    `

    Generates the following files:
    `{output}/{actor}/{1,2,3}.{mp3,mp4}`

    The processing pipeline is:
    - replace <generate> with GPT generated text
    - translate the text into German using deepl
    - split the text into cues for each speaker
    - generate audio or video for each speaker

    Arguments:
        story_file {str} -- path to the story file
        output {str} -- path to the output dir
    """
    with open(story_file, "r") as f:
        parts = [Part(i) for i in f.readlines()]
    parts = fill_template_gpt(parts)
    chapter = "\n".join(str(i) for i in parts)
    chapter_de = translate(chapter)
    print(chapter_de)


def translate(text: str, lang: str = "DE") -> str:
    """Translate text using deepl
    
    Arguments:
        text {str} -- text to translate
        lang {str} -- language to translate to
    
    Returns:
        translated_text {str} -- translated text
    """
    translator = deepl.Translator(secrets.DEEPL) 
    result = translator.translate_text(text, target_lang=lang) 
    translated_text = result.text
    return translated_text

@click.command()
@click.argument("story_template", type=click.Path(exists=True))
@click.argument("story_out", type=click.Path())
@click.option("--play", is_flag=True, help="auto-play the generated media")
@click.option("--generate_all", is_flag=True,
            help=" whether to generate all media or just the new ones (<generate> replacements)")
def main(story_template: str, story_out: str, play: bool = False, generate_all: bool = True):
    """Iterate through all chapter and generate media
    
    Arguments:
        story_template -- path to the dir with the template story
        story_out -- path to the dir where the generated media will be stored
        play -- whether to auto-play the generated media
        generate_all -- whether to generate all media or just the new ones
            (<generate> replacements)
    """
    os.makedirs(story_out, exist_ok=True)
    for chapter in glob(f"{story_template}/*.txt"):
        generate_chapter(chapter, chapter.replace(story_template, story_out))


if __name__ == "__main__":
    main()