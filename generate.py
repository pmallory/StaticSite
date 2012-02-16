import os
from string import Template

import settings

def render(file, template):
    template = os.path.join(template,'post.tmpl')
    with open(template) as template_file:
        template_string = Template(template_file.read())
    print template_string.safe_substitute(parse_content(file))

def parse_content(path):
    content_dict = {}
    with open(path) as raw_post:
        for line in raw_post.readlines():
            if line.startswith('#'):
                current_tag = line.strip('#\n')
                content_dict[current_tag]= ''
            else:
                content_dict[current_tag] += line

    print content_dict
    return content_dict

        

for root, dirs, files in os.walk(settings.content_path):
    for file in files:
        if file.endswith('.pst'):
            render(os.path.join(root,file), settings.template_path)


