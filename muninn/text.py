import os
import re

from muninn.common import logger


def get_non_comment_lines(text):
    pure_text = []
    for line in text.split('\n'):
        li = line.strip()
        if not li.startswith("#"):
            pure_text.append(line.rstrip())
    # return result without any empty lines
    return [line for line in pure_text if line]


def extract_value_from_tags(text_input,
                            opening_tag="<!s>",
                            closing_tag="</!s>"):
    rstr = opening_tag + '(.*?)' + closing_tag

    return re.findall(rstr, text_input)


def replace_tags(text_input, key, value,
                 opening_tag="<!s>", closing_tag="</!s>"):
    # Not most efficient maybe, but okay for my simple use case
    return text_input.replace(opening_tag + key + closing_tag,  # Look For
                              value)  # Replace by


def get_params(fn_sample):
    if not os.path.exists(fn_sample):
        logger.error("\"%s\" does not exist. Can't load sample file.",
                     fn_sample)
        return None
    else:
        with open(fn_sample, 'r') as f_sample:
            d_sample = f_sample.read()
            return extract_value_from_tags(d_sample)