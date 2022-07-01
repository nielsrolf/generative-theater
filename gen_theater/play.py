from gen_theater.main import *
import os


@click.command()
@click.argument("story", type=click.Path(exists=True))
def main(story: str):
    """Iterate through all chapter and generate media
    
    Arguments:
        story: path to the ready text file
    """
    story_de = parse_template(story)
    text_to_media(story_de, True, True)


if __name__ == "__main__":
    main()
  