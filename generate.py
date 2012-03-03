#!/usr/bin/env python

import os
from string import Template
import markdown2

import settings
def main():
    for root, dirs, files in os.walk(settings.content_path):
        for file in files:
            if file.endswith('.cnt'):
                render(os.path.join(root,file))


def render(file):
    template = os.path.join(settings.template_path, get_template(file))
    with open(template) as template_file:
        template_string = Template(template_file.read())

    out_file = file.replace(settings.content_path,
                            settings.output_path, 1).replace(
                            '.cnt', '.html', 1)
    if not os.path.exists(os.path.dirname(out_file)):
        os.makedirs(os.path.dirname(out_file))
    with open(out_file, 'w') as out_file:
        out_file.write(template_string.safe_substitute(parse_content(file)))

def get_template(path):
    with open(path) as content:
        if content.readline().strip() == '#template':
            return content.readline().strip()
        else:
            return settings.default_template

def parse_content(path):
    content_dict = {}
    with open(path) as raw_post:
        for line in raw_post.readlines():
            if line.startswith('#'):
                current_tag = line.strip('#\n')
                content_dict[current_tag]= ''
            else:
                content_dict[current_tag] += line

    body = content_dict.get('body', '')
    content_dict['body'] = markdown2.markdown(body)

    return content_dict

main()
