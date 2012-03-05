#!/usr/bin/env python

import argparse
import os
import shutil
import filecmp
from string import Template

import markdown2

import settings

def main():
    """Handle command line arguments, control flow"""

    parser = argparse.ArgumentParser(description='Generate a static website by \
                                        rendering new and modified files.')
    parser.add_argument('--clean', dest='to_clean', action='store_const',
                         const=True, default=False,
                         help='Clear the output directory and exit.')
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
    """Return html file given a raw conent file."""
    template = os.path.join(settings.template_path, get_template(file))
    with open(template) as template_file:
        template_string = Template(template_file.read())

    return template_string.safe_substitute(parse_content(file))

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

def process_content():
    """Take raw content from content directory and render it to the output
    directory.

    Doesn't replace files that haven't changed.
    """
    if not os.path.exists(settings.output_path):
        os.mkdir(settings.output_path)

    # Render content, put it in output directory
    for root, dirs, files in os.walk(settings.content_path):
        for file in files:
            # render content files
            if file.endswith('.cnt'):
                output = render(os.path.join(root,file))
                outpath = os.path.join(settings.output_path,
                                       file.replace('.cnt', '.html', 1))
                # don't bother copying if there is no change
                if not diff(output, outpath):
                    with open(outpath, 'w') as outfile:
                        outfile.write(output)
            # just copy other files (images, etc)
            else:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(settings.output_path, file)
                # only copy if the file is new or changed
                if (not os.path.exists(dest_file) or
                   not filecmp.cmp(src_file, dest_file)):
                        shutil.copy(os.path.join(root, file), 
                                    os.path.join(settings.output_path, file))

def diff(string, path):
    """See if a string is the same as the contents of a file

    Return true if the string and file are the same
    """
    if not os.path.exists(path):
        return False
    with open(path) as file:
        return file.read() == string

main()

