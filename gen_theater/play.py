from gen_theater.main import *


@click.command()
@click.argument("story", type=click.Path(exists=True))
def main(story: str):
    """Iterate through all chapter and generate media
    
    Arguments:
        story: path to the ready text file
    """
    story_en = parse_template(story)
    story_de = translate_parts(story_en)
    text_to_media(story_de, True, True)


if __name__ == "__main__":
    main()
  