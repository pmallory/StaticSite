import os

# The outward facing url (needed for feed links)
url = 'http://www.pmallory.com'

# where to find templates
template_path = './templates'
digest_template = os.path.join(template_path, 'digest.tmpl')
feed_template = os.path.join(template_path, 'feed.xml')

# where to find content
content_path = './content'

# where to output the rendered site
output_path = './www'

# template to use for category index pages
category_index_template = './templates/base.tmpl'

