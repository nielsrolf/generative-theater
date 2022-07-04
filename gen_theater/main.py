from dataclasses import dataclass
from glob import glob
import os
from typing import List
from xmlrpc.client import boolean
import nlpcloud
import openai
import deepl 
import click
from tqdm import tqdm


from gen_theater import secrets


def system(prompt):
    print(prompt)
    os.system(prompt)


voices = {
    "Luzia": "Anna",
    "Marin": "Markus",
    "Kriemhild": "Yannick"
}


shortnames = {
    "kriemhild": "ki",
    "luzia": "lu",
    "marin": "x",
}

CHAR_LIMIT = 900

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
        if "):" in raw:
            actor, raw = raw.split(" (", 1)
            media, text = raw.split("): ", 1)
            text = text.strip()
        else:
            actor, text = raw.split(":", 1)
            media = "audio"
            text = text.strip()
        return Part(raw, actor, media, text, False, voices.get(actor, "Anna"))
    
    def __str__(self):
        return f"{self.actor} ({self.media}): {self.text}"
    
    def shortstr(self):
        return f"{self.actor}: {self.text}"
    
    def translate(self):
        text_de = translate(self.text)
        return Part(self.raw, self.actor, self.media, text_de, self.generated, self.voice)


# def fill_template_gpt(parts: List[Part]) -> List[Part]:
#     """Replace <generate> with generated text from GPT"""
#     client = nlpcloud.Client("gpt-neox-20b", secrets.NLPCLOUD, True)
#     # client = nlpcloud.Client("fast-gpt-j", secrets.NLPCLOUD, True)
#     story = []
#     for i, part in enumerate(parts):
#         if part.text == "<generate>":
#             prompt = create_prompt(story + [part])
#             print(f"PROMPT: {prompt}", end="\n" + "-" * 80 + "\n")
#             text = client.generation(prompt,
#                 min_length=10,
#                 max_length=50,
#                 length_no_input=True,
#                 remove_input=True,
#                 end_sequence="\n",
#                 top_p=1,
#                 temperature=1,
#                 top_k=50,
#                 repetition_penalty=2,
#                 length_penalty=1,
#                 do_sample=True,
#                 early_stopping=False,
#                 num_beams=1,
#                 no_repeat_ngram_size=3,
#                 num_return_sequences=1,
#                 bad_words=None,
#                 remove_end_sequence=False
#             )['generated_text'].strip()
#             story.append(Part(part.raw, part.actor, part.media, text, True, part.voice))
#         else:
#             story.append(part)
#     return story

def postprocess_gpt_text(text):
    """Do some heuristics to fix frequent formatting errors"""
    """ Replace ... Marin: ... with:
    ...
    Marin (audio): ...
    """
    text = text.replace("Maren", "Marin")
    for actor in voices:
        text = text.replace(f"{actor}:", f"\n{actor} (audio): ")
        text = text.replace(f"{actor} (audio) :", f"\n{actor} (audio): ")
    text = text.replace("\n[", "\nStage directions (audio): ")
    text = text.replace("\n(", "\nStage directions (audio): ")
    text = text.replace("\n{", "\nStage directions (audio): ")

    while "  " in text:
        text = text.replace("  ", " ")
    text = text.replace("\n ", "\n")

    text = text.split("http")[0] # if gpt starts talking about random websites we dont want that

    return text    

def fill_template_gpt3(parts: List[Part], min_length=10000) -> List[Part]:
    """Replace <generate> with generated text from GPT"""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    story = []
    for i, part in enumerate(parts):
        if part.text == "<generate>":
            prompt = create_prompt(story + [part])[-CHAR_LIMIT:]
            print(f"PROMPT: {prompt}", end="\n" + "-" * 80 + "\n")
            try:
                response = openai.Completion.create(
                    model="davinci",
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=1800,
                    top_p=1,
                    frequency_penalty=1,
                    presence_penalty=0
                )
            except Exception as e:
                print(f"Could not generate text: {type(e)}{e}")
                breakpoint()
                print(len(prompt))

            text = response.choices[0].text
            text = postprocess_gpt_text(text)
            text = text.split("\n")#.split("\n")[0]
            story.append(Part(part.raw, part.actor, part.media, text[0], True, part.voice))
            for line in text[1:]:
                try:
                    story.append(Part.parse(line))
                except:
                    print(f"Could not parse line: {line}")
                    break
        else:
            story.append(part)
    return continue_story(story, min_length)


def continue_story(story: List[Part], min_length=10000) -> List[Part]:
    """Continue the story with generated text from GPT"""
    full_prompt = create_prompt(story)
    while len(full_prompt) < min_length:
        prompt = full_prompt[-CHAR_LIMIT:]
        try:
            text = openai.Completion.create(
                model="davinci",
                prompt=prompt,
                temperature=0.7,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=1,
                presence_penalty=0
            ).choices[0].text
            text = postprocess_gpt_text(text).split("\n")
        except Exception as e:
            print(f"Could not generate text: {type(e)}{e}")
            breakpoint()
            print(len(prompt))
        for line in text[1:]:
            try:
                story.append(Part.parse(line))
            except:
                print(f"Could not parse line: {line}")
                break
        full_prompt = create_prompt(story)
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
        # prompt += part.shortstr() + "\n"
        prompt += str(part) + "\n"
    prompt += f"{parts[-1].actor} ({parts[-1].media}):"
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
        parts = []
        for line in f.readlines():
            line = line.strip()
            if line == "":
                continue
            try:
                parts.append(Part.parse(line))
            except:
                print(line)
                parts[-1].text += line
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
    result = translator.translate_text(text, target_lang=lang, formality="less") 
    translated_text = result.text
    return translated_text


def text_to_media(parts, play, generate_all, target=None):
    """Generate audio and video for each actor in the script
    
    Arguments:
        story_out {str} -- path to the output dir
        play {bool} -- whether to play the generated media
        generate_all {bool} -- whether to generate all media
    """
    for i, part in tqdm(enumerate(parts)):
        next_actor = parts[i + 1].actor if i < len(parts) - 1 else part.actor
        if next_actor == part.actor:
            hint = part.actor
        else:
            hint = f"{part.actor} zu {next_actor}"

        if not (part.generated or generate_all):
            continue
        if part.media == "audio":
            print(part.actor)
            text = part.text.replace("'", "")
            if part.generated or generate_all:
                if target is not None:
                    actor_dir = f"{target}/{part.actor}"
                    filename = os.path.join(actor_dir, f"{i + 1}.wav")
                    os.makedirs(actor_dir, exist_ok=True)
                    system(f"say -o {filename} --data-format=LEF32@22050 '{text}'")
                if play:
                    actor_short = shortnames.get(part.actor.lower(), part.actor)
                    system(f"say -v {part.voice} '{actor_short}: {text}'")
    

@click.command()
@click.argument("story_template", type=click.Path(exists=True))
@click.argument("story_out", type=click.Path())
@click.option("--generate", is_flag=True, help="auto-play the generated media")
@click.option("--play", is_flag=True, help="auto-play the generated media")
@click.option("--generate_all", is_flag=True,
            help=" whether to generate all media or just the new ones (<generate> replacements)")
def main(story_template: str, story_out: str, generate: bool = True, play: bool = False, generate_all: bool = True):
    """Iterate through all chapter and generate media
    
    Arguments:
        story_template -- path to the dir with the template story
        story_out -- path to the dir where the generated media will be stored
        play -- whether to auto-play the generated media
        generate_all -- whether to generate all media or just the new ones
            (<generate> replacements)
    """
    generate = generate or generate_all
    os.makedirs(story_out, exist_ok=True)
    for chapter in glob(f"{story_template}*.txt"):
        target = chapter.replace(story_template, story_out).split(".txt")[0]
        if generate:
            template = parse_template(chapter)
            story = fill_template_gpt3(template)
            write_parts(story, target, "story_en.txt")
            story_de = translate_parts(story)
            write_parts(story_de, target, "story_de.txt")
            text_to_media(story_de, play, generate_all, target)
        else:
            story_de = parse_template(f"{target}/story_de.txt")
            text_to_media(story_de, play, True, target)


if __name__ == "__main__":
    main()
  