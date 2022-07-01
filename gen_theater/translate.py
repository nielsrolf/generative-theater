from gen_theater.main import *
import os


@click.command()
@click.argument("story", type=click.Path(exists=True))
def main(story: str):
    """Iterate through all chapter and generate media
    
    Arguments:
        story: path to the ready text file
    """
    story_en = parse_template(story)
    story_de = translate_parts(story_en)
    target = os.path.dirname(os.path.realpath(story))
    write_parts(story_de, target, "story_de.txt")


if __name__ == "__main__":
    main()
  