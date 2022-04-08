from glob import glob
import os
from typing import List
import nlpcloud



story_in = "story"
story_out = "media/1"


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
    client = nlpcloud.Client("fast-gpt-j", KEY, True)
    for i, part in enumerate(parts):
        if part.text == "<generate>":
            prompt = create_prompt(parts[:i + 1])
            part.text = client.generation(prompt,
                min_length=10,
                max_length=50,
                length_no_input=False,
                remove_input=True,
                end_sequence="\n",
                top_p=1,
                temperature=0.8,
                top_k=50,
                repetition_penalty=1,
                length_penalty=1,
                do_sample=True,
                early_stopping=False,
                num_beams=1,
                no_repeat_ngram_size=0,
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
    print("\n".join(str(i) for i in parts))


def main(story_in: str, story_out: str):
    """Iterate through all chapter and generate media
    
    Arguments:
        story_in -- path to the dir with the template story
        story_out -- path to the dir where the generated media will be stored
    """
    os.makedirs(story_out, exist_ok=True)
    for chapter in glob(f"{story_in}/*.txt"):
        generate_chapter(chapter, chapter.replace(story_in, story_out))


if __name__ == "__main__":
    main("story", "media")