#!/usr/bin/env python

import argparse
import os
import shutil
from string import Template

import markdown2

import settings

def main():
    """Handle command line arguments, control flow"""

    parser = argparse.ArgumentParser(description='Generate a static website.')
    parser.add_argument('--clean', dest='to_clean', action='store_const',
                         const=True, default=False,
                         help='Clear the output directory.')
    parser.add_argument('--refresh', dest='to_refresh', action='store_const',
                         const=True, default=False,
                         help='Empty the output directory before generating.')
    args = parser.parse_args()

    if args.to_clean:
        clean()
    elif args.to_refresh:
        clean()
        process_content()
    else:
        process_content()

def clean():
    """Delete the output directory"""
    shutil.rmtree(settings.output_path)

def render(file):
    """Generate an html file given a raw conent file.

    Overwrites files that already exist.
    """
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
    """Get the template name from a content file.

    If the content file doesn't specify a template, return the default
    from the settings file.
    """
    with open(path) as content:
        if content.readline().strip() == '#template':
            return content.readline().strip()
        else:
            return settings.default_template

def parse_content(path):
    """Parse a content file, returning a dictionary of tag names mapped
    to tag content.

    Content in the #body tag is processed as markdown
    """
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

