from dataclasses import dataclass
from glob import glob
import os
from typing import List
from xmlrpc.client import boolean
import nlpcloud
import deepl 
import click

from gen_theater import secrets


voices = {
    "Luzia": "Anna",
    # "Marin": "Markus",
    # "Kriemhild": "Yannick"
}

@dataclass
class Part:
    """Class for one part of the story - i.e. one line of the script
    
    Attributes:
        - raw: the raw text of the part
        - actor: the actor of the part, or 'room' if it's the narrator
        - media: one of ['audio', 'video', 'text']
        - text: the text of the part
    """
    raw: str
    actor: str
    media: str
    text: str
    generated: boolean = False
    voice: str = "Anna"
    
    @staticmethod
    def parse(raw: str):
        actor, raw = raw.split(" (", 1)
        media, text = raw.split("): ", 1)
        text = text.strip()
        return Part(raw, actor, media, text, False, voices.get(actor, "Anna"))
    
    def __str__(self):
        return f"{self.actor}: {self.text}"
    
    def translate(self):
        text_de = translate(self.text)
        return Part(self.raw, self.actor, self.media, text_de, self.generated, self.voice)


def fill_template_gpt(parts: List[Part]) -> List[Part]:
    """Replace <generate> with generated text from GPT"""
    # client = nlpcloud.Client("gpt-neox-20b", secrets.NLPCLOUD, True)
    client = nlpcloud.Client("fast-gpt-j", secrets.NLPCLOUD, True)
    story = []
    for i, part in enumerate(parts):
        if part.text == "<generate>":
            prompt = create_prompt(story + [part])
            print(f"PROMPT: {prompt}", end="\n" + "-" * 80 + "\n")
            text = client.generation(prompt,
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
            story.append(Part(part.raw, part.actor, part.media, text, True, part.voice))
        else:
            story.append(part)
    return story


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

def parse_template(story_file: str) -> List[Part]:
    """Open the story file and return a list of parts.

    Format of the story_file:
    `
        Luzia (audio): Hi
        Context: something happens
        Marin (audio): Hey what's up?
        Kriemhild (audio): <generate>
        Room (video): bla
        Room (audio): bla
    `
    """
    with open(story_file, "r") as f:
        parts = [Part.parse(i) for i in f.readlines()]
    return parts


def write_parts(parts: List[Part], output_dir: str, filename: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    output = os.path.join(output_dir, filename)
    chapter = "\n".join(str(i) for i in parts)
    with open(output, "w") as f:
        f.write(chapter)
    return parts


def translate_parts(parts: List[Part]) -> List[Part]:
    """Translate all parts of the script
    
    Arguments:
        parts {List[Part]} -- list of parts of the script
    
    Returns:
        translated_parts {List[Part]} -- list of translated parts
    """
    return [i.translate() for i in parts]
    


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


def text_to_media(parts, play, generate_all, target):
    """Generate audio and video for each actor in the script
    
    Arguments:
        story_out {str} -- path to the output dir
        play {bool} -- whether to play the generated media
        generate_all {bool} -- whether to generate all media
    """
    for i, part in enumerate(parts):
        if not (part.generated or generate_all):
            continue
        if part.media == "audio":
            if part.generated or generate_all:
                if not play:
                    actor_dir = f"{target}/{part.actor}"
                    filename = os.path.join(actor_dir, f"/{i + 1}.mp3")
                    os.system(f"say -v {part.voice} -o {filename} {part.text}")
                else:
                    os.system(f"say -v {part.voice} {part.text}")
    

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
    for chapter in glob(f"{story_template}*.txt"):
        target = chapter.replace(story_template, story_out).split(".txt")[0]
        template = parse_template(chapter)
        story = fill_template_gpt(template)
        write_parts(story, target, "story_en.txt")
        story_de = translate_parts(story)
        write_parts(story_de, target, "story_de.txt")
        text_to_media(story_de, play, generate_all, target)


if __name__ == "__main__":
    main()