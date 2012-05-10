#!/usr/bin/env python

import argparse
import codecs
import os
import shutil
import filecmp
from string import Template

import markdown2

import settings


class Category:
    """Represent a category of pages such as 'posts'. 
    
    A category consists of a name and a list of pages.
    """
    def __init__(self, name):
        self.name = name
        self.pages = []

    # list of all categories
    categories = []

    @staticmethod
    def get_category(name):
        for c in Category.categories:
            if c.name == name:
                return c
            else:
               return None

    def add_page(self, path, title):
        """Add a rendered page to this category."""
        self.pages.append((path, title))

    def build_index(self):
        """Build an index page listing the pages in this category.

        The index will be called <self.name>.html and placed in the root of the
        output directory.
        """
        link_list = '<ul>'
        for page in self.pages:
            link_list += '<li><a href="{}">{}</a></li>'.format(page[0], page[1])
        link_list += '</ul>'

        replacement_dict = {'title':self.name, 'body':link_list}

        with codecs.open(settings.category_index_template, 'r', 'utf-8') as template_file:
            template = Template(template_file.read())

        index_path = os.path.join(settings.output_path, self.name) + '.html'
        with codecs.open(index_path, 'w', 'utf-8') as index_file:
            index_file.write(template.safe_substitute(replacement_dict))


def main():
    """Handle command line arguments, control flow"""

    parser = argparse.ArgumentParser(description='Generates a static website by \
                                        rendering new and modified files.')
    parser.add_argument('--clean', dest='to_clean', action='store_const',
                         const=True, default=False,
                         help='Clears the output directory and exit.')
    parser.add_argument('--refresh', dest='to_refresh', action='store_const',
                         const=True, default=False,
                         help='Empties the output directory before generating.')
    args = parser.parse_args()

    if args.to_clean:
        clean()
    elif args.to_refresh:
        clean()
        process_content()
    else:
        process_content()

    for category in Category.categories:
        category.build_index()

def clean():
    """Delete the contents of the output directory"""
    for root, dirs, files in os.walk(settings.output_path):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

def render(file):
    """Return html string given a raw content file."""
    template = os.path.join(settings.template_path, read_template(file))
    with codecs.open(template, 'r', 'utf-8') as template_file:
        template_string = Template(template_file.read())

    return template_string.safe_substitute(parse_content(file))

def read_template(path):
    """Get the template name from a content file.

    If the content file doesn't specify a template, return the default
    from the settings file.
    """
    with codecs.open(path, 'r', 'utf-8') as content:
        if content.readline().strip() == '#template':
            return content.readline().strip()
        else:
            return settings.default_template

def read_category(path):
    """Get the category name from a content file.

    If the content file doesn't specify a category return None
    """
    with codecs.open(path, 'r', 'utf-8') as content:
        prevline = '' 
        for line in content:
            if prevline.strip() == '#category':
                return line.strip()
            else:
                prevline = line

def read_title(path):
    """Get the titlefrom a content file.

    If the content file doesn't specify a title return None
    """
    with codecs.open(path, 'r', 'utf-8') as content:
        prevline = '' 
        for line in content:
            if prevline.strip() == '#title':
                return line.strip()
            else:
                prevline = line

# TODO test then use this, delete the other read funcs
def read_element(path, element_name):
    """Get the value of a tag in a content file

    Specify the path of the content file and the name of the tag you want.
    eg "content/blog/post1.cnt" and "title".
    """
    with codecs.open(path, 'r', 'utf-8') as content:
        prevline = ''
        for line in content:
            if prevline.strip() == '#'+element_name:
                return line.strip()
            else:
                prevline = line

def parse_content(path):
    """Parse a content file, returning a dictionary of tag names mapped
    to tag content.

    Content in the #body tag is processed as markdown
    """
    content_dict = {}
    with codecs.open(path, 'r', 'utf-8') as raw_post:
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
        for file in sorted(files, key=lambda f:os.path.getmtime(os.path.join(root, f))):
            # render content files
            if file.endswith('.cnt'):
                server_path = file.replace('.cnt', '.html', 1)
                output = render(os.path.join(root, file))
                outpath =  os.path.join(root, server_path).replace(settings.content_path,
                                                       settings.output_path)
                category_name = read_category(os.path.join(root, file)) 
                title = read_title(os.path.join(root, file))
                if category_name:
                    if category_name not in [c.name for c in Category.categories]:
                        new_category = Category(category_name)
                        new_category.add_page(server_path, title)
                        Category.categories.append(new_category)
                    else:
                        Category.get_category(category_name).add_page(server_path, title)
                        
                # don't bother copying if there is no change
                if not diff(output, outpath):
                    if not os.path.exists(os.path.dirname(outpath)):
                        os.mkdir(os.path.dirname(outpath))
                    with codecs.open(outpath, 'w', 'utf-8') as outfile:
                        outfile.write(output)
            # just copy other files (images, etc)
            else:
                # ignore vim's swap files
                if file.endswith(('swp', 'swo')):
                    continue
                src_file = os.path.join(root, file)
                dest_file = src_file.replace(settings.content_path,
                                             settings.output_path)
                
                # make destination directory if needed
                if not os.path.exists(os.path.dirname(dest_file)):
                    os.mkdir(os.path.dirname(dest_file))

                # only copy if the file is new or changed
                if (not os.path.exists(dest_file) or
                   not filecmp.cmp(src_file, dest_file)):
                        shutil.copy(src_file, dest_file)

def diff(string, path):
    """See if a string is the same as the contents of a file

    Return true if the string and file are the same
    """
    if not os.path.exists(path):
        return False
    with codecs.open(path, 'r', 'utf-8') as file:
        return file.read() == string

main()

