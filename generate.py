import os
from string import Template

import settings

def render(file, template):
    template = os.path.join(template,'post.tmpl')
    with open(template) as template_file:
        template_string = Template(template_file.read())
    print template_string.safe_substitute(title='tits')

for root, dirs, files in os.walk(settings.content_path):
    for file in files:
        if file.endswith('.pst'):
            render(os.path.join(root,file), settings.template_path)


