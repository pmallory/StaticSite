#!/usr/bin/env python

import os
from string import Template

import settings

def render(file):
    template = os.path.join(settings.template_path, get_template(file))
    with open(template) as template_file:
        template_string = Template(template_file.read())

    out_name = os.path.basename(file).split('.')[0]+'.html'
    with open(os.path.join(settings.output_path, out_name), 'w') as out_file:
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

    return content_dict

for root, dirs, files in os.walk(settings.content_path):
    for file in files:
        if file.endswith('.cnt'):
            render(os.path.join(root,file))


